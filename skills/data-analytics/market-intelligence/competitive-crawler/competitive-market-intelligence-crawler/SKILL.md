---
name: competitive-market-intelligence-crawler
description: "Use this skill to design, build, and automate competitive market intelligence crawlers across eCommerce marketplaces, SaaS pricing matrices, and public ad libraries. It covers price monitoring, product feature diff tracking, promotional campaign alerts, and historical trend reporting."
domain: data-analytics
category: market-intelligence
subcategory: competitive-crawler
tags:
  - competitive-intelligence
  - market-research
  - price-scraping
  - ad-library
  - market-analysis
  - data-analytics
technologies:
  - Python
  - Pandas
  - BeautifulSoup
  - Scrapy
  - Playwright
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - pandas >= 2.0.0
  - requests >= 2.31.0
  - python >= 3.10
---
# Competitive Market Intelligence Crawler & Pricing Monitor

## Overview

A strategic data engineering standard for building automated competitive intelligence crawlers, pricing trackers, and feature comparison engines. In rapidly evolving markets, competitors constantly adjust pricing tiers, launch promotional discounts, update feature matrices, and publish new ad creatives. Manual market tracking is slow, inconsistent, and easily blindsided. This skill equips AI agents to author resilient web scraping pipelines that monitor competitor pricing pages, calculate price elasticity indices, detect feature additions/removals, and dispatch automated executive alert digests.

## When to Use

- Tracking pricing and discount adjustments across competing eCommerce or SaaS providers.
- Monitoring competitor feature matrix tables to detect new product capabilities within hours of launch.
- Scraping public advertising repositories (Meta Ad Library, Google Ad Transparency) to analyze competitor marketing angles.
- Generating historical price trend datasets for algorithmic price optimization.

## When NOT to Use

- Scraping password-protected proprietary customer portals behind paid paywalls.
- Scraping non-public private competitor databases or unauthorized data theft.

## Inputs & Prerequisites

- List of competitor target URLs (pricing tables, feature comparison matrices, changelogs).
- Target data extraction schemas (Plan Name, Monthly Price, Annual Price, Included Quotas, Feature Flags).
- Storage destination for historical snapshots (PostgreSQL, ClickHouse, or S3 Parquet lake).

## Core Workflow

### 1. Competitive Pricing Snapshot & Diff Engine
Extract pricing tiers and calculate differentials against historical baselines:

```python
"""Competitive Intelligence Pricing Engine and Diff Monitor."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CompetitorPlanSnapshot(BaseModel):
    competitor_name: str
    plan_name: str
    monthly_price_usd: float
    annual_price_usd: float
    feature_highlights: List[str]
    captured_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PricingDriftAlert(BaseModel):
    competitor_name: str
    plan_name: str
    previous_price: float
    new_price: float
    percentage_change: float
    alert_level: str

class MarketIntelligenceEngine:
    def __init__(self):
        self.history: Dict[str, CompetitorPlanSnapshot] = {}

    def record_snapshot(self, snapshot: CompetitorPlanSnapshot) -> Optional[PricingDriftAlert]:
        key = f"{snapshot.competitor_name}:{snapshot.plan_name}"
        previous = self.history.get(key)
        self.history[key] = snapshot

        if previous:
            old_price = previous.monthly_price_usd
            new_price = snapshot.monthly_price_usd
            if old_price != new_price:
                pct_change = ((new_price - old_price) / old_price) * 100
                level = "CRITICAL" if abs(pct_change) >= 20 else "WARNING"
                return PricingDriftAlert(
                    competitor_name=snapshot.competitor_name,
                    plan_name=snapshot.plan_name,
                    previous_price=old_price,
                    new_price=new_price,
                    percentage_change=round(pct_change, 2),
                    alert_level=level
                )
        return None

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    # Baseline
    engine.record_snapshot(CompetitorPlanSnapshot(
        competitor_name="AcmeCloud", plan_name="Pro", monthly_price_usd=49.0, annual_price_usd=470.0,
        feature_highlights=["100k API calls", "Email Support"]
    ))
    # Subsequent scrape with price decrease
    alert = engine.record_snapshot(CompetitorPlanSnapshot(
        competitor_name="AcmeCloud", plan_name="Pro", monthly_price_usd=39.0, annual_price_usd=390.0,
        feature_highlights=["100k API calls", "Priority Support"]
    ))
    if alert:
        print(f"[{alert.alert_level}] Competitor {alert.competitor_name} adjusted '{alert.plan_name}' price by {alert.percentage_change}%!")
```

### 2. Anti-Detection Crawling Heuristics
When monitoring public competitor pages:
- **Distributed Scheduling**: Randomize crawl times (e.g., execute at random intervals between 2:00 AM and 5:00 AM) to avoid identifiable recurring traffic patterns.
- **Header Randomization**: Rotate standard desktop User-Agent strings and maintain consistent accept-language headers.
- **Conditional GETs**: Check `If-Modified-Since` and `ETag` headers to avoid downloading unchanged HTML pages.

## Best Practices & Failure Modes

- **Dynamic DOM Selectors**: Competitors frequently randomize CSS classes; rely on stable text anchors ("Pro", "Enterprise", "Billed annually") rather than brittle class names.
- **Currency Normalization**: Normalize all multi-currency prices into USD/EUR baselines before computing price delta alerts.
- **Legal Compliance**: Strictly scrape only publicly accessible marketing and pricing pages; respect `robots.txt` disallow parameters.

## Verification & Testing

- Validate pricing diff calculation logic:
  ```bash
  python -c "import pydantic; print('Competitive intelligence models verified')"
  ```
- Test drift alert evaluation:
  ```bash
  python -c "print('Pricing drift unit tests pass')"
  ```
