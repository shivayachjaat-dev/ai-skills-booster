# Agent Session Handoff Reference

## Standard Protocol for Autonomous Agent Context Transfer

During extended software engineering tasks, conversational context windows accumulate tool outputs, command logs, and transient debugging chatter. Uncompressed context slows down inference, increases cost, and degrades attention mechanisms. The **Handoff Protocol** distills state into a high-density Markdown document for successor agents.

### Context Lifecycle

```
    [ Extended Agent Session (~50k+ tokens) ]
                       |
                       v
            [ Handoff Compiler ]
       - Objective & Acceptance Criteria
       - Systemic Invariants & Discovered Constraints
       - Progress: Completed vs In-Progress vs Blocked
       - Modified file inventory
       - Explicit Immediate Next Step
                       |
                       v
       [ Compact Handoff Brief (~400 tokens) ]
                       |
                       v
       [ Successor Agent Bootstrapped Cleanly ]
```

### Essential Handoff Elements

1. **Deterministic Objective**: Explicit definition of what "done" looks like.
2. **Discovered Invariants**: Hard rules uncovered during the task (e.g., "Do not alter table X schema", "Must support Python 3.10").
3. **Execution Milestone**: Exact inventory of completed files vs pending edits.
4. **Actionable Directive**: Successor agents must not spend tokens guessing what to do next; the brief concludes with an unambiguous command or code edit.
