---
name: claude-delegate
description: "Use this skill to delegate bounded coding, refactoring, or investigation tasks to an isolated subordinate CLI agent process. The orchestrator maintains executive oversight, generates self-contained task briefs, enforces execution timeouts and sandboxes, audits generated git diffs, and controls final commit and merge landing gates."
domain: ai-engineering
category: agents
subcategory: claude_delegate
tags:
  - agent-delegation
  - subagent-orchestration
  - cli-process-supervision
  - git-diff-review
  - sandboxed-execution
  - supervisory-control
technologies:
  - Python
  - Subprocess
  - Git
  - JSON
  - POSIX-Signals
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

# Subordinate Agent Process Delegation & Supervision Standard

## Overview

The `claude-delegate` skill establishes the supervisory protocol, execution sandbox, and quality-gate workflow for delegating concrete software tasks to an external subordinate coding process (such as a separate CLI agent session or background subagent). In hierarchical agentic systems, the primary agent acts as the **Orchestrator** (owning project architecture, requirements scoping, diff auditing, and git commit landing), while the subordinate process acts as the **Implementer** (working inside a confined working tree to produce code changes). This pattern prevents primary context pollution, isolates risky experimental modifications, and enforces independent code review before changes are merged.

```
+-----------------------------------------------------------------------------------+
|                        Orchestrator - Subagent Delegation Loop                    |
|                                                                                   |
|  [ Orchestrator Agent ]                                                           |
|         |                                                                         |
|         v                                                                         |
|  [ 1. Synthesize Delegation Brief ] <--- Explicit Goal, Target Files, Test Cmd    |
|         |                                                                         |
|         v                                                                         |
|  [ 2. Subprocess Dispatcher ]                                                     |
|         |-- Spawn subordinate CLI process with timeout (e.g. 180s)                |
|         |-- Pipe brief via stdin / temporary task manifest                        |
|         |                                                                         |
|         v                                                                         |
|  [ 3. Process Execution & Telemetry Capture ]                                     |
|         |                                                                         |
|         v                                                                         |
|  [ 4. Git Diff Forensic Audit ]                                                   |
|         |-- Verify modified files match allowed scope whitelist                   |
|         |-- Scan diff for suspicious deletions or security leaks                  |
|         |                                                                         |
|         v                                                                         |
|  [ 5. Verification Gate (Run Test Command) ]                                      |
|    /                    \                                                         |
|   / (Pass)               \ (Fail)                                                 |
|  v                        v                                                       |
| [ Land Change ]          [ Reject Diff & Revert / Escalate ]                      |
| (git commit / PR)                                                                 |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When an orchestrating agent wants to offload an intensive, multi-step coding task to a clean subordinate subagent to keep the primary conversation context uncluttered.
- When the user explicitly requests delegating a task to a background CLI coding process.
- When running exploratory refactors or test generation in an isolated branch or git worktree.
- When an independent verification and diff-review step is mandatory prior to landing code changes.

## When NOT to Use

- For trivial, single-line edits where spawning a separate subprocess introduces unnecessary latency.
- When the target CLI agent tool is not installed or lacks local environment credentials.
- When the task requires interactive human clarification in real time during implementation.

---

## Inputs & Prerequisites

1. **Delegation Brief**: Clear, unambiguous natural language instruction specifying exact objectives.
2. **Permitted Scope Whitelist**: List of files or directories the subordinate agent is authorized to modify.
3. **Verification Command**: Shell command required to prove that the subordinate's implementation is correct.
4. **Execution Timeout**: Maximum allowed runtime (in seconds) before the subagent process is terminated.

---

## Core Workflow

### Step 1: Author the Standalone Delegation Brief
The brief must be completely self-contained, as the subordinate process has no access to orchestrator chat history:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class DelegationBrief:
    task_id: str
    objective: str
    target_files: List[str]
    verification_command: str
    timeout_seconds: int = 180

def render_brief_markdown(brief: DelegationBrief) -> str:
    """Formats the delegation brief for the subagent stdin/manifest."""
    lines = [
        f"# Delegation Brief: {brief.task_id}",
        f"**Objective**: {brief.objective}",
        "",
        "## Authorized Scope (Do NOT modify files outside this list)",
    ]
    for f in brief.target_files:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append(f"## Mandatory Verification Command\n`{brief.verification_command}`")
    lines.append("Run this command before signaling task completion.")
    return "\n".join(lines)
```

### Step 2: Supervised Execution with Hard Timeouts
Execute the subordinate process with defensive watchdog monitoring:

```python
import subprocess
import sys

def dispatch_subordinate_process(cmd: list[str], input_brief: str, timeout: int) -> tuple[int, str, str]:
    """Spawns subagent process with strict timeout and output capturing."""
    try:
        proc = subprocess.run(
            cmd,
            input=input_brief,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Subordinate process exceeded timeout ({timeout}s) and was terminated."
```

### Step 3: Git Working Tree Diff Audit
The orchestrator inspects the working tree diff before committing:

```python
def audit_git_diff(allowed_files: List[str]) -> tuple[bool, List[str]]:
    """Inspects git status to ensure no out-of-scope files were mutated."""
    res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
    violations = []
    
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        status, filepath = line[:2], line[3:].strip()
        if filepath not in allowed_files:
            violations.append(filepath)
            
    return (len(violations) == 0, violations)
```

---

## Best Practices & Failure Modes

- **Never Blindly Commit**: Never execute `git commit -am` immediately after a subagent exits. Always inspect `git diff` and re-run test suites independently.
- **Hanging Processes**: Always set explicit timeouts on subprocess invocations to prevent orphaned subagents from hanging indefinitely on network or deadlock stalls.
- **Scope Creep Rejection**: If a subagent modifies `package.json` or unrelated files when tasked with a localized bug fix, reject the diff and rollback via `git restore`.

---

## Verification & Testing

1. Run the delegation supervisor and diff audit test suite:
   ```bash
   python scripts/claude-delegate_helper.py
   ```
2. Verify brief generation, diff auditing, and timeout guards via CLI:
   ```bash
   python scripts/subagent_delegation_supervisor.py --test-all
   ```
