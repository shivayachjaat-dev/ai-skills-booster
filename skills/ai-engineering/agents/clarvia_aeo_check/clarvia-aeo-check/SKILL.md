---
name: clarvia-aeo-check
description: "Use this skill to audit, score, and optimize APIs, MCP (Model Context Protocol) servers, and CLI tools for Agent Experience Optimization (AEO). It evaluates agent-readiness across schema clarity, token efficiency, deterministic error handling, and security sandboxing, generating a 0-100 AEO score with actionable optimization guidance."
domain: ai-engineering
category: agents
subcategory: clarvia_aeo_check
tags:
  - agent-experience-optimization
  - aeo
  - mcp-tool-quality
  - agent-readiness
  - api-scoring
  - schema-validation
  - token-efficiency
technologies:
  - Python
  - JSON-Schema
  - MCP
  - Pydantic
  - OpenAPI
  - AST
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

# Agent Experience Optimization (AEO) & Tool Readiness Audit Standard

## Overview

The `clarvia-aeo-check` skill provides the evaluation methodology, automated heuristics, and scoring rubric for **Agent Experience Optimization (AEO)**. Just as Search Engine Optimization (SEO) aligns human web pages with search crawlers, AEO aligns APIs, Model Context Protocol (MCP) servers, and CLI utilities with the cognitive constraints of autonomous AI agents. Conventional APIs designed for human developers often fail when invoked by LLMs due to ambiguous parameter docstrings, unconstrained output token sizes, non-deterministic error payloads, and interactive blocking prompts. This skill evaluates tools across four foundational dimensions to generate a 0-100 AEO Readiness Score.

```
+-----------------------------------------------------------------------------------+
|                     AEO (Agent Experience Optimization) Framework                 |
|                                                                                   |
|  [ Candidate MCP Server / Tool Definition / API Spec ]                            |
|         |                                                                         |
|         +-----------------------+-----------------------+                         |
|         |                       |                       |                         |
|         v                       v                       v                         |
|  [ 1. Schema Clarity ]    [ 2. Data Structure ]   [ 3. Token Efficiency ]         |
|    - Parameter docs         - Strict typed JSON     - Output conciseness          |
|    - Explicit enums         - Machine-parseable     - Truncation handling         |
|    - Typed defaults           error contracts       - No redundant boilerplate    |
|         |                       |                       |                         |
|         +-----------------------+-----------------------+                         |
|                                 |                                                 |
|                                 v                                                 |
|                   [ 4. Trust, Safety & Sandboxing ]                               |
|                     - Idempotency guarantees & read/write classification          |
|                     - Clear side-effect warnings and permission bounds            |
|                                 |                                                 |
|                                 v                                                 |
|               [ Composite AEO Readiness Score (0-100) ]                           |
|                 Grade A (90-100): Agent-Ready Production                          |
|                 Grade B (75-89): Minor Telemetry / Schema Gaps                     |
|                 Grade C (<75): High Failure / Hallucination Risk                  |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When building or refactoring an MCP server to ensure autonomous coding agents invoke tools reliably without hallucinating parameters.
- When vetting third-party APIs or MCP tools before integrating them into production multi-agent workflows.
- When diagnosing why an agent repeatedly misuses a specific tool or fails schema validation.
- When generating automated AEO compliance reports for enterprise API governance.

## When NOT to Use

- For auditing low-level network packet protocols or hardware device drivers that agents never invoke directly.
- Standard human UX/UI reviews (use `ai-native-ui` or design skills instead).
- General unit testing of application business logic unrelated to agent tool-calling interfaces.

---

## Inputs & Prerequisites

1. **Target Tool Manifest**: MCP tool definition JSON or OpenAPI 3.x schema.
2. **Sample Invocation Payloads**: Typical request arguments and response payloads.
3. **Target Context Window Constraints**: Expected agent context budget (e.g. 8k, 32k, 128k).

---

## Core Workflow

### Step 1: Tool Schema Analysis & Documentation Scoring
Evaluate whether parameters provide unambiguous descriptions, types, and default values:

```python
from typing import Dict, Any, List

def evaluate_tool_schema(tool_def: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits an MCP tool definition for agent readability and parameter clarity.
    """
    score = 25  # Max 25 for schema dimension
    deductions = []
    
    # 1. Description completeness
    desc = tool_def.get("description", "")
    if len(desc) < 30:
        score -= 10
        deductions.append("Tool description is too short (<30 chars) to inform LLM routing.")
        
    # 2. Parameter schema checks
    params = tool_def.get("parameters", {}).get("properties", {})
    required = tool_def.get("parameters", {}).get("required", [])
    
    if not params:
        score -= 5
        deductions.append("No explicit parameters defined.")
    else:
        for p_name, p_spec in params.items():
            if not p_spec.get("description"):
                score -= 3
                deductions.append(f"Parameter '{p_name}' lacks a descriptive explanation.")
            if not p_spec.get("type"):
                score -= 4
                deductions.append(f"Parameter '{p_name}' lacks a strong type definition.")
                
    return {
        "dimension": "Schema Clarity",
        "score": max(0, score),
        "deductions": deductions
    }
```

### Step 2: Token Economy & Payload Footprint Audit
Verify that tool outputs do not flood agent context with conversational chatter or unstructured HTML dumps:

```python
def evaluate_token_footprint(sample_output: str, max_recommended_tokens: int = 1500) -> Dict[str, Any]:
    """Assesses response payload size to prevent context overflow."""
    # Rough approximation: 1 token ~= 4 chars
    approx_tokens = len(sample_output) // 4
    
    if approx_tokens > max_recommended_tokens:
        score = max(0, 25 - int((approx_tokens - max_recommended_tokens) / 100))
        verdict = "PAYLOAD_TOO_LARGE"
    else:
        score = 25
        verdict = "OPTIMAL_TOKEN_BUDGET"
        
    return {
        "dimension": "Token Efficiency",
        "estimated_tokens": approx_tokens,
        "score": score,
        "verdict": verdict
    }
```

### Step 3: Composite AEO Scoring & Guidance
Sum scores across all four dimensions to produce the final AEO Index:
- **90 - 100 (Grade A)**: Production agent-ready.
- **75 - 89 (Grade B)**: Usable, but prompt injection or parameter hallucination risk exists.
- **Below 75 (Grade C)**: High failure rate; requires refactoring before agent deployment.

---

## Best Practices & Failure Modes

- **Silent Stdin Blockers**: Tools must never pause execution waiting for interactive user terminal input (e.g. `[y/N]` prompt). Always provide a non-interactive `--yes` or `--force` flag.
- **Stringified JSON in Strings**: Avoid double-encoding JSON objects as raw escaped strings inside JSON responses.
- **Descriptive Error Payloads**: When validation fails, return structured diagnostics with the exact field name and valid acceptable enum values.

---

## Verification & Testing

1. Run the AEO tool readiness scoring harness:
   ```bash
   python scripts/clarvia-aeo-check_helper.py
   ```
2. Audit an MCP tool definition via CLI:
   ```bash
   python scripts/aeo_readiness_scorer.py --test-all
   ```
