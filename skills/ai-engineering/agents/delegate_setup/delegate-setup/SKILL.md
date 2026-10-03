---
name: delegate-setup
description: "Configure approved delegation lanes, CLI capability discovery, and fallback cascades across implementer coding agents."
domain: ai-engineering
category: agents
subcategory: delegate_setup
tags:
  - ai-engineering
  - agents
  - delegation
  - cli-orchestration
  - multi-agent
technologies:
  - Python
  - Bash
  - JSON Schema
  - Process Subprocess
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Delegate Setup Architecture & Implementation Standard

## Overview

The **Delegate Setup** skill defines an authoritative standard for orchestrating, discovering, and configuring delegation lanes across installed autonomous coding agent CLIs. In enterprise agentic workflows, complex tasks often require routing to specialized agent runtimes (such as Gemini, Claude, Copilot, Cline, or Aider). Without explicit delegation setup, agents risk running without sandboxing, invoking unverified binaries, or halting upon individual agent failures.

This skill equips engineers and autonomous systems with deterministic tools to probe the host environment, assign security tiers (`strict_read_only`, `workspace_write_isolated`, `supervised_commit`, `full_delegation`), and assemble resilient failover cascades.

```
+------------------------------------------------------------------------+
|                       Delegate Setup Pipeline                          |
|                                                                        |
|  [ CLI Binary Discovery ]  ---> Checks system PATH & version status    |
|                                           |                            |
|                                           v                            |
|  [ Capability Assessment ] ---> Evaluates stdin pipes, JSON streams    |
|                                           |                            |
|                                           v                            |
|  [ Permission Tiering ]    ---> Enforces read/write/commit boundaries  |
|                                           |                            |
|                                           v                            |
|  [ Policy & Cascades ]     ---> Emits .delegate-lanes.json routing     |
+------------------------------------------------------------------------+
```

## When to Use

- When configuring multi-agent systems that delegate subtasks to external CLI agents.
- When establishing secure operational sandboxes and authorization boundaries for automated coding agents.
- When setting up multi-tier agent fallback ladders (e.g., primary LLM agent falling back to alternative local CLI engines).
- When initializing a new development workstation or CI/CD container for autonomous operations.

## When NOT to Use

- Single-model agent environments that do not interact with or spawn secondary CLIs.
- Embedded or microcontroller targets with no subprocess execution support.

## Core Workflow

### 1. Environment & Implementer Discovery
Probe system environment paths for known agent CLIs and construct a verified inventory:

```python
from delegate_setup_orchestrator import DelegateSetupManager

manager = DelegateSetupManager()
agents = manager.discover_installed_clis()
for name, meta in agents.items():
    print(f"Agent: {name} | Installed: {meta.installed} | Path: {meta.path}")
```

### 2. Configure Security & Permission Lanes
Assign each implementer agent to an appropriate security lane according to blast radius:
- `strict_read_only`: Prohibits filesystem writes and version control modifications. Ideal for security analysis and code audits.
- `workspace_write_isolated`: Allows modifying files strictly within current repository boundaries without git commit permissions.
- `supervised_commit`: Permits staging and committing changes, requiring CI or user review for pushing.
- `full_delegation`: Unrestricted pipeline execution for trusted release automation.

### 3. Generate Delegation Policy and Failover Ladder
Emit a validated `.delegate-lanes.json` configuration file:

```python
manager.configure_lane("gemini", "full_delegation")
manager.configure_lane("claude", "supervised_commit")

policy = manager.generate_policy(
    primary="gemini",
    fallbacks=["claude", "aider", "copilot"]
)
```

## Verification & Testing

Execute the comprehensive diagnostics suite to verify CLI detection and policy generation:

```bash
python scripts/delegate-setup_helper.py
```

All status checks should complete cleanly with zero policy validation errors.
