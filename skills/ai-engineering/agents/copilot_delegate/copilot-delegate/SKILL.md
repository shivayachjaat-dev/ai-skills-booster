---
name: copilot-delegate
description: "Use this skill to delegate bounded coding, refactoring, or planning tasks to the GitHub Copilot CLI agent. It manages reasoning effort dials (low to max), enforces plan versus act execution modes, audits working tree git diffs against strict scope whitelists, and validates acceptance test suites prior to landing changes."
domain: ai-engineering
category: agents
subcategory: copilot_delegate
tags:
  - copilot-cli
  - agent-delegation
  - reasoning-effort
  - plan-mode
  - subagent-supervision
  - git-diff-review
  - landing-gates
technologies:
  - Python
  - Subprocess
  - Git
  - JSON
  - Copilot-CLI
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

# GitHub Copilot CLI Agent Delegation & Supervision Standard

## Overview

The `copilot-delegate` skill specifies the invocation protocol, parameter sanitization, and verification gates for delegating engineering tasks to the **GitHub Copilot CLI** (`copilot`). In a hierarchical agent orchestration framework, the primary agent acts as the supervisor, formulating a self-contained delegation brief and retaining landing authority over all proposed modifications. This skill formalizes mode selection (`--mode plan` for read-only architectural analysis vs. default implementation mode), configures the reasoning effort dial (`low` to `max`), audits working tree git diffs against strict scope boundaries, and verifies that test suites pass before landing code changes.

```
+-----------------------------------------------------------------------------------+
|                     GitHub Copilot CLI Delegation Pipeline                        |
|                                                                                   |
|  [ Orchestrator Context ]                                                         |
|         |                                                                         |
|         v                                                                         |
|  [ Configuration & Effort Dial Gate ]                                             |
|    - Mode: `plan` (Read-only RFC) vs `default` (Code synthesis)                   |
|    - Effort: `low`, `medium`, `high`, `xhigh`, `max`                              |
|    - Model: Sanitized model flag (letters, digits, hyphens only)                  |
|         |                                                                         |
|         v                                                                         |
|  [ Synthesize Delegation Brief ] <--- Goal, Target Files, Test Command            |
|         |                                                                         |
|         v                                                                         |
|  [ Dispatch Subordinate `copilot` CLI Process ]                                   |
|    - Non-interactive batch execution with hard watchdog timeout                   |
|         |                                                                         |
|         v                                                                         |
|  [ Working Tree Git Diff Inspection Gate ]                                        |
|    - Scope whitelist verification: no unauthorized files altered                  |
|    - Reject unexpected changes in build manifests or dependency locks             |
|         |                                                                         |
|         v                                                                         |
|  [ Automated Test Verification & Git Commit Landing ]                             |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When delegating an isolated coding task or bugfix to the GitHub Copilot CLI.
- When conducting an architectural investigation using Copilot's read-only plan mode.
- When tuning the reasoning effort dial based on algorithmic complexity (e.g. `max` for formal verification, `low` for boilerplate).
- When the user explicitly requests execution via `copilot`.

## When NOT to Use

- When `copilot` CLI is not installed or unauthenticated (`copilot login`).
- For trivial single-line changes where subagent process startup overhead is unjustified.
- In environments requiring hard kernel sandboxes without isolated git worktrees.

---

## Inputs & Prerequisites

1. **Target Execution Mode**: `plan` (read-only analysis) or `default` (implementation).
2. **Reasoning Effort Level**: One of `low`, `medium`, `high`, `xhigh`, `max`.
3. **Delegation Brief**: Focused instructions describing the target deliverable.
4. **Authorized Scope Whitelist**: Explicit list of files permitted for modification.

---

## Core Workflow

### Step 1: Parameter Validation & Effort Dial Calibration
Validate effort levels and sanitize model arguments:

```python
import re
from typing import Dict, Any, List

VALID_EFFORT_LEVELS = {"low", "medium", "high", "xhigh", "max"}
SAFE_MODEL_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.:/]+$")

def configure_copilot_invocation(
    mode: str = "default",
    effort: str = "medium",
    model: str = "auto",
    target_files: List[str] = None
) -> Dict[str, Any]:
    """Validates Copilot CLI arguments to ensure safe, bounded execution."""
    if effort not in VALID_EFFORT_LEVELS:
        raise ValueError(f"Invalid effort '{effort}'. Must be one of: {sorted(list(VALID_EFFORT_LEVELS))}")
        
    if model and not SAFE_MODEL_PATTERN.match(model):
        raise ValueError(f"Security error: Invalid character in model: '{model}'")
        
    flags = [f"--effort", effort]
    if mode == "plan":
        flags.extend(["--mode", "plan"])
    if model and model != "auto":
        flags.extend(["--model", model])
        
    return {
        "mode": mode,
        "effort": effort,
        "model": model,
        "cli_flags": flags,
        "is_read_only": (mode == "plan"),
        "target_files": target_files or []
    }
```

### Step 2: Build the Standalone Brief
Pass the self-contained brief to the Copilot CLI process:

```markdown
# Copilot Delegation Brief

## Goal
Implement structured logging with correlation IDs in `src/logger.py`.

## Authorized Files
- `src/logger.py`
- `tests/test_logger.py`

## Acceptance Test
`pytest tests/test_logger.py`
```

### Step 3: Git Working Tree Diff Verification Gate
Verify that modified files match the authorized scope before landing:

```python
import subprocess

def audit_and_verify(allowed_files: list[str], test_cmd: str) -> bool:
    """Audits diff scope and executes verification harness."""
    res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
    changed = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    
    for c in changed:
        if c not in allowed_files:
            raise PermissionError(f"Scope violation: Copilot altered '{c}', which was not whitelisted.")
            
    test_run = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    return test_run.returncode == 0
```

---

## Best Practices & Failure Modes

- **Calibrate Reasoning Effort**: Do not use `max` effort for trivial variable renaming; reserve `high` and `max` for multi-step algorithmic proofs and complex refactors to conserve token budgets.
- **Isolate in Worktrees**: Always dispatch mutating runs in an isolated git worktree to prevent uncommitted changes from polluting the primary working tree.
- **Zero-Tolerance Scope Creep**: If the subordinate agent alters configuration files outside the brief, roll back with `git checkout -- .`.

---

## Verification & Testing

1. Run the Copilot CLI relay supervisor test suite:
   ```bash
   python scripts/copilot-delegate_helper.py
   ```
2. Verify effort level gating and diff audit checks via CLI:
   ```bash
   python scripts/copilot_relay_supervisor.py --test-all
   ```
