---
name: cmux
description: "Use this skill to orchestrate, monitor, and automate parallel AI coding agent sessions within terminal multiplexers. It manages hierarchical workspaces, split panes, and execution surfaces via IPC socket/CLI protocols, enabling programmatic session spawning, screen state capture, and keystroke dispatching."
domain: ai-engineering
category: agents
subcategory: cmux
tags:
  - terminal-multiplexing
  - cmux
  - parallel-agents
  - split-panes
  - session-orchestration
  - cli-automation
  - ipc-socket
technologies:
  - Python
  - Bash
  - Unix-Sockets
  - JSON-RPC
  - POSIX
  - Pty
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Terminal Multiplexer & Parallel Agent Session Standard

## Overview

The `cmux` skill defines the architecture, topology management, and programmatic control protocol for running concurrent, multi-agent AI coding sessions across terminal multiplexers. Coordinating multiple autonomous agents working on different branches, microservices, or verification suites requires structured process isolation. Without a dedicated multiplexer layer, parallel agents collide on stdout streams, clobber shared working directories, and fail to report granular execution status. This skill establishes programmatic control over hierarchical multiplexer structures (**Workspaces**, **Panes**, and **Surfaces**), enabling agents to inspect running processes, capture terminal screen buffers, and dispatch commands safely.

```
+-----------------------------------------------------------------------------------+
|                     Terminal Multiplexer Session Topology                         |
|                                                                                   |
|  [ Multiplexer Window ]                                                           |
|         |                                                                         |
|         +---> [ Workspace 1: feature-auth (git worktree /auth) ]                   |
|         |        |                                                                |
|         |        +-- [ Pane 1: Agent CLI (Surface 1) ] <--- Code Synthesizer      |
|         |        `-- [ Pane 2: Test Runner (Surface 2) ] <--- Continuous Pytest   |
|         |                                                                         |
|         `---> [ Workspace 2: refactor-db (git worktree /db) ]                     |
|                  |                                                                |
|                  +-- [ Pane 1: Agent CLI (Surface 3) ] <--- Migration Agent       |
|                  `-- [ Pane 2: Local DB Container (Surface 4) ]                   |
|                                                                                   |
|  [ IPC Socket Controller (/tmp/multiplexer.sock or CLI) ]                         |
|         |-- list-panes, list-surfaces                                             |
|         |-- send-keys --surface surface:N "cmd\n"                                 |
|         `-- read-screen --surface surface:N                                       |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When managing or monitoring multiple AI coding agents running in parallel across separate terminals or worktrees.
- When an orchestrator agent needs to inspect background dev servers, build watchers, or log output without killing the active process.
- When programmatically splitting panes, switching workspaces, or capturing terminal screens for diagnostic analysis.
- When creating automated multi-agent environments with isolated visual and terminal state.

## When NOT to Use

- For single-process, linear command execution where standard shell execution (`subprocess.run` or bash tool) suffices.
- In headless container environments where no graphical multiplexer or terminal emulator is present.
- When interacting with web browser DOMs (use browser automation or generative UI skills instead).

---

## Inputs & Prerequisites

1. **Multiplexer IPC Socket or CLI**: Reachable control socket (e.g. Unix domain socket) or installed multiplexer CLI binary on PATH.
2. **Explicit Reference Target**: Fully-qualified prefixed reference (`workspace:N`, `pane:N`, `surface:N`).
3. **Environment Context**: Anchored `WORKSPACE_ID` or active branch directory.

---

## Core Workflow

### Step 1: Reference Syntax Validation
In terminal multiplexer automation, bare integer indexes cause silent target collisions. Always parse and enforce strict prefixed reference syntax:

```python
import re
from typing import Tuple

REF_PATTERN = re.compile(r"^(workspace|pane|surface):([a-zA-Z0-9_\-]+)$")

def validate_multiplexer_ref(raw_ref: str, expected_type: str = None) -> Tuple[str, str]:
    """
    Parses and asserts valid multiplexer ref syntax (e.g. 'pane:12', 'surface:4').
    Rejects ambiguous bare integers (e.g. '12').
    """
    clean = raw_ref.strip()
    match = REF_PATTERN.match(clean)
    if not match:
        raise ValueError(
            f"Invalid reference '{raw_ref}'. Must be prefixed like '{expected_type or 'type'}:N'. "
            "Bare numbers are ambiguous indexes and prohibited."
        )
        
    ref_type, ref_id = match.groups()
    if expected_type and ref_type != expected_type:
        raise ValueError(f"Reference type mismatch: Expected '{expected_type}', got '{ref_type}'.")
        
    return ref_type, ref_id
```

### Step 2: Screen Buffer Capture & Ansi Sanitization
Read screen contents from a target surface and strip ANSI color/cursor escapes:

```python
import subprocess
import re

ANSI_ESCAPE_PATTERN = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def strip_ansi_escapes(raw_text: str) -> str:
    """Removes terminal escape codes to produce clean plain-text log data."""
    return ANSI_ESCAPE_PATTERN.sub("", raw_text)
```

### Step 3: Lifecycle Management & Automated Clean Up
When a subagent completes its task, close the allocated pane or workspace cleanly to release terminal memory and file descriptors.

---

## Best Practices & Failure Modes

- **Never Silence Stderr**: Never pipe multiplexer commands to `2>/dev/null`. Errors reveal reference type mismatches and missing target surfaces.
- **Surface-Targeted Reads**: Screen reading and pane captures must target the explicit surface ID, never the abstract pane or workspace.
- **Anchor to Workspace ID**: Always explicitly pass `--workspace "$WORKSPACE_ID"`; never assume the visually focused window is the current caller's workspace.

---

## Verification & Testing

1. Run the terminal multiplexer manager test suite:
   ```bash
   python scripts/cmux_helper.py
   ```
2. Verify reference parsing, screen sanitization, and topology modeling via CLI:
   ```bash
   python scripts/terminal_multiplexer_manager.py --test-all
   ```
