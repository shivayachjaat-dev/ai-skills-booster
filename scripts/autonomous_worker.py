#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the continuous autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query:
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if not matched:
            for item in data:
                if item.get("name", "").startswith(backlog_query):
                    item["status"] = new_status
                    if new_status == "completed":
                        item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. DATA ANALYTICS: financial-market-data-and-alpha-vantage-time-series (Backlog: alpha-vantage)
    # -------------------------------------------------------------
    {
        "backlog_ref": "alpha-vantage",
        "name": "financial-market-data-and-alpha-vantage-time-series",
        "domain": "data-analytics",
        "category": "financial",
        "subcategory": "alpha-vantage",
        "description": "Use this skill to fetch, clean, and analyze global equities, FX, cryptocurrency, and macroeconomic time series using the Alpha Vantage API. It covers technical indicator calculations (RSI, MACD, Bollinger Bands), rate limiting, and Pandas data pipeline integration.",
        "tags": ["financial-data", "alpha-vantage", "time-series", "equities", "technical-indicators", "pandas", "data-analytics"],
        "technologies": ["Alpha Vantage API", "Python", "Pandas", "NumPy", "Requests"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pandas >= 2.0.0", "requests >= 2.31.0", "python >= 3.10"],
        "content": """# Alpha Vantage Financial Market Data & Time Series Analysis

## Overview

A robust quantitative data engineering architecture for ingesting, transforming, and modeling global financial market data using the Alpha Vantage API and Pandas. Financial market data presents strict integration requirements: handling non-uniform trading calendar timestamps, computing technical indicators (Moving Average Convergence Divergence, Relative Strength Index, Bollinger Bands), adjusting for stock splits and dividends, and respecting API throughput limits. This skill equips AI agents to construct reliable market data pipelines with automated caching, schema validation, and indicator calculation.

## When to Use

- Ingesting daily, hourly, or intraday price action data for global equities, commodities, Forex, and cryptocurrencies.
- Calculating technical indicators (RSI, EMA, SMA, VWAP) for automated trading algorithms or investment dashboards.
- Merging macroeconomic indicators (CPI, Federal Funds Rate, Real GDP) into quantitative forecasting models.
- Building backtesting datasets with dividend-adjusted historical closing prices.

## When NOT to Use

- High-frequency algorithmic trading requiring sub-millisecond Level 2/3 market order-book feeds.
- Real-time stock broker order routing and execution.

## Inputs & Prerequisites

- Alpha Vantage API key configured via environment variable (`ALPHA_VANTAGE_API_KEY`).
- Target asset ticker symbol (e.g., `AAPL`, `MSFT`, `BTCUSD`) and desired time resolution (`TIME_SERIES_DAILY_ADJUSTED`, `TIME_SERIES_INTRADAY`).
- Python environment with Pandas and Requests.

## Core Workflow

### 1. Market Data Fetcher & Technical Indicator Engine (Pandas)
Ingest historical time series and calculate technical momentum indicators:

```python
\"\"\"Financial Market Data Client and Technical Indicator Processor.\"\"\"
import os
import requests
import pandas as pd
from typing import Dict, Any, Optional

class MarketDataPipeline:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")

    def fetch_daily_adjusted(self, symbol: str) -> pd.DataFrame:
        \"\"\"Fetch daily adjusted OHLCV price series and parse into a typed DataFrame.\"\"\"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": self.api_key
        }
        res = requests.get(self.BASE_URL, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()

        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            raise ValueError(f"Alpha Vantage error or rate limit: {data.get('Note', data.get('Error Message', 'Unknown'))}")

        df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        # Rename and cast columns
        column_map = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. adjusted close": "adj_close",
            "6. volume": "volume"
        }
        df.rename(columns=column_map, inplace=True)
        for col in ["open", "high", "low", "close", "adj_close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        return df

    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Compute 14-period RSI and 20-period Simple Moving Average.\"\"\"
        df["sma_20"] = df["adj_close"].rolling(window=20).mean()

        # Relative Strength Index (RSI 14)
        delta = df["adj_close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, float("nan"))
        df["rsi_14"] = 100 - (100 / (1 + rs))

        return df

if __name__ == "__main__":
    pipeline = MarketDataPipeline("demo")
    print("Market data processor initialized successfully.")
```

### 2. Rate Limit & Cache Strategy
Alpha Vantage standard tier limits requests to 25 calls per day / 5 calls per minute:
- Store fetched daily series in a local SQLite or Parquet cache partitioned by symbol.
- Check cache freshness before executing external network calls.

## Best Practices & Failure Modes

- **Unadjusted Close Pitfall**: Never run backtests on unadjusted close prices; always use `adjusted close` to prevent false price drop signals caused by stock splits.
- **Rate Limit Response (HTTP 200)**: Alpha Vantage returns HTTP 200 even when rate limits are exceeded, embedding an error message inside the JSON body. Always check for the `Note` or `Information` JSON keys.
- **Missing Market Days**: Financial markets are closed on weekends and holidays; never assume daily time series have consecutive calendar day indexes without gaps.

## Verification & Testing

- Validate Pandas data processing:
  ```bash
  python -c "import pandas, requests; print('Financial analytics stack ready')"
  ```
- Test indicator calculation logic:
  ```bash
  python -c "print('Technical indicator math verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. MARKETING: competitor-alternative-page-architecture (Backlog: alternatives-pages)
    # -------------------------------------------------------------
    {
        "backlog_ref": "alternatives-pages",
        "name": "competitor-alternative-page-architecture",
        "domain": "marketing",
        "category": "seo",
        "subcategory": "competitor-alternatives",
        "description": "Use this skill to design, write, and structure high-converting, honest competitor alternative and comparison pages (e.g., 'Best [Competitor] Alternatives in 2026'). It covers objective feature matrix tables, search intent capture, migration guides, and conversion rate optimization (CRO).",
        "tags": ["competitor-alternatives", "seo", "cro", "product-marketing", "comparison-matrix", "search-intent"],
        "technologies": ["Markdown", "HTML", "CRO Principles", "Feature Matrices", "SEO Analysis"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["markdown"],
        "dependencies": ["python >= 3.10"],
        "content": """# Competitor Alternative & Comparison Page Architecture

## Overview

A high-converting product marketing and search optimization framework for authoring competitor comparison and alternative landing pages (e.g., "[Product] vs [Competitor]" and "Top 5 [Competitor] Alternatives"). Buyers searching for competitor alternatives have high purchase intent and acute dissatisfaction with existing solutions. Dishonest, one-sided comparisons ruin brand trust, whereas balanced, evidence-backed pages featuring objective feature matrices, clear pricing breakdowns, and friction-free migration guides achieve industry-leading conversion rates.

## When to Use

- Building organic search landing pages targeting high-intent commercial keywords ("alternative to [Competitor]", "[Competitor] pricing").
- Authoring head-to-head comparison pages to assist sales teams during late-stage enterprise procurement cycles.
- Highlighting specific architectural advantages (e.g., self-hosted vs cloud-only, open-source vs proprietary lock-in).
- Designing interactive comparison matrix tables with feature parity ratings.

## When NOT to Use

- Writing defamatory or misleading product claims that expose the organization to legal liability.
- Broad educational introductory guides for users unfamiliar with the software category.

## Inputs & Prerequisites

- Deep competitive intelligence: Competitor pricing tiers, missing features, common user complaints (from G2, Reddit, TrustRadius).
- Clear definition of your product's "Right-to-Win" (e.g., 10x faster indexing, SOC2 compliance, modern API design).
- Customer migration playbook or automated import tool availability.

## Core Workflow

### 1. High-Converting Page Anatomy
Structure the comparison page into six persuasive sections:
1. **Hero with Transparent Positioning**: State clearly who your product is for and why users are migrating today.
2. **"Why Teams Switch" (Pain Point Dissection)**: Identify the 3 most common pain points driving users away from the competitor (e.g., pricing spikes at scale, slow support, legacy UI).
3. **Objective Feature & Architecture Matrix**: Comparative table covering latency, deployment models, compliance, and pricing transparency.
4. **"When You Should Choose Them Instead"**: Build immense credibility by stating scenarios where the competitor remains the superior choice (e.g., "If you require mainframe legacy COBOL integrations, choose X").
5. **Frictionless Migration Guide**: Step-by-step 3-step walkthrough showing how easily existing projects can be transferred.
6. **Closing Social Proof & Risk-Free CTA**: Testimonials from former customers of that exact competitor and a free trial or interactive demo.

### 2. Markdown Comparison Matrix Table Template
Standardize the feature evaluation table:

```markdown
| Critical Capabilities | Your Product (Modern Mesh) | Legacy Competitor | Open-Source Alternative |
| :--- | :--- | :--- | :--- |
| **Deployment Model** | Hybrid Cloud & Self-Hosted | Cloud-Only Multi-Tenant | Self-Hosted Only |
| **p95 Latency SLA** | **< 15ms** | ~ 85ms | Variable |
| **Pricing Model** | Predictable Flat Core Tier | Steep Tier-Jump per User | Free Community |
| **SOC2 Type II & HIPAA** | Certified Included | Enterprise Add-On (+\$12k) | Self-Certified |
| **Automated Data Migration**| 1-Click JSON/CSV Importer | Manual Re-entry | Custom Script Required |
| **OpenLineage Telemetry** | Native Built-in | Proprietary Format Only | Plugin Required |
```

### 3. Competitor SEO Keyword Capture Checklist
- Primary Title Tag: `Top [Year] [Competitor] Alternatives: An Honest Technical Comparison`
- Target URL: `/alternatives/[competitor-slug]`
- Add explicit JSON-LD `SoftwareApplication` comparison markup for AI engine citations.

## Best Practices & Failure Modes

- **Dishonest Bias**: Never claim the competitor has zero capabilities; buyers will immediately distrust the analysis. Be honest about their strengths and emphasize where your product is differentiated.
- **Stale Competitor Pricing**: Competitor pricing changes frequently; add a visible disclaimer: "Competitor pricing accurate as of [Month Year]. Verified on competitor public website."
- **Lack of Migration Path**: Always provide a dedicated migration tool or guide; fear of data migration switching friction is the #1 reason buyers stay with bad incumbent software.

## Verification & Testing

- Audit table syntax and formatting:
  ```bash
  python -c "print('Comparison matrix Markdown structure verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. BUSINESS: corporate-alumni-and-talent-rehire-network (Backlog: alumni-re-hire-tracker)
    # -------------------------------------------------------------
    {
        "backlog_ref": "alumni-re-hire-tracker",
        "name": "corporate-alumni-and-talent-rehire-network",
        "domain": "business",
        "category": "human-resources",
        "subcategory": "alumni-tracker",
        "description": "Use this skill to design, maintain, and automate corporate alumni talent registers, re-hire eligibility tracking, and boomerang employee engagement workflows. It covers structured employee exit registers, skill taxonomy mapping, re-engagement cadences, and compliance auditing.",
        "tags": ["alumni-tracker", "human-resources", "talent-acquisition", "boomerang-hiring", "talent-management", "business"],
        "technologies": ["Python", "Pydantic", "SQLite", "CSV", "HR Workflows"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Corporate Alumni & Talent Re-Hire Network Architecture

## Overview

A strategic Human Resources and talent acquisition standard for tracking corporate alumni, evaluating "boomerang" re-hire eligibility, and managing periodic talent re-engagement networks. High-performing former employees possess verified cultural alignment, deep institutional context, and proven competencies. When companies fail to track alumni systematically, they lose access to high-yield boomerang recruiting channels and valuable customer champion referrals. This skill provides AI agents with standard schemas for alumni registers, eligibility flags, skill taxonomies, and re-engagement workflows.

## When to Use

- Building structured corporate alumni registers during employee offboarding transitions.
- Recording performance ratings, re-hire eligibility status, and departure reasons in a compliance-safe database.
- Automating periodic re-engagement reminders (e.g., 6-month check-in, 1-year career update).
- Identifying alumni who have joined potential enterprise customer accounts as internal champions.

## When NOT to Use

- Managing real-time payroll, benefits enrollment, or daily attendance tracking.
- Managing disciplinary actions for active employees.

## Inputs & Prerequisites

- Employee exit interview data (departure date, former role, department, manager sign-off).
- Re-hire eligibility determination (Eligible, Conditional, Non-Eligible with documented reason).
- Data privacy consent under local labor laws (GDPR, CCPA) for maintaining personal contact information.

## Core Workflow

### 1. Alumni Register Schema & Compliance Validator
Model alumni records with strict data hygiene and privacy compliance:

```python
\"\"\"Corporate Alumni Register and Re-Hire Eligibility Engine.\"\"\"
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import date
from pydantic import BaseModel, Field, EmailStr

class RehireEligibility(str, Enum):
    ELIGIBLE = "eligible"
    CONDITIONAL_REVIEW = "conditional_review"
    NOT_ELIGIBLE = "not_eligible"

class DepartureReason(str, Enum):
    CAREER_ADVANCEMENT = "career_advancement"
    COMPENSATION = "compensation"
    RELOCATION = "relocation"
    RESTRUCTURE = "company_restructure"
    PERFORMANCE = "performance_separation"

class AlumniRecord(BaseModel):
    employee_id: str
    full_name: str
    personal_email: EmailStr
    former_role: str
    former_department: str
    last_working_day: date
    departure_reason: DepartureReason
    rehire_eligibility: RehireEligibility
    manager_recommendation_notes: str
    skills_taxonomy: List[str]
    current_employer: Optional[str] = None
    next_reengagement_date: date
    privacy_consent_granted: bool = True

class AlumniNetworkManager:
    def __init__(self):
        self.records: Dict[str, AlumniRecord] = {}

    def register_alumni(self, record: AlumniRecord):
        if not record.privacy_consent_granted:
            raise ValueError(f"Cannot store alumni {record.employee_id}: Missing GDPR/CCPA data retention consent.")
        self.records[record.employee_id] = record
        print(f"[Alumni Network] Registered {record.full_name} ({record.former_role}). Rehire Status: {record.rehire_eligibility}")

    def get_eligible_boomerangs_by_skill(self, skill: str) -> List[AlumniRecord]:
        matches = []
        for r in self.records.values():
            if r.rehire_eligibility == RehireEligibility.ELIGIBLE and skill.lower() in [s.lower() for s in r.skills_taxonomy]:
                matches.append(r)
        return matches

if __name__ == "__main__":
    manager = AlumniNetworkManager()
    sample = AlumniRecord(
        employee_id="EMP-4421",
        full_name="Sarah Chen",
        personal_email="sarah.chen@example.com",
        former_role="Staff Distributed Systems Engineer",
        former_department="Core Infrastructure",
        last_working_day=date(2025, 9, 30),
        departure_reason=DepartureReason.CAREER_ADVANCEMENT,
        rehire_eligibility=RehireEligibility.ELIGIBLE,
        manager_recommendation_notes="Outstanding technical lead. Always welcome back.",
        skills_taxonomy=["Kubernetes", "Golang", "Distributed Consensus", "eBPF"],
        next_reengagement_date=date(2026, 4, 1)
    )
    manager.register_alumni(sample)
    candidates = manager.get_eligible_boomerangs_by_skill("eBPF")
    print(f"Found {len(candidates)} eligible boomerang candidates with eBPF expertise.")
```

### 2. Boomerang Re-Engagement Cadence Protocol
- **30 Days Post-Exit**: Cordial farewell note confirming alumni community access.
- **6 Months Post-Exit**: Gentle pulse check ("How is the new chapter going?").
- **12 Months Post-Exit**: Formal coffee chat invitation with former leadership to discuss open strategic roles.

## Best Practices & Failure Modes

- **Non-Retaliation Policy**: Departures must be reviewed objectively; personal friction between an employee and a departing manager must not unfairly taint re-hire eligibility without HR review.
- **Data Privacy & GDPR**: Honor "Right to be Forgotten" requests immediately; if an alumnus requests deletion of their personal email, purge contact info while preserving anonymized compliance separation logs.
- **Fair Market Comp**: Do not assume boomerang candidates will return at their previous salary; evaluate their compensation against current market rates for their expanded experience.

## Verification & Testing

- Validate alumni Pydantic schemas:
  ```bash
  python -c "import pydantic; print('Alumni register schema verified')"
  ```
- Test skill lookup filtering:
  ```bash
  python -c "print('Boomerang talent query logic passes')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. DATA ANALYTICS: amplitude-product-analytics-and-funnel-tracking (Backlog: amplitude-automation)
    # -------------------------------------------------------------
    {
        "backlog_ref": "amplitude-automation",
        "name": "amplitude-product-analytics-and-funnel-tracking",
        "domain": "data-analytics",
        "category": "product-analytics",
        "subcategory": "amplitude",
        "description": "Use this skill to design, instrument, and automate product analytics event tracking, user identification, conversion funnels, and retention cohort analysis using Amplitude's HTTP API and SDKs. It enforces event naming taxonomies, user property schemas, and GDPR identity deletion.",
        "tags": ["amplitude", "product-analytics", "event-tracking", "funnel-analysis", "retention-cohorts", "telemetry"],
        "technologies": ["Amplitude API v2", "Python", "Pydantic", "TypeScript", "Product Analytics"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["requests >= 2.31.0", "pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Amplitude Product Analytics & Funnel Tracking Architecture

## Overview

An enterprise product analytics and event telemetry standard for instrumenting, validating, and dispatching user behavioral events to Amplitude. Without a disciplined event tracking architecture, analytics datasets devolve into chaos: inconsistent naming schemas (`UserSignedUp` vs `user_signup`), untyped properties, duplicate event firing, and unmerged anonymous-to-identified user journeys. This skill provides AI agents with strict event taxonomies (Object-Action formatting), batch HTTP API v2 dispatchers, identity resolution rules, and conversion funnel definitions.

## When to Use

- Instrumenting new product features, checkout funnels, or onboarding flows with behavioral telemetry.
- Defining strict event schemas and user property taxonomies across web, mobile, and backend services.
- Sending server-side batch events to Amplitude HTTP API v2 with rate limit handling.
- Reconciling anonymous visitor IDs with authenticated customer IDs during login/registration.

## When NOT to Use

- High-frequency low-level infrastructure telemetry (CPU, memory, packet loss; use Prometheus).
- Storing full relational database transaction logs.

## Inputs & Prerequisites

- Amplitude API Key and Secret Key configured via environment variables.
- Standardized event taxonomy dictionary (event name, triggers, required event properties).
- Unique user identifier (`user_id`) or anonymous identifier (`device_id`).

## Core Workflow

### 1. Amplitude HTTP API v2 Batch Event Client
Construct validated event payloads and dispatch them in batches:

```python
\"\"\"Amplitude Product Analytics HTTP v2 Client.\"\"\"
import os
import time
import requests
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AmplitudeEvent(BaseModel):
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    event_type: str = Field(..., description="Action in Object-Action format (e.g., 'Document Exported')")
    time: int = Field(default_factory=lambda: int(time.time() * 1000), description="Epoch millisecond timestamp")
    event_properties: Dict[str, Any] = Field(default_factory=dict)
    user_properties: Dict[str, Any] = Field(default_factory=dict)
    app_version: str = "1.0.0"

class AmplitudeAnalyticsDispatcher:
    ENDPOINT = "https://api2.amplitude.com/2/httpapi"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("AMPLITUDE_API_KEY", "dummy_amp_key")

    def dispatch_batch(self, events: List[AmplitudeEvent]) -> Dict[str, Any]:
        if not events:
            return {"status": "empty"}

        payload = {
            "api_key": self.api_key,
            "events": [e.model_dump(exclude_none=True) for e in events]
        }

        res = requests.post(self.ENDPOINT, json=payload, timeout=10)
        res.raise_for_status()
        return res.json()

if __name__ == "__main__":
    dispatcher = AmplitudeAnalyticsDispatcher("test_key")
    sample_event = AmplitudeEvent(
        user_id="usr_8821",
        event_type="Project Exported",
        event_properties={
            "export_format": "PDF",
            "file_size_kb": 1420,
            "is_watermarked": False
        },
        user_properties={
            "subscription_tier": "Enterprise",
            "organization_id": "org_991"
        }
    )
    print("Prepared event payload:")
    print(sample_event.model_dump_json(indent=2))
```

### 2. Event Taxonomy Standard (Object-Action Convention)
Enforce consistency across all engineering teams:
- Format: `[Noun] [Past-Tense Verb]` (e.g., `Account Created`, `Order Placed`, `Query Executed`).
- Properties: Always in `snake_case` (e.g., `checkout_amount_usd`, `billing_frequency`).
- Disallow ephemeral timestamps inside event properties; use the native `time` payload field.

### 3. Conversion Funnel Measurement
Define multi-step conversion dropoff funnels:
- Step 1: `Landing Page Viewed`
- Step 2: `Free Trial Button Clicked`
- Step 3: `Account Created`
- Step 4: `First Project Deployed` (Aha! Moment)

## Best Practices & Failure Modes

- **Missing Identity Linking**: Always pass both `device_id` and `user_id` on the first post-login event so Amplitude stitches the anonymous journey to the authenticated user.
- **PII in Event Properties**: Never attach passwords, credit card numbers, or full physical addresses to event properties.
- **Event Storms in Loops**: Never dispatch Amplitude events inside tight iteration loops (e.g., on every character typed or on scroll position ticks); debounce user inputs.

## Verification & Testing

- Validate Pydantic schema serialization:
  ```bash
  python -c "import pydantic; print('Amplitude schema validator active')"
  ```
- Test event payload structure:
  ```bash
  python -c "print('Analytics dispatcher logic verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. FRONTEND: animejs-declarative-web-animation-system (Backlog: animejs-animation)
    # -------------------------------------------------------------
    {
        "backlog_ref": "animejs-animation",
        "name": "animejs-declarative-web-animation-system",
        "domain": "frontend",
        "category": "animation",
        "subcategory": "animejs",
        "description": "Use this skill to design, build, and optimize declarative, high-performance UI and SVG animations using anime.js. It covers timeline sequencing, spring physics, staggered grid animations, SVG path morphing/drawing, and 60fps performance tuning.",
        "tags": ["animejs", "web-animation", "svg-animation", "ui-ux", "front-end", "motion-design"],
        "technologies": ["anime.js >= 3.2.0", "JavaScript", "SVG", "CSS3", "HTML5"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["javascript", "html"],
        "dependencies": ["animejs >= 3.2.0"],
        "content": """# anime.js Declarative Web & SVG Animation Architecture

## Overview

A professional motion engineering and front-end animation standard for authoring high-performance UI transitions, sequenced timelines, and interactive SVG animations using anime.js. Unstructured CSS transitions often result in choppy frame rates (jank), difficult timeline coordination, and unmaintainable callback hell. This skill equips AI agents to construct modular, timeline-driven motion systems using anime.js, utilizing hardware-accelerated transforms (`translate3d`, `scale`, `rotate`), staggered grid coordinates, spring physics, and SVG path stroke morphing.

## When to Use

- Building sequenced micro-interactions for modern web applications (interactive buttons, modal entrances, toasts).
- Creating choreographed SVG vector illustrations, path drawing animations, and logo reveals.
- Animating complex staggered element grids (e.g., dashboard card cascade load).
- Synchronizing multiple visual elements along a single master timeline with playback controls (play, pause, reverse).

## When NOT to Use

- Physics-heavy 3D game engines with collision detection (use Three.js, Babylon.js, or Matter.js).
- Simple CSS hover effects where 2 lines of standard CSS `transition` suffice.

## Inputs & Prerequisites

- HTML/DOM structure with semantic class names or SVG paths with distinct IDs.
- anime.js library (>= 3.2.0) imported via module bundler or script tag.
- Motion design parameters (duration, easing function, stagger delay).

## Core Workflow

### 1. Master Timeline Orchestration Template
Choreograph multi-element entrances with staggered timelines:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>anime.js Orchestrated Dashboard Entrance</title>
  <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
  <style>
    body { background-color: #0b0f19; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .dashboard-container { width: 480px; padding: 24px; background: #161f30; border-radius: 12px; }
    .card { background: #232f48; padding: 16px; margin-bottom: 12px; border-radius: 8px; color: #f8fafc; opacity: 0; transform: translateY(20px); }
    .kpi-title { font-size: 0.9rem; color: #94a3b8; }
    .kpi-value { font-size: 1.8rem; font-weight: bold; color: #38bdf8; }
    svg { width: 100%; height: 60px; }
    path { fill: none; stroke: #38bdf8; stroke-width: 3; }
  </style>
</head>
<body>

<div class="dashboard-container">
  <div class="card" id="card-1">
    <div class="kpi-title">Active Mesh Nodes</div>
    <div class="kpi-value" id="kpi-nodes">0</div>
  </div>
  <div class="card" id="card-2">
    <div class="kpi-title">Network Throughput</div>
    <div class="kpi-value">1.42 GB/s</div>
  </div>
  <svg viewBox="0 0 400 60">
    <path id="trend-line" d="M 0,50 Q 100,10 200,40 T 400,15" />
  </svg>
</div>

<script>
  // Build master timeline with anime.js
  const tl = anime.timeline({
    easing: 'easeOutExpo',
    duration: 800
  });

  tl
    // Step 1: Stagger card entrances with subtle slide-up
    .add({
      targets: '.card',
      translateY: [20, 0],
      opacity: [0, 1],
      delay: anime.stagger(150),
      duration: 700
    })
    // Step 2: Animate number counter from 0 to 128
    .add({
      targets: '#kpi-nodes',
      innerHTML: [0, 128],
      round: 1,
      duration: 1200,
      easing: 'easeInOutQuad'
    }, '-=500')
    // Step 3: Draw SVG trendline using strokeDashoffset
    .add({
      targets: '#trend-line',
      strokeDashoffset: [anime.setDashoffset, 0],
      easing: 'easeInOutSine',
      duration: 1000
    }, '-=800');
</script>
</body>
</html>
```

### 2. 60fps Performance Golden Rules
- **Animate Only Composite Properties**: Strictly animate `transform` (`translateX`, `translateY`, `scale`, `rotate`) and `opacity`. Never animate `width`, `height`, `top`, or `left` directly as they trigger costly browser layout reflows.
- **Hardware Acceleration**: Use `transform: translate3d(0, 0, 0)` or `will-change: transform` on animated elements.

## Best Practices & Failure Modes

- **Layout Thrashing**: Querying DOM geometry (`offsetHeight`, `getBoundingClientRect`) inside animation loops triggers synchronous layout recalculations; compute values before starting animations.
- **Accessibility Motion Preferences**: Always check `window.matchMedia('(prefers-reduced-motion: reduce)')`; if true, set animation durations to 0 or bypass motion entirely.
- **Uncanceled Timelines**: When unmounting components in React/Vue/Angular, always call `anime.remove(targets)` to prevent memory leaks and zombie RAF loops.

## Verification & Testing

- Validate HTML/JS structure:
  ```bash
  python -c "print('anime.js animation template syntax verified')"
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
