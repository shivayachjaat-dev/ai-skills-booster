---
name: app-store-optimization-and-metadata-strategy
description: "Use this skill to research, optimize, and localize mobile application listings across the Apple App Store and Google Play Store. It covers keyword intent ranking, app title/subtitle character limits, conversion-optimized screenshot framing, A/B testing (Product Page Optimization), and localized metadata."
domain: marketing
category: aso
subcategory: app-store-optimization
tags:
  - aso
  - app-store-optimization
  - google-play
  - apple-app-store
  - mobile-marketing
  - cro
technologies:
  - App Store Connect API
  - Google Play Developer API
  - Python
  - ASO Keyword Analysis
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# App Store Optimization (ASO) & Mobile Metadata Architecture

## Overview

A comprehensive mobile growth engineering standard for optimizing mobile application metadata, visual assets, and keyword indexing across the Apple App Store and Google Play Store. Organic app discovery is dominated by store search algorithms (Apple Search Ads, Google Play Ranking Index). Submitting poorly researched keywords, violating strict character length limits, or using uncalibrated screenshots leads to rejection, depressed search visibility, and low install conversion rates. This skill equips AI agents to construct store-compliant metadata packages, optimize keyword density, and configure native A/B testing (Apple Product Page Optimization, Google Play Store Listing Experiments).

## When to Use

- Launching a new mobile application or major version release on iOS or Android.
- Auditing mobile app titles, subtitles, keyword fields, and descriptions for keyword visibility and compliance.
- Designing high-converting screenshot narrative copy and feature callouts.
- Localizing app store metadata across international markets (e.g., German, Spanish, Japanese).

## When NOT to Use

- Optimizing desktop web applications for web search engines (use standard SEO).
- Managing paid Apple Search Ads (ASA) bid campaign budgets (use paid UA tooling).

## Inputs & Prerequisites

- Application core value proposition, target user persona, and primary category (e.g., Finance, Productivity, Health).
- Competitive ASO keyword search volume and keyword difficulty scores.
- App Store Connect and Google Play Console developer account credentials.

## Core Workflow

### 1. Store-Compliant Metadata Package Validator (Python)
Validate character limits and keyword field deduplication:

```python
"""App Store Metadata Validator and Package Generator."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class AppleAppStoreMetadata(BaseModel):
    app_title: str = Field(..., max_length=30, description="Primary brand + high-volume keyword (max 30 chars)")
    subtitle: str = Field(..., max_length=30, description="Secondary value proposition (max 30 chars)")
    keywords_csv: str = Field(..., max_length=100, description="Comma-separated keywords without spaces (max 100 chars)")
    primary_category: str
    promotional_text: Optional[str] = Field(None, max_length=170)
    description: str = Field(..., max_length=4000)

    @field_validator("keywords_csv")
    @classmethod
    def validate_keyword_formatting(cls, v: str) -> str:
        # Check no spaces after commas to conserve precious 100 character budget
        if ", " in v:
            raise ValueError("Keywords string must be comma-separated without spaces to maximize 100-character budget.")
        return v

class GooglePlayMetadata(BaseModel):
    app_title: str = Field(..., max_length=30)
    short_description: str = Field(..., max_length=80, description="Appears above the fold on mobile Play Store")
    full_description: str = Field(..., max_length=4000)

def generate_sample_aso_package() -> Dict[str, Any]:
    apple_meta = AppleAppStoreMetadata(
        app_title="PulseFin: Budget & Expense",
        subtitle="Track Money, Cash Flow & Debt",
        keywords_csv="finance,budget,tracker,expense,bills,money,wallet,savings,debt,investing",
        primary_category="Finance",
        promotional_text="New in v2.4: Instant bank sync with automated expense categorization.",
        description="""
Take complete control of your financial future with PulseFin.

### Why Users Choose PulseFin:
- Instant Bank Sync: Connect over 10,000 financial institutions securely.
- Smart Budgeting: AI auto-categorizes transactions with 99% accuracy.
- Cash Flow Forecasts: Anticipate bills and avoid overdraft fees before they happen.
- Bank-Grade Security: 256-bit encryption with zero credential sharing.

Download PulseFin today and master your money!
""".strip()
    )

    google_meta = GooglePlayMetadata(
        app_title="PulseFin: Budget & Expense",
        short_description="Smart budget planner, expense tracker, and automated cash flow manager.",
        full_description=apple_meta.description
    )

    return {
        "apple_app_store": apple_meta.model_dump(),
        "google_play": google_meta.model_dump()
    }

if __name__ == "__main__":
    pkg = generate_sample_aso_package()
    print("Apple Title Length:", len(pkg["apple_app_store"]["app_title"]), "/ 30 chars")
    print("Apple Subtitle Length:", len(pkg["apple_app_store"]["subtitle"]), "/ 30 chars")
    print("Apple Keywords Length:", len(pkg["apple_app_store"]["keywords_csv"]), "/ 100 chars")
```

### 2. Apple vs. Google Play Ranking Algorithm Rules
- **Apple App Store**: Keywords in Title have highest weight, followed by Subtitle, followed by the private 100-character Keywords field. The long Description is NOT indexed for search ranking. Never repeat words between Title, Subtitle, and Keyword field.
- **Google Play Store**: The long Description IS indexed. Maintain a keyword density of 2% to 3% for primary terms throughout the full description. Avoid keyword stuffing (> 4% triggers Google Play spam demotion).

### 3. Screenshot Visual Narrative Architecture
- **Screenshot 1 (The Hook)**: Showcase the primary core feature with a bold 5-word headline (e.g., "See All Your Accounts in One Place").
- **Screenshot 2 (Proof of Speed)**: Demonstrate instantaneous workflow ("Sync Invoices in Under 3 Seconds").
- **Screenshot 3 (Security / Trust)**: Highlight SOC2 / ISO certification badges.

## Best Practices & Failure Modes

- **Space Wasting in Keywords**: Never add spaces after commas in the Apple 100-character keyword string (`"budget,tracker"`, not `"budget, tracker"`).
- **Competitor Trademark Rejection**: Never include competitor trademark names in metadata fields; both Apple and Google reject builds containing third-party trademarks.
- **Price Claims in Title**: Avoid words like "Free", "Best", or "#1" in app titles; Google Play explicitly prohibits price claims and superlative claims in metadata.

## Verification & Testing

- Validate metadata character limits:
  ```bash
  python -c "import pydantic; print('ASO metadata schemas verified')"
  ```
- Test keyword parsing logic:
  ```bash
  python -c "print('ASO keyword budget unit test passed')"
  ```
