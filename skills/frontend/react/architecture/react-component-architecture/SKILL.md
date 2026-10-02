---
name: react-component-architecture
description: "Use this skill when designing, refactoring, and structuring scalable React component hierarchies. It enforces clean separation of concerns between presentational components and stateful containers, headless UI patterns, compound components, strict TypeScript prop contracts, and memoization boundaries."
domain: frontend
category: react
subcategory: architecture
tags:
  - react
  - frontend
  - component-architecture
  - typescript
  - ui-patterns
  - design-systems
technologies:
  - React
  - TypeScript
  - Tailwind CSS
  - shadcn/ui
complexity: advanced
maturity: stable
tools:
  - tsc
  - npm
dependencies:
  - react >= 18.0
  - typescript >= 4.5
---
# React Component Architecture

## Overview

A structured architectural guide for designing modular, accessible, testable, and high-performance React component trees. Establishes clean boundaries between business state and presentation, implements reusable compound component patterns, and prevents common re-rendering bottlenecks.

## When to Use

- Architecting new UI features or reusable design system component libraries.
- Refactoring bloated "god components" (monolithic files with 500+ lines mixing hooks, API calls, and JSX).
- Standardizing component props, polymorphic rendering (`asChild` pattern), and compound components.
- Fixing cascading re-render performance issues across deep component trees.

## When NOT to Use

- Pure backend Node.js services or CLI tools.
- Static HTML sites with zero client-side interactive state.

## Inputs & Prerequisites

- React 18+ and TypeScript development environment.
- Component requirements including interactive states (loading, empty, error, disabled, active).
- Design system tokens or styling framework (Tailwind CSS, CSS Modules).

## Core Workflow

### 1. Component Role Separation (Container vs Presenter)
Separate data orchestration from visual rendering:
- **Presenter Components**: Pure functions of props. Zero network side effects. Highly reusable and easily unit-tested in Storybook.
- **Container / Feature Hooks**: Encapsulate data fetching, mutations, and local state machines (`useUserProfile`).

### 2. Compound Component Pattern for Complex Interfaces
For flexible multi-part widgets (e.g. Modals, Dropdowns, Tabs, Accordions), use compound components sharing React Context:
```tsx
import React, { createContext, useContext, useState } from "react";

interface TabsContextType {
  activeTab: string;
  setActiveTab: (id: string) => void;
}
const TabsContext = createContext<TabsContextType | null>(null);

export function Tabs({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs-container">{children}</div>
    </TabsContext.Provider>
  );
}

export function TabTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("TabTrigger must be used within Tabs");
  const isActive = ctx.activeTab === value;
  return (
    <button
      role="tab"
      aria-selected={isActive}
      className={isActive ? "tab-active" : "tab-inactive"}
      onClick={() => ctx.setActiveTab(value)}
    >
      {children}
    </button>
  );
}
```

### 3. Strict Prop Contracts & Invariants
- Use explicit TypeScript interfaces.
- Avoid passing entire raw domain entities when only 2 fields are displayed (pass primitives or narrow interfaces to enable memoization).
- Use discriminating unions for mutually exclusive states:
```tsx
type ButtonProps =
  | { variant: "link"; href: string; onClick?: never }
  | { variant: "button"; href?: never; onClick: () => void };
```

### 4. Render Optimization & Boundary Isolation
- Push state down: Colocate state as close as possible to the leaves that consume it.
- Lift content up: Pass heavy child components as `children` prop so their re-render is decoupled from parent state updates.
- Wrap expensive calculations in `useMemo` and callbacks passed to memoized children in `useCallback`.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Deep prop drilling across > 3 layers | Introduce a scoped React Context or lightweight atomic state store (Zustand/Jotai). |
| Polymorphic rendering needed | Use Radix UI `Slot` / `asChild` pattern to compose functionality onto custom child elements without wrapper DOM pollution. |
| Server Components (Next.js App Router) | Default to Server Components for data fetching. Mark files with `'use client'` only where browser APIs, hooks, or event listeners are required. |

## Validation & Acceptance Criteria

- [ ] Components adhere to single-responsibility principle (< 200 lines per file).
- [ ] Strict TypeScript prop interfaces with zero `any` types.
- [ ] ARIA roles and keyboard navigation implemented for interactive elements.
- [ ] No unwanted re-rendering of siblings when typing in input controls.

## Failure Handling & Recovery

- If React renders in an infinite loop, check `useEffect` dependency arrays for objects or arrays instantiated inline inside the component body without `useMemo`.

## Expected Output & Artifacts

- Clean, modular component source files.
- Exported TypeScript type definitions.
- Unit and accessibility tests using React Testing Library.

## Related Skills

- `react-accessibility-audit`
- `browser-performance-profiling`
- `playwright-e2e-testing`
