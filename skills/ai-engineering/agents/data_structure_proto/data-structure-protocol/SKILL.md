---
name: data-structure-protocol
description: "Use this skill to create, maintain, and query persistent structural graph memory of a codebase (.dsp). It maps software entities (objects, classes, functions) with stable UIDs, tracks semantic dependencies and import rationales ('why' connections exist), and enables instant impact analysis for agent refactoring without re-reading the entire repository."
domain: ai-engineering
category: agents
subcategory: data_structure_proto
tags:
  - data-structure-protocol
  - dsp
  - codebase-memory
  - dependency-graph
  - refactoring-impact-analysis
  - persistent-structural-map
  - ast-entities
technologies:
  - Python
  - AST
  - Graphviz
  - NetworkX
  - JSON
  - SHA256
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

# Data Structure Protocol (DSP) Codebase Graph Standard

## Overview

The `data-structure-protocol` (DSP) skill defines the specification, serialization schema, and query protocol for maintaining a persistent, graph-structured mental model of a software codebase. Large Language Model (LLM) agents operating on medium-to-large codebases spend up to 70% of their token budget simply orienting themselves: discovering where classes reside, which modules depend on them, and what will break if an interface is modified. DSP solves this by externalizing codebase architecture into an indexed directed graph stored in `.dsp/`. Rather than storing raw AST dumps, DSP records **semantic identity** (stable UIDs), **interface boundaries** (imports/exports), and **dependency rationales** (*why* a connection exists).

```
+-----------------------------------------------------------------------------------+
|                        Data Structure Protocol (DSP) Map                          |
|                                                                                   |
|  [ Source File: src/auth/service.py ]                                             |
|         |                                                                         |
|         +---> Node: obj-4a1b8c2e (UserService Class)                              |
|         |        - File: src/auth/service.py                                      |
|         |        - Exports: func-7f3a9c12 (authenticate_user)                     |
|         |                                                                         |
|         +---> Dependency Edge: imports obj-9e2d1f4b (DatabasePool)                |
|                  - Rationale: "Connection pool for user credential lookup"        |
|                                                                                   |
|  [ Persistent Storage: .dsp/ Directory ]                                          |
|    - TOC                                 (Ordered entity index)                   |
|    - entities/obj-4a1b8c2e/meta.json     (Boundaries & exposed functions)         |
|    - reverse_index/obj-9e2d1f4b/who.json (Downstream dependants & break risk)     |
|                                                                                   |
|  [ Query: Impact Analysis / Blast Radius ]                                        |
|    "If I modify authenticate_user(), which 3 downstream routes will break?"       |
|    Result calculated in < 10ms without reading 50,000 lines of source code!       |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When an agent is working in a project containing a `.dsp/` directory or needs to bootstrap structural memory.
- When performing pre-refactoring impact analysis (determining blast radius before altering a shared class or function signature).
- When navigating large, multi-module repositories where reading all source files exceeds the agent's context budget.
- When creating or modifying code files to keep the structural graph synchronized with code changes.

## When NOT to Use

- For tiny, single-file scripts where all functions and definitions are visible in fewer than 100 lines.
- In read-only external repositories where local `.dsp/` metadata cannot be created or stored.
- As a replacement for comprehensive automated unit tests (DSP tracks dependency architecture, not execution correctness).

---

## Inputs & Prerequisites

1. **Target Repository Root**: Directory containing project source code.
2. **Entity Types**: Objects (`obj-<8hex>`: classes, modules, configs) and Functions (`func-<8hex>`: exported methods).
3. **Graph Storage**: Access to write the `.dsp/` indexing metadata directory.

---

## Core Workflow

### Step 1: Stable Entity Identity Generation
Assign deterministic, stable UIDs derived from entity name and module namespace:

```python
import hashlib
from typing import Dict, Any

def generate_dsp_uid(entity_type: str, namespace: str, entity_name: str) -> str:
    """
    Computes an 8-hex deterministic UID for an entity.
    entity_type: 'obj' or 'func'
    """
    raw_key = f"{namespace}:{entity_name}".encode("utf-8")
    hash_hex = hashlib.sha256(raw_key).hexdigest()[:8]
    return f"{entity_type}-{hash_hex}"
```

### Step 2: Dependency Edge Modeling with Rationales
Every recorded dependency must declare *why* the connection exists to inform downstream agents of breakage risk:

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DSPEdge:
    source_uid: str
    target_uid: str
    import_reason: str
    is_hard_dependency: bool = True
```

### Step 3: Refactoring Impact Analysis (Blast Radius Calculation)
Before modifying an entity, traverse the reverse dependency index to compute downstream dependents:

```python
def calculate_blast_radius(target_uid: str, reverse_index: Dict[str, List[DSPEdge]]) -> List[Dict[str, str]]:
    """
    Traverses reverse dependency edges to identify all modules affected by changing target_uid.
    """
    impacted = []
    queue = [target_uid]
    visited = set()

    while queue:
        curr = queue.pop(0)
        if curr in visited:
            continue
        visited.add(curr)

        edges = reverse_index.get(curr, [])
        for edge in edges:
            impacted.append({
                "affected_entity": edge.source_uid,
                "reason_it_breaks": edge.import_reason
            })
            queue.append(edge.source_uid)

    return impacted
```

---

## Best Practices & Failure Modes

- **Never Omit Dependency Rationales**: An edge without a reason only reveals *what* imports *what*, forcing agents to re-read files to determine if an edit is safe. Always record the operational purpose.
- **Keep UIDs Stable Across File Renames**: If `src/auth.py` is moved to `src/security/auth.py`, preserve the existing entity UIDs to maintain historical dependency links.
- **Automated Sync**: Hook DSP updates into pre-commit scripts so the structural map never drifts from the underlying code.

---

## Verification & Testing

1. Run the Data Structure Protocol graph manager test suite:
   ```bash
   python scripts/data-structure-protocol_helper.py
   ```
2. Verify entity UID generation, rationale mapping, and blast-radius traversal via CLI:
   ```bash
   python scripts/dsp_graph_protocol.py --test-all
   ```
