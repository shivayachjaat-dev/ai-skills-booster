---
name: n8n-agents
description: "Use this skill to design, implement, and operate production workflows for n8n agents. Design n8n AI agents, chains, classifiers, extractors, tool calling, memory, RAG, structured output, and human-review flows."
domain: ai-engineering
category: models
subcategory: n8n_agents
tags:
  - ai-engineering
  - models
  - n8n
  - automation
  - production-ready
technologies:
  - N8N Agents
  - Python
  - Bash
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---
# N8N Agents Architecture & Implementation Standard

## Overview

A comprehensive engineering standard and operational guide for n8n agents. In modern production environments, reliable execution requires structured workflows, defensive exception handling, clear input/output contracts, and measurable verification criteria. This skill guides software engineers, systems architects, and autonomous AI agents in executing end-to-end tasks associated with n8n-agents.

```
+------------------------------------------------------------------------+
|                   N8N Agents                                          |
|                                                                        |
|  [ Request / Trigger ] ---> [ Input Validation & Sanitization ]        |
|                                           |                            |
|                                           v                            |
|                          [ Core Execution Pipeline ]                   |
|                                           |                            |
|                                           v                            |
|                          [ Output Contract & Telemetry ]               |
+------------------------------------------------------------------------+
```

## When to Use

- When architecting or refactoring systems related to n8n agents.
- When standardizing production operations, automation scripts, or data pipelines for this domain.
- When an AI agent requires deterministic, repeatable procedural guidelines for execution.

## When NOT to Use

- Unrelated domain workflows with conflicting performance or architectural requirements.
- Deprecated legacy systems where modern automated patterns cannot be safely applied.

## Inputs & Prerequisites

- Appropriate development environment, runtime dependencies, and secure configuration variables.
- Required credentials and network access to target APIs or services.
- Clean project workspace initialized with version control.

## Core Workflow

### Step 1: Environment and Context Initialization
Initialize configuration, validate required system dependencies, and establish secure execution contexts:

```bash
# Verify runtime environment and dependencies
echo "Initializing execution context for n8n-agents..."
```

### Step 2: Implementation and Execution
Execute the primary task logic following standard defensive programming principles:

```python
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("n8n-agents")

def execute_pipeline(payload: dict) -> dict:
    logger.info("Starting execution for n8n-agents")
    if not payload:
        raise ValueError("Invalid execution payload: payload must not be empty.")
    
    # Process workflow
    result = {"status": "success", "processed": True, "details": payload}
    logger.info("Completed execution successfully.")
    return result

if __name__ == "__main__":
    execute_pipeline({"initialized": True})
```

### Step 3: Telemetry, Error Handling & Recovery
Enforce robust error isolation, structured logging, and fallback mechanisms:
- Catch specific, actionable exceptions rather than swallowing broad errors.
- Ensure all emitted events conform to standardized observability schemas.
- Clean up ephemeral resources or connections in `finally` blocks.

## Best Practices & Failure Modes

- **Idempotency**: Ensure operations can be retried safely without causing duplicate records or resource corruption.
- **Defensive Timeouts**: Always configure explicit connection and read timeouts on external service calls.
- **Zero Secret Exposure**: Never log raw authorization tokens, API keys, or sensitive customer identifiers.

## Verification & Testing

1. Run automated unit tests to verify contract compliance.
2. Execute the verification script: `python scripts/n8n-agents_helper.py`.
3. Confirm clean linting and type checks across all modules.
