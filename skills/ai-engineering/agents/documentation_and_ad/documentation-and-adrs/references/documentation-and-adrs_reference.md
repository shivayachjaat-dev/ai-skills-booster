# Documentation and ADRs Technical Reference

## MADR 3.0 Standard & Decision Topology

In high-velocity software engineering—especially when autonomous agents make iterative code changes—unrecorded architectural decisions lead to architectural drift, regressions, and lost historical context. Architecture Decision Records (ADRs) capture the **Why**, the **Trade-offs**, and the **Downstream Consequences** of critical choices.

### ADR Lifecycle State Machine

```
   +-------------+
   |  Proposed   |
   +------+------+
          |
    +-----+-----+
    |           |
    v           v
+---+------+  +-+--------+
| Accepted |  | Rejected |
+---+------+  +----------+
    |
    v
+---+----------------------------+
| Superseded (by ADR-XXXX)       |
+--------------------------------+
```

### MADR Document Structure

Each record must contain:
1. **Title & Number**: Zero-padded identifier (e.g. `0004-isolate-tenant-workspaces.md`).
2. **Status**: Explicit state from `[Proposed, Accepted, Rejected, Deprecated, Superseded]`.
3. **Deciders**: List of participating architects, engineers, or autonomous agents.
4. **Context & Problem Statement**: What technical constraints or business drivers forced a choice.
5. **Decision Outcome**: What path was chosen and why alternatives were dismissed.
6. **Consequences**: Categorized into positive, negative, and neutral impacts.

### Agent Context Grounding

When an AI agent is instructed to refactor, upgrade dependencies, or alter APIs, it must first inspect `docs/adrs/README.md`. Decisions marked `Accepted` must be respected as invariants unless a new ADR is formally proposed to supersede them.
