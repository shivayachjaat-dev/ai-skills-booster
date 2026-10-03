---
name: cline-delegate
description: "Use this skill to delegate bounded coding, exploration, or planning tasks to the Cline CLI agent process. It configures operational execution modes (Act vs. Plan), specifies provider model backends, enforces working tree isolation, monitors execution traces, audits git diffs, and coordinates final review and landing."
domain: ai-engineering
category: agents
subcategory: cline_delegate
tags:
  - cline-cli
  - agent-delegation
  - plan-mode
  - act-mode
  - subagent-supervision
  - git-diff-review
  - model-routing
technologies:
  - Python
  - Subprocess
  - Git
  - JSON
  - Cline-CLI
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

# Cline CLI Agent Delegation & Supervision Standard

## Overview

The `cline-delegate` skill defines the protocol, invocation parameters, and validation gates for delegating engineering tasks to the **Cline CLI** (`cline`). When orchestrating multi-agent systems, the primary agent delegates isolated coding tasks to Cline while retaining complete architectural oversight and landing authority. This skill formalizes the choice between read-only architectural investigation (**Plan Mode**) and file-modifying implementation (**Act Mode**), validates model provider flags to prevent shell injection, audits working tree git deltas, and validates acceptance tests before committing changes.

```
+-----------------------------------------------------------------------------------+
|                        Cline CLI Delegation & Review Pipeline                     |
|                                                                                   |
|  [ Orchestrator Context ]                                                         |
|         |                                                                         |
|         v                                                                         |
|  [ Mode Selection Gate ]                                                          |
|    /                    \                                                         |
|   / (Read-Only)          \ (Mutating Code)                                        |
|  v                        v                                                       |
| [ PLAN MODE ]            [ ACT MODE ]                                             |
| (Architecture/RFC)       (Target File Whitelist)                                  |
|         |                        |                                                |
|         +------------------------+                                                |
|                                  |                                                |
|                                  v                                                |
|                  [ Sanitize Model & Provider Flags ]                              |
|                  (Letters, digits, hyphens only: regex whitelist)                 |
|                                  |                                                |
|                                  v                                                |
|                  [ Execute Subordinate `cline` Process ]                          |
|                                  |                                                |
|                                  v                                                |
|                  [ Working Tree Git Diff Inspection Gate ]                        |
|                    - Check scope whitelist adherence                              |
|                    - Run verification test harness                                |
|                                  |                                                |
|                                  v                                                |
|                  [ Final Landing: git commit / PR ]                               |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When delegating a contained module implementation, bugfix, or test suite generation to Cline CLI.
- When performing a read-only architectural exploration using Cline's `--plan` mode.
- When the user explicitly requests execution via `cline`.
- When separating architectural design from mechanical code generation to preserve context.

## When NOT to Use

- When `cline` is not installed on the system PATH or lacks API credentials.
- For trivial single-line changes where subagent process startup overhead is unjustified.
- When tasks require interactive conversational disambiguation while coding.

---

## Inputs & Prerequisites

1. **Target Execution Mode**: `plan` (read-only analysis) or `act` (code modification).
2. **Delegation Brief**: Focused instructions describing the target deliverable.
3. **Model / Provider Specification**: Optional provider name (e.g. `anthropic`, `openrouter`) and model identifier.
4. **Scope Boundaries**: Explicit list of files authorized for modification.

---

## Core Workflow

### Step 1: Mode Selection & Input Sanitization
Validate mode and sanitize provider flags:

```python
import re
from typing import Dict, Any

SAFE_FLAG_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.:/]+$")

def validate_cline_parameters(mode: str, model: str, provider: str) -> Dict[str, Any]:
    """Validates Cline CLI flags to prevent command injection."""
    if mode not in ("plan", "act"):
        raise ValueError(f"Invalid mode: '{mode}'. Must be 'plan' or 'act'.")
        
    for name, val in [("model", model), ("provider", provider)]:
        if val and not SAFE_FLAG_PATTERN.match(val):
            raise ValueError(f"Invalid characters in {name}: '{val}'")
            
    return {
        "mode_flag": f"--{mode}",
        "model_flag": f"--model {model}" if model else "",
        "provider_flag": f"--provider {provider}" if provider else ""
    }
```

### Step 2: Build the Standalone Brief
The brief is passed to Cline via stdin or file parameter:

```markdown
# Cline Delegation Brief

## Goal
Implement exponential backoff retry logic in `src/http_client.py`.

## Authorized Files
- `src/http_client.py`
- `tests/test_http_client.py`

## Verification Command
`pytest tests/test_http_client.py`
```

### Step 3: Diff Inspection & Quality Gate
After Cline exits, inspect `git diff` to ensure no out-of-scope files were touched:

```python
import subprocess

def verify_and_land(allowed_files: list[str], test_cmd: str) -> bool:
    """Verifies diff scope and executes test command before landing."""
    # 1. Check modified files
    res = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, check=True)
    changed = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    
    for f in changed:
        if f not in allowed_files:
            raise PermissionError(f"Scope violation: Cline modified unauthorized file '{f}'")
            
    # 2. Run independent test suite
    test_res = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    return test_res.returncode == 0
```

---

## Best Practices & Failure Modes

- **Plan-First on Ambiguity**: When an issue is complex or dependencies are unclear, run `--plan` mode first to produce an RFC before executing `--act`.
- **Credential Hygiene**: Ensure API keys (e.g. `ANTHROPIC_API_KEY`) are passed via secure environment variables rather than command-line argument flags visible in process listings (`ps`).
- **Diff Rejection**: If the subordinate agent introduces unnecessary dependencies in `package.json` without authorization, reject the change with `git checkout -- .`.

---

## Verification & Testing

1. Run the Cline CLI relay supervisor test suite:
   ```bash
   python scripts/cline-delegate_helper.py
   ```
2. Verify argument sanitization and mode gating via CLI:
   ```bash
   python scripts/cline_relay_supervisor.py --test-all
   ```
