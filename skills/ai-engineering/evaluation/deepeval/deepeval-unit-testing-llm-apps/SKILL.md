---
name: deepeval-unit-testing-llm-apps
description: "Use this skill when designing, authoring, and automating CI/CD unit testing suites for Large Language Model applications using DeepEval. It guides the agent through defining LLM test cases (LLMTestCase), configuring G-Eval custom criteria metrics, hallucination and answer relevancy scoring, integrating with pytest, and setting regression assertions."
domain: ai-engineering
category: evaluation
subcategory: deepeval
tags:
  - deepeval
  - llm-testing
  - ai-evaluation
  - pytest
  - unit-testing
  - g-eval
  - ci-cd
technologies:
  - DeepEval
  - pytest
  - OpenAI
  - Python
  - GitHub Actions
complexity: intermediate
maturity: stable
tools:
  - pytest
  - deepeval
  - python
dependencies:
  - deepeval >= 0.21.0
  - pytest >= 7.4.0
---
# DeepEval Production Unit Testing for LLM Applications

## Overview

A comprehensive engineering guide for writing automated unit tests and regression assertions for LLM applications and agents using DeepEval. DeepEval treats LLM outputs like standard software unit tests: test cases define inputs, actual outputs, expected outputs, and retrieval contexts, evaluated against quantitative metrics (G-Eval custom rubric, Hallucination, Faithfulness, Toxicity). This skill instructs AI agents on integrating LLM unit tests directly into `pytest` and CI/CD pipelines.

## When to Use

- Writing deterministic, automated unit tests for RAG pipelines, chatbots, and AI agents.
- Enforcing quantitative pass/fail thresholds in pull requests (e.g. `assert_test(test_case, [metric])`).
- Measuring custom business criteria using the G-Eval framework with custom evaluation rubrics.
- Tracking score degradation across prompt versions, model upgrades, and embedding parameter changes.

## When NOT to Use

- Offline model training loss tracking (use TensorBoard or WandB).
- Simple string matching assertions where standard `assert "needle" in haystack` suffices without LLM judges.

## Inputs & Prerequisites

- Python 3.10+ with `deepeval` and `pytest` installed.
- Target LLM output generator function or agent interface.
- Evaluator model API key (`OPENAI_API_KEY`).

## Core Workflow

### 1. Test Case Definition & Standard Metrics
Define test cases and evaluate Answer Relevancy and Faithfulness:

```python
# test_customer_support.py
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

def query_customer_support_rag(prompt: str) -> dict:
    # Simulated RAG response
    return {
        "actual_output": "You can return any unopened merchandise within 30 days for a full refund.",
        "retrieval_context": [
            "Our standard return policy permits returns of unopened items within 30 calendar days of delivery for a 100% refund."
        ]
    }

def test_return_policy_relevancy_and_faithfulness():
    user_query = "What is your return policy?"
    rag_result = query_customer_support_rag(user_query)

    test_case = LLMTestCase(
        input=user_query,
        actual_output=rag_result["actual_output"],
        retrieval_context=rag_result["retrieval_context"]
    )

    relevancy_metric = AnswerRelevancyMetric(threshold=0.8)
    faithfulness_metric = FaithfulnessMetric(threshold=0.85)

    # assert_test fails the pytest test if any metric drops below threshold
    assert_test(test_case, [relevancy_metric, faithfulness_metric])
```

### 2. Custom Business Rubric Testing with G-Eval
Define arbitrary domain criteria scored from 0.0 to 1.0 using G-Eval:

```python
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

def test_financial_advice_disclaimer():
    user_prompt = "Should I invest all my savings in cryptocurrency?"
    assistant_reply = "I cannot give specific investment advice. Diversification is generally recommended, and you should consult a licensed financial advisor."

    test_case = LLMTestCase(
        input=user_prompt,
        actual_output=assistant_reply
    )

    disclaimer_metric = GEval(
        name="Financial Disclaimer Compliance",
        criteria="Determine whether the assistant refuses to provide direct financial advice and advises consulting a licensed professional.",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.8
    )

    assert_test(test_case, [disclaimer_metric])
```

### 3. CI/CD Automated Execution in GitHub Actions
Run the pytest suite with DeepEval summary reporting:

```yaml
# .github/workflows/llm-tests.yaml
name: LLM Unit Tests

on:
  pull_request:
    paths:
      - 'app/ai/**'
      - 'prompts/**'
      - 'tests/test_ai/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pytest deepeval

      - name: Run LLM Unit Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest tests/test_ai/ -v --tb=short
```

## Best Practices & Failure Modes

1. **Flaky Tests from Loose Thresholds**: Setting thresholds too high (e.g. `threshold=0.98`) causes occasional stochastic LLM scoring drops. Calibrate baseline scores on a known test set and set thresholds at baseline - 0.05.
2. **Missing `retrieval_context` in Faithfulness Tests**: Calling `FaithfulnessMetric` without populating `retrieval_context` on the `LLMTestCase` raises a runtime configuration error.
3. **Cost Accrual in High-Volume CI**: Running hundreds of tests with `gpt-4o` on every git push incurs high API costs. Use smaller fast evaluators (e.g. `gpt-4o-mini`) for routine PR runs, and reserve large frontier judges for nightly regression pipelines.

## Verification & Testing

- Execute test suite via CLI:
  ```bash
  pytest test_customer_support.py -s
  ```
- View metric score breakdowns and reasoning logs:
  ```python
  # In test function:
  relevancy_metric.measure(test_case)
  print(f"Score: {relevancy_metric.score}")
  print(f"Reason: {relevancy_metric.reason}")
  ```
