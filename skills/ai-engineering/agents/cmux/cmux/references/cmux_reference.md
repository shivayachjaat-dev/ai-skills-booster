# Terminal Multiplexer & Agent Process Isolation Technical Reference

## 1. Multiplexer Structural Hierarchy

A terminal multiplexer models parallel processes as a tree:

```
[ Window (Display Container) ]
       |
       +---> [ Workspace (Project / Branch Context) ]
                  |
                  +---> [ Pane (Spatial Split Region) ]
                             |
                             +---> [ Surface (Terminal / Browser Tab) ]
```

### Reference Syntax Invariants:
- References must always be prefixed (`workspace:N`, `pane:N`, `surface:N`).
- Bare numbers are ambiguous indices and are rejected by automated validation to avoid routing commands to unintended terminals.

---

## 2. Screen Buffer Capture & Terminal Emulation

Reading the output of long-running agent tasks requires polling terminal buffer state:
1. **ANSI Sequences**: Raw buffers contain terminal escape codes (`\x1b[31m` colors, cursor jumps). The orchestrator must strip ANSI sequences before feeding logs into LLM contexts.
2. **Surface Target Specificity**: Captures must explicitly target the underlying surface ID rather than the parent pane.
3. **Non-Blocking Telemetry**: Invocations must read buffer snapshots asynchronously without sending SIGINT (`Ctrl+C`) to the running process.

---

## 3. Concurrency Safety for Multi-Agent Workspaces

When multiple agents run concurrently in a multiplexer:
- **Worktree Anchoring**: Each workspace should map to a distinct git worktree (`git worktree add`) to avoid git lock file collisions.
- **Dedicated Socket Paths**: IPC socket requests must include the explicit `WORKSPACE_ID` header to prevent cross-workspace contamination.
- **Graceful Teardown**: Upon task completion, close child surfaces cleanly with `exit` or SIGTERM before destroying parent panes.
