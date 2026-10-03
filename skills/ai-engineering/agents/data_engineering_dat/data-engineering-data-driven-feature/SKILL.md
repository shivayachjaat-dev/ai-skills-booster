---
name: data-engineering-data-driven-feature
description: "Use this skill to design, build, and instrument data-driven software features powered by controlled A/B experimentation, deterministic hashing bucketing, statistical hypothesis testing (Z-score, p-value, confidence intervals), and structured telemetry event pipelines."
domain: ai-engineering
category: agents
subcategory: data_engineering_dat
tags:
  - data-driven-features
  - ab-testing
  - statistical-significance
  - feature-flags
  - deterministic-bucketing
  - telemetry-instrumentation
  - conversion-rate-optimization
technologies:
  - Python
  - Scipy
  - NumPy
  - MD5-Hashing
  - OpenTelemetry
  - Statsmodels
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
  - numpy@>=1.24.0
version: 1.0.0
author: Antigravity Team
---

# Data-Driven Feature Engineering & Controlled A/B Experimentation Standard

## Overview

The `data-engineering-data-driven-feature` skill establishes the architectural patterns, statistical methodologies, and telemetry instrumentation required to develop and validate software features guided by empirical user data. Shipping software based purely on intuition risks releasing features that silently degrade conversion rates, elevate user churn, or introduce performance regressions. This skill formalizes the full lifecycle of data-driven feature development: baseline metric discovery, deterministic user hash bucketing, telemetry event logging, and rigorous two-proportion hypothesis testing (Z-score, p-value, and confidence interval calculation).

```
+-----------------------------------------------------------------------------------+
|                        Data-Driven Feature Experimentation                        |
|                                                                                   |
|  [ User Traffic Ingress ]                                                         |
|         |                                                                         |
|         v                                                                         |
|  [ Deterministic Hash Bucketer ] (MD5(salt + user_id) % 100)                      |
|    /                       \                                                      |
|   / (< 50: Control)         \ (>= 50: Treatment)                                  |
|  v                           v                                                    |
| [ Baseline Feature UX ]     [ Experimental Variant UX ]                           |
|         |                            |                                            |
|         +-------------+--------------+                                            |
|                       |                                                           |
|                       v                                                           |
|        [ Telemetry Ingestion Pipeline ]                                           |
|          - Impression events: { experiment_id, variant, user_id, timestamp }      |
|          - Conversion events: { action: "checkout_complete", revenue }            |
|                       |                                                           |
|                       v                                                           |
|        [ Statistical Evaluation Engine (Two-Proportion Z-Test) ]                  |
|          - Calculate Conversion Rates: p_control vs p_treatment                   |
|          - Compute Z-Score, p-value (alpha = 0.05, 95% CI)                        |
|                       |                                                           |
|                       +-- p < 0.05 & Uplift > 0 ---> [ 100% Production Rollout ]  |
|                       `-- p >= 0.05 or Regression -> [ Safe Automated Rollback ]  |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When building new product capabilities that must be validated via A/B or multivariate testing before 100% rollout.
- When instrumenting real-time event telemetry pipelines to monitor funnel drop-off and conversion lift.
- When computing statistical significance (Z-tests, p-values, Minimum Detectable Effects) on experiment results.
- When implementing deterministic, client-side or edge feature flag allocation without database lookups.

## When NOT to Use

- For internal developer tooling or infrastructure scripts that have no end-user traffic or probabilistic behavior.
- For emergency security patches or critical zero-day bugfixes (these must be deployed 100% immediately without A/B splits).
- In low-traffic enterprise deployments with insufficient sample sizes to reach statistical power.

---

## Inputs & Prerequisites

1. **Feature Hypothesis**: Explicit statement of intended impact (e.g. "One-click checkout increases checkout conversion by $+3.0\%$").
2. **Experiment Parameters**: Target significance level ($\alpha = 0.05$, $95\%$ confidence), statistical power ($1 - \beta = 0.80$).
3. **Primary & Guardrail Metrics**: Conversion metric (e.g. purchase rate) and safety guardrail (e.g. page load latency p95).

---

## Core Workflow

### Step 1: Deterministic User Hash Bucketing
Assign users deterministically to experiment variants without stateful database writes:

```python
import hashlib

def assign_experiment_variant(user_id: str, experiment_id: str, traffic_split: float = 0.5) -> str:
    """
    Computes deterministic variant assignment using cryptographic hashing.
    Ensures uniform distribution across cohorts and repeatable assignments.
    """
    seed = f"{experiment_id}:{user_id}".encode("utf-8")
    hash_hex = hashlib.md5(seed).hexdigest()
    # Normalize to bucket 0..99
    bucket = int(hash_hex[:8], 16) % 100
    
    return "treatment" if bucket < int(traffic_split * 100) else "control"
```

### Step 2: Statistical Significance (Two-Proportion Z-Test)
Evaluate whether observed uplift between control and treatment cohorts is statistically significant:

```python
import math
from typing import Dict, Any

def calculate_two_proportion_z_test(
    control_successes: int,
    control_total: int,
    treatment_successes: int,
    treatment_total: int
) -> Dict[str, Any]:
    """Computes pooled two-proportion Z-test and two-tailed p-value."""
    p_ctrl = control_successes / control_total
    p_treat = treatment_successes / treatment_total
    
    p_pooled = (control_successes + treatment_successes) / (control_total + treatment_total)
    se = math.sqrt(p_pooled * (1 - p_pooled) * (1 / control_total + 1 / treatment_total))
    
    if se == 0:
        return {"z_score": 0.0, "p_value": 1.0, "is_significant": False}
        
    z_score = (p_treat - p_ctrl) / se
    # Normal CDF approximation for two-tailed p-value
    p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z_score) / math.sqrt(2.0))))
    
    relative_lift = ((p_treat - p_ctrl) / p_ctrl) * 100.0 if p_ctrl > 0 else 0.0
    
    return {
        "control_cr": round(p_ctrl, 4),
        "treatment_cr": round(p_treat, 4),
        "relative_lift_pct": round(relative_lift, 2),
        "z_score": round(z_score, 3),
        "p_value": round(p_value, 5),
        "is_significant": p_value < 0.05
    }
```

### Step 3: Automated Decision Gate
- If $p < 0.05$ and relative lift is positive: Promote variant to 100% general availability.
- If $p \ge 0.05$: Continue gathering data until target sample size is reached.
- If guardrail metrics degrade (e.g. latency $+20\%$): Trigger emergency kill-switch and revert to control.

---

## Best Practices & Failure Modes

- **Peeking Problem**: Never terminate an experiment early the moment a p-value drops below 0.05 before reaching the pre-calculated sample size. Early peeking severely inflates false-positive rates.
- **Sample Ratio Mismatch (SRM)**: Always run a chi-square test on total user counts in control vs. treatment. If traffic deviates significantly from 50/50, bucketing logic is flawed.
- **Shared Seed Collisions**: Always salt hash inputs with the unique `experiment_id` to prevent cross-experiment user correlation.

---

## Verification & Testing

1. Run the A/B experimentation and statistical verification test suite:
   ```bash
   python scripts/data-engineering-data-driven-feature_helper.py
   ```
2. Verify deterministic bucketing uniformity and Z-test math via CLI:
   ```bash
   python scripts/ab_experimentation_engine.py --test-all
   ```
