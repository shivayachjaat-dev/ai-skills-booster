---
name: e2e-acceptance-testing-orchestrator
description: "Use this skill when orchestrating end-to-end acceptance testing pipelines, behavior-driven development (BDD) workflows, and automated issue acceptance verification. It guides the agent through converting user stories into executable Gherkin specifications, integrating Playwright and Behave/Cucumber, managing test data fixtures, and enforcing release acceptance criteria."
domain: testing
category: acceptance-testing
subcategory: bdd-orchestration
tags:
  - acceptance-testing
  - bdd
  - cucumber
  - gherkin
  - playwright
  - testing
  - qa
technologies:
  - Gherkin
  - Python Behave
  - Playwright
  - pytest
  - GitHub Actions
complexity: advanced
maturity: stable
tools:
  - behave
  - playwright
  - python
dependencies:
  - behave >= 1.2.6
  - playwright >= 1.40.0
---
# E2E Acceptance Testing & BDD Orchestration Architecture

## Overview

A definitive production testing standard for driving end-to-end acceptance verification using Behavior-Driven Development (BDD). By translating product requirements and user stories into unambiguous, executable Gherkin specifications (`Given-When-Then`), engineering, product, and QA align on definition-of-done. This skill instructs AI agents on authoring clean feature files, implementing reusable step definitions with Playwright, isolating test databases, and integrating automated acceptance gates into release pipelines.

## When to Use

- Validating critical business user journeys (checkout flows, account onboarding, permission downgrades).
- Automating acceptance criteria verification directly from issue tracker specifications.
- Fostering collaboration between product managers, developers, and QA using human-readable feature files.
- Preventing regressions in complex cross-service workflows before merging release candidates.

## When NOT to Use

- Low-level unit testing of mathematical algorithms or utility functions (use `pytest` or Jest directly).
- Micro-benchmarking database query latency.

## Inputs & Prerequisites

- Running staging or local preview environment of the application.
- Python 3.10+ with `behave` and `playwright` installed.
- Documented acceptance criteria for target features.

## Core Workflow

### 1. Declarative Gherkin Feature File (`features/checkout.feature`)
Express business acceptance criteria in plain, structured English:

```gherkin
Feature: Customer Checkout & Order Placement
  As an authenticated customer
  I want to checkout items in my cart
  So that I can purchase products securely

  Background:
    Given the store catalog has an item "Wireless Headphones" with price "$99"
    And a registered customer "alice@example.com" is logged in

  Scenario: Successful checkout with valid payment
    Given the customer has added "Wireless Headphones" to their cart
    When they navigate to the checkout page
    And they enter shipping address:
      | Street         | City       | PostalCode | Country |
      | 123 Main St    | Metropolis | 10001      | US      |
    And they complete payment with valid credit card
    Then an order confirmation screen is displayed
    And the customer receives an order confirmation email with subject "Your Order Confirmation"
    And the cart is emptied
```

### 2. Step Definitions Implementation with Playwright
Execute browser automation corresponding to each step:

```python
# features/steps/checkout_steps.py
from behave import given, when, then
from playwright.sync_api import Page, expect

@given('the store catalog has an item "{item_name}" with price "{price}"')
def step_catalog_setup(context, item_name, price):
    # Seed test database via backend API fixture
    context.api_client.seed_catalog_item(name=item_name, price=price)

@given('a registered customer "{email}" is logged in')
def step_customer_logged_in(context, email):
    context.page.goto(f"{context.base_url}/login")
    context.page.fill('input[name="email"]', email)
    context.page.fill('input[name="password"]', "TestPassword123!")
    context.page.click('button[type="submit"]')
    expect(context.page.locator('.navbar-user')).to_contain_text(email)

@given('the customer has added "{item_name}" to their cart')
def step_add_to_cart(context, item_name):
    context.page.goto(f"{context.base_url}/products")
    context.page.click(f'button[data-item="{item_name}"]')

@when('they navigate to the checkout page')
def step_navigate_checkout(context):
    context.page.goto(f"{context.base_url}/checkout")

@when('they enter shipping address')
def step_enter_shipping(context):
    row = context.table[0]
    context.page.fill('input[name="street"]', row["Street"])
    context.page.fill('input[name="city"]', row["City"])
    context.page.fill('input[name="postal_code"]', row["PostalCode"])

@when('they complete payment with valid credit card')
def step_submit_payment(context):
    context.page.click('button#submit-order')

@then('an order confirmation screen is displayed')
def step_verify_confirmation(context):
    expect(context.page.locator('h1.confirmation-heading')).to_be_visible()
    expect(context.page.locator('.order-id')).not_to_be_empty()
```

### 3. Environment Lifecycle Hooks (`features/environment.py`)
Launch and teardown headless browser instances per scenario:

```python
from playwright.sync_api import sync_playwright

def before_all(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)
    context.base_url = "http://localhost:3000"

def before_scenario(context, scenario):
    context.page = context.browser.new_page()

def after_scenario(context, scenario):
    if scenario.status == "failed":
        # Capture failure screenshot for debugging
        context.page.screenshot(path=f"screenshots/failed_{scenario.name.replace(' ', '_')}.png")
    context.page.close()

def after_all(context):
    context.browser.close()
    context.playwright.stop()
```

## Best Practices & Failure Modes

1. **Brittle Selectors**: Using fragile XPath or DOM layout selectors (`div > div:nth-child(3) > button`) causes tests to break whenever CSS layout changes. Use semantic user-facing locators (`getByRole('button', { name: 'Submit' })` or `data-testid`).
2. **Shared State Pollution Between Scenarios**: Relying on database state created by a previous scenario causes cascade failures when tests run in arbitrary order. Every scenario must be completely isolated and seed its own fresh test data.
3. **Flaky Hardcoded Sleeps**: Using `time.sleep(5)` slows tests down and fails on busy CI nodes. Use Playwright's auto-waiting assertions (`expect(locator).to_be_visible()`).

## Verification & Testing

- Run the full acceptance test suite:
  ```bash
  behave features/
  ```
- Run tests filtered by specific feature tag:
  ```bash
  behave --tags=@smoke features/
  ```
