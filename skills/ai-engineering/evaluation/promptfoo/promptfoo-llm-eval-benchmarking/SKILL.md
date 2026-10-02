---
name: promptfoo-llm-eval-benchmarking
description: "Use this skill when designing, executing, and automating LLM prompt evaluations and adversarial red-teaming benchmarks using promptfoo. It guides the agent through defining test matrices (providers x prompts x variables), configuring deterministic and LLM-as-a-judge assertions, running red-team vulnerability scans, and integrating evaluations into CI/CD pipelines."
domain: ai-engineering
category: evaluation
subcategory: promptfoo
tags:
  - promptfoo
  - llm-eval
  - prompt-engineering
  - benchmarking
  - red-teaming
  - ai-testing
technologies:
  - promptfoo
  - OpenAI
  - Anthropic
  - Python
  - Node.js
complexity: intermediate
maturity: stable
tools:
  - promptfoo
  - npx
dependencies:
  - promptfoo >= 0.50.0
---
# Promptfoo LLM Evaluation & Adversarial Benchmarking

## Overview

A comprehensive engineering guide for automated prompt engineering, regression testing, and security red-teaming of Large Language Models using promptfoo. This skill instructs AI agents on authoring declarative evaluation test matrices, writing programmatic assertions (regex, JSON schema, cosine similarity, LLM-as-a-judge), and configuring automated CI/CD quality gates to prevent performance regressions across prompt iterations.

## When to Use

- Comparing response quality, latency, and cost across multiple model providers (e.g. GPT-4o vs Claude 3.5 Sonnet vs Llama 3).
- Regression-testing prompt iterations to verify that fixing one edge case does not break existing behaviors.
- Running automated adversarial red-team scans to detect jailbreaks, PII leakage, and brand risk.
- Establishing quantifiable quality metrics for agent prompts and tool calls.

## When NOT to Use

- Real-time streaming latency profiling of backend API sockets.
- Evaluating fine-tuned model weight checkpoints during active GPU training (use loss metrics or Eval Harness).

## Inputs & Prerequisites

- Node.js 18+ environment.
- promptfoo installed: `npm install -g promptfoo` or `npx promptfoo`.
- API keys configured for target providers (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`).

## Core Workflow

### 1. Declarative Evaluation Configuration (`promptfooconfig.yaml`)
Define the prompt templates, model providers, and test assertions:

```yaml
# promptfooconfig.yaml
description: "Customer Support Agent Prompt Benchmark"

prompts:
  - "file://prompts/support_v1.txt"
  - "file://prompts/support_v2.txt"

providers:
  - id: openai:gpt-4o
    config:
      temperature: 0.2
  - id: anthropic:claude-3-5-sonnet-20240620
    config:
      temperature: 0.2

tests:
  # Test Case 1: Polite return policy explanation
  - vars:
      topic: "damaged package"
      customer_tier: "gold"
    assert:
      - type: contains
        value: "refund"
      - type: icontains
        value: "priority"
      - type: latency
        threshold: 2500 # Must complete under 2.5 seconds

  # Test Case 2: LLM-as-a-Judge for Tone and Helpfulness
  - vars:
      topic: "billing dispute"
      customer_tier: "standard"
    assert:
      - type: llm-rubric
        value: "The response is empathetic, professional, and provides a clear next step without admitting legal liability."

  # Test Case 3: Structured JSON Output Compliance
  - vars:
      topic: "order cancellation"
      customer_tier: "standard"
    assert:
      - type: is-json
      - type: javascript
        value: "output.status === 'success' && typeof output.ticket_id === 'string'"
```

### 2. Automated Adversarial Red-Teaming Scan
Run automated vulnerability testing for security compliance:

```bash
# Run automated promptfoo red-team scan targeting prompt injection and PII leakage
npx promptfoo redteam run \
    --provider openai:gpt-4o \
    --purpose "Customer service chatbot for a bank" \
    --plugins contracts,excessive-agency,hallucination,pii,prompt-extraction
```

### 3. CI/CD Automated Regression Gate (GitHub Actions)
Integrate evaluation into pull requests to fail code reviews on quality drops:

```yaml
# .github/workflows/prompt-eval.yaml
name: Prompt Quality Gate

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'promptfooconfig.yaml'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Run promptfoo evaluation
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          npx promptfoo eval --no-cache -o output.json

      - name: Enforce pass rate threshold
        run: |
          node -e "
            const results = require('./output.json');
            const passRatio = results.results.stats.successes / results.results.stats.total;
            console.log('Pass ratio: ' + (passRatio * 100).toFixed(1) + '%');
            if (passRatio < 0.95) {
              console.error('Prompt evaluation pass rate below 95% threshold!');
              process.exit(1);
            }
          "
```

## Best Practices & Failure Modes

1. **Non-Deterministic Test Flakiness**: Testing with high temperatures (e.g. `temperature: 1.0`) produces intermittent assertion failures. Set `temperature: 0.0` or `0.2` during automated CI evaluations for reproducible results.
2. **Vague LLM-as-a-Judge Rubrics**: Writing assertions like `type: llm-rubric, value: "Good response"` results in unreliable grading. Provide clear, objective criteria in the rubric ("Must mention return window of 30 days and provide support email").
3. **Hardcoding API Keys in Config**: Never commit API keys inside `promptfooconfig.yaml`. Use environment variables or cloud secret stores.

## Verification & Testing

- Execute evaluation and view CLI summary table:
  ```bash
  npx promptfoo eval
  ```
- Launch web interface to compare model responses side-by-side:
  ```bash
  npx promptfoo view
  ```
