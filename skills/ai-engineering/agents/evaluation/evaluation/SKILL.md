---
name: evaluation
description: "Build and operate evaluation frameworks for agent systems to test performance systematically, validate context engineering, and measure drift."
domain: ai-engineering
category: agents
subcategory: evaluation
tags:
  - ai-engineering
  - agents
  - evaluation
  - benchmarks
  - llm-as-a-judge
technologies:
  - Python
  - JSON Schema
  - Benchmark Suites
  - Telemetry
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Agent Evaluation & Benchmarking Standard

## Overview

The **Evaluation** skill provides an enterprise standard for constructing, executing, and monitoring systematic evaluation pipelines for autonomous AI agents. Unlike standard unit tests that assess static deterministic code, agentic systems involve nondeterministic model inference, tool execution chains, and dynamic context windows.

This skill equips engineers and autonomous agents with the `AgentEvaluationHarness`, enabling automated multi-dimensional grading: tool call fidelity, schema validation, forbidden token detection, and latency SLA adherence.

```
+------------------------------------------------------------------------+
|                      Agent Evaluation Pipeline                         |
|                                                                        |
|  [ Golden Test Dataset ]     ---> Input prompt & expectation contracts |
|                                           |                            |
|                                           v                            |
|  [ Agent Execution Trace ]   ---> Emits tool calls, output & latency   |
|                                           |                            |
|                                           v                            |
|  [ Assertion Graders ]       ---> Checks schema, tools & safety bounds |
|                                           |                            |
|                                           v                            |
|  [ Drift & Pass Rate Gate ]  ---> Blocks CI on performance regression   |
+------------------------------------------------------------------------+
```

## When to Use

- When validating prompt engineering changes, system prompt adjustments, or context window strategies.
- When benchmarking new LLM model releases against an established task baseline.
- When validating tool-calling accuracy across multi-agent workflows.
- When establishing continuous automated quality gates in CI/CD pipelines for agent applications.

## When NOT to Use

- Simple unit testing of standard non-AI utility functions (use `pytest` directly).
- Ad-hoc manual chat experimentation where persistent tracking is not required.

## Core Workflow

### 1. Define Golden Evaluation Test Cases
Establish explicit test cases specifying input prompts, expected tools, and negative safety constraints:

```python
from agent_eval_framework import AgentEvaluationHarness, EvalTestCase

harness = AgentEvaluationHarness(passing_threshold=0.85)

harness.add_case(EvalTestCase(
    test_id="eval-sql-generation",
    description="Verify query generator generates parameterized SQL without string concatenation",
    agent_input="Generate query for finding users active in last 30 days",
    expected_tools=["schema_lookup"],
    forbidden_tokens=["+ user_input +", "DROP DATABASE"],
    required_substrings=["SELECT", "WHERE", "INTERVAL"],
    max_latency_sec=4.0
))
```

### 2. Execute Suite Against Agent Outputs
Evaluate agent outputs and tool invocation telemetry against the test suite:

```python
simulated_runs = {
    "eval-sql-generation": {
        "output": "SELECT * FROM users WHERE last_login > NOW() - INTERVAL '30 days'",
        "tools": ["schema_lookup"],
        "latency_sec": 1.2
    }
}

report = harness.run_suite(simulated_runs)
print(f"Pass Rate: {report['summary']['pass_rate_percent']}%")
print(f"Suite Status: {'PASSED' if report['summary']['suite_passed'] else 'FAILED'}")
```

### 3. Analyze Failures and Guard Against Drift
Inspect per-case failures, evaluate tool accuracy drops, and verify SLA adherence before shipping model changes:

```python
for item in report["case_results"]:
    if not item["passed"]:
        print(f"Test {item['test_id']} failed: {item['failures']}")
```

## Verification & Testing

Execute the evaluation benchmark harness to verify multi-dimensional scoring and gate calculations:

```bash
python scripts/evaluation_helper.py
```

Expected output:
- Test cases evaluated across tool accuracy, safety constraints, and latency.
- Summary pass rate computed cleanly.
- Status returned cleanly.
