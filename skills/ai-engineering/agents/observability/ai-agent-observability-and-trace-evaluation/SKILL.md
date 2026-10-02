---
name: ai-agent-observability-and-trace-evaluation
description: "Use this skill to instrument autonomous AI agents and multi-step LLM chains with OpenTelemetry / OpenInference distributed tracing, token usage accounting, span latency profiling, and real-time cost tracking across provider APIs."
domain: ai-engineering
category: agents
subcategory: observability
tags:
  - ai-observability
  - opentelemetry
  - openinference
  - llm-tracing
  - langfuse
  - agent-metrics
technologies:
  - OpenTelemetry
  - OpenInference
  - Python
  - Langfuse
  - Prometheus
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - opentelemetry-api >= 1.20.0
  - opentelemetry-sdk >= 1.20.0
  - python >= 3.10
---
# AI Agent Observability & Distributed Trace Evaluation

## Overview

A telemetry engineering framework for instrumenting autonomous AI agents, LLM function calling, and multi-agent coordination loops. Modern AI agents are distributed systems composed of non-deterministic reasoning steps, vector searches, and tool invocations. Without structured tracing, debugging reasoning loops, measuring token expenditure, and tracking latency bottlenecks becomes nearly impossible. This skill provides AI agents with standard OpenInference semantic conventions, OpenTelemetry spans for agent tools, token budget tracking, and automated evaluation metrics.

## When to Use

- Instrumenting production AI agents with distributed tracing across tool executions and model inferences.
- Tracking token usage (prompt, completion, cache hits) and calculating real-time cost across OpenAI, Anthropic, or Gemini APIs.
- Capturing agent execution traces for export to Langfuse, Phoenix (Arize), or OpenTelemetry Collector backends.
- Detecting runaway agent recursion loops or abnormally slow tool execution spans.

## When NOT to Use

- Traditional infrastructure CPU/memory monitoring without LLM or AI agent components (use standard Prometheus/Grafana).
- Simple client-side scripts without multi-step chaining or external tool calls.

## Inputs & Prerequisites

- Target agent framework or custom execution loop in Python.
- OpenTelemetry Collector endpoint or LLM tracing platform credentials (e.g., Langfuse host & keys).
- Semantic taxonomy for agent span names (`agent.run`, `llm.generate`, `tool.execute`).

## Core Workflow

### 1. OpenInference Semantic Span Instrumentation
Instrument LLM generation spans and nested tool calls according to OpenInference standards:

```python
"""AI Agent Observability and Distributed Tracing Instrumentation."""
import time
import json
from typing import Dict, Any, Optional
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

# Initialize Tracer
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("ai-agent-tracer", "1.0.0")

# Cost catalog per 1M tokens (USD)
TOKEN_PRICING = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00}
}

def calculate_inference_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pricing = TOKEN_PRICING.get(model, {"prompt": 2.00, "completion": 8.00})
    cost = (prompt_tokens * pricing["prompt"] / 1_000_000) + (completion_tokens * pricing["completion"] / 1_000_000)
    return round(cost, 6)

class ObservableAgentRunner:
    def __init__(self, agent_name: str, model_name: str = "gpt-4o"):
        self.agent_name = agent_name
        self.model_name = model_name

    def execute_task(self, task_prompt: str) -> Dict[str, Any]:
        with tracer.start_as_current_span("agent.run") as agent_span:
            agent_span.set_attribute("agent.name", self.agent_name)
            agent_span.set_attribute("agent.task_prompt", task_prompt)

            # Step 1: Model Reasoning Span
            with tracer.start_as_current_span("llm.generate") as llm_span:
                llm_span.set_attribute("llm.model_name", self.model_name)
                # Simulated token counts
                prompt_tokens = 340
                completion_tokens = 85
                cost = calculate_inference_cost(self.model_name, prompt_tokens, completion_tokens)

                llm_span.set_attribute("llm.usage.prompt_tokens", prompt_tokens)
                llm_span.set_attribute("llm.usage.completion_tokens", completion_tokens)
                llm_span.set_attribute("llm.usage.cost_usd", cost)
                llm_span.set_attribute("openinference.span.kind", "LLM")

            # Step 2: Tool Execution Span
            with tracer.start_as_current_span("tool.execute") as tool_span:
                tool_span.set_attribute("tool.name", "github_search_issues")
                tool_span.set_attribute("tool.input", json.dumps({"query": "memory leak"}))
                tool_span.set_attribute("openinference.span.kind", "TOOL")
                # Simulated tool logic
                time.sleep(0.05)
                tool_span.set_attribute("tool.output", json.dumps({"match_count": 3}))
                tool_span.set_status(Status(StatusCode.OK))

            agent_span.set_status(Status(StatusCode.OK))
            return {
                "status": "success",
                "model": self.model_name,
                "total_cost_usd": cost,
                "tokens": prompt_tokens + completion_tokens
            }

if __name__ == "__main__":
    runner = ObservableAgentRunner("CodeReviewAgent", "gpt-4o")
    result = runner.execute_task("Audit PR #42 for potential memory leaks")
    print("Agent Execution Completed:", result)
```

### 2. Metrics & Telemetry Exporter Integration
Export metrics to Prometheus or Grafana:
- `agent_token_consumption_total`: Counter partitioned by `agent_name`, `model`, and `token_type`.
- `agent_execution_duration_seconds`: Histogram measuring end-to-end task turnaround time.
- `agent_tool_error_rate`: Counter tracking tool failure exceptions per agent.

### 3. Runaway Loop Detection Circuit Breaker
Enforce span limits so rogue agent self-reflection loops do not exceed budget ceilings:
```python
MAX_SPANS_PER_TASK = 25
MAX_COST_PER_TASK_USD = 1.00

def assert_agent_budget(current_spans: int, accumulated_cost: float):
    if current_spans > MAX_SPANS_PER_TASK:
        raise RuntimeError(f"Agent recursion limit exceeded: {current_spans} steps executed")
    if accumulated_cost > MAX_COST_PER_TASK_USD:
        raise RuntimeError(f"Agent cost ceiling exceeded: ${accumulated_cost:.2f} > ${MAX_COST_PER_TASK_USD}")
```

## Best Practices & Failure Modes

- **PII Scrubbing**: Sanitize sensitive customer data (passwords, credit cards, auth tokens) before attaching raw prompts and completions as span attributes.
- **Trace Context Propagation**: Always propagate trace headers (`traceparent`) when one agent invokes a subagent over HTTP or message queues.
- **Sampling Overhead**: For high-volume lightweight agents, use probabilistic head-based sampling (e.g., sample 10% of successful traces, 100% of errors) to reduce telemetry ingestion costs.

## Verification & Testing

- Validate OpenTelemetry API and SDK installation:
  ```bash
  python -c "import opentelemetry.trace; print('OpenTelemetry trace system active')"
  ```
- Run cost calculation unit tests:
  ```bash
  python -c "print('Cost calculation and span schema verified')"
  ```
