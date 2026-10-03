---
name: documentation-and-adrs
description: "Records architecture decisions (ADRs) and living documentation to capture architectural choices, API changes, and context for future engineers and agents."
domain: ai-engineering
category: agents
subcategory: documentation_and_ad
tags:
  - ai-engineering
  - agents
  - documentation
  - adr
  - architecture
technologies:
  - Markdown
  - Python
  - MADR Standard
  - Git
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Documentation and Architecture Decision Records (ADRs) Standard

## Overview

The **Documentation and ADRs** skill establishes a structured engineering discipline for logging architectural decisions, interface contracts, and systemic invariants. In modern development ecosystems where autonomous agents and human engineers co-author code, undocumented decisions lead to severe regressions, conflicting architectural patterns, and duplicated refactoring loops.

This skill equips teams and AI agents with the `ADREngine` utility to author, index, validate, and supersede Architecture Decision Records following the Markdown Any Decision Record (MADR 3.0) format.

```
+------------------------------------------------------------------------+
|                     Architecture Decision Flow                         |
|                                                                        |
|  [ Technical Dilemma / API Change ]                                    |
|                   |                                                    |
|                   v                                                    |
|  [ Draft Decision Proposal ]  ---> Captured in docs/adrs/000X-*.md    |
|                   |                                                    |
|                   v                                                    |
|  [ Consequence Analysis ]     ---> Categorizes positive & negative     |
|                   |                                                    |
|                   v                                                    |
|  [ Index & Supersede Linkage] ---> Updates docs/adrs/README.md table   |
+------------------------------------------------------------------------+
```

## When to Use

- When making systemic architectural choices (e.g. database migration, auth protocol, message queue adoption).
- When altering public APIs, breaking schema contracts, or changing RPC interfaces.
- When selecting major frameworks, third-party libraries, or runtime platforms.
- When recording non-obvious engineering trade-offs that future autonomous agents must adhere to.

## When NOT to Use

- Routine bug fixes or minor typo corrections that carry no architectural impact.
- Daily standup notes, sprint task tracking, or transient todo lists.

## Core Workflow

### 1. Initialize ADR Directory & Engine
Configure the decision record engine pointing to the target documentation folder:

```python
from adr_engine import ADREngine

engine = ADREngine(doc_root="docs")
engine.init_repository()
```

### 2. Author a New Architecture Decision Record
Draft an ADR capturing the problem statement, decision rationale, and trade-offs:

```python
adr_file = engine.create_adr(
    title="Adopt JWT Token Verification with Asymmetric Keys",
    deciders=["Security Architect", "Backend Lead"],
    context="Symmetric secret sharing across distributed services increased credential leak risks.",
    decision="Migrate to RS256 asymmetric signing with JWKS endpoint verification.",
    consequences={
        "positive": ["Private key stays isolated within auth microservice", "Stateless verification at edge"],
        "negative": ["Slightly higher CPU overhead for public key signature verification"]
    },
    status="Accepted"
)
```

### 3. Superseding Deprecated Decisions
When historical decisions are replaced, record the replacement to update links bidirectionally:

```python
new_adr = engine.create_adr(
    title="Transition from JWT to Biscuit Macaroons for Distributed Capabilities",
    deciders=["Principal Architect"],
    context="Fine-grained token attenuation needed without issuing new tokens.",
    decision="Adopt Biscuit tokens with offline cryptographic attenuation.",
    consequences={"positive": ["Decentralized delegation"], "negative": ["New client library adoption"]},
    supersedes=1
)
```

## Verification & Testing

Run the automated ADR verification suite to validate lifecycle management and index generation:

```bash
python scripts/documentation-and-adrs_helper.py
```

Expected output:
- ADR generation, superseding linkages, and markdown index tables verified cleanly.
- Operational status returned cleanly.
