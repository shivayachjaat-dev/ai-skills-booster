---
name: zustand-state-management-patterns
description: "Use this skill when designing, structuring, and optimizing global client-side state in React applications using Zustand. It guides the agent through the slice pattern for modular domain separation, persistent middleware (localStorage/IndexedDB), selector optimization with shallow equality, DevTools debugging, and async action flows."
domain: frontend
category: state-management
subcategory: zustand
tags:
  - zustand
  - react
  - state-management
  - typescript
  - frontend
  - hooks
technologies:
  - Zustand
  - React 18+
  - TypeScript
  - Redux DevTools
complexity: intermediate
maturity: stable
tools:
  - npm
  - pnpm
dependencies:
  - zustand >= 4.5.0
  - react >= 18.2.0
---
# Zustand Enterprise State Management Architecture

## Overview

A production guide for architecting lightweight, boilerplate-free global state in React applications using Zustand. This skill instructs AI agents on organizing complex stores using the Slice Pattern, preventing unnecessary component re-renders through atomic selectors and shallow equality checks, handling persistent state synchronization with storage backends, and integrating Redux DevTools.

## When to Use

- Managing cross-component UI state, authentication tokens, shopping carts, or user preferences in React.
- Replacing heavy Redux / Redux Toolkit setups with minimal, unopinionated stores.
- Accessing or updating state outside of React component trees (e.g. inside Axios/Fetch interceptors).
- Preventing widespread re-render cascades in high-frequency update UIs.

## When NOT to Use

- Server state caching and synchronization with REST/GraphQL APIs (use TanStack React Query or SWR).
- Local ephemeral form inputs where standard `useState` or `useReducer` suffices.

## Inputs & Prerequisites

- React 18+ application initialized with TypeScript.
- Zustand installed: `npm install zustand`.

## Core Workflow

### 1. The Slice Pattern for Modular State
Divide large applications into separate typed slices and combine them into a single root store:

```typescript
// store/slices/authSlice.ts
import { StateCreator } from 'zustand';

export interface UserProfile {
  id: string;
  name: string;
  role: 'admin' | 'member';
}

export interface AuthSlice {
  user: UserProfile | null;
  isAuthenticated: boolean;
  login: (userData: UserProfile) => void;
  logout: () => void;
}

export const createAuthSlice: StateCreator<AuthSlice> = (set) => ({
  user: null,
  isAuthenticated: false,
  login: (userData) => set({ user: userData, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
});
```

```typescript
// store/slices/cartSlice.ts
import { StateCreator } from 'zustand';

export interface CartItem {
  id: string;
  title: string;
  quantity: number;
  price: number;
}

export interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (itemId: string) => void;
  clearCart: () => void;
}

export const createCartSlice: StateCreator<CartSlice> = (set) => ({
  items: [],
  addItem: (newItem) =>
    set((state) => {
      const existing = state.items.find((i) => i.id === newItem.id);
      if (existing) {
        return {
          items: state.items.map((i) =>
            i.id === newItem.id ? { ...i, quantity: i.quantity + newItem.quantity } : i
          ),
        };
      }
      return { items: [...state.items, newItem] };
    }),
  removeItem: (itemId) =>
    set((state) => ({ items: state.items.filter((i) => i.id !== itemId) })),
  clearCart: () => set({ items: [] }),
});
```

```typescript
// store/useAppStore.ts (Root Store with Middleware)
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { AuthSlice, createAuthSlice } from './slices/authSlice';
import { CartSlice, createCartSlice } from './slices/cartSlice';

export type RootStore = AuthSlice & CartSlice;

export const useAppStore = create<RootStore>()(
  devtools(
    persist(
      (...a) => ({
        ...createAuthSlice(...a),
        ...createCartSlice(...a),
      }),
      {
        name: 'app-storage',
        // Only persist cart items; do not persist session state to localStorage
        partialize: (state) => ({ items: state.items }),
      }
    ),
    { name: 'AppStore' }
  )
);
```

### 2. Selective Subscriptions & Avoiding Re-Renders
Never consume the whole store (`const store = useAppStore()`). Subscribe strictly to specific selectors using shallow equality:

```tsx
// components/cart-badge.tsx
import React from 'react';
import { useAppStore } from '@/store/useAppStore';
import { useShallow } from 'zustand/react/shallow';

export const CartBadge: React.FC = () => {
  // Only re-renders when the derived count changes!
  const itemCount = useAppStore((state) =>
    state.items.reduce((sum, item) => sum + item.quantity, 0)
  );

  return <span className="badge">{itemCount}</span>;
};
```

### 3. Imperative State Access Outside React
Access and mutate state in vanilla TypeScript functions (e.g. HTTP interceptors):

```typescript
// lib/api-client.ts
import axios from 'axios';
import { useAppStore } from '@/store/useAppStore';

export const apiClient = axios.create({ baseURL: '/api' });

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Trigger logout action directly without React component hooks
      useAppStore.getState().logout();
    }
    return Promise.reject(error);
  }
);
```

## Best Practices & Failure Modes

1. **Object Selector Without Shallow Check**: Doing `const { items, addItem } = useAppStore((s) => ({ items: s.items, addItem: s.addItem }))` generates a new object reference on every render, triggering an infinite re-render loop. Use atomic selectors (`useAppStore(s => s.items)`) or `useShallow`.
2. **Server State Duplication**: Storing paginated API responses in Zustand leads to stale data bugs and complex manual synchronization. Use Zustand for client/UI state and React Query for server cache.
3. **Persisting Sensitive Tokens to localStorage**: Persisting raw JWT tokens via `persist` middleware exposes tokens to XSS attacks. Store authentication tokens in HTTP-only cookies.

## Verification & Testing

- Verify state updates in Jest/Vitest:
  ```typescript
  import { useAppStore } from '@/store/useAppStore';

  it('adds item to cart correctly', () => {
    useAppStore.getState().clearCart();
    useAppStore.getState().addItem({ id: '1', title: 'Widget', quantity: 2, price: 10 });
    
    expect(useAppStore.getState().items).toHaveLength(1);
    expect(useAppStore.getState().items[0].quantity).toBe(2);
  });
  ```
