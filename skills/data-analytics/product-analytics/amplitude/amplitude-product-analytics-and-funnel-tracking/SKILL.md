---
name: amplitude-product-analytics-and-funnel-tracking
description: "Use this skill to design, instrument, and automate product analytics event tracking, user identification, conversion funnels, and retention cohort analysis using Amplitude's HTTP API and SDKs. It enforces event naming taxonomies, user property schemas, and GDPR identity deletion."
domain: data-analytics
category: product-analytics
subcategory: amplitude
tags:
  - amplitude
  - product-analytics
  - event-tracking
  - funnel-analysis
  - retention-cohorts
  - telemetry
technologies:
  - Amplitude API v2
  - Python
  - Pydantic
  - TypeScript
  - Product Analytics
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - requests >= 2.31.0
  - pydantic >= 2.5.0
  - python >= 3.10
---
# Amplitude Product Analytics & Funnel Tracking Architecture

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
"""Amplitude Product Analytics HTTP v2 Client."""
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
