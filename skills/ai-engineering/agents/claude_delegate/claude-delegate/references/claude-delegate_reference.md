# Subagent Process Delegation & Supervisory Control Technical Reference

## 1. Hierarchical Delegation Architecture

In complex multi-stage agent workflows, monolithic single-context execution degrades rapidly due to context saturation:

$$\text{Error Probability} \propto \frac{\text{Accumulated Token History}}{\text{Context Window Budget}}$$

### The Orchestrator-Implementer Pattern:
- **Orchestrator Role**: Manages overall task decomposition, maintains high-level architecture, evaluates diffs, and executes final git commits.
- **Implementer Role**: Ephemeral subagent process launched with a clean, focused task brief. Modifies the working tree, executes localized verification, and terminates.

```
[ Orchestrator Context (Clean) ]
              |
              +---> [ Spawn Subprocess: Implementer ] ---> [ Working Tree Edits ]
              |                                                   |
              | <--- [ Subprocess Returns: Exit Code & Logs ] <---+
              |
              v
[ Git Diff Inspection Gate ]
  1. Scope Whitelist Check
  2. Independent Test Suite Execution
  3. git commit / PR merge
```

---

## 2. Git Worktree Isolation vs. Working Tree Mutex

To prevent concurrent file mutation collisions:
1. **Serialized Working Tree**: When running a single subagent, the orchestrator freezes its own file edits while the subordinate process executes.
2. **Git Worktree Isolation**: For concurrent subagents, each process executes in an isolated worktree (`git worktree add ../temp-branch`), preventing write conflicts until explicit merge time.

---

## 3. Defensive Audit Checklist Before Landing

The orchestrator must verify four criteria before accepting a subagent's changes:
1. **Scope Confinement**: Only files explicitly whitelisted in the delegation brief were created, modified, or deleted.
2. **Deterministic Verification**: The required verification command exited with code 0.
3. **No Unintended Side-Effects**: Untracked configuration files or secret tokens were not deposited on disk.
4. **Clean Git Diff**: No cosmetic or stylistic refactoring beyond the bounded task scope.
