---
name: enterprise-software-selection-and-rfp
description: "Use this skill when evaluating, scoring, and selecting commercial-off-the-shelf (COTS) and SaaS software solutions through evidence-backed scoring matrices and Request for Proposal (RFP) processes. It covers requirements weighting, compliance auditing (SOC2, HIPAA, GDPR), Total Cost of Ownership (TCO) modeling, security reviews, and vendor pilot proof-of-concepts."
domain: business
category: procurement
subcategory: software-selection
tags:
  - software-selection
  - procurement
  - rfp
  - vendor-evaluation
  - tco
  - business
technologies:
  - Python
  - Pandas
  - Scoring Matrices
  - Financial Modeling
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pandas >= 2.0.0
  - python >= 3.10
---
# Enterprise Software Selection & RFP Evaluation Architecture

## Overview

A definitive enterprise procurement engineering standard for objectively scoring, shortlisting, and selecting commercial software systems. Selecting enterprise software (ERPs, CRM, CI/CD tooling, cloud observability) based on vendor marketing leads to expensive failed migrations and contract lock-in. This skill instructs AI agents on authoring functional and non-functional requirements matrices, modeling 3-year Total Cost of Ownership (TCO), executing weighted multi-attribute decision scoring, and evaluating vendor security posture.

## When to Use

- Selecting replacement ERP, accounting, HRIS, or database software for enterprise organizations.
- Authoring structured Requests for Proposal (RFPs) and vendor questionnaire scorecards.
- Calculating 3-year Total Cost of Ownership (licensing, implementation, maintenance, training, integration).
- Comparing shortlisted vendors using weighted multi-criteria decision analysis (MCDA).

## When NOT to Use

- Choosing lightweight open-source software libraries for a developer script.
- Single-vendor contract renewals where no market evaluation is being conducted.

## Inputs & Prerequisites

- Stakeholder requirements categorized by priority (Must-Have, Should-Have, Nice-to-Have).
- Compliance and security baseline requirements (SOC2 Type II, ISO 27001, data residency).
- Budget ceiling and projected 3-year user growth.

## Core Workflow

### 1. Weighted Evaluation Matrix Engine
Score competing vendors across weighted functional and compliance criteria:

```python
import pandas as pd

CRITERIA_WEIGHTS = {
    "core_functional_fit": 0.35,       # Must satisfy accounting/business requirements
    "api_and_extensibility": 0.20,     # Webhooks, REST/GraphQL APIs, SDK support
    "security_and_compliance": 0.20,   # SOC2, SSO/SAML, encryption at rest, RBAC
    "total_cost_of_ownership": 0.15,   # License + implementation + support over 3 years
    "vendor_viability_and_sla": 0.10   # 99.9% uptime SLA, financial stability, roadmap
}

def evaluate_vendor_score(vendor_name: str, raw_scores: dict[str, float]) -> dict:
    """
    raw_scores contains ratings from 1 (poor) to 10 (exceptional) for each criteria key.
    """
    weighted_total = sum(raw_scores[k] * CRITERIA_WEIGHTS[k] for k in CRITERIA_WEIGHTS)
    return {
        "vendor": vendor_name,
        "weighted_score": round(weighted_total, 2),
        "breakdown": {k: round(raw_scores[k] * CRITERIA_WEIGHTS[k], 2) for k in CRITERIA_WEIGHTS}
    }
```

### 2. 3-Year Total Cost of Ownership (TCO) Model
Calculate comprehensive true costs beyond base subscription price:

```python
def calculate_3yr_tco(
    annual_subscription: float,
    implementation_fee: float,
    seats: int,
    training_days: int,
    internal_engineering_hours_integration: int
) -> dict:
    # Industry averages: $150/hr internal engineering, $1500/day specialized training
    internal_eng_cost = internal_engineering_hours_integration * 150.0
    training_cost = training_days * 1500.0
    year1_cost = annual_subscription + implementation_fee + internal_eng_cost + training_cost
    year2_cost = annual_subscription * 1.05 # Account for typical 5% annual contract escalation
    year3_cost = year2_cost * 1.05

    total_3yr = year1_cost + year2_cost + year3_cost
    return {
        "year_1_cost": round(year1_cost, 2),
        "year_2_cost": round(year2_cost, 2),
        "year_3_cost": round(year3_cost, 2),
        "total_3yr_tco": round(total_3yr, 2),
        "cost_per_seat_per_month": round(total_3yr / (seats * 36), 2)
    }
```

## Best Practices & Failure Modes

1. **Unweighted Feature Checklists**: Counting raw checkmarks on a vendor sales sheet treats "Supports Single Sign-On" as equal in importance to "Supports dark mode theme". Always assign explicit mathematical weights to requirements.
2. **Hidden Egress & API Overages**: Cloud software contracts frequently include hidden costs for API call quotas, storage overages, or export fees. Demand explicit API rate limits and data extraction commitments in RFP documents.
3. **Skipping Sandboxed Proof-of-Concept (POC)**: Never sign a multi-year enterprise contract based on slide decks. Always execute a 2-week hands-on technical pilot verifying API throughput and authentication integration with real test data.

## Verification & Testing

- Unit test verifying score calculations and weights sum to 1.0:
  ```python
  assert round(sum(CRITERIA_WEIGHTS.values()), 2) == 1.0
  vendor_res = evaluate_vendor_score("AcmeERP", {
      "core_functional_fit": 8,
      "api_and_extensibility": 9,
      "security_and_compliance": 10,
      "total_cost_of_ownership": 7,
      "vendor_viability_and_sla": 8
  })
  assert vendor_res["weighted_score"] == 8.45
  ```
