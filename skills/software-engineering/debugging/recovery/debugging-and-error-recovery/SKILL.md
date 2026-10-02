---
name: debugging-and-error-recovery
description: "Use this skill when diagnosing obscure bugs, production failures, memory leaks, race conditions, or unhandled exceptions. It enforces scientific hypothesis-driven debugging, minimal reproduction synthesis, stack trace isolation, binary search bisecting, and permanent regression test installation."
domain: software-engineering
category: debugging
subcategory: recovery
tags:
  - debugging
  - troubleshooting
  - error-recovery
  - root-cause-analysis
  - software-engineering
technologies:
  - Git
  - Python
  - TypeScript
  - GDB
  - Node.js
complexity: advanced
maturity: stable
tools:
  - git
  - node
  - python
dependencies:
  - git >= 2.30
---
# Debugging and Error Recovery

## Overview

A disciplined, scientific methodology for diagnosing and resolving complex software defects. Rather than guessing or making random changes ("shotgun debugging"), this skill guides the agent through forming falsifiable hypotheses, isolating minimal reproductions, bisecting regressions, verifying root causes, and locking in fixes with automated regression tests.

## When to Use

- An application crashes or throws uncaught exceptions in production or staging.
- Flaky tests, intermittent race conditions, or concurrency deadlocks occur.
- Performance degrades or memory usage grows continuously over time (memory leaks).
- A regression is introduced into a large codebase and the causal commit is unknown.

## When NOT to Use

- Simple, obvious syntax or compiler errors that are directly explained by the language compiler.
- General feature development or planned refactoring.

## Inputs & Prerequisites

- Stack trace, error logs, or user bug report detailing unexpected vs expected behavior.
- Access to the codebase and test execution runner.

## Core Workflow

### 1. Minimal Reproduction Creation
Never attempt to fix a bug you cannot reliably reproduce:
1. Isolate the smallest possible script, unit test, or curl command that triggers the failure.
2. Confirm the test fails consistently (100% of the time, or a known statistical frequency for race conditions).

### 2. Scientific Hypothesis Generation & Falsification
1. Formulate 2 to 3 distinct, testable hypotheses:
   - *Hypothesis A*: Database transaction commits before asynchronous event completes.
   - *Hypothesis B*: Deserialization fails on null values in newly added schema field.
2. Design a fast test to disprove each hypothesis:
   - Inspect variables with targeted breakpoints or strategic structured logging.
   - Never leave temporary logging statements in production code.

### 3. Binary Search Regression Bisecting (When Cause is Historical)
If the bug worked previously but is now broken:
```bash
git bisect start
git bisect bad HEAD
git bisect good <KNOWN_WORKING_COMMIT_OR_TAG>
git bisect run npm test
```
Git will automatically isolate the exact commit that introduced the regression.

### 4. Root Cause Surgical Remediation
- Fix the underlying architectural or logical defect, not merely the symptom (do not simply wrap failing code in an empty `try/catch` block).
- Ensure error states fail fast and explicitly rather than silently propagating invalid state downstream.

### 5. Automated Regression Test Locking
Before closing the issue:
1. Convert the minimal reproduction into a permanent automated test in the repository test suite.
2. Verify the test fails on unpatched code and passes cleanly on the patched code.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Non-deterministic race condition / heisenbug | Run reproduction loop under simulated high CPU/network latency or use concurrency stress tools (e.g. `--repeat-each=100`). |
| Third-party vendor library bug | Verify against upstream issue tracker. Create a minimal reproduction and implement a defensive local adapter/workaround while tracking upstream fix. |
| Production emergency outage | Prioritize immediate mitigation (rollback or feature flag deactivation) before deep root cause investigation. |

## Validation & Acceptance Criteria

- [ ] Bug reproduced in an isolated test environment.
- [ ] Root cause definitively proven with evidence (not speculative).
- [ ] Fix addresses root cause without breaking existing functionality.
- [ ] Permanent regression test added to test suite.
- [ ] Post-mortem or bug summary documented.

## Failure Handling & Recovery

- If a proposed fix creates secondary regressions in adjacent modules, revert the patch immediately and re-evaluate initial assumptions.

## Expected Output & Artifacts

- Minimal regression test suite file.
- Clean, surgical patch resolving root cause.
- Diagnostic root cause analysis summary.

## Related Skills

- `code-simplification`
- `test-driven-development`
- `observability-and-instrumentation`
