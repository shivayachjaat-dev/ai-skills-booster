---
name: multi-agent-tmux-process-orchestrator
description: "Use this skill when managing, supervising, and coordinating multiple autonomous CLI coding agents and subprocesses across detached terminal sessions using tmux. It covers automated tmux session and pane lifecycle management, sending keystrokes and instructions (send-keys), monitoring stdout/stderr activity buffers, and auto-restarting stalled agent workers."
domain: ai-engineering
category: agents
subcategory: process-management
tags:
  - tmux
  - agent-orchestration
  - multi-agent
  - cli
  - process-management
  - automation
technologies:
  - tmux
  - Bash
  - Python subprocess
  - Linux
complexity: advanced
maturity: stable
tools:
  - tmux
  - python
  - bash
dependencies:
  - tmux >= 3.2
---
# Multi-Agent Terminal Orchestration with Tmux

## Overview

A definitive production engineering reference for managing, isolating, and supervising multiple autonomous CLI coding agents running in parallel across headless terminal sessions using `tmux`. Running autonomous agents in interactive foreground shells blocks developer environments and risks premature termination upon SSH disconnect. This skill instructs AI agents on spawning isolated background tmux sessions, multiplexing panes, piping prompts into running agent shells via `tmux send-keys`, capturing buffer snapshots for progress auditing, and terminating zombie workers.

## When to Use

- Running multiple concurrent CLI agents (e.g. frontend agent, backend agent, test runner agent) on a local workstation or remote server.
- Detaching and preserving agent executions across unstable SSH sessions.
- Automating inter-agent communication by inspecting terminal output buffers programmatically.
- Building autonomous agent supervisor daemons that monitor worker health.

## When NOT to Use

- Cloud container orchestration at scale across multiple physical nodes (use Kubernetes or Nomad).
- Pure programmatic Python agents communicating via queues or HTTP (use Celery or Redis Streams).

## Inputs & Prerequisites

- Linux or macOS environment with `tmux >= 3.2` installed.
- CLI coding agents installed in PATH (e.g. `claude`, `aider`, `agy`).

## Core Workflow

### 1. Programmatic Tmux Session Lifecycle in Python
Spawn, inspect, and manage detached tmux sessions using `subprocess`:

```python
import subprocess
import time

class TmuxAgentManager:
    def __init__(self, session_prefix: str = "agent"):
        self.session_prefix = session_prefix

    def _run_tmux(self, args: list[str]) -> str:
        res = subprocess.run(["tmux"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.stdout.strip()

    def spawn_agent(self, agent_id: str, command: str) -> str:
        session_name = f"{self.session_prefix}-{agent_id}"
        
        # Check if session exists
        if self.is_running(session_name):
            return f"Session {session_name} is already active."

        # Create new detached session running bash
        self._run_tmux(["new-session", "-d", "-s", session_name])
        time.sleep(0.2)

        # Launch agent command inside session
        self._run_tmux(["send-keys", "-t", session_name, command, "C-m"])
        return f"Spawned agent in detached tmux session '{session_name}'."

    def is_running(self, session_name: str) -> bool:
        sessions = self._run_tmux(["list-sessions", "-F", "#{session_name}"]).splitlines()
        return session_name in sessions

    def send_prompt(self, agent_id: str, prompt: str):
        session_name = f"{self.session_prefix}-{agent_id}"
        # Send text followed by Enter (C-m)
        self._run_tmux(["send-keys", "-t", session_name, prompt, "C-m"])

    def capture_output_buffer(self, agent_id: str, lines: int = 50) -> str:
        session_name = f"{self.session_prefix}-{agent_id}"
        # Capture last N lines from pane history
        return self._run_tmux(["capture-pane", "-p", "-t", session_name, "-S", f"-{lines}"])

    def terminate_agent(self, agent_id: str):
        session_name = f"{self.session_prefix}-{agent_id}"
        self._run_tmux(["kill-session", "-t", session_name])
```

### 2. Multi-Pane Workspace Split (Supervisor View)
Create a unified dashboard splitting one window into 3 agent panes:

```bash
#!/bin/bash
SESSION="dev-team"

# 1. Start session with Frontend Agent
tmux new-session -d -s $SESSION -n "agents" "agy --role frontend"

# 2. Split vertically for Backend Agent
tmux split-window -h -t $SESSION:0 "agy --role backend"

# 3. Split lower half for QA Test Agent
tmux split-window -v -t $SESSION:0.1 "agy --role qa"

# Attach to view all 3 agents working simultaneously
tmux attach-session -t $SESSION
```

## Best Practices & Failure Modes

1. **Unescaped Quotes in `send-keys`**: Sending prompts containing double quotes or special shell characters (`$`, `&`, `;`) directly to `send-keys` can execute unintended commands in bash. Always sanitize prompts or write them to temporary files and instruct the agent to read the file.
2. **Orphaned Sessions Leaking RAM**: Forgetting to terminate tmux sessions when agents complete tasks leaves long-running idle processes consuming memory. Implement idle timeouts that automatically kill sessions inactive for > 2 hours.
3. **Buffer Capture Truncation**: Default tmux scrollback buffer is 2000 lines. For verbose tasks, increase history limit in `~/.tmux.conf`: `set -g history-limit 50000`.

## Verification & Testing

- Verify active agent sessions:
  ```bash
  tmux list-sessions
  ```
- Capture snapshot of agent terminal:
  ```bash
  tmux capture-pane -p -t agent-backend -S -20
  ```
