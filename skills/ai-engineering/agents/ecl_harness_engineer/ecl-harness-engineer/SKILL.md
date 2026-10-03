---
name: ecl-harness-engineer
description: "Create or audit ECL Agent Harness infrastructure: AGENTS.md, change tracking, repository guidance, lint checks, CI gates, and agent handoff docs."
domain: ai-engineering
category: agents
subcategory: ecl_harness_engineer
tags:
  - ai-engineering
  - agents
  - harness
  - repo-infrastructure
  - handoff-management
technologies:
  - Python
  - Bash
  - Markdown
  - CI Gates
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# ECL Agent Harness Architecture & Implementation Standard

## Overview

The **ECL Harness Engineer** skill provides the blueprint and automation tools for constructing, auditing, and maintaining an enterprise-grade agent harness inside any code repository. Autonomous coding agents lack implicit institutional memory; without a structured harness, agents commit breaking changes, bypass testing suites, or introduce architectural drift.

The ECL (Engineering Capability Lifecycle) Harness establishes a deterministic framework consisting of `AGENTS.md` operating contracts, pre-flight verification gates, append-only intervention journals, and standardized agent-to-human handoff documentation.

```
+------------------------------------------------------------------------+
|                      ECL Agent Harness Workflow                        |
|                                                                        |
|  [ Repository Audit ]        ---> Checks AGENTS.md compliance          |
|                                           |                            |
|                                           v                            |
|  [ Harness Provisioning ]    ---> Scaffolds .agent-harness & contracts |
|                                           |                            |
|                                           v                            |
|  [ Pre-Flight Validation ]   ---> Enforces test gates & syntax checks  |
|                                           |                            |
|                                           v                            |
|  [ Handoff Generation ]      ---> Emits structured session review brief|
+------------------------------------------------------------------------+
```

## When to Use

- When preparing a new or legacy repository for safe, reliable autonomous AI agent contributions.
- When standardizing agent instructions, testing commandments, and forbidden command policies via `AGENTS.md`.
- When generating structured handoff documents after completing autonomous coding sessions.
- When auditing existing agent configuration files for missing security boundaries or incomplete testing guidelines.

## When NOT to Use

- Repositories that do not use or intend to support AI coding assistants or autonomous agent workflows.
- Lightweight temporary scratchpads where formal architecture contracts are unnecessary.

## Core Workflow

### 1. Audit Repository Readiness
Run the audit engine to evaluate whether the repository contains the mandatory AGENTS.md guidelines:

```python
from ecl_harness import ECLHarness

harness = ECLHarness(repo_root=".")
report = harness.audit_repository()
if not report.compliant:
    print(f"Missing sections: {report.missing_sections}")
```

### 2. Scaffold and Initialize the Harness
Generate the baseline `.agent-harness` directory structure and `AGENTS.md` operational contract:

```python
harness.init_harness()
print("AGENTS.md and .agent-harness infrastructure initialized.")
```

### 3. Generate Agent Session Handoff Brief
At the conclusion of an autonomous coding intervention, compile a verified handoff brief:

```python
handoff_path = harness.generate_handoff(
    agent_id="refactor-agent-42",
    task_summary="Migrated user authentication endpoint to async/await and updated unit tests.",
    touched_files=["src/auth/service.py", "tests/test_auth.py"],
    verification_status="Passed"
)
print(f"Handoff written to: {handoff_path}")
```

## Verification & Testing

Execute the ECL harness verification suite to test contract generation, repository audits, and handoff compilation:

```bash
python scripts/ecl-harness-engineer_helper.py
```

Expected output:
- Pre-initialization and post-initialization audits execute cleanly.
- Sample handoff brief is verified on disk.
- Operational status returned cleanly.
