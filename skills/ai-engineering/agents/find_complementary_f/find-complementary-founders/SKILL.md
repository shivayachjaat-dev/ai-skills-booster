---
name: find-complementary-founders
description: "Identify, assess, and rank complementary cofounders or project partners by evaluating skill deficits, GTM/technical synergy, and commitment alignment."
domain: ai-engineering
category: agents
subcategory: find_complementary_f
tags:
  - ai-engineering
  - agents
  - founder-matching
  - talent-discovery
  - startup-formation
technologies:
  - Python
  - Capability Vectors
  - Matchmaking Heuristics
  - Privacy Scrubber
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Complementary Founder Matching Standard

## Overview

The **Find Complementary Founders** skill provides a rigorous framework for identifying, assessing, and ranking prospective startup cofounders and project partners. Most founding teams suffer from redundancy traps—such as technical founders teaming up with other pure engineers rather than bringing on essential Go-To-Market (GTM), sales, or operational leadership.

This skill equips agents with `ComplementaryFounderMatcher`, evaluating candidate capability vectors across four primary pillars: **Technical Engineering**, **Product Design**, **GTM & Enterprise Sales**, and **Operations & Finance**. It calculates gap coverage scores and identifies potential cultural or commitment frictions while maintaining strict privacy boundaries.

```
+------------------------------------------------------------------------+
|                     Founder Matchmaking Pipeline                       |
|                                                                        |
|  [ Owner Profile Assessment ] ---> Identifies strengths & skill gaps   |
|                                           |                            |
|                                           v                            |
|  [ Candidate Ingestion ]      ---> Evaluates verified opt-in profiles  |
|                                           |                            |
|                                           v                            |
|  [ Gap Coverage Scoring ]     ---> Computes complementary synergy delta|
|                                           |                            |
|                                           v                            |
|  [ Alignment & Friction Check]---> Flags commitment or style conflicts |
|                                           |                            |
|                                           v                            |
|  [ Ranked Recommendations ]   ---> Emits partner brief with synergies  |
+------------------------------------------------------------------------+
```

## When to Use

- When an entrepreneur or solo builder seeks a complementary cofounder with orthogonal strengths (e.g. Technical seeking GTM, or Sales seeking Technical).
- When assessing early-stage startup team composition for critical structural blindspots.
- When vetting project collaboration requests for mutual value alignment and shared domain interest.
- When screening opt-in founder directories without disclosing confidential project details.

## When NOT to Use

- Standard corporate hiring or recruiting of employees/contractors where salary, title, and job descriptions dominate rather than equity partnerships.
- Non-consensual automated scraping or unsolicited cold outbound spamming of individuals.

## Core Workflow

### 1. Model Owner Capability Profile
Define the founder's existing skill scores, working style, and commitment:

```python
from founder_matching_engine import ComplementaryFounderMatcher, FounderProfile

owner = FounderProfile(
    founder_id="founder-tech",
    headline="Lead AI Architect & Infrastructure Engineer",
    skills={"technical_engineering": 9.5, "product_design": 4.0, "gtm_sales": 2.0, "operations_finance": 3.5},
    commitment="full-time",
    domains_of_interest=["Developer Tools", "AI Agents"],
    working_style="fast_prototyping"
)
```

### 2. Ingest Candidates and Compute Synergy Scores
Initialize the matching engine and rank prospective candidate profiles:

```python
matcher = ComplementaryFounderMatcher(owner)
ranked_matches = matcher.rank_candidates(candidate_pool)

for match in ranked_matches:
    print(f"Candidate: {match.headline} | Score: {match.complementarity_score}/100")
    print(f"Synergies: {match.synergy_reasons}")
    print(f"Frictions: {match.potential_frictions}")
```

### 3. Review Top Complementary Candidates
Select candidates that maximize coverage over critical deficits while sharing identical commitment levels:

```python
top_choice = ranked_matches[0]
print(f"Selected Top Partner Candidate: {top_choice.candidate_id}")
```

## Verification & Testing

Execute the founder matchmaking verification suite to test gap calculation and candidate ranking:

```bash
python scripts/find-complementary-founders_helper.py
```

Expected output:
- Owner profile evaluated against candidates.
- GTM candidate prioritized over duplicate technical candidate.
- Status returned cleanly.
