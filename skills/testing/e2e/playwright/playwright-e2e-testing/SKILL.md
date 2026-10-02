---
name: playwright-e2e-testing
description: "Use this skill when authoring, debugging, and maintaining end-to-end (E2E) automated browser test suites using Playwright. It guides the agent through resilient locator strategies (user-facing role/text), page object models, network mocking, authenticated session caching, parallel execution, and flaky test elimination."
domain: testing
category: e2e
subcategory: playwright
tags:
  - playwright
  - testing
  - e2e
  - browser-automation
  - qa
  - ci-cd
technologies:
  - Playwright
  - TypeScript
  - Node.js
  - Chromium
complexity: advanced
maturity: stable
tools:
  - npx
  - playwright
  - node
dependencies:
  - @playwright/test >= 1.35
---
# Playwright E2E Testing

## Overview

A production-grade methodology for writing robust, maintainable, and deterministic end-to-end browser tests using Microsoft Playwright. Eliminates test flakiness through auto-waiting, resilient role-based locators, authenticated storage state caching, and comprehensive trace inspection.

## When to Use

- Writing automated regression test suites for critical user journeys (signup, checkout, onboarding, settings).
- Debugging intermittent test failures or race conditions in CI pipelines.
- Establishing test fixtures with pre-authenticated sessions or seeded database states.
- Running multi-browser cross-platform matrix testing (Chromium, Firefox, WebKit, Mobile).

## When NOT to Use

- Isolated pure function logic or algorithmic unit tests (use Vitest / Jest).
- Backend unit testing of database queries without UI involvement.

## Inputs & Prerequisites

- Node.js project with `@playwright/test` installed.
- Running application server or baseURL configured in `playwright.config.ts`.

## Core Workflow

### 1. Resilient Locator Strategy
Always prefer user-visible locators over fragile CSS selectors or XPath:
```typescript
// GOOD: Resilient, accessible locators
page.getByRole("button", { name: "Submit Order" });
page.getByLabel("Email Address");
page.getByTestId("checkout-summary"); // Safe fallback when semantic roles are ambiguous

// BAD: Fragile, brittle selectors that break on style changes
page.locator(".btn-primary.submit-btn");
page.locator("div > div:nth-child(3) > button");
```

### 2. Page Object Model (POM) Design
Encapsulate page interactions inside reusable classes:
```typescript
import { type Page, type Locator, expect } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.submitButton = page.getByRole("button", { name: "Sign In" });
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, pass: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(pass);
    await this.submitButton.click();
    await expect(this.page).toHaveURL(/.*dashboard/);
  }
}
```

### 3. Authenticated Session Caching (Storage State)
Avoid logging in through the UI before every test. Authenticate once in a setup project and reuse saved cookies and localStorage:
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: "setup", testMatch: /.*\.setup\.ts/ },
    {
      name: "e2e tests",
      use: { storageState: "playwright/.auth/user.json" },
      dependencies: ["setup"],
    },
  ],
});
```

### 4. Flakiness Elimination & Auto-Waiting
- Never use arbitrary `page.waitForTimeout(5000)` sleeps.
- Rely on Playwright's built-in auto-waiting (`click`, `fill`, `check` automatically wait for element visibility, stability, and actionable state).
- Use web-first assertions with automatic retry:
  ```typescript
  await expect(page.getByText("Welcome back")).toBeVisible({ timeout: 10000 });
  ```

### 5. Network Mocking & API Interception
Mock unpredictable third-party APIs (Stripe, Twilio, analytics):
```typescript
await page.route("**/api/payments/charge", async (route) => {
  await route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ success: true, transactionId: "mock_tx_123" }),
  });
});
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Test fails only in headless CI environment | Enable trace recording on retry (`trace: 'on-first-retry'`) and inspect trace using `npx playwright show-trace trace.zip`. |
| Flaky timing on dynamic animations | Disable animations in Playwright config or wait for specific network requests (`page.waitForResponse(...)`). |
| Multi-tab or popup windows | Listen for popup event: `const [popup] = await Promise.all([page.waitForEvent('popup'), page.getByRole('button').click()]);`. |

## Validation & Acceptance Criteria

- [ ] Tests run successfully in headless mode across all target browsers.
- [ ] No arbitrary sleeps (`waitForTimeout`) present in test code.
- [ ] Authentication setup isolates user sessions efficiently.
- [ ] CI pipeline captures screenshots and traces on test failure.

## Failure Handling & Recovery

- If a test fails intermittently, run it in repeat-each mode: `npx playwright test --repeat-each=20` to reproduce and isolate race conditions.

## Expected Output & Artifacts

- Clean test specification files (`tests/e2e/*.spec.ts`).
- Modular Page Object Model files (`tests/models/*.ts`).
- HTML test execution reports (`playwright-report/`).

## Related Skills

- `browser-testing-with-devtools`
- `react-component-architecture`
- `ci-cd-and-automation`
