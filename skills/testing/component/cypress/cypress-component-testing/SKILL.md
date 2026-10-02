---
name: cypress-component-testing
description: "Use this skill when authoring, running, and debugging isolated component tests using Cypress Component Testing for React, Vue, or Angular. It guides the agent through mounting components in real browser DOMs, asserting visual states, stubbing network requests via cy.intercept, simulating user events, and verifying CSS animations without firing up full backend environments."
domain: testing
category: component
subcategory: cypress
tags:
  - cypress
  - component-testing
  - testing
  - frontend
  - react
  - vue
technologies:
  - Cypress
  - React
  - TypeScript
  - Vite
  - Webpack
complexity: intermediate
maturity: stable
tools:
  - cypress
  - npm
  - node
dependencies:
  - cypress >= 12.0
---
# Cypress Component Testing

## Overview

A guide for authoring and running fast, reliable component tests in real browser runtimes using Cypress Component Testing. Unlike traditional simulated DOM environments (jsdom) that lack real CSS rendering and layout engines, Cypress executes components directly within Chromium/Firefox, verifying real visual styling, event bubbling, and component lifecycles in complete isolation from backend servers.

## When to Use

- Testing complex interactive UI components (autocomplete search, data tables, modals, multi-step wizards) in isolation.
- Verifying CSS layout, styling, and visual rendering that jsdom cannot accurately simulate.
- Testing component prop variations and slot rendering in design systems and component libraries.
- Rapid test-driven development (TDD) of frontend components with real-time browser preview.

## When NOT to Use

- Full end-to-end user journeys requiring multiple page transitions and live backend databases (use `playwright-e2e-testing`).
- Pure algorithmic utility functions without UI rendering (use Vitest / Jest).

## Inputs & Prerequisites

- Frontend project with Cypress installed (`npm install -D cypress`).
- Component testing configured in `cypress.config.ts` (Vite, Webpack, or Next.js bundler).
- Component source file and TypeScript type definitions.

## Core Workflow

### 1. Configuration & Mounting Setup
Ensure `cypress.config.ts` enables component testing:
```typescript
import { defineConfig } from "cypress";

export default defineConfig({
  component: {
    devServer: {
      framework: "react",
      bundler: "vite",
    },
    specPattern: "src/**/*.cy.{js,jsx,ts,tsx}",
  },
});
```

### 2. Authoring Component Tests (Mounting & Interaction)
Mount the component with props and simulate user events:
```tsx
import React from "react";
import { UserProfileCard } from "./UserProfileCard";

describe("<UserProfileCard />", () => {
  it("renders user information and triggers onUpdate callback", () => {
    const onUpdateSpy = cy.spy().as("onUpdateSpy");
    
    // Mount component directly into real browser DOM
    cy.mount(
      <UserProfileCard
        user={{ id: "u_1", name: "Alice Smith", role: "Admin", email: "alice@example.com" }}
        onUpdateRole={onUpdateSpy}
      />
    );

    // Assert visual text and styling
    cy.get("[data-testid='user-name']").should("have.text", "Alice Smith");
    cy.get("[data-testid='user-role-badge']").should("have.class", "badge-admin");

    // Interact with form controls
    cy.get("select[name='role']").select("Editor");
    cy.get("button[type='submit']").click();

    // Verify spy was called with expected arguments
    cy.get("@onUpdateSpy").should("have.been.calledWith", "u_1", "Editor");
  });
});
```

### 3. Stubbing Network Calls with `cy.intercept`
When components make internal network calls (e.g. data fetching hooks), stub responses:
```tsx
it("displays loading spinner and handles API error state", () => {
  cy.intercept("GET", "/api/user/status", {
    statusCode: 500,
    body: { error: "Service unavailable" },
    delay: 500, // Simulate network latency
  }).as("getStatus");

  cy.mount(<UserStatusWidget userId="123" />);

  // Verify loading skeleton is visible
  cy.get(".skeleton-loader").should("be.visible");

  // Wait for intercepted API call
  cy.wait("@getStatus");

  // Verify error banner is rendered
  cy.get("[role='alert']").should("contain.text", "Unable to load status");
});
```

### 4. Testing Responsive Viewports & CSS States
Test component layouts across multiple screen sizes:
```typescript
it("collapses menu on mobile viewports", () => {
  cy.viewport(375, 667); // iPhone SE
  cy.mount(<NavigationDrawer />);
  
  cy.get(".desktop-menu").should("not.be.visible");
  cy.get(".hamburger-btn").should("be.visible").click();
  cy.get(".mobile-drawer").should("have.class", "drawer-open");
});
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Component depends on ThemeProvider or Redux Store | Wrap component in a custom mount command (`cy.mountWithProviders(<Component />)`) that injects necessary context wrappers. |
| Third-party icon or font loading race conditions | Pre-load web fonts and design system CSS in `cypress/support/component.ts`. |
| Flaky timing on CSS transitions/animations | Rely on Cypress automatic assertion retries (`should('be.visible')`) rather than hardcoded sleeps (`cy.wait(1000)`). |

## Validation & Acceptance Criteria

- [ ] Component tests execute in real browser DOM without requiring full backend services.
- [ ] Spies verify event callback arguments accurately.
- [ ] Network requests stubbed via `cy.intercept` to prevent external dependencies.
- [ ] Visual assertions test real computed CSS and element visibility.
- [ ] Tests pass in headless CI mode (`npx cypress run --component`).

## Failure Handling & Recovery

- If component fails to mount due to missing CSS styles, import global stylesheets (`import '../src/index.css'`) into `cypress/support/component.ts`.

## Expected Output & Artifacts

- Cypress component test specification files (`*.cy.tsx`).
- Custom provider mounting utilities in `cypress/support/component.ts`.
- Component test execution reports and screenshots on failure.

## Related Skills

- `react-component-architecture`
- `playwright-e2e-testing`
- `wcag-accessibility-audit`
