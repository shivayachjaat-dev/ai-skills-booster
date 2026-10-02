---
name: code-simplification
description: "Use this skill when simplifying convoluted code, eliminating accidental complexity, unwinding deeply nested conditionals, and removing speculative abstractions. It guides the agent through guard clauses, cyclomatic complexity reduction, dead code pruning, and establishing transparent data flow."
domain: software-engineering
category: refactoring
subcategory: simplification
tags:
  - software-engineering
  - refactoring
  - clean-code
  - simplification
  - code-quality
technologies:
  - TypeScript
  - Python
  - Go
  - Rust
complexity: intermediate
maturity: stable
tools:
  - git
dependencies:
  - git >= 2.30
---
# Code Simplification

## Overview

Simplicity is a prerequisite for reliability. Complex code is hard to read, hard to test, and prone to edge-case bugs. This skill instructs the agent on systematically identifying and pruning accidental complexity, reducing cognitive load, collapsing deeply nested indentation, and removing over-engineered abstractions.

## When to Use

- A function or module exceeds 50 lines or has a cyclomatic complexity > 8.
- Code is indented more than 3 levels deep with nested `if/else` or `try/catch` blocks.
- Speculative generality ("we might need this in the future") has bloated interfaces with unused parameters and indirection.
- Code review identifies that logic is difficult to reason about or verify mentally.

## When NOT to Use

- High-performance hot paths where micro-optimizations or loop unrolling are explicitly required and benchmarked.
- Code that is already concise and straightforward.

## Inputs & Prerequisites

- Target source file and test suite.
- Working automated test coverage to verify that refactoring causes zero regressions.

## Core Workflow

### 1. Verification Gate Before Refactoring
Ensure test suite passes before touching any code:
```bash
npm test # or pytest / cargo test
```
If tests do not exist, write characterization tests first to capture current behavior.

### 2. Flattening Nested Logic with Early Return Guard Clauses
Replace deep nested `if-else` cascades with immediate inverted returns:
```typescript
// BEFORE: 4 levels of indentation
function processPayment(user, order) {
  if (user) {
    if (user.isActive) {
      if (order.items.length > 0) {
        return executeCharge(user, order);
      } else {
        throw new Error("Order is empty");
      }
    } else {
      throw new Error("User inactive");
    }
  } else {
    throw new Error("User missing");
  }
}

// AFTER: 1 level of indentation, crystal-clear control flow
function processPayment(user, order) {
  if (!user) throw new Error("User missing");
  if (!user.isActive) throw new Error("User inactive");
  if (order.items.length === 0) throw new Error("Order is empty");

  return executeCharge(user, order);
}
```

### 3. Eliminating Speculative Generalization (YAGNI)
- Remove unused interface methods, unread configuration flags, and dead variables.
- Replace generic factory-of-factories with direct instantiation unless multiple dynamic implementations actively exist today.
- Replace dynamic reflection with explicit typed calls.

### 4. Replacing Complex State Machines with Pure Transformations
- Where possible, replace mutable multi-step accumulator objects with pure functional array transformations (`map`, `filter`, `reduce`).
- Make data flow strictly unidirectional.

### 5. Regression Check
Re-run full test suite to guarantee semantic equivalence:
```bash
npm test
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Deep nesting required due to asynchronous callbacks | Convert callback-hell to modern `async/await` syntax with structured error boundaries. |
| Complex boolean expression `if (A && (!B || C) && (D || E))` | Extract into well-named descriptive boolean variables: `const isEligibleForDiscount = ...`. |
| Ambiguous edge cases in existing legacy code | Preserve existing behavior exactly unless the user has explicitly requested bug fixing alongside simplification. |

## Validation & Acceptance Criteria

- [ ] Cyclomatic complexity reduced significantly (maximum 3 nesting levels).
- [ ] 100% of pre-existing automated tests continue to pass without modification.
- [ ] Code line count reduced without compromising readability or type safety.
- [ ] No speculative layers of indirection remain.

## Failure Handling & Recovery

- If a test fails after refactoring, use `git diff` to locate the exact logic discrepancy, revert that specific change, and re-test.

## Expected Output & Artifacts

- Clean, readable, and simplified source code.
- Verification test run report showing zero regressions.

## Related Skills

- `code-review-and-quality`
- `test-driven-development`
- `api-and-interface-design`
