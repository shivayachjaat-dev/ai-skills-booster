---
name: ai-agent-development
description: "Use this skill to design, implement, and deploy production-grade autonomous AI agents and multi-agent systems using LangGraph, CrewAI, and custom ReAct loops. It covers typed state graphs, tool schema validation with Pydantic, cyclic reflection edges, checkpointed memory persistence, and strict execution boundary limits."
domain: ai-engineering
category: models
subcategory: ai_agent_development
tags:
  - ai-engineering
  - agent-development
  - langgraph
  - crewai
  - react-loop
  - tool-calling
  - state-management
technologies:
  - LangGraph
  - Python
  - Pydantic
  - CrewAI
  - OpenAI / Anthropic APIs
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
  - pydantic@>=2.0.0
version: 1.0.0
author: Antigravity Team
---

# Autonomous AI Agent Development & StateGraph Orchestration

## Overview

A production engineering standard for building deterministic, resilient autonomous AI agents and multi-agent systems. While naive prompt chaining or unbounded while-loops frequently suffer from reasoning degradation, infinite loops, and unrecoverable tool errors, robust agent architectures leverage cyclic directed graphs (such as LangGraph or custom ReAct state machines). This skill guides AI engineers in structuring typed state schemas, integrating strongly-typed Pydantic tools, configuring conditional routing edges (tool invocation vs human reflection vs termination), enforcing execution limits (recursion bounds), and snapshotting state to persistent storage.

```
+--------------------------------------------------------------------------------+
|                       LangGraph Cyclic Agent Architecture                      |
|                                                                                |
|  [ User Input / Goal ] ---> [ Initialize Typed AgentState ]                    |
|                                         |                                      |
|                                         v                                      |
|                        +-----> [ Model Reasoning Node ]                        |
|                        |                |                                      |
|                        |                v                                      |
|                        |   [ Conditional Edge: Route? ]                        |
|                        |                |                                      |
|                        |    +-----------+-----------+                          |
|                        |    | Has Tool Calls        | No Tool Calls            |
|                        |    v                       v                          |
|                        | [ Tool Execution Node ]   [ End / Deliver Output ]    |
|                        | (Execute & Append Result)                             |
|                        +------------+                                          |
|                                     |                                          |
|                   (Check: Iteration Count < Max Bounds)                        |
+--------------------------------------------------------------------------------+
```

## When to Use

- Developing autonomous coding agents, research assistants, data analysis agents, or multi-agent squads.
- Implementing tool-using LLM workflows that require multi-turn reasoning and dynamic error correction.
- Structuring multi-agent delegation (e.g., Planner agent delegating sub-tasks to specialized Worker agents).
- Adding checkpointed state persistence enabling long-running workflows to pause, wait for human review, and resume.

## When NOT to Use

- Simple single-turn text transformation or classification tasks (use direct LLM inference calls).
- Static deterministic pipelines with zero dynamic branching or unpredictable inputs (use standard DAG orchestrators like Airflow or Prefect).

## Inputs & Prerequisites

- Python 3.10+ runtime with `pydantic` v2 installed.
- Target LLM provider API credentials (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) or local inference server (Ollama/vLLM).
- Defined tool set with explicit input/output schemas.

## Core Workflow

### Step 1: Typed State Schema Definition
Define an immutable or append-only state structure tracking message history and execution bounds:

```python
from typing import Annotated, Sequence, TypedDict
from pydantic import BaseModel, Field
import operator

class AgentState(TypedDict):
    messages: Annotated[list[dict], operator.add] # Append-only message history
    iteration_count: int
    current_goal: str
    is_complete: bool
```

### Step 2: Strongly-Typed Tool Schema Modeling (Pydantic v2)
Every tool must define strict field types, descriptions, and validation constraints:

```python
from pydantic import BaseModel, Field

class DatabaseQueryInput(BaseModel):
    query: str = Field(description="Read-only SQL query to execute")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of rows to return")

def execute_db_query(params: DatabaseQueryInput) -> dict:
    """Executes a read-only query against the application database."""
    # Enforce read-only constraint
    if any(forbidden in params.query.upper() for forbidden in ["DROP", "DELETE", "UPDATE", "INSERT"]):
        raise ValueError("Security violation: Only SELECT queries are permitted.")
    return {"rows": [{"id": 1, "status": "active"}], "count": 1}
```

### Step 3: ReAct Reasoning & Execution Loop
Implement the core decision loop with explicit recursion limits and error isolation:

```python
import logging

logger = logging.getLogger("agent")

def agent_reasoning_step(state: AgentState) -> dict:
    """Invokes LLM with current state and bound tools."""
    # Guard against runaway infinite loops
    if state["iteration_count"] >= 10:
        logger.warning("Max recursion depth reached (10 iterations). Forcing termination.")
        return {
            "messages": [{"role": "assistant", "content": "Task halted: Maximum iteration budget reached."}],
            "is_complete": True
        }

    # Simulate model reasoning decision
    last_msg = state["messages"][-1]
    if "status" in last_msg.get("content", ""):
        return {
            "messages": [{"role": "assistant", "content": "Database audit complete: System active."}],
            "is_complete": True,
            "iteration_count": state["iteration_count"] + 1
        }
    else:
        # Agent decides to call a tool
        return {
            "messages": [{
                "role": "assistant", 
                "tool_calls": [{"name": "execute_db_query", "args": {"query": "SELECT status FROM nodes"}}]
            }],
            "is_complete": False,
            "iteration_count": state["iteration_count"] + 1
        }
```

### Step 4: Conditional Routing & Tool Dispatch
Route execution based on whether the model requested tool invocation:

```python
def should_continue(state: AgentState) -> str:
    if state.get("is_complete", False):
        return "end"
    last_message = state["messages"][-1]
    if "tool_calls" in last_message:
        return "tools"
    return "end"
```

### Step 5: Checkpointing & State Persistence
Save state snapshots to disk after every node execution to ensure fault tolerance:

```python
import json
import os

def checkpoint_state(session_id: str, state: AgentState, checkpoint_dir: str = ".checkpoints"):
    os.makedirs(checkpoint_dir, exist_ok=True)
    filepath = os.path.join(checkpoint_dir, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
```

## Best Practices & Failure Modes

- **Hard Recursion Limits**: Always configure a strict `recursion_limit` (e.g., 15-25 turns). Unconstrained agents can consume hundreds of dollars in API tokens if caught in a cyclic reasoning trap.
- **Graceful Tool Error Recovery**: Never allow an unhandled tool exception to crash the agent process. Catch the exception, serialize the error message as a tool output message, and let the model observe the error and attempt a fix.
- **Read-Only vs Write Tools**: Separate destructive mutations from read operations. Require human confirmation before executing state mutations.

## Verification & Testing

1. Validate execution bounds: Run `python scripts/ai_agent_runner.py --test-limits` to confirm the agent terminates when iteration limits are hit.
2. Test tool recovery: Run `python scripts/ai_agent_runner.py --test-error-recovery` to verify self-correction when a tool fails.
3. Verify state checkpointing: Verify that interrupted session states can be reloaded and resumed from serialized JSON snapshots.
