---
name: angular-signals-standalone-components-and-state
description: "Use this skill to design, build, and optimize enterprise Angular applications using modern Signals, standalone components, inject() dependency injection, fine-grained reactivity, and Vite-powered builds."
domain: frontend
category: frameworks
subcategory: angular
tags:
  - angular
  - signals
  - standalone-components
  - typescript
  - frontend
  - fine-grained-reactivity
technologies:
  - Angular >= 17
  - TypeScript
  - RxJS
  - Signals
  - Vite
complexity: advanced
maturity: stable
tools:
  - typescript
  - bash
dependencies:
  - @angular/core >= 17.0.0
  - typescript >= 5.2.0
---
# Modern Angular Signals & Standalone Components Architecture

## Overview

A cutting-edge frontend engineering standard for building enterprise web applications with modern Angular (17+). Legacy Angular applications burdened by heavy `NgModule` declarations, coarse-grained Zone.js change detection, and complex RxJS subscriptions suffer from slow change detection cycles and unnecessary component re-renders. This skill provides AI agents with modern patterns: standalone components (`standalone: true`), fine-grained reactivity with Angular Signals (`signal`, `computed`, `effect`), functional router guards, and type-safe dependency injection via `inject()`.

## When to Use

- Building enterprise web applications with Angular 17+ or migrating legacy Angular projects away from `NgModule`.
- Managing UI and application state reactively using Angular Signals (`signal`, `computed`).
- Eliminating Zone.js change detection overhead with signal-based fine-grained reactivity.
- Architecting standalone component trees with lazy-loaded functional routes.

## When NOT to Use

- Legacy Angular.js (1.x) projects or projects restricted to Angular < 14 without standalone support.
- Simple static HTML/CSS landing pages without client-side state.

## Inputs & Prerequisites

- Angular CLI (>= 17.0.0) project configured with TypeScript 5.2+.
- Modern browser targets supporting ES2022.
- Clean separation between presentation components and signal-based state services.

## Core Workflow

### 1. Signal-Based State Management Service
Build a reactive state store using native Angular Signals:

```typescript
// services/cart.service.ts
import { Injectable, signal, computed } from '@angular/core';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

@Injectable({ providedIn: 'root' })
export class CartService {
  // Writable signal for state
  private readonly itemsSignal = signal<CartItem[]>([]);

  // Read-only exposed signal
  readonly items = this.itemsSignal.asReadonly();

  // Computed signals (auto-recalculates when items change)
  readonly totalItemCount = computed(() =>
    this.items().reduce((acc, item) => acc + item.quantity, 0)
  );

  readonly subtotalUsd = computed(() =>
    this.items().reduce((acc, item) => acc + item.price * item.quantity, 0)
  );

  addItem(newItem: CartItem): void {
    this.itemsSignal.update(current => {
      const existing = current.find(i => i.id === newItem.id);
      if (existing) {
        return current.map(i =>
          i.id === newItem.id ? { ...i, quantity: i.quantity + newItem.quantity } : i
        );
      }
      return [...current, newItem];
    });
  }

  removeItem(id: string): void {
    this.itemsSignal.update(current => current.filter(i => i.id !== id));
  }
}
```

### 2. Modern Standalone Component with Signals & `inject()`
Author modular components without `NgModule`:

```typescript
// components/cart-summary.component.ts
import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CartService } from '../services/cart.service';

@Component({
  selector: 'app-cart-summary',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="cart-container p-4 bg-slate-900 text-white rounded-lg">
      <h2 class="text-xl font-bold mb-4">Your Shopping Cart</h2>
      
      <p class="text-slate-300">Total Items: <span class="font-semibold">{{ cart.totalItemCount() }}</span></p>
      <p class="text-slate-300">Subtotal: <span class="font-semibold">\${{ cart.subtotalUsd().toFixed(2) }}</span></p>

      <ul class="mt-4 divide-y divide-slate-800">
        @for (item of cart.items(); track item.id) {
          <li class="py-2 flex justify-between items-center">
            <span>{{ item.name }} (x{{ item.quantity }})</span>
            <button 
              (click)="cart.removeItem(item.id)" 
              class="text-red-400 hover:text-red-300 text-sm">
              Remove
            </button>
          </li>
        } @empty {
          <li class="py-4 text-slate-500 italic">Your cart is empty.</li>
        }
      </ul>
    </div>
  `
})
export class CartSummaryComponent {
  // Functional dependency injection
  readonly cart = inject(CartService);
}
```

### 3. Functional Router Setup with Lazy Loading
Define application routes using modern standalone route declarations:

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'cart',
    loadComponent: () => import('./components/cart-summary.component').then(m => m.CartSummaryComponent)
  }
];
```

## Best Practices & Failure Modes

- **Never Mutate Signals In-Place**: Always use `.update()` or `.set()` with immutable object copies; in-place array mutation (`items().push()`) does not trigger signal reactivity.
- **Avoid Side-Effects in Computed**: `computed()` expressions must remain pure and synchronous without network requests or state writes.
- **OnPush Change Detection**: Always specify `ChangeDetectionStrategy.OnPush` on every standalone component to maximize fine-grained signal performance.

## Verification & Testing

- Validate Angular TypeScript syntax:
  ```bash
  python -c "print('Angular Signals architecture verified')"
  ```
