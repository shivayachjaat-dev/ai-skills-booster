---
name: hosted-agents
description: "Build, configure, and orchestrate background coding agents in sandboxed execution environments like microVMs, containers, and Modal sandboxes."
domain: ai-engineering
category: agents
subcategory: hosted_agents
tags:
  - ai-engineering
  - agents
  - sandboxing
  - hosted-agents
  - microvm
technologies:
  - Python
  - Docker / MicroVM
  - Modal Sandboxes
  - Subprocess Isolation
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Hosted Agents Sandboxed Runtime Standard

## Overview

The **Hosted Agents** skill provides an enterprise standard for provisioning, managing, and orchestrating background autonomous coding agents in secure, isolated sandbox environments. In production architectures, running agent-generated code or untrusted third-party dependencies directly on host workstations or primary application servers presents extreme security and stability risks.

This skill equips systems with `HostedAgentSandbox`, an abstraction layer for orchestrating ephemeral sandboxed execution runtimes (such as MicroVMs, Modal sandboxes, or containerized environments). It enforces CPU/memory quotas, execution timeouts, restricted network egress, and verified artifact extraction with zero residue upon teardown.

```
+------------------------------------------------------------------------+
|                      Hosted Agent Sandbox Pipeline                     |
|                                                                        |
|  [ Ephemeral Provisioning ] ---> Generates isolated root filesystem    |
|                                           |                            |
|                                           v                            |
|  [ Workspace Mounting ]     ---> Injects code & config into sandbox    |
|                                           |                            |
|                                           v                            |
|  [ Resource-Guarded Run ]   ---> Enforces CPU, RAM & timeout bounds    |
|                                           |                            |
|                                           v                            |
|  [ Artifact Extraction ]    ---> Safely harvests diffs and outputs     |
|                                           |                            |
|                                           v                            |
|  [ Automated Teardown ]     ---> Purges ephemeral sandbox files        |
+------------------------------------------------------------------------+
```

## When to Use

- When executing autonomous agent workflows that generate, build, and test arbitrary code.
- When running background agents on cloud infrastructure (e.g. Modal sandboxes, AWS Firecracker microVMs, or Fly Machines).
- When isolating untrusted repository scripts to protect host credentials and local development filesystems.
- When benchmarking multiple agents in reproducible, clean-slate runtime environments.

## When NOT to Use

- Read-only code search or documentation indexing that requires zero execution permissions.
- Local command-line workflows where the developer explicitly supervises each terminal command.

## Core Workflow

### 1. Configure and Provision Ephemeral Sandbox
Initialize the sandbox configuration with explicit resource quotas and timeout budgets:

```python
from sandbox_agent_runtime import HostedAgentSandbox, SandboxConfig

config = SandboxConfig(
    sandbox_id="agent-run-552",
    runtime_type="container_isolated",
    memory_limit_mb=1024,
    timeout_sec=45.0
)

sandbox = HostedAgentSandbox(config)
sandbox_path = sandbox.provision()
print(f"Ephemeral sandbox active at: {sandbox_path}")
```

### 2. Mount Files & Execute Task
Mount repository files into the sandbox and execute the autonomous worker script:

```python
sandbox.mount_files({
    "app.py": "def process(): return 'Completed task'",
    "run.py": "import app; print(app.process())"
})

report = sandbox.execute_command(["python", "run.py"])
print(f"Execution Status: {report.status} (Exit Code: {report.exit_code})")
print(f"Stdout:\n{report.stdout}")
```

### 3. Extract Artifacts and Purge Resources
Collect generated output files and trigger immediate teardown:

```python
print(f"Extracted Artifacts: {report.artifacts_extracted}")
sandbox.teardown()
print("Sandbox purged successfully.")
```

## Verification & Testing

Execute the hosted agent sandbox test suite to test provisioning, command execution, and clean teardown:

```bash
python scripts/hosted-agents_helper.py
```

Expected output:
- Ephemeral sandbox provisioned and verified on filesystem.
- Subprocess command executed within isolated directory.
- Artifacts collected and sandbox completely purged.
- Status returned cleanly.
