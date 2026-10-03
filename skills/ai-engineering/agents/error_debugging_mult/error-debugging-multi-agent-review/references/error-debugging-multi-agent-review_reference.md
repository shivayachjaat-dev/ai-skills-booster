# Multi-Agent Error Debugging & Triaging Reference

## Multi-Perspective Root Cause Analysis (RCA) Protocol

Complex production defects—particularly race conditions, intermittent distributed failures, and memory leaks—are notoriously difficult for single-agent systems to diagnose because individual models often fall into cognitive confirmation traps. Multi-agent review deploys complementary investigative roles to challenge and cross-examine hypotheses.

### Role Specialization Matrix

| Reviewer Role | Primary Focus | Evaluated Artifacts |
| :--- | :--- | :--- |
| **Trace Analyzer** | Frame traversal, dereferences, type safety, argument bounds | Stack traces, AST call sites, local variable state |
| **Concurrency Auditor** | Lock contention, async lifecycle, deadlocks, shared state | Async runtimes, thread pools, mutex guards, queue backpressure |
| **Regression Investigator** | Recent git commits, schema changes, dependency bumps | Git diffs, PR logs, semver upgrades, environment drift |
| **Remediation Synthesizer** | Hypothesis weighting, patch generation, regression test strategy | Aggregated reports, unit test frameworks, CI gate configs |

### Conflict Resolution & Consensus Engine

1. **Independent Evaluation**: Each reviewer independently formulates a hypothesis with a confidence score `[0.0 - 1.0]` and concrete supporting evidence.
2. **Cross-Examination**: Reviewers highlight conflicting assumptions (e.g. Trace Analyzer claiming deterministic failure vs Concurrency Auditor identifying nondeterministic thread starvation).
3. **Consensus Ranking**: The highest-confidence hypothesis backed by verified line-level evidence is promoted to Primary Root Cause, while secondary signals are documented as Contributing Factors.
