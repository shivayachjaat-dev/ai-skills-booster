---
name: ai-product
description: "Use this skill to engineer production AI products with defensible unit economics, SLA-bound latency budgets, structured schema contracts, prompt version regression testing, and tiered human-in-the-loop fallback mechanisms."
domain: ai-engineering
category: models
subcategory: ai_product
tags:
  - ai-product-management
  - unit-economics
  - token-budgeting
  - latency-budgets
  - prompt-lifecycle
  - human-in-the-loop
  - structured-schemas
technologies:
  - Python
  - Pydantic
  - JSON-Schema
  - FastAPI
  - Prometheus
  - OpenTelemetry
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

# Production AI Product Architecture & Unit Economics Standard

## Overview

The `ai-product` skill establishes the engineering discipline and financial modeling required to build sustainable, enterprise-grade AI products. Moving from a prototype demo to a profitable, high-retention production software system requires solving product problems that are unique to probabilistic models: unpredictable API cost scaling, variable inference latencies, non-deterministic failure modes, and user trust erosion caused by hallucinations. This skill equips product architects, engineering leads, and autonomous agents to design robust AI features governed by strict token budgets, latency SLAs, and structured schema contracts.

```
+-----------------------------------------------------------------------------------+
|                        AI Product Architecture & Economics Gate                   |
|                                                                                   |
|  [ User Request ]                                                                 |
|         |                                                                         |
|         v                                                                         |
|  [ Token & Rate Quota Guard ] <--- Block runaway prompt loops & abuse             |
|         |                                                                         |
|         v                                                                         |
|  [ Intelligent Model Tier Router ]                                                |
|         |-- Simple extraction / classification --> [ Fast Model: $0.15 / 1M ]     |
|         `-- Complex synthesis / reasoning    --> [ Frontier:   $3.00 / 1M ]     |
|         |                                                                         |
|         v                                                                         |
|  [ Structured Schema Contract (Pydantic) ]                                        |
|         |                                                                         |
|         +-- Pass Valid Schema ---> [ Telemetry: Record TTFT & Cost ] -> [ User ]  |
|         |                                                                         |
|         `-- Validation Failure --> [ Heuristic Repair / Fallback Router ]         |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When defining product requirements, token quotas, and financial budgets for LLM-powered features.
- When designing pricing tiers (e.g. Free vs. Pro vs. Enterprise) based on projected model inference Cost of Goods Sold (COGS).
- When establishing Service Level Agreements (SLAs) for Time-To-First-Token (TTFT) and Total Response Time.
- When creating structured output contracts and fallback degradation paths for mission-critical product surfaces.

## When NOT to Use

- Pure low-level model architecture training (pre-training transformers or writing CUDA kernels).
- Static web applications that do not consume generative AI or machine learning inference.
- Informal research sandboxes with no production deployment or economic constraints.

---

## Inputs & Prerequisites

1. **Target Product Metrics**: Latency SLA (e.g. TTFT $< 800\text{ ms}$, total time $< 3.5\text{ s}$), target gross margin ($\ge 75\%$).
2. **User Consumption Profile**: Projected daily active users (DAU), average prompts per session, token distribution (input/output).
3. **Structured Schema Contract**: Defined schema specifying mandatory output fields and data types.

---

## Core Workflow

### Step 1: Unit Economics Modeling (COGS & Margin Protection)
Calculate inference expenditure per user session to guarantee product profitability:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ProductTierBudget:
    tier_name: str
    monthly_subscription_price_usd: float
    max_token_budget_per_user: int
    target_gross_margin: float = 0.75  # 75% gross margin target

def evaluate_user_profitability(
    monthly_tokens_consumed: int,
    blended_cost_per_million_tokens: float,
    budget: ProductTierBudget
) -> Dict[str, Any]:
    """Computes monthly inference cost, gross profit, and margin compliance."""
    monthly_inference_cost = (monthly_tokens_consumed / 1_000_000.0) * blended_cost_per_million_tokens
    gross_profit = budget.monthly_subscription_price_usd - monthly_inference_cost
    actual_margin = (gross_profit / budget.monthly_subscription_price_usd) if budget.monthly_subscription_price_usd > 0 else 0.0
    
    is_compliant = (actual_margin >= budget.target_gross_margin) and (monthly_tokens_consumed <= budget.max_token_budget_per_user)
    
    return {
        "monthly_inference_cost_usd": round(monthly_inference_cost, 4),
        "gross_profit_usd": round(gross_profit, 4),
        "actual_margin_pct": round(actual_margin * 100, 2),
        "margin_compliant": is_compliant
    }
```

### Step 2: Latency Budget & Streaming Strategy
To maintain user engagement, enforce a two-tier latency budget:
1. **Interactive Co-Pilot Surface**:
   - Time-To-First-Token (TTFT): $< 600\text{ ms}$ (Server-Sent Events streaming).
   - Perceived latency managed via contextual typing indicators and immediate partial rendering.
2. **Background Automation Task**:
   - Total batch completion: $< 60\text{ seconds}$ with webhooks or asynchronous polling status endpoints.

### Step 3: Structured Schema Fallback Recovery
When generative models emit malformed JSON or violate domain bounds, execute deterministic repair:

```python
import json
from typing import Optional

def validate_and_repair_schema(raw_output: str, required_keys: list[str]) -> tuple[bool, dict]:
    """Validates schema adherence and applies deterministic fallback if keys are missing."""
    try:
        data = json.loads(raw_output)
    except Exception:
        return False, {"error": "Malformed JSON output", "fallback_applied": True}

    missing = [k for k in required_keys if k not in data]
    if missing:
        # Graceful degradation: populate missing fields with null defaults
        for k in missing:
            data[k] = None
        data["_schema_warning"] = f"Missing required fields: {missing}"
        return False, data

    return True, data
```

---

## Best Practices & Failure Modes

- **Uncapped Token Leaks**: Never permit unbounded loops where agents trigger recursive queries without per-session spending caps. Enforce hard monthly token quotas per API key / workspace.
- **Over-Engineering Model Selection**: Do not route simple classification or entity extraction to frontier models (\$5/1M). Use small, distilled models (\$0.15/1M) for $80\%$ of background tasks.
- **Fail-Open Fallback**: If an AI feature experiences an outage or latency spike $> 5\text{s}$, gracefully degrade to traditional rule-based search or cached static responses rather than presenting an error screen.

---

## Verification & Testing

1. Run the AI product economics and schema contract test harness:
   ```bash
   python scripts/ai-product_helper.py
   ```
2. Verify margin protection and budget threshold enforcement:
   ```bash
   python scripts/ai_product_economics_engine.py --test-all
   ```
