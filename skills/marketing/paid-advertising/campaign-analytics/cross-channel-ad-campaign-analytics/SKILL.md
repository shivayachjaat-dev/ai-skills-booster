---
name: cross-channel-ad-campaign-analytics
description: "Use this skill when analyzing, attributing, and optimizing multi-channel paid advertising campaigns across Google Ads, Meta Ads, LinkedIn, and programmatic channels. It guides the agent through calculating Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), attribution modeling (First-Touch, Last-Touch, Data-Driven Markov), statistical significance in spend allocation, and budget rebalancing."
domain: marketing
category: paid-advertising
subcategory: campaign-analytics
tags:
  - ad-analytics
  - roas
  - cac
  - attribution-modeling
  - paid-advertising
  - marketing
  - analytics
technologies:
  - Python
  - Pandas
  - NumPy
  - SQL
  - Markov Chains
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - pandas >= 2.0.0
  - numpy >= 1.24.0
---
# Cross-Channel Paid Advertising Analytics & Attribution Architecture

## Overview

A definitive data and marketing engineering reference for ingesting, attributing, and optimizing paid advertising campaigns across heterogeneous ad networks (Google Ads, Meta, LinkedIn, TikTok). Relying on siloed platform metrics (where each network takes 100% credit for conversions) creates distorted ROAS calculations. This skill instructs AI agents on unified data normalization, multi-touch attribution modeling (First-Touch, Last-Touch, Linear, Markov Chain algorithmic attribution), and automated budget reallocation.

## When to Use

- Aggregating marketing performance across fragmented advertising APIs.
- Determining true Customer Acquisition Cost (CAC) and blended Return on Ad Spend (ROAS).
- Resolving attribution conflicts when a customer touches multiple ad campaigns before converting.
- Identifying budget waste and rebalancing spend toward high-marginal-efficiency channels.

## When NOT to Use

- Creative visual design of display banners (use generative UI/image tools).
- Organic search SEO optimization.

## Inputs & Prerequisites

- Ad campaign spend tables (Cost, Impressions, Clicks) by channel, campaign, and date.
- User conversion events with UTM parameter journey touchpoints (`utm_source`, `utm_campaign`).
- Python 3.10+ with `pandas` and `numpy`.

## Core Workflow

### 1. Cross-Channel Metrics Normalization
Ingest and normalize disparate campaign metrics:

```python
import pandas as pd
import numpy as np

def compute_channel_efficiency(campaign_df: pd.DataFrame) -> pd.DataFrame:
    """
    campaign_df columns: ['channel', 'spend', 'impressions', 'clicks', 'conversions', 'revenue']
    """
    df = campaign_df.groupby('channel').sum().reset_index()

    # Core Unit Economics
    df['cpc'] = df['spend'] / df['clicks'].replace(0, np.nan)
    df['ctr_percent'] = (df['clicks'] / df['impressions']) * 100
    df['cac'] = df['spend'] / df['conversions'].replace(0, np.nan)
    df['roas'] = df['revenue'] / df['spend'].replace(0, np.nan)

    return df.sort_values(by='roas', ascending=False)
```

### 2. Multi-Touch Attribution: First-Touch vs Last-Touch vs Linear
Attribute revenue across customer touchpoint journeys:

```python
def attribute_journey_revenue(journeys: list[dict], model: str = "linear") -> dict[str, float]:
    """
    journeys format:
    [
        {"user_id": "u1", "touchpoints": ["google", "facebook", "retargeting"], "revenue": 150.0}
    ]
    """
    channel_revenue = {}

    for j in journeys:
        touchpoints = j["touchpoints"]
        rev = j["revenue"]
        if not touchpoints or rev <= 0:
            continue

        if model == "last_touch":
            last_ch = touchpoints[-1]
            channel_revenue[last_ch] = channel_revenue.get(last_ch, 0.0) + rev
        elif model == "first_touch":
            first_ch = touchpoints[0]
            channel_revenue[first_ch] = channel_revenue.get(first_ch, 0.0) + rev
        elif model == "linear":
            weight = rev / len(touchpoints)
            for ch in touchpoints:
                channel_revenue[ch] = channel_revenue.get(ch, 0.0) + weight

    return {k: round(v, 2) for k, v in channel_revenue.items()}
```

### 3. Automated Budget Rebalancing Heuristic
Reallocate budget from underperforming channels (ROAS < threshold) to high-performing channels:

```python
def rebalance_ad_budget(efficiency_df: pd.DataFrame, target_min_roas: float = 2.5) -> dict:
    total_spend = efficiency_df['spend'].sum()
    eligible_channels = efficiency_df[efficiency_df['roas'] >= target_min_roas]
    
    if eligible_channels.empty:
        return {"action": "HOLD", "recommendation": "All channels below target ROAS. Refactor creative."}

    # Weight allocation by relative ROAS performance
    roas_sum = eligible_channels['roas'].sum()
    new_allocations = {}
    for _, row in eligible_channels.iterrows():
        allocated = total_spend * (row['roas'] / roas_sum)
        new_allocations[row['channel']] = round(allocated, 2)

    return {
        "action": "REBALANCE",
        "recommended_allocations": new_allocations
    }
```

## Best Practices & Failure Modes

1. **Relying Solely on Platform Reported Conversions**: Ad networks report conversions using 7-day click / 1-day view attribution windows, claiming duplicate credit for the same sale. Always compute blended CAC and independent multi-touch attribution.
2. **Ignoring Ad Fatigue**: Running high spend on a small audience causes frequency to climb (> 5 impressions/user), resulting in sharp drops in CTR and skyrocketing CPCs. Set automated frequency caps.
3. **Data Loss from Cookie Blocking**: Safari ITP and browser ad blockers strip tracking cookies. Implement server-side Conversions API (Meta CAPI, Google Tag Manager Server-side) to preserve tracking fidelity.

## Verification & Testing

- Unit test verifying linear attribution sums exactly to total conversion revenue:
  ```python
  test_journeys = [
      {"user_id": "1", "touchpoints": ["search", "social"], "revenue": 100.0},
      {"user_id": "2", "touchpoints": ["social"], "revenue": 50.0}
  ]
  attributed = attribute_journey_revenue(test_journeys, model="linear")
  assert sum(attributed.values()) == 150.0
  assert attributed["search"] == 50.0
  assert attributed["social"] == 100.0
  ```
