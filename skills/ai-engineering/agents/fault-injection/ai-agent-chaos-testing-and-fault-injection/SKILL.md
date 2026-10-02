---
name: ai-agent-chaos-testing-and-fault-injection
description: "Use this skill when stress-testing, chaos-testing, and verifying the fault-tolerance of autonomous AI agents and tool-calling pipelines. It guides the agent through simulating tool API failures, network timeouts, corrupt JSON payloads, context window truncation, and verifying agent self-healing and recovery strategies."
domain: ai-engineering
category: agents
subcategory: fault-injection
tags:
  - chaos-engineering
  - fault-injection
  - ai-agents
  - resilience
  - testing
  - llm-agents
technologies:
  - Python
  - pytest
  - LangChain
  - AutoGen
  - Asyncio
complexity: advanced
maturity: stable
tools:
  - python
  - pytest
dependencies:
  - python >= 3.10
  - pytest >= 7.4.0
---
# AI Agent Chaos Testing & Fault Injection Architecture

## Overview

A definitive production AI engineering standard for verifying the resilience, self-healing, and error recovery of autonomous LLM agents. In production, AI agents interact with unpredictable external environments: third-party APIs return HTTP 503 errors, webhooks timeout, tool outputs contain corrupted JSON, and context windows reach capacity. Without deliberate fault-injection testing, agents enter unrecoverable loops, hallucinate fake tool outputs, or crash unhandled. This skill instructs AI agents on injecting realistic faults into tool execution harnesses and asserting proper recovery behavior.

## When to Use

- Verifying that an autonomous agent can recover when a tool call raises an unhandled exception.
- Testing agent behavior when an external database or API returns HTTP 429 Too Many Requests.
- Stress-testing prompt self-correction when a tool returns malformed or incomplete data.
- Guaranteeing that agents terminate gracefully rather than looping infinitely on stubborn errors.

## When NOT to Use

- Standard unit testing of isolated deterministic helper functions.
- Production load testing of server network bandwidth.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Agent harness decoupling tool execution through an interceptable proxy.
- Test suite configured with `pytest`.

## Core Workflow

### 1. Chaos Tool Interceptor Proxy
Intercept tool execution calls and inject probabilistic or deterministic faults:

```python
import random
from typing import Callable, Any, Dict

class FaultInjectionPolicy:
    def __init__(self, failure_rate: float = 0.0, latency_seconds: float = 0.0, inject_corrupt_json: bool = False):
        self.failure_rate = failure_rate
        self.latency_seconds = latency_seconds
        self.inject_corrupt_json = inject_corrupt_json

class ChaosToolHarness:
    def __init__(self):
        self.policies: Dict[str, FaultInjectionPolicy] = {}
        self.invocation_log = []

    def set_fault_policy(self, tool_name: str, policy: FaultInjectionPolicy):
        self.policies[tool_name] = policy

    def execute_tool(self, tool_name: str, tool_func: Callable, *args, **kwargs) -> Any:
        self.invocation_log.append(tool_name)
        policy = self.policies.get(tool_name)

        if policy:
            # Simulate Network Latency / Timeout
            if policy.latency_seconds > 0:
                import time
                time.sleep(policy.latency_seconds)

            # Simulate Transient Service Outage
            if policy.failure_rate > 0 and random.random() < policy.failure_rate:
                raise ConnectionError(f"CHAOS INJECTED: Simulated network partition calling {tool_name}")

            # Simulate Malformed / Corrupted Data Output
            if policy.inject_corrupt_json:
                return '{"status": "error", "corrupted_payload": true' # Unterminated JSON

        return tool_func(*args, **kwargs)
```

### 2. Asserting Agent Self-Healing in Pytest
Assert that the agent receives the error, acknowledges it, and switches to an alternate tool:

```python
import pytest

class MockAgent:
    def __init__(self, harness: ChaosToolHarness):
        self.harness = harness

    def fetch_data_resilient(self, primary_url: str, backup_url: str):
        try:
            return self.harness.execute_tool("primary_fetch", lambda: "primary_data")
        except ConnectionError:
            # Agent self-heals by falling back to secondary backup tool
            return self.harness.execute_tool("backup_fetch", lambda: "backup_data")

def test_agent_fallback_on_chaos_failure():
    harness = ChaosToolHarness()
    # Force 100% failure on primary tool
    harness.set_fault_policy("primary_fetch", FaultInjectionPolicy(failure_rate=1.0))

    agent = MockAgent(harness)
    result = agent.fetch_data_resilient("http://primary", "http://backup")

    assert result == "backup_data"
    assert harness.invocation_log == ["primary_fetch", "backup_fetch"]
```

## Best Practices & Failure Modes

1. **Infinite Retry Hallucination Loops**: When a tool repeatedly fails, poorly instructed agents repeat the identical failed tool call with identical arguments 20 times. Always enforce a hard loop counter (`max_retries = 3`) and instruct agents to formulate alternative strategies or ask the human user.
2. **Leaking Internal Stack Traces into Prompt**: Feeding raw 50-line Python stack traces into the agent's context window wastes valuable context tokens and confuses the model. Catch exceptions and summarize into clean error messages (`Tool 'search' failed: Connection timeout`).
3. **Silent Swallowing of Errors**: If a tool returns an empty dictionary `{}` on failure without error signaling, the agent assumes the operation succeeded and produces false hallucinated conclusions. Tools must return explicit error schemas.

## Verification & Testing

- Run the chaos test suite with pytest:
  ```bash
  pytest tests/test_agent_chaos.py -v
  ```
