---
name: claude-code-guide
description: "Use this skill to configure, optimize, and orchestrate CLI-based autonomous coding agents (Claude Code, Codex CLI, Cursor, and Antigravity). It establishes deterministic project memory via CLAUDE.md / AGENT.md guidelines, permission whitelists, subagent delegation architectures, and test verification harnesses."
domain: ai-engineering
category: agents
subcategory: claude_code_guide
tags:
  - cli-agents
  - claude-code
  - agentic-coding
  - project-guidelines
  - claude-md
  - tool-permissions
  - test-verification
technologies:
  - Python
  - Bash
  - Git
  - Markdown
  - JSON
  - Subprocess
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

# CLI Autonomous Coding Agent & Project Configuration Standard

## Overview

The `claude-code-guide` skill provides the operational standards, configuration templates, and guardrail rules for deploying autonomous terminal coding agents (such as Claude Code, AGY CLI, and Codex terminal). Without explicit repository instructions, terminal agents default to generic heuristics, guessing build systems, invoking non-standard test runners, and potentially running risky destructive shell commands. This skill formalizes repository-level persistent context via `CLAUDE.md` (or `AGENT.md`), establishes non-interactive execution commands, defines security permission whitelists, and sets up automated pre-commit verification loops.

```
+-----------------------------------------------------------------------------------+
|                   CLI Agent Execution & Configuration Lifecycle                   |
|                                                                                   |
|  [ Repository Root Initialized ]                                                  |
|         |                                                                         |
|         v                                                                         |
|  [ Persistent Directives (CLAUDE.md / AGENT.md) ]                                 |
|    - Verified commands: Test, Build, Lint, Typecheck                              |
|    - Architectural invariants & code conventions                                  |
|         |                                                                         |
|         v                                                                         |
|  [ Execution Sandbox & Security Policy ]                                          |
|    - Whitelisted bash operations                                                  |
|    - Blacklisted destructive commands (rm -rf, git push --force)                  |
|         |                                                                         |
|         v                                                                         |
|  [ Autonomous Action Cycle ]                                                      |
|    Read File -> Edit Patch -> Run Verification Test -> Evaluate Delta             |
|         |                                                                         |
|         v                                                                         |
|  [ Pre-Commit Quality Gate ] (Lint 0 errors, Tests 100% passing)                 |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When onboarding a terminal-based autonomous coding agent to a new or existing repository.
- When generating or auditing a repository's `CLAUDE.md`, `AGENT.md`, or `.cursorrules` directive file.
- When configuring safe tool execution permissions, avoiding interactive blocking prompts, and enforcing non-destructive boundaries.
- When troubleshooting agent loop failures or divergent coding conventions in terminal sessions.

## When NOT to Use

- For configuring graphical IDE themes, keymaps, or human editor typography.
- For managing cloud container orchestrators (Kubernetes, ECS) unrelated to local coding agent sessions.
- In manual pair programming sessions with no autonomous AI agent tools.

---

## Inputs & Prerequisites

1. **Repository Root Directory**: File system access to inspect project manifests (`package.json`, `pyproject.toml`, `Cargo.toml`).
2. **Target Tool Runtime**: Target agent specification (Claude Code, AGY CLI, Cursor agent).
3. **Primary Commands**: Explicit developer commands for running dev servers, unit tests, linters, and typecheckers.

---

## Core Workflow

### Step 1: Detect Project Manifests & Sniff Build Commands
Automatically extract canonical commands from manifest files:

```python
import os
from typing import Dict, Any

def detect_project_toolchain(root_dir: str) -> Dict[str, Any]:
    """Inspects root directory to identify language runtime and test commands."""
    files = set(os.listdir(root_dir))
    
    if "pyproject.toml" in files or "requirements.txt" in files:
        return {
            "runtime": "python",
            "test_cmd": "pytest",
            "lint_cmd": "ruff check .",
            "typecheck_cmd": "mypy ."
        }
    elif "package.json" in files:
        return {
            "runtime": "node",
            "test_cmd": "npm test",
            "lint_cmd": "npm run lint",
            "typecheck_cmd": "npx tsc --noEmit"
        }
    elif "Cargo.toml" in files:
        return {
            "runtime": "rust",
            "test_cmd": "cargo test",
            "lint_cmd": "cargo clippy",
            "typecheck_cmd": "cargo check"
        }
    return {
        "runtime": "generic",
        "test_cmd": "make test",
        "lint_cmd": "make lint",
        "typecheck_cmd": ""
    }
```

### Step 2: Generate Authoritative `CLAUDE.md` Directives
Synthesize a concise, high-signal instruction document:

```markdown
# Repository Agent Guidelines

## Commands
- Test: `pytest tests/`
- Lint: `ruff check . --fix`
- Typecheck: `mypy .`

## Architecture & Code Style
- Python 3.10+ with strict type hints on all function signatures.
- Use Pydantic for data transfer objects.
- Prefer early returns over nested conditional branches.

## Rules for Autonomous Execution
- NEVER run destructive commands: `rm -rf`, `git reset --hard`, `git push --force`.
- Always read existing file implementations before applying edits.
- Run `pytest` and verify clean execution before concluding any task.
```

### Step 3: Enforce Execution Sandbox & Security Policy
Ensure commands executed by the agent are non-interactive and within safe boundaries.

---

## Best Practices & Failure Modes

- **Verbosity Dilution**: Keep `CLAUDE.md` under 150 lines. Bloating directives with exhaustive prose crowds out the agent's context window.
- **Interactive Stdin Hangs**: Always ensure test commands run in non-interactive batch mode (e.g. `npm test -- --watchAll=false` or `pytest -s`).
- **Path Specificity**: Instruct the agent to run tests against specific changed modules rather than running full 45-minute monolithic suites on small edits.

---

## Verification & Testing

1. Run the agent CLI configurator and guideline generator test suite:
   ```bash
   python scripts/claude-code-guide_helper.py
   ```
2. Verify project detection and command whitelist safety checks via CLI:
   ```bash
   python scripts/agent_cli_configurator.py --test-all
   ```
