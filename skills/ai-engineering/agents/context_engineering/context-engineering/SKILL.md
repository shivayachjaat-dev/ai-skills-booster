---
name: context-engineering
description: "Use this skill to design, curate, and optimize LLM agent context architectures. It implements hierarchical context layering (persistent rules, feature specifications, AST code slices, and targeted test diagnostics), prevents 'Lost in the Middle' attention degradation, and enforces proactive token budget pruning."
domain: ai-engineering
category: agents
subcategory: context_engineering
tags:
  - context-engineering
  - token-budgeting
  - prompt-architecture
  - context-hierarchy
  - attention-optimization
  - ast-slicing
  - lost-in-the-middle
technologies:
  - Python
  - AST
  - Tokenizers
  - JSON-Schema
  - Markdown
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

# LLM Agent Context Engineering & Attention Optimization Standard

## Overview

The `context-engineering` skill provides the rigorous engineering methodology for structuring, curating, and budgeting information provided to autonomous LLMs and coding agents. Context is the primary operational lever governing agent task performance: providing too little context triggers hallucinated APIs and incorrect architectural assumptions, while providing excessive, unfiltered context triggers attention degradation (the empirical "Lost in the Middle" phenomenon), instruction neglect, and prohibitive token expenditure. This skill formalizes a 4-tier context hierarchy, AST-driven source slicing, and primacy/recency positioning to maximize reasoning fidelity.

```
+-----------------------------------------------------------------------------------+
|                        The 4-Tier Context Hierarchy                               |
|                                                                                   |
|  [ Layer 1: Persistent Rules ] (CLAUDE.md / Invariants)        | < 1,000 tokens   |
|         |                                                      | Always loaded    |
|         v                                                      +------------------+
|  [ Layer 2: Task Specification ] (RFC / Goal Checklist)        | 1,000 - 2,000 tok|
|         |                                                      | Feature-scoped   |
|         v                                                      +------------------+
|  [ Layer 3: AST Source Slices ] (Target Classes & Signatures)  | 2,000 - 6,000 tok|
|         |                                                      | Extracted AST    |
|         v                                                      +------------------+
|  [ Layer 4: Immediate Telemetry ] (Target Test Error Snippet)  | < 500 tokens     |
|                                                                | Ephemeral delta  |
|                                                                                   |
|  [ Attention Window Placement (U-Shaped Attention Optimization) ]                 |
|    - Primacy (Beginning of Prompt): System Invariants & Safety Constraints        |
|    - Middle (Internal Context): Background documentation & secondary context      |
|    - Recency (End of Prompt): Immediate task objective & failing test stack trace |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When structuring agent prompt templates for multi-step reasoning, coding, or code refactoring workflows.
- When an agent begins hallucinating non-existent methods or disregarding repository conventions due to context bloat.
- When packing multiple documentation files or source code repositories into a finite LLM context window.
- When designing automated context ingestion pipelines (e.g. vector search RAG re-rankers).

## When NOT to Use

- For short, atomic single-turn questions that require no surrounding codebase context.
- When editing trivial standalone scripts where the entire file is under 40 lines.
- As a substitute for vector databases or disk storage (context is ephemeral RAM; databases are persistent disk).

---

## Inputs & Prerequisites

1. **Target Context Budget**: Total allowable tokens allocated for prompt context (e.g. 8k, 32k, 128k).
2. **Repository Artifacts**: Raw source files, project rules, and test diagnostic output.
3. **Task Definition**: Specific feature requirements or bug reproduction steps.

---

## Core Workflow

### Step 1: Hierarchical Context Layer Allocation
Allocate strict token budgets across the four tiers:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ContextBudget:
    max_total_tokens: int = 16000
    persistent_rules_budget: int = 1000
    task_spec_budget: int = 2500
    source_code_budget: int = 10000
    diagnostics_budget: int = 1500

def evaluate_context_composition(components: Dict[str, str], budget: ContextBudget) -> Dict[str, Any]:
    """Measures component token consumption against tier allocations."""
    # Approximation: 1 token ~= 4 characters
    stats = {}
    total_consumed = 0
    
    for name, text in components.items():
        tokens = len(text) // 4
        stats[name] = tokens
        total_consumed += tokens
        
    is_compliant = total_consumed <= budget.max_total_tokens
    
    return {
        "tier_tokens": stats,
        "total_consumed": total_consumed,
        "budget_limit": budget.max_total_tokens,
        "is_compliant": is_compliant
    }
```

### Step 2: AST Code Slicing (Eliminate Irrelevant Bulk)
Instead of feeding entire multi-thousand-line files, extract only the targeted class signatures and functions:

```python
import ast

def extract_target_function_ast(source_code: str, target_func_name: str) -> str:
    """Extracts only the specified function AST node from a large source file."""
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == target_func_name:
            return ast.get_source_segment(source_code, node) or ""
    return ""
```

### Step 3: Primacy & Recency Attention Layout
Structure the prompt string to leverage the LLM's U-shaped attention distribution:
1. **Top (Primacy)**: Core directives, role definitions, and strict negative constraints (rules that must never be broken).
2. **Middle**: Reference examples, type definitions, and background documentation.
3. **Bottom (Recency)**: The immediate task goal, file path to edit, and exact failing test assertion.

---

## Best Practices & Failure Modes

- **The Dumping Trap**: Never concatenate raw terminal logs containing 10,000 lines of build output into prompt context. Filter logs down to the final 20 lines containing the exception trace.
- **Lost in the Middle**: Placing critical instructions in the exact middle of a 50k-token prompt results in up to 30% lower adherence. Keep instructions at the extreme top or bottom.
- **Context Compaction Triggers**: When a conversation exceeds 60% of the model's maximum window, compact prior turns into an immutable summary and clear the raw chat buffer.

---

## Verification & Testing

1. Run the context budget optimizer and AST slicing test suite:
   ```bash
   python scripts/context-engineering_helper.py
   ```
2. Verify token allocation compliance and attention ordering via CLI:
   ```bash
   python scripts/context_budget_optimizer.py --test-all
   ```
