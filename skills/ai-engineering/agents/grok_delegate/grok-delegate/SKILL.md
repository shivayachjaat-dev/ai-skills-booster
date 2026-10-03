---
name: grok-delegate
description: "Delegate coding tasks to the Grok Build CLI only when explicitly authorized by the user, with sandbox isolation and exit code normalization."
domain: ai-engineering
category: agents
subcategory: grok_delegate
tags:
  - ai-engineering
  - agents
  - delegation
  - grok-cli
  - subprocess-orchestration
technologies:
  - Python
  - Grok CLI
  - Subprocess Management
  - JSON Contracts
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Grok CLI Delegation Standard

## Overview

The **Grok Delegate** skill provides an enterprise standard for delegating autonomous coding subtasks to the Grok Build CLI. In heterogeneous multi-agent systems, routing tasks to secondary external CLI engines requires strict authorization boundaries, explicit user consent checks, filesystem sandboxing, and standardized exit code handling.

This skill equips agents with `GrokDelegator`, an execution orchestrator that validates user consent, configures subprocess execution sandboxes, enforces timeouts, and normalizes output diffs into structured result payloads.

```
+------------------------------------------------------------------------+
|                         Grok Delegation Flow                           |
|                                                                        |
|  [ Inbound Task & Prompt ]                                             |
|             |                                                          |
|             v                                                          |
|  [ Explicit Consent Gate ] ---> Rejects if user has not authorized     |
|             |                                                          |
|             v (Authorized)                                             |
|  [ Process Sandboxing ]    ---> Binds to workspace directory & limits  |
|             |                                                          |
|             v                                                          |
|  [ Process Subprocess ]    ---> Executes CLI with timeout guard        |
|             |                                                          |
|             v                                                          |
|  [ Telemetry & Diff Log ]  ---> Captures modified files & exit codes   |
+------------------------------------------------------------------------+
```

## When to Use

- When the user explicitly requests to delegate an implementation task to the Grok Build CLI.
- When benchmarking Grok code generation capabilities on isolated modules.
- When managing secondary coding agent CLI runtimes within an automated pipeline.
- When executing sandbox-isolated code generation with strict process timeouts.

## When NOT to Use

- When the user has not given explicit consent to route code or prompts to Grok.
- General development workflows where the primary internal agent runtime suffices.

## Core Workflow

### 1. Initialize Delegator & Check Availability
Inspect the system environment to determine whether the Grok CLI is installed:

```python
from grok_delegator import DelegationRequest, GrokDelegator

delegator = GrokDelegator(cli_binary="grok")
print(f"Grok CLI Available: {delegator.is_available()}")
```

### 2. Formulate Request with Explicit Consent
Assemble the delegation request ensuring `explicit_user_consent` is verified:

```python
request = DelegationRequest(
    task_id="task-grok-101",
    prompt="Refactor src/cache.py to use Redis connection pooling",
    workspace_root="./project-root",
    explicit_user_consent=True,
    timeout_sec=45.0
)
```

### 3. Execute Delegation and Process Response
Dispatch the request through the delegator and inspect results:

```python
response = delegator.execute_delegation(request)
if not response.success:
    print(f"Delegation failed: {response.error_message}")
else:
    print(f"Task completed in {response.duration_ms}ms: {response.output_summary}")
```

## Verification & Testing

Execute the Grok delegation verification suite to test consent enforcement and execution normalization:

```bash
python scripts/grok-delegate_helper.py
```

Expected output:
- Unconsented delegation requests rejected with security invariant violation.
- Consented requests processed cleanly.
- Status returned cleanly.
