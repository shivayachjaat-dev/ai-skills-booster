---
name: five-axis-code-review
description: "Use this skill to design, implement, and operate production workflows for five axis code review. Five-axis code review checklist (correctness, security, readability, performance, test coverage) producing actionable comments instead of style nitpicks. Use when the user asks to review code, a diff, or a pull request."
domain: ai-engineering
category: rag
subcategory: five_axis_code_revie
tags:
  - ai-engineering
  - rag
  - five
  - automation
  - production-ready
technologies:
  - Five Axis Code Review
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
# Five Axis Code Review Architecture & Implementation Standard

## Overview

A comprehensive engineering standard and operational guide for five axis code review. In modern production environments, reliable execution requires structured workflows, defensive exception handling, clear input/output contracts, and measurable verification criteria. This skill guides software engineers, systems architects, and autonomous AI agents in executing end-to-end tasks associated with five-axis-code-review.

```
+------------------------------------------------------------------------+
|                   Five Axis Code Review                               |
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

- When architecting or refactoring systems related to five axis code review.
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
echo "Initializing execution context for five-axis-code-review..."
```

### Step 2: Implementation and Execution
Execute the primary task logic following standard defensive programming principles:

```python
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("five-axis-code-review")

def execute_pipeline(payload: dict) -> dict:
    logger.info("Starting execution for five-axis-code-review")
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
2. Execute the verification script: `python scripts/five-axis-code-review_helper.py`.
3. Confirm clean linting and type checks across all modules.
