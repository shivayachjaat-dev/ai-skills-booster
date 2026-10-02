---
name: ab-test-experiment-design
description: "Use this skill when designing, sizing, and analyzing A/B and multivariate split experiments. It guides the agent through statistical hypothesis formulation, sample size calculation via power analysis, minimum detectable effect (MDE) estimation, guardrail metric tracking, CUPED variance reduction, and p-value significance evaluation."
domain: data-analytics
category: experimentation
subcategory: ab-testing
tags:
  - ab-testing
  - experimentation
  - statistics
  - data-analytics
  - metrics
  - product-growth
technologies:
  - Python
  - SciPy
  - Statsmodels
  - SQL
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.9
  - scipy
  - statsmodels
---
# A/B Test Experiment Design

## Overview

A rigorous statistical framework for designing, sizing, and evaluating online randomized controlled experiments (A/B tests). Enables AI agents to prevent common experimentation pitfalls, such as underpowered samples, peeking bias (p-hacking), multiple testing errors, and unmonitored metric cannibalization.

## When to Use

- Designing a split test for a new UI feature, onboarding flow, checkout optimization, or pricing page.
- Calculating required sample sizes and run durations prior to launching an experiment.
- Determining statistical significance (Z-test, T-test, Mann-Whitney U) after an experiment concludes.
- Implementing variance reduction techniques (CUPED) to accelerate experiment velocity.

## When NOT to Use

- Non-randomized observational data studies where confounders dominate (use propensity score matching).
- Low-traffic environments (< 100 conversions per week) where qualitative user testing is more informative.

## Inputs & Prerequisites

- Baseline conversion rate (e.g. 5.2%) or continuous metric mean and standard deviation.
- Target Minimum Detectable Effect (MDE) (e.g. 5% relative lift).
- Significance level ($\alpha = 0.05$) and statistical power ($1 - \beta = 0.80$).
- Primary evaluation metric, secondary operational metrics, and negative guardrail metrics.

## Core Workflow

### 1. Hypothesis Formulation & Metric Architecture
Formulate a testable directional hypothesis:
- *Hypothesis*: "Streamlining the checkout form from 3 steps to 1 step will increase order conversion rate by at least 5% relative without increasing cancellation rate."
- **Primary Metric**: Order Conversion Rate (conversions / unique checkout visitors).
- **Secondary Metrics**: Average Order Value (AOV), checkout completion time.
- **Guardrail Metrics**: Post-purchase cancellation rate, customer support ticket volume.

### 2. Sample Size & Duration Calculation (Power Analysis)
Calculate required sample size per variant before launch:
```python
import statsmodels.stats.api as sms

baseline_p = 0.05
relative_lift = 0.08  # 8% lift target -> 0.054
p2 = baseline_p * (1 + relative_lift)

effect_size = sms.proportion_effectsize(baseline_p, p2)
sample_size_per_variant = sms.NormalIndPower().solve_power(
    effect_size=effect_size,
    power=0.80,
    alpha=0.05,
    ratio=1.0
)
print(f"Required sample size per variant: {int(sample_size_per_variant):,}")
```
Determine test duration based on daily traffic: `duration_days = (2 * sample_size) / daily_visitors`. Never run for less than 7 full days to account for day-of-week seasonality.

### 3. Randomization & Unit of Diversion
- Assign users randomly at the `user_id` level (or `cookie_id` for logged-out visitors) using a cryptographic hash:
  `variant = md5(user_id + experiment_salt) % 100 < 50 ? 'control' : 'treatment'`.
- Verify Sample Ratio Mismatch (SRM) using a Chi-Square goodness-of-fit test. If SRM fails ($p < 0.001$), stop immediately: the randomization or tracking pipeline is biased.

### 4. Post-Experiment Significance Evaluation
Evaluate results once the pre-determined sample size is reached:
```python
from scipy import stats

def analyze_conversion_test(conversions_ctrl, total_ctrl, conversions_treat, total_treat):
    p_ctrl = conversions_ctrl / total_ctrl
    p_treat = conversions_treat / total_treat
    p_pooled = (conversions_ctrl + conversions_treat) / (total_ctrl + total_treat)
    se = (p_pooled * (1 - p_pooled) * (1/total_ctrl + 1/total_treat)) ** 0.5
    z_stat = (p_treat - p_ctrl) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    relative_lift = (p_treat - p_ctrl) / p_ctrl
    return {"p_value": p_value, "relative_lift": relative_lift, "statistically_significant": p_value < 0.05}
```

### 5. Variance Reduction (CUPED)
For continuous metrics (revenue, sessions), utilize pre-experiment covariates to eliminate variance:
$$\hat{Y}_{CUPED} = Y - 	heta (X - E[X])$$
Where $	heta = rac{Cov(Y, X)}{Var(X)}$ and $X$ is pre-experiment metric value.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Sample Ratio Mismatch (SRM) detected (e.g. 52% control vs 48% treatment) | Halt the test immediately. Do NOT interpret results. Investigate client-side redirect drops or bot filter skews. |
| Stakeholders want to stop test early after 2 days because $p < 0.01$ | Strictly refuse early stopping due to the peeking problem (false positive inflation). Enforce full predetermined sample size or use sequential testing (mSPRT). |
| Primary metric is positive but guardrail metric degrades significantly | Do not ship. Trigger cross-functional review to evaluate the net business trade-off. |

## Validation & Acceptance Criteria

- [ ] Clear hypothesis, primary metric, secondary metrics, and guardrail metrics declared in advance.
- [ ] Power calculation performed with documented MDE, alpha (0.05), and power (0.80).
- [ ] SRM check verified before analyzing metrics.
- [ ] Minimum 7-day runtime enforced to account for weekly cycles.
- [ ] Decision to ship, iterate, or discard supported by confidence intervals and p-values.

## Failure Handling & Recovery

- If external outages or marketing campaigns skew traffic midway through a test, either discard the affected dates from analysis or restart the experiment after stabilizing traffic.

## Expected Output & Artifacts

- Pre-experiment test plan with sample size and duration targets.
- Statistical analysis report with relative lifts, p-values, and 95% confidence intervals.

## Related Skills

- `polars-high-throughput-data-pipeline`
- `postgres-query-performance-analysis`
- `react-component-architecture`
