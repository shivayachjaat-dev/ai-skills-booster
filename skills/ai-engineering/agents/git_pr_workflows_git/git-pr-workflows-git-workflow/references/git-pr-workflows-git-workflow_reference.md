# Git PR Workflows & Guarded Merge Reference

## Branch Topology & Automated PR Specification

In agentic software engineering, changes produced by autonomous coding agents must adhere strictly to repository branching models, commit specifications, and automated review standards before entering integration branches.

### Automated PR Lifecycle

```
    [ Working Tree Changes ]
               |
               v
    [ Branch Validation ]      ---> feat/*, fix/*, refactor/*
               |
               v
    [ Pre-Commit Test Gate ]   ---> pytest, linters, coverage check
               |
               v
    [ Conventional Commits ]   ---> type(scope): imperative message
               |
               v
    [ PR Body Synthesis ]      ---> Changes, Touched Files, Test Proof
               |
               v
    [ Remote Push & Guard Gate]---> gh pr create / CI validation
```

### Conventional Commit Types

| Type | Intended Workload |
| :--- | :--- |
| `feat` | New feature or capability introduced to codebase |
| `fix` | Bug fix or regression remediation |
| `refactor` | Code restructuring without altering external functionality |
| `perf` | Performance improvement or latency reduction |
| `test` | Adding or updating unit/integration test coverage |
| `docs` | Documentation, ADR, or markdown changes |
| `chore` | Build script, dependency bump, or configuration update |

### Guarded Merge Invariants

1. **Zero Secret Policy**: Pre-commit hooks scan for API tokens, private keys, and passwords.
2. **Atomic Commits**: Each commit represents a coherent, buildable increment.
3. **Automated Evidence**: Pull Requests must include verifiable test output or reproduction scripts proving the fix.
