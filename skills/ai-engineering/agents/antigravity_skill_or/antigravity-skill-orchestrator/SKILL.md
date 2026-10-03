---
name: antigravity-skill-orchestrator
description: "Use this skill to dynamically analyze multi-domain user tasks, evaluate execution complexity, select and compose optimal combinations of agent skills from the repository catalog, construct dependency-aware execution DAGs, and prevent skill over-engineering on simple tasks."
domain: ai-engineering
category: agents
subcategory: antigravity_skill_or
tags:
  - skill-orchestration
  - meta-agent
  - task-evaluation
  - multi-skill-composition
  - dependency-graph
  - agentic-workflows
  - execution-dag
technologies:
  - Python
  - NetworkX
  - JSON-Schema
  - AST
  - Graphlib
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Agent Skill Meta-Orchestrator Architecture Standard

## Overview

The `antigravity-skill-orchestrator` is a meta-orchestration skill designed to coordinate and compose multiple specialized agent skills for complex, multi-domain software engineering challenges. Autonomous agents often fall into one of two traps: either under-utilizing specialized domain skills by attempting naive single-prompt implementations, or over-engineering trivial tasks by triggering unnecessary multi-agent loops that consume excessive tokens and latency. This skill provides an intelligent task complexity gate, semantic capability matching against the local skill catalog, and topological execution of dependency Directed Acyclic Graphs (DAGs).

```
+-----------------------------------------------------------------------------------+
|                        Agent Skill Meta-Orchestrator Pipeline                     |
|                                                                                   |
|  [ User Request ]                                                                 |
|         |                                                                         |
|         v                                                                         |
|  [ Task Complexity Gate ]                                                         |
|    /                  \                                                           |
|   / (Low Complexity)   \ (High Complexity / Multi-Domain)                         |
|  v                      v                                                         |
| [ Direct Execution ]   [ Domain & Intent Decomposition ]                          |
| (Native edit/bash)      |                                                         |
|                         v                                                         |
|                        [ Skill Discovery & Capability Matching ]                  |
|                         | (Catalog query: tags, technologies, domain affinity)     |
|                         v                                                         |
|                        [ Dependency DAG Resolver ]                                |
|                         | (Topological Sort: e.g. Schema -> API -> Frontend)       |
|                         v                                                         |
|                        [ Orchestrated Multi-Stage Execution ]                     |
|                         |                                                         |
|                         v                                                         |
|                        [ Cross-Skill Telemetry & Memory Logging ]                 |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When executing complex user requests that cross multiple architectural boundaries (e.g. database schema migrations, API backend implementation, and responsive frontend UI synthesis).
- When selecting the optimal specialized skills from a library of 2,000+ skills based on task context.
- When sequencing multiple interdependent skills into a coherent execution DAG with verified data contracts between stages.
- When recording skill composition telemetry to continuously refine future orchestration decisions.

## When NOT to Use

- For localized, single-step tasks (e.g. fixing a typo, updating a CSS color variable, running a single unit test). These must be executed directly without orchestration overhead.
- When the user explicitly requests execution using a single designated skill.
- When tasks are purely conversational or conceptual without multi-stage implementation deliverables.

---

## Inputs & Prerequisites

1. **User Request / Goal**: Full description of the multi-domain target system.
2. **Skill Catalog Registry**: Access to local repository catalog metadata (`INDEX.md` or JSON registry).
3. **Complexity Threshold**: Configurable threshold (e.g. cross-domain count $\ge 2$) determining when orchestration is invoked.

---

## Core Workflow

### Step 1: Task Complexity Gating
Before invoking any orchestration overhead, classify the task complexity:

```python
from typing import List, Dict, Any

def evaluate_task_complexity(prompt: str) -> Dict[str, Any]:
    """
    Evaluates whether a request warrants multi-skill orchestration
    or should be executed directly with baseline tools.
    """
    prompt_lower = prompt.lower()
    
    # Identifiers of cross-domain engineering complexity
    domain_signals = {
        "database": ["database", "schema", "migration", "sql", "orm", "postgres"],
        "backend": ["api", "endpoint", "fastapi", "rest", "graphql", "authentication"],
        "frontend": ["ui", "component", "react", "nextjs", "css", "tailwind"],
        "devops": ["docker", "kubernetes", "ci/cd", "terraform", "deploy", "monitoring"],
        "security": ["rbac", "jwt", "encryption", "audit", "sanitization"]
    }
    
    matched_domains = [d for d, terms in domain_signals.items() if any(t in prompt_lower for t in terms)]
    word_count = len(prompt.split())
    
    requires_orchestration = len(matched_domains) >= 2 or (word_count > 60 and len(matched_domains) >= 1)
    
    return {
        "requires_orchestration": requires_orchestration,
        "detected_domains": matched_domains,
        "complexity_level": "multi_domain" if requires_orchestration else "simple_direct"
    }
```

### Step 2: Skill Discovery & Topological DAG Scheduling
Construct a DAG representing execution order across detected domains:

```python
import graphlib
from typing import List, Tuple

def schedule_skill_execution(dependencies: List[Tuple[str, str]]) -> List[str]:
    """
    Resolves topological order for skill execution stages.
    dependencies format: (child_skill, parent_skill_it_depends_on)
    """
    graph = {}
    for child, parent in dependencies:
        if child not in graph:
            graph[child] = set()
        graph[child].add(parent)
        if parent not in graph:
            graph[parent] = set()

    sorter = graphlib.TopologicalSorter(graph)
    return list(sorter.static_order())
```

### Step 3: Execution Monitoring & Inter-Skill Contracts
Each executed skill outputs structured artifacts that feed as inputs into subsequent DAG stages. If an upstream skill fails verification, the downstream pipeline is paused immediately.

---

## Best Practices & Failure Modes

- **Over-Orchestration Trap**: Triggering a multi-agent orchestration graph for a 2-line bug fix consumes unnecessary tokens and degrades user experience. Always obey the complexity gate.
- **Circular Dependencies**: Ensure execution graphs are strictly acyclic. If circular feedback is required, model it as bounded iteration passes rather than cyclical dependencies.
- **Contract Boundary Validation**: Between DAG nodes, assert that expected artifacts (e.g. OpenAPI specs, schema models) exist and validate before calling the next skill.

---

## Verification & Testing

1. Run the meta-skill orchestrator DAG engine and complexity classifier test suite:
   ```bash
   python scripts/antigravity-skill-orchestrator_helper.py
   ```
2. Test DAG resolution and complexity filtering via CLI:
   ```bash
   python scripts/meta_skill_orchestrator.py --test-all
   ```
