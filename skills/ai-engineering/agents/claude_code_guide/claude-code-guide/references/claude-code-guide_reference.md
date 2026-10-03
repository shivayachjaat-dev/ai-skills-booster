# CLI Autonomous Coding Agent Directives Technical Reference

## 1. Context Optimization & Memory Architecture (`CLAUDE.md`)

When autonomous coding agents execute inside a terminal environment, repository guidelines must be compact, explicit, and actionable:

```
[ Session Initialization ]
            |
            v
[ Parse CLAUDE.md / AGENT.md ] ---> Injects verified build, test, and style invariants
            |
            v
[ Agent System Prompt Context Budget ]
  Total Budget: 200k tokens
  Guidelines allocation: < 1k tokens (0.5% of context window)
```

### Why Brevity Matters:
- Every line in `CLAUDE.md` is re-injected on every turn or session start.
- Bloated narrative documents dilute the LLM's attention, causing it to disregard critical architectural constraints.
- Stick to factual command lines and atomic bullet points.

---

## 2. Shell Command Sandbox & Non-Interactive Invariants

Autonomous execution requires zero-friction command execution:

| Operation Type | Interactive Flaw | Safe Non-Interactive Form |
| :--- | :--- | :--- |
| **Package Install** | Prompts for confirmation `[y/N]` | `npm install --yes` or `pip install --no-input` |
| **Test Runner** | Watch mode keeps process open | `npm test -- --watchAll=false` or `pytest -q` |
| **Git Operations** | Opens interactive vim editor for commit msg | `git commit -m "feat: description"` |
| **Destructive Commands**| Overwrites or purges working directory | Prohibited by policy; fail-closed gate |

---

## 3. Pre-Commit Quality Verification Loop

Before concluding any automated coding turn, the agent must execute:
1. **Linter / Formatter**: Fix formatting defects automatically (`ruff format`, `prettier --write`).
2. **Type Checker**: Verify no type safety regressions (`mypy`, `tsc --noEmit`).
3. **Targeted Unit Tests**: Execute tests covering the modified functions to ensure 100% pass rate.
