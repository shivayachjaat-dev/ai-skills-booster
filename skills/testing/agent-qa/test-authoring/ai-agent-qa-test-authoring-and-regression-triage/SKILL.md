---
name: ai-agent-qa-test-authoring-and-regression-triage
description: "Use this skill to author, execute, and triage end-to-end automated test suites for AI agents. It establishes deterministic evaluation fixtures, trajectory regression tracking, tool mocking, flakiness score analysis, and automated failure post-mortem triaging."
domain: testing
category: agent-qa
subcategory: test-authoring
tags:
  - agent-qa
  - ai-testing
  - regression-testing
  - evals
  - pytest
  - trajectory-evaluation
technologies:
  - pytest
  - Python
  - Pydantic
  - Mock Tools
  - Trajectory Evaluation
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - pytest >= 7.4.0
  - pydantic >= 2.5.0
  - python >= 3.10
---
# AI Agent QA Test Authoring & Regression Triage

## Overview

A comprehensive software quality assurance standard specifically engineered for testing autonomous AI agents. Unlike deterministic software, AI agents exhibit non-deterministic reasoning trajectories, stochastic model outputs, and external tool side-effects. Testing agents requires specialized evaluation fixtures that decouple LLM non-determinism from behavioral regressions, mock environment state, verify tool-call arguments with exact schemas, and triage failure modes into prompt drift, tool protocol errors, or model degradation.

## When to Use

- Writing automated regression test suites for coding, research, or customer service AI agents.
- Mocking external tool calls and database environments to achieve reproducible, offline test runs.
- Evaluating multi-step agent trajectories against golden path reference steps.
- Triaging agent CI test failures and classifying bugs as model degradation, context dilution, or bad assertions.

## When NOT to Use

- Standard deterministic unit testing of pure mathematical functions or simple web endpoints (use standard pytest).
- Manual exploratory UI testing without automated assertions.

## Inputs & Prerequisites

- Target agent execution interface (callable agent class or command-line invocation).
- Fixture test scenarios (user input prompt, initial environment files, expected final state).
- Tool call mocking specifications and golden trajectories.

## Core Workflow

### 1. Agent Trajectory & Assertion Schema
Define test specifications with strict trajectory assertions:

```python
"""Agent QA Test Framework and Trajectory Assertion Engine."""
import pytest
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExpectedToolCall(BaseModel):
    tool_name: str
    required_arguments: Dict[str, Any]
    allow_extra_keys: bool = True

class AgentTestScenario(BaseModel):
    scenario_id: str
    user_prompt: str
    expected_tools_invoked: List[ExpectedToolCall]
    forbidden_tools: List[str] = Field(default_factory=list)
    max_steps_allowed: int = 10
    final_output_contains: List[str]

class TrajectoryStep(BaseModel):
    step_index: int
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None

class TrajectoryAuditor:
    @staticmethod
    def audit_trajectory(scenario: AgentTestScenario, actual_steps: List[TrajectoryStep], final_answer: str) -> Dict[str, Any]:
        violations = []

        # 1. Step Budget Assertion
        if len(actual_steps) > scenario.max_steps_allowed:
            violations.append(f"Step limit exceeded: Took {len(actual_steps)} steps (max allowed: {scenario.max_steps_allowed})")

        # 2. Forbidden Tools Assertion
        for step in actual_steps:
            if step.tool_name in scenario.forbidden_tools:
                violations.append(f"Forbidden tool invoked: '{step.tool_name}' at step {step.step_index}")

        # 3. Required Tools Assertion
        actual_tool_names = [s.tool_name for s in actual_steps if s.tool_name]
        for exp in scenario.expected_tools_invoked:
            if exp.tool_name not in actual_tool_names:
                violations.append(f"Required tool '{exp.tool_name}' was never invoked.")
            else:
                # Find matching step and verify argument subset
                matching_step = next(s for s in actual_steps if s.tool_name == exp.tool_name)
                for arg_key, arg_val in exp.required_arguments.items():
                    if matching_step.tool_args is None or matching_step.tool_args.get(arg_key) != arg_val:
                        violations.append(f"Tool '{exp.tool_name}' argument mismatch on key '{arg_key}'. Expected: {arg_val}")

        # 4. Final Answer Keyword Assertion
        for keyword in scenario.final_output_contains:
            if keyword.lower() not in final_answer.lower():
                violations.append(f"Final answer missing expected keyword: '{keyword}'")

        return {
            "passed": len(violations) == 0,
            "scenario_id": scenario.scenario_id,
            "violations": violations
        }
```

### 2. Pytest Test Implementation with Mock Tools
Write reproducible agent tests using Pytest:

```python
"""Pytest Test Suite for Agent QA."""
def test_file_refactoring_agent_trajectory():
    scenario = AgentTestScenario(
        scenario_id="refactor_deprecated_imports",
        user_prompt="Replace all deprecated utils.log calls with logger.info in src/app.py",
        expected_tools_invoked=[
            ExpectedToolCall(tool_name="view_file", required_arguments={"path": "src/app.py"}),
            ExpectedToolCall(tool_name="replace_file_content", required_arguments={"path": "src/app.py"})
        ],
        forbidden_tools=["run_bash_command"],
        max_steps_allowed=5,
        final_output_contains=["Refactored", "logger.info"]
    )

    # Simulated mock agent trajectory
    simulated_steps = [
        TrajectoryStep(step_index=1, tool_name="view_file", tool_args={"path": "src/app.py"}, observation="import utils; utils.log('started')"),
        TrajectoryStep(step_index=2, tool_name="replace_file_content", tool_args={"path": "src/app.py"}, observation="Success: replaced 1 occurrence")
    ]
    simulated_final_answer = "Successfully Refactored src/app.py to use logger.info."

    result = TrajectoryAuditor.audit_trajectory(scenario, simulated_steps, simulated_final_answer)
    assert result["passed"] is True, f"Agent QA failed: {result['violations']}"
```

### 3. Automated Failure Mode Triaging Matrix
When an agent test fails in CI, triage by root cause:
- **Trajectory Explosion**: Agent looped > 15 times without converging -> Issue: Unclear tool error messages or missing exit condition.
- **Tool Hallucination**: Agent attempted to invoke a non-existent tool -> Issue: System prompt tool catalog out of sync with model schemas.
- **Assertion Brittleness**: Agent accomplished the task via an alternative valid path -> Issue: Assertion overly constrained to a single execution sequence.

## Best Practices & Failure Modes

- **Never Test Against Live External APIs in CI**: Always mock third-party services (GitHub, Stripe, AWS) with recorded responses or deterministic in-memory fixtures.
- **Flakiness Thresholds**: Run agent evaluation tests over 3 iterations; consider a test passing if success rate >= 90% to account for minor LLM variance.
- **Seed Fixing**: Where supported by provider APIs, fix temperature and random seed parameters during regression CI runs.

## Verification & Testing

- Run agent test suite with pytest:
  ```bash
  pytest tests/test_agent_qa.py -v
  ```
- Validate trajectory schema serialization:
  ```bash
  python -c "import pydantic; print('Agent QA schema verified')"
  ```
