---
name: idea-evaluator
description: "Evaluate product, technical, and business ideas through a structured multi-turn dialectical debate between Proponent and Skeptic agents with impartial adjudication."
domain: ai-engineering
category: agents
subcategory: idea_evaluator
tags:
  - ai-engineering
  - agents
  - idea-evaluation
  - multi-agent-debate
  - decision-analysis
technologies:
  - Python
  - Dialectical Debate
  - Multi-Agent Orchestration
  - Viability Scoring
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Dialectical Multi-Agent Idea Evaluation Standard

## Overview

The **Idea Evaluator** skill provides a rigorous framework for stress-testing product, architectural, and business concepts using adversarial multi-agent debate. Solitary evaluation by human founders or individual AI models frequently suffers from cognitive confirmation bias or sycophancy.

This skill equips autonomous systems with `DialecticalIdeaEvaluator`, orchestrating a structured multi-turn debate between a **Proponent Agent** (championing the bull case, market pull, and defensibility) and a **Skeptic Agent** (interrogating execution risks, moat durability, and unit economics). An impartial **Judge** synthesizes the discourse into a calibrated 0-100 Viability Score, an explicit verdict (`PURSUE_AGGRESSIVELY`, `PURSUE_WITH_PIVOT`, `DE_PRIORITIZE`, `ABANDON`), and targeted risk mitigations.

```
+------------------------------------------------------------------------+
|                      Dialectical Evaluation Flow                       |
|                                                                        |
|  [ Proposal & Context Ingestion ]                                      |
|                 |                                                      |
|                 v                                                      |
|  [ Round 1: Thesis & Antithesis ]  ---> Proponent vs Skeptic Arguments|
|                 |                                                      |
|                 v                                                      |
|  [ Round 2: Cross-Examination ]    ---> Direct Rebuttals & Counters    |
|                 |                                                      |
|                 v                                                      |
|  [ Impartial Adjudication ]        ---> Computes Opportunity & Risk    |
|                 |                                                      |
|                 v                                                      |
|  [ Actionable Verdict & Plan ]     ---> Emits Decision & Mitigations   |
+------------------------------------------------------------------------+
```

## When to Use

- When vetting new technical product ideas, open-source initiatives, or startup concepts.
- When conducting pre-mortem analysis on significant architectural migrations.
- When evaluating feature requests against product roadmap priorities.
- When seeking a balanced, non-sycophantic evaluation of high-stakes technical proposals.

## When NOT to Use

- Deterministic algorithm verification or mathematical correctness proofs.
- Minor routine code implementation decisions (e.g. naming a local helper variable).

## Core Workflow

### 1. Ingest Proposal Concept & Metadata
Define the proposal's title, scope, target market, and hypothesized moat:

```python
from dialectical_idea_evaluator import DialecticalIdeaEvaluator, IdeaProposal

evaluator = DialecticalIdeaEvaluator()
proposal = IdeaProposal(
    title="Real-time WebAssembly Sandboxing for Edge Microservices",
    description="Embed lightweight Wasm runtimes at the edge to execute untrusted user plugins.",
    target_market="Edge Computing & Cloud Infrastructure",
    estimated_engineering_months=4,
    defensible_moat="Proprietary memory-isolation layer and near-zero cold start latency"
)
```

### 2. Execute Dialectical Debate and Adjudication
Dispatch the proposal through the multi-agent debate engine:

```python
verdict = evaluator.evaluate_proposal(proposal)

print(f"Verdict: {verdict.verdict}")
print(f"Net Viability Score: {verdict.net_viability_score}/100")
print(f"Opportunity: {verdict.opportunity_score} | Risk Discount: {verdict.risk_discount}")
```

### 3. Review Transcript & Implement Risk Mitigations
Inspect the arguments surfaced by the skeptic and incorporate recommended guardrails:

```python
for mitigation in verdict.key_mitigations:
    print(f"Mitigation: {mitigation}")
```

## Verification & Testing

Execute the idea evaluation verification suite to test the multi-turn debate simulation and verdict scoring:

```bash
python scripts/idea-evaluator_helper.py
```

Expected output:
- Proponent and Skeptic arguments generated across debate rounds.
- Viability score and definitive verdict rendered cleanly.
- Status returned cleanly.
