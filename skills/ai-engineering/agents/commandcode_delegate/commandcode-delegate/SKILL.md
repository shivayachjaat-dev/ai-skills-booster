---
name: commandcode-delegate
description: "Use this skill to delegate bounded coding, refactoring, or review tasks to the Command Code CLI agent process. It manages permission autonomy modes (read-only exploration vs. permissioned execution), constructs structured delegation briefs, audits git diffs against allowed file scopes, and verifies test suites prior to landing changes."
domain: ai-engineering
category: agents
subcategory: commandcode_delegate
tags:
  - commandcode-cli
  - agent-delegation
  - permission-autonomy
  - subagent-supervision
  - git-diff-review
  - landing-gates
technologies:
  - Python
  - Subprocess
  - Git
  - JSON
  - CommandCode-CLI
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Command Code CLI Agent Delegation & Autonomy Standard

## Overview

The `commandcode-delegate` skill specifies the invocation protocol, permission safety boundaries, and verification workflow for delegating software engineering tasks to the **Command Code CLI** (`cmd` or `cmdc`). When orchestrating subordinate coding tools, the orchestrating agent retains executive control, drafting a standalone implementation brief and auditing the resultant code modifications. Because headless CLI agents operate with distinct autonomy levels (read-only inspection vs. full-access execution), this skill formalizes permission boundaries, git diff forensics, and mandatory test suite verification prior to merging code changes.

```
+-----------------------------------------------------------------------------------+
|                     Command Code CLI Delegation Pipeline                          |
|                                                                                   |
|  [ Orchestrator Agent Context ]                                                   |
|         |                                                                         |
|         v                                                                         |
|  [ Autonomy Mode Gate ]                                                           |
|    /                  \                                                           |
|   / (Inspection)       \ (Implementation)                                         |
|  v                      v                                                         |
| [ READ-ONLY MODE ]     [ FULL AUTONOMY MODE ]                                     |
| (-p flag: read/grep)   (--dangerously-skip-permissions in confined worktree)       |
|         |                      |                                                  |
|         +----------------------+                                                  |
|                                |                                                  |
|                                v                                                  |
|             [ Dispatch Subordinate CLI Process ]                                  |
|               - Pass structured brief via stdin                                   |
|               - Enforce hard execution watchdog timeout                           |
|                                |                                                  |
|                                v                                                  |
|             [ Working Tree Git Diff Inspection Gate ]                             |
|               - Validate all modified files belong to authorized scope            |
|               - Reject unexpected dependency additions in package.json            |
|                                |                                                  |
|                                v                                                  |
|             [ Automated Acceptance Test Verification ]                            |
|                                |                                                  |
|                                v                                                  |
|             [ Land Change: git commit / Merge PR ]                                |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When delegating a focused implementation or investigation task to the Command Code CLI.
- When performing a read-only codebase exploration without risk of accidental file mutations.
- When the user explicitly requests delegation to `commandcode`.
- When offloading heavy syntax refactoring to a subordinate process while keeping the primary orchestrator context clean.

## When NOT to Use

- When the `cmd` / `cmdc` binary is not present or unauthenticated.
- For small inline edits where subagent invocation latency exceeds manual implementation.
- When tasks require interactive step-by-step guidance from the human user.

---

## Inputs & Prerequisites

1. **Target Autonomy Mode**: `read_only` (inspection only) or `implementation` (file mutation).
2. **Delegation Brief**: Focused instructions describing the goal, target files, and constraints.
3. **Authorized Scope Whitelist**: Exact file paths the subordinate process is permitted to alter.
4. **Acceptance Verification Command**: Shell command required to validate the output.

---

## Core Workflow

### Step 1: Autonomy Mode Configuration
Select the appropriate permission flags based on task risk:

```python
from typing import Dict, Any, List

def configure_commandcode_invocation(
    mode: str,
    target_files: List[str] = None
) -> Dict[str, Any]:
    """Configures CLI flags based on autonomy mode."""
    clean_mode = mode.lower().strip()
    if clean_mode not in ("read_only", "implementation"):
        raise ValueError("Mode must be 'read_only' or 'implementation'.")
        
    if clean_mode == "read_only":
        flags = ["-p"]  # Default read, grep, glob; writes refused
        is_mutating = False
    else:
        if not target_files:
            raise ValueError("Implementation mode requires an explicit target files whitelist.")
        flags = ["-p", "--dangerously-skip-permissions"]
        is_mutating = True
        
    return {
        "mode": clean_mode,
        "flags": flags,
        "is_mutating": is_mutating,
        "target_files": target_files or []
    }
```

### Step 2: Build the Standalone Brief
The brief contains everything needed for the subordinate run:

```markdown
# Command Code Delegation Brief

## Goal
Refactor database connection pool settings in `config/database.py`.

## Authorized Files
- `config/database.py`
- `tests/test_database.py`

## Acceptance Test
`pytest tests/test_database.py`
```

### Step 3: Git Working Tree Diff Verification Gate
Before committing, inspect `git status` and `git diff`:

```python
import subprocess

def audit_and_verify(allowed_files: list[str], test_cmd: str) -> bool:
    """Audits diff scope and executes verification harness."""
    res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
    changed = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    
    for c in changed:
        if c not in allowed_files:
            raise PermissionError(f"Scope violation: Command Code altered '{c}', which was not whitelisted.")
            
    test_run = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    return test_run.returncode == 0
```

---

## Best Practices & Failure Modes

- **Full-Trust Implementation Runs**: In `--dangerously-skip-permissions` mode, Command Code can access any file reachable by the user. Constrain runs by using clean git worktrees and tight scope briefs.
- **Dependency Invariant**: If an implementation run introduces new packages without explicit approval, reject the change.
- **Explicit Timeout**: Always wrap subordinate process calls with hard timeouts (e.g. 180 seconds) to terminate hung commands.

---

## Verification & Testing

1. Run the Command Code relay supervisor test suite:
   ```bash
   python scripts/commandcode-delegate_helper.py
   ```
2. Verify autonomy mode configuration and diff audit checks via CLI:
   ```bash
   python scripts/commandcode_relay_supervisor.py --test-all
   ```
