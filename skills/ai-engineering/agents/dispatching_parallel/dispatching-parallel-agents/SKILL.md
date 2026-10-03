---
name: dispatching-parallel-agents
description: "Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies, orchestrating fan-out and fan-in workflows."
domain: ai-engineering
category: agents
subcategory: dispatching_parallel
tags:
  - ai-engineering
  - agents
  - parallel-execution
  - concurrency
  - fan-out-fan-in
technologies:
  - Python
  - ThreadPoolExecutor
  - AsyncIO
  - Multi-Agent Orchestration
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Dispatching Parallel Agents Architecture & Implementation Standard

## Overview

The **Dispatching Parallel Agents** skill provides enterprise guidelines and production utilities for orchestrating concurrent AI agent workflows. In non-trivial software engineering tasks—such as simultaneous security audits, unit test generation, cross-browser compatibility checks, or documentation generation—running tasks sequentially introduces unnecessary latency.

This skill equips autonomous systems with a robust fan-out / fan-in execution harness (`ParallelAgentDispatcher`) that manages task partitioning, thread pool concurrency, per-task timeout enforcement, error isolation, and unified report reconciliation.

```
+------------------------------------------------------------------------+
|                   Dispatching Parallel Agents Pipeline                 |
|                                                                        |
|  [ Task Partitioning ]    ---> Validates state independence            |
|                                           |                            |
|                                           v                            |
|  [ Concurrency Throttle ] ---> Regulates worker pool & TPM quotas      |
|                                           |                            |
|                                           v                            |
|  [ Parallel Fan-Out ]     ---> Executes subagents asynchronously       |
|                                           |                            |
|                                           v                            |
|  [ Error Isolation ]      ---> Captures timeouts & faults per worker   |
|                                           |                            |
|                                           v                            |
|  [ Fan-In Reconciliation] ---> Aggregates outputs & telemetry report   |
+------------------------------------------------------------------------+
```

## When to Use

- When breaking down a large task into 2 or more completely independent subtasks that do not share mutable state.
- When performing multi-perspective code reviews (e.g. security specialist, performance reviewer, and style checker running concurrently).
- When running batch migrations or unit test generation across disparate modules.
- When wall-clock latency is critical and API rate limits allow concurrent requests.

## When NOT to Use

- Highly sequential pipelines where Task B strictly depends on the output of Task A.
- Tasks that mutate the same files, database records, or shared state simultaneously without locking mechanisms.
- Environments with strict single-threaded or serial execution constraints.

## Core Workflow

### 1. Partition Workload into Independent Subagent Tasks
Define distinct `AgentTask` objects specifying role, prompt, payload, and timeouts:

```python
from parallel_agent_dispatcher import AgentTask, ParallelAgentDispatcher

tasks = [
    AgentTask(task_id="sec-1", role="Security Auditor", prompt="Scan for authorization bypasses"),
    AgentTask(task_id="perf-1", role="Performance Profiler", prompt="Identify N+1 database queries"),
    AgentTask(task_id="test-1", role="Test Generator", prompt="Author edge-case unit tests")
]
```

### 2. Configure Concurrency and Dispatch Workers
Initialize `ParallelAgentDispatcher` with an approved concurrency ceiling and dispatch the tasks:

```python
dispatcher = ParallelAgentDispatcher(max_concurrency=4)

def worker_callback(task: AgentTask):
    # Delegate to LLM subagent or tool execution
    return {"status": "ok", "role": task.role, "findings": f"Processed {task.prompt}"}

report = dispatcher.dispatch(tasks, worker_callback)
```

### 3. Reconcile Fan-In Results
Process aggregated findings, inspect execution durations, and handle isolated failures defensively:

```python
print(f"Completed: {report['summary']['completed']}/{report['summary']['total_tasks']}")
print(f"Effective Speedup: {report['summary']['effective_speedup']}")
for item in report["results"]:
    if item["status"] != "completed":
        print(f"Warning: Task {item['task_id']} failed: {item['error']}")
```

## Verification & Testing

Verify parallel execution, concurrency throttling, and fan-in aggregation by running:

```bash
python scripts/dispatching-parallel-agents_helper.py
```

Expected output:
- Concurrency simulation runs cleanly across all workers.
- Effective speedup exceeds 1.0x.
- Zero uncaught exceptions.
