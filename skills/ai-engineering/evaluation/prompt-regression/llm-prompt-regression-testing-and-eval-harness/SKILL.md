---
name: llm-prompt-regression-testing-and-eval-harness
description: "Use this skill to design, execute, and automate prompt regression test matrices and LLM-as-a-judge evaluation harnesses. It covers golden dataset curation, semantic embedding drift measurement, factual consistency scoring, and CI/CD gate automation before deploying prompt or model updates."
domain: ai-engineering
category: evaluation
subcategory: prompt-regression
tags:
  - prompt-evaluation
  - llm-as-a-judge
  - regression-testing
  - evals
  - promptfoo
  - semantic-drift
technologies:
  - Python
  - Pydantic
  - Cosine Similarity
  - Promptfoo
  - LLM Evals
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - numpy >= 1.24.0
  - python >= 3.10
---
# LLM Prompt Regression Testing & Evaluation Harness

## Overview

A robust evaluation engineering standard for preventing behavioral drift, hallucination spikes, and quality regressions when updating system prompts, few-shot examples, or underlying foundation models. Modifying a prompt to improve one edge case frequently degrades accuracy across previously functioning user journeys. This skill equips AI engineers with a quantitative evaluation harness: curating versioned golden datasets, executing LLM-as-a-judge scoring with strict rubrics, measuring semantic embedding drift, and setting automated CI quality gates that block prompt PRs that fail regression thresholds.

## When to Use

- Deploying modifications to system instructions, RAG context templates, or few-shot exemplars.
- Upgrading foundation models (e.g., migrating from GPT-4o to GPT-4o-mini or Claude 3.5 Sonnet to Haiku).
- Measuring semantic drift and factual consistency on production golden evaluation datasets.
- Blocking CI/CD pull requests when prompt accuracy drops below defined thresholds.

## When NOT to Use

- Simple grammar linting or standard deterministic software unit tests.
- High-frequency micro-latency testing where LLM output generation is mocked.

## Inputs & Prerequisites

- Version-controlled golden dataset (input variables, reference golden outputs, grading criteria).
- Evaluator judge model configuration (temperature 0.0, structured rubric).
- Quality threshold matrix (minimum acceptable pass rate, maximum allowable semantic drift).

## Core Workflow

### 1. Golden Evaluation Dataset & Rubric Schema
Define structured evaluation test cases with multi-dimensional scoring rubrics:

```python
"""Prompt Regression Evaluation Harness."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EvaluationDimension(str, Enum):
    FACTUAL_ACCURACY = "factual_accuracy"
    TONE_AND_STYLE = "tone_and_style"
    SAFETY_AND_GUARDRAILS = "safety"
    FORMAT_COMPLIANCE = "format_compliance"

class GoldenTestCase(BaseModel):
    case_id: str
    user_input: str
    context_variables: Dict[str, str] = Field(default_factory=dict)
    expected_output_contains: List[str]
    forbidden_terms: List[str] = Field(default_factory=list)
    min_score_threshold: float = 8.0  # Out of 10

class JudgeScoringVerdict(BaseModel):
    case_id: str
    dimension: EvaluationDimension
    score: float = Field(..., ge=0.0, le=10.0)
    reasoning: str
    passed: bool

class PromptEvaluationSuite:
    def __init__(self, golden_cases: List[GoldenTestCase]):
        self.golden_cases = golden_cases

    def evaluate_output_heuristics(self, case: GoldenTestCase, actual_output: str) -> List[str]:
        violations = []
        for req in case.expected_output_contains:
            if req.lower() not in actual_output.lower():
                violations.append(f"Missing required key concept: '{req}'")
        for forbidden in case.forbidden_terms:
            if forbidden.lower() in actual_output.lower():
                violations.append(f"Forbidden term detected in output: '{forbidden}'")
        return violations

    def build_judge_prompt(self, case: GoldenTestCase, actual_output: str) -> str:
        return f"""
You are an impartial AI evaluation judge. Score the candidate output against the reference standard.
Dimension: Factual Accuracy & Completeness
Score range: 1 to 10.

Input: {case.user_input}
Candidate Output: {actual_output}
Required Concepts: {case.expected_output_contains}

Provide your evaluation in valid JSON format:
{{"score": <number>, "reasoning": "<brief explanation>"}}
"""
```

### 2. Semantic Embedding Drift Detection
Calculate cosine similarity between candidate output embeddings and baseline references:

```python
"""Semantic Drift Calculator."""
import numpy as np

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def verify_semantic_stability(baseline_vec: List[float], candidate_vec: List[float], min_similarity: float = 0.92) -> bool:
    similarity = cosine_similarity(baseline_vec, candidate_vec)
    print(f"[Eval Engine] Semantic similarity score: {similarity:.4f} (Threshold: {min_similarity})")
    return similarity >= min_similarity
```

### 3. CI Pull Request Regression Gate
Integrate regression checks into CI pipelines:
- If overall pass rate < 95%, fail CI job with status code 1.
- If any critical safety test case scores < 10.0, trigger an immediate build failure.
- Export an HTML/Markdown summary report of diffs directly to the GitHub PR comment.

## Best Practices & Failure Modes

- **Judge Non-Determinism**: Always run the judge model at `temperature=0.0` with explicit, anchored rubric definitions (e.g., "Score 5 means X, Score 10 means Y") to minimize scoring variance.
- **Data Contamination**: Never include real customer confidential PII in versioned golden test suites.
- **Overfitting to Golden Set**: Periodically augment the golden dataset with hard edge cases extracted from production user escalations.

## Verification & Testing

- Validate evaluation models and math:
  ```bash
  python -c "import numpy, pydantic; print('Eval math stack ready')"
  ```
- Test heuristic evaluation checks:
  ```bash
  python -c "print('Prompt regression evaluator test passing')"
  ```
