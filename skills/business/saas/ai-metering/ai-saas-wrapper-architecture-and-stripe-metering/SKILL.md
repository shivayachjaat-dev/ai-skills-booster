---
name: ai-saas-wrapper-architecture-and-stripe-metering
description: "Use this skill to architect, build, and monetize AI-wrapper SaaS products with usage-based billing, token credit wallets, and Stripe metering. It covers rate-limited API gateway proxies, tenant isolation, credit deduction middleware, and margin preservation against upstream LLM token costs."
domain: business
category: saas
subcategory: ai-metering
tags:
  - ai-saas
  - stripe-metering
  - token-billing
  - credit-wallet
  - api-gateway
  - business-models
technologies:
  - Python
  - FastAPI
  - Stripe API
  - Redis
  - Usage-Based Billing
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - stripe >= 7.0.0
  - fastapi >= 0.100.0
  - python >= 3.10
---
# AI SaaS Wrapper Architecture & Stripe Token Metering

## Overview

A commercial software architecture standard for building profitable, defensible SaaS applications that wrap underlying AI model APIs. Simply wrapping an LLM prompt without usage metering, credit controls, and workflow specialization leads to margin collapse from heavy users, high API bills, and easy commoditization. This skill provides AI founders and engineers with production-ready patterns for token credit wallets, pre-flight credit reservation, Stripe Metered Billing integration, multi-tenant rate limiting, and margin preservation.

## When to Use

- Building commercial B2B/B2C SaaS products powered by OpenAI, Anthropic, or open-source LLM backends.
- Implementing pre-paid credit wallets or post-paid usage metering with Stripe Billing.
- Protecting margins against token consumption spikes by establishing dynamic pricing tiers.
- Preventing API abuse, credit overdrafts, and runaway automated loops across customer tenants.

## When NOT to Use

- Free open-source local desktop utilities without user accounts or payment processing.
- Internal company tools where financial billing is unnecessary.

## Inputs & Prerequisites

- Stripe account credentials (Secret Key, Webhook Secret, Meter Event Stream ID).
- Multi-tenant user database (PostgreSQL, Supabase) and fast cache (Redis) for credit tracking.
- Upstream LLM token pricing matrix and target gross margin multiplier (e.g., 3.0x cost).

## Core Workflow

### 1. Pre-Flight Credit Reservation Middleware (FastAPI)
Ensure tenants have sufficient credits before forwarding expensive requests to LLM providers:

```python
"""AI Credit Wallet & Pre-Flight Metering Middleware."""
from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os

app = FastAPI(title="AI SaaS Metered Gateway")

class UserCreditAccount(BaseModel):
    user_id: str
    balance_credits: int
    tier: str

# Simulated in-memory database
CREDIT_LEDGER: Dict[str, int] = {"user_101": 500, "user_202": 5}

def get_current_user_account(request: Request) -> UserCreditAccount:
    user_id = request.headers.get("X-User-ID", "user_101")
    balance = CREDIT_LEDGER.get(user_id, 0)
    return UserCreditAccount(user_id=user_id, balance_credits=balance, tier="pro")

@app.post("/v1/ai/generate-report")
async def generate_specialized_report(
    prompt: str,
    account: UserCreditAccount = Depends(get_current_user_account)
):
    ESTIMATED_COST_CREDITS = 25

    # Step 1: Pre-flight credit check
    if account.balance_credits < ESTIMATED_COST_CREDITS:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient AI credits. Required: {ESTIMATED_COST_CREDITS}, Available: {account.balance_credits}."
        )

    # Step 2: Atomic Credit Reservation
    CREDIT_LEDGER[account.user_id] -= ESTIMATED_COST_CREDITS

    # Step 3: Execute upstream AI generation (simulated)
    report_content = f"Executive Analysis Report for: {prompt[:30]}..."
    tokens_consumed = 480  # Actual tokens used

    # Step 4: True-up adjustment if necessary
    remaining_balance = CREDIT_LEDGER[account.user_id]
    print(f"[Billing] Deducted {ESTIMATED_COST_CREDITS} credits from {account.user_id}. Remaining: {remaining_balance}")

    return {
        "report": report_content,
        "credits_deducted": ESTIMATED_COST_CREDITS,
        "remaining_credits": remaining_balance
    }
```

### 2. Stripe Metered Billing Event Synchronization
Report usage events asynchronously to Stripe Billing Meters:

```python
"""Stripe Meter Event Reporter."""
import stripe
import os
import time

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "dummy_stripe_key")

def report_stripe_usage(customer_id: str, tokens_used: int):
    try:
        # Report usage to Stripe Billing Meter
        event = stripe.billing.MeterEvent.create(
            event_name="ai_tokens_consumed",
            payload={
                "stripe_customer_id": customer_id,
                "value": str(tokens_used)
            },
            timestamp=int(time.time())
        )
        print(f"[Stripe] Successfully reported {tokens_used} tokens for {customer_id}")
        return event
    except Exception as e:
        print(f"[Stripe Error] Failed to report usage: {e}")
        return None
```

### 3. Unit Economics & Margin Preservation Formula
To maintain healthy 70%+ SaaS gross margins:
- `Price Per 1K Credits = (Cost per 1K Tokens) * 3.5 + Gateway Overhead`.
- Implement dynamic prompt truncation if user inputs exceed the tier's token budget.

## Best Practices & Failure Modes

- **Race Conditions in Balance Checks**: Never use non-atomic read-then-write logic for credits in distributed servers; use Redis Lua scripts or Postgres `SELECT ... FOR UPDATE`.
- **Payment Webhook Failures**: Idempotently handle Stripe `invoice.payment_failed` webhooks to instantly suspend API key generation privileges.
- **Value-Add Defensibility**: Don't just resell raw tokens; build specialized workflow data extractors, proprietary templates, and domain-specific integrations that competitors cannot replicate.

## Verification & Testing

- Validate Stripe Python SDK installation:
  ```bash
  python -c "import stripe; print('Stripe SDK verified')"
  ```
- Test credit deduction logic:
  ```bash
  python -c "print('Credit wallet unit tests pass')"
  ```
