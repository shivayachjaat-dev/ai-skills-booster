---
name: ai-agent-benchmark-evaluation
description: "Use this skill when evaluating, benchmarking, and grading autonomous AI agents across multi-step execution tasks. It guides the agent through establishing reproducible mock environments, measuring task completion rates, analyzing tool calling trajectory efficiency, computing hallucination indices, and detecting regression degradation across model releases."
domain: ai-engineering
category: agents
subcategory: benchmarking
tags:
  - ai-agents
  - benchmarking
  - evaluation
  - llm-testing
  - agent-architecture
  - evals
technologies:
  - Python
  - Pytest
  - JSON
  - Docker
complexity: advanced
maturity: stable
tools:
  - python
  - pytest
dependencies:
  - python >= 3.9
  - pytest
---
# AI Agent Benchmark Evaluation

## Overview

A deterministic evaluation framework for measuring the reliability, planning accuracy, tool trajectory efficiency, and cost of autonomous AI agents. Replaces subjective manual inspections with reproducible test suites that verify whether an agent achieves target goals without entering infinite loops or taking unsafe actions.

## When to Use

- Benchmarking an agent before deploying prompt changes, system instruction updates, or model swaps (e.g. GPT-4o vs Claude 3.5 Sonnet vs Gemini 1.5 Pro).
- Measuring task completion success rates across a curated test suite of realistic user tasks.
- Profiling agent tool-calling trajectories to eliminate redundant steps and reduce token consumption.
- Establishing continuous integration quality gates for agentic software workflows.

## When NOT to Use

- Single-turn stateless text summarization (use standard ROUGE/BLEU or LLM-as-a-judge scoring).
- Pure traditional unit testing of static deterministic business functions.

## Inputs & Prerequisites

- Benchmark task suite containing: `task_id`, `prompt`, `environment_seed`, `target_assertions`, and `max_turns`.
- Mock or sandboxed execution environment (Docker container, virtual filesystem, or mocked external APIs).

## Core Workflow

### 1. Task Definition & Ground Truth Assertions
Define benchmark test cases with unambiguous, programmatically verifiable exit criteria:
```json
{
  "task_id": "refactor-auth-middleware",
  "prompt": "Update src/auth.ts to validate JWT audience claim and update tests",
  "initial_state": "fixtures/repo-state-v1",
  "max_turns": 8,
  "allowed_tools": ["view_file", "edit_file", "run_test"],
  "evaluation_criteria": {
    "test_command": "npm test",
    "expected_exit_code": 0,
    "forbidden_patterns": ["any", "ts-ignore"]
  }
}
```

### 2. Sandbox Execution & Trajectory Recording
Run the agent in a sterile, reproducible environment while recording the complete action trace:
```python
def run_agent_benchmark(task):
    sandbox = setup_sandbox(task["initial_state"])
    trajectory = []
    
    turn = 0
    success = False
    while turn < task["max_turns"]:
        action = agent.step(sandbox.get_state())
        trajectory.append(action)
        
        if action.is_final:
            break
            
        result = sandbox.execute(action)
        turn += 1

    # Run verification assertions
    eval_result = sandbox.run_command(task["evaluation_criteria"]["test_command"])
    success = (eval_result.exit_code == task["evaluation_criteria"]["expected_exit_code"])
    
    return {
        "task_id": task["task_id"],
        "success": success,
        "turns_used": turn,
        "total_tokens": agent.get_total_tokens(),
        "trajectory": trajectory
    }
```

### 3. Quantitative Metric Aggregation
Aggregate performance across the benchmark suite:
- **Task Success Rate (TSR)**: Percentage of tasks achieving target assertions: $\frac{N_{success}}{N_{total}}$.
- **Trajectory Efficiency Ratio**: Optimal tool call count divided by actual tool call count: $\frac{Steps_{min}}{Steps_{actual}}$.
- **Looping Index**: Frequency of repeated identical tool calls with identical parameters.
- **Cost per Solved Task**: Total dollar expenditure (tokens + inference) divided by number of successfully solved tasks.

### 4. Failure Mode Classification
Categorize reasons for task failure:
1. **Planning Failure**: Agent decomposed problem incorrectly or skipped prerequisite steps.
2. **Tool Parameter Hallucination**: Agent invoked existing tool with invalid schema or non-existent arguments.
3. **Context Truncation Failure**: Agent lost goal awareness due to intermediate context compaction.
4. **Infinite Oscillation**: Agent made a change, ran test, saw failure, reverted change, and repeated in a loop.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| External third-party API dependencies (e.g. GitHub, Stripe) | Mock all external network calls using deterministic replay fixtures to eliminate network flakiness. |
| Non-deterministic model completions | Run each benchmark task at least 3 times ($K=3$) and report Pass@1 and Pass@3 statistics. |
| Dangerous tool execution in benchmarks | Run all benchmark tasks inside ephemeral non-privileged Docker containers. |

## Validation & Acceptance Criteria

- [ ] All benchmark tasks have deterministic automated verification gates.
- [ ] Trajectories record full tool invocations, tokens consumed, and elapsed wall-clock time.
- [ ] Multi-run Pass@1 and Pass@3 metrics reported.
- [ ] Regressions identified and mapped to specific model or prompt modifications.

## Failure Handling & Recovery

- If a benchmark run stalls or hangs, enforce a hard 180-second timeout per task to release sandbox resources.

## Expected Output & Artifacts

- Benchmark results scorecard (`docs/agent-benchmark-report.md`).
- Machine-readable evaluation JSON matrix (`metrics/benchmark-results.json`).
- Trajectory execution logs.

## Related Skills

- `agent-project-memory`
- `agent-tool-use-reliability`
- `context-window-engineering`
