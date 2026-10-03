---
name: brave-man
description: "Use this skill to run a structured, phased requirements extraction interview for new project requests before building. Instead of guessing and writing premature code, it guides the user through calibrated triage, core workflows, data modeling, and edge cases, synthesizing a fully specified prompt.md specification for deterministic downstream execution."
domain: ai-engineering
category: agents
subcategory: brave_man
tags:
  - requirements-engineering
  - pre-build-interview
  - prompt-specification
  - project-triage
  - edge-case-discovery
  - software-scoping
  - specification-first
technologies:
  - Python
  - Markdown
  - JSON-Schema
  - AST
  - Interview Frameworks
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# Pre-Build Clarification & Specification Interview Standard

## Overview

The `brave-man` skill implements a rigorous, phased requirements-engineering interview protocol designed to eliminate the most expensive failure mode in autonomous software generation: premature implementation driven by unstated assumptions. When users provide brief, informal requests (e.g. "build me a dashboard" or "create a task manager"), naive agents immediately scaffold directories and write code, guessing at data schemas, authentication models, edge cases, and user flows. This skill mandates an exhaustive, phased discovery interview first, culminating in a clean, self-contained `prompt.md` specification ready for deterministic execution.

```
+-----------------------------------------------------------------------------------+
|                        Pre-Build Discovery & Interview Funnel                     |
|                                                                                   |
|  [ User Request: "Build me an X" ]                                                |
|         |                                                                         |
|         v                                                                         |
|  [ Phase 0: Triage Calibration ] <--- Scope (1-page vs SaaS), Audience, Stack     |
|         |                                                                         |
|         v                                                                         |
|  [ Phase 1: Purpose & Core Value ] <--- Target user, primary action, success test  |
|         |                                                                         |
|         v                                                                         |
|  [ Phase 2: User Journey & Scope Boundary ] <--- Must-have v1 vs Future nice-to-have|
|         |                                                                         |
|         v                                                                         |
|  [ Phase 3: Data Entities & State Model ] <--- Storage, persistence, relationships|
|         |                                                                         |
|         v                                                                         |
|  [ Phase 4: Edge Cases & Non-Functional Needs ] <--- Auth, rate limits, offline  |
|         |                                                                         |
|         v                                                                         |
|  [ Structured Synthesis: prompt.md ]                                              |
|    - Explicit Definition of Done                                                  |
|    - Verified Acceptance Harness                                                  |
|    - Zero Unvalidated Assumptions                                                 |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When a user asks to build a new application, service, tool, website, or multi-component feature from scratch.
- When the initial user request is less than 150 words or lacks explicit data models and verification commands.
- BEFORE writing any code, scaffolding repository directories, or creating implementation plans.
- When aligning cross-functional requirements across ambiguous product briefs.

## When NOT to Use

- For targeted bug fixes, localized refactoring of existing functions, or minor styling tweaks where scope is already narrow and clear.
- When an authoritative, complete formal specification (`specs/*.md` or `prompt.md`) already exists.
- In automated headless CI/CD execution pipelines where interactive user dialogue is unavailable.

---

## Inputs & Prerequisites

1. **Initial Project Request**: The natural language description of what the user wishes to construct.
2. **Interactive Communication Channel**: Ability to query the user in structured, batched question rounds.
3. **Target Output Path**: Default location for the synthesized specification (`prompt.md` or `specs/<feature>.md`).

---

## Core Workflow

### Phase 0: Rapid Triage Calibration
Assess scale to determine interview depth:
1. Is this a single-user local utility or a multi-user shared production service?
2. What is the complexity scale (micro-tool $\le 3$ files vs multi-tier system)?
3. Are there hard technology stack constraints (e.g. Next.js, FastAPI, SQLite) or is the technical architecture open?

### Phase 1 through 4: Phased Structured Dialogue
Execute batched question rounds (3-4 focused questions per phase):
- **Phase 1 (Purpose)**: Who is the user? What single action delivers core value? What does "done" look like?
- **Phase 2 (Flows)**: Step-by-step user journey. Explicit boundary between v1 requirements and deferred backlog items.
- **Phase 3 (Data)**: Primary entities, schemas, lifetime/persistence requirements, relational dependencies.
- **Phase 4 (Edge Cases)**: Error handling, offline behavior, security boundaries, rate limiting.

### Phase 5: Specification Synthesis
Generate the standardized `prompt.md` execution document:

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ProjectSpec:
    title: str
    target_audience: str
    core_value_proposition: str
    v1_must_haves: List[str]
    explicit_out_of_scope: List[str]
    entities: List[Dict[str, str]]
    technical_stack: List[str]
    edge_cases: List[str]
    verification_criteria: List[str]

def format_prompt_spec(spec: ProjectSpec) -> str:
    """Formats structured interview responses into an authoritative prompt.md document."""
    lines = [
        f"# Execution Specification: {spec.title}",
        "",
        "## 1. Project Purpose & Scope",
        f"- **Audience**: {spec.target_audience}",
        f"- **Core Value**: {spec.core_value_proposition}",
        "",
        "## 2. Mandatory Scope (v1 MVP)",
    ]
    for item in spec.v1_must_haves:
        lines.append(f"- [ ] {item}")
        
    lines.append("\n## 3. Explicitly Out-of-Scope (Do NOT Build)")
    for item in spec.explicit_out_of_scope:
        lines.append(f"- {item}")
        
    lines.append("\n## 4. Technical Constraints & Stack")
    for tech in spec.technical_stack:
        lines.append(f"- {tech}")
        
    lines.append("\n## 5. Verification & Acceptance Criteria")
    for crit in spec.verification_criteria:
        lines.append(f"- {crit}")
        
    return "\n".join(lines)
```

---

## Best Practices & Failure Modes

- **Never Scaffold Prematurely**: Do not run `npm create` or `mkdir -p` before the specification is approved. Scaffolding commits you to mental patterns before requirements are locked.
- **Batched Questioning**: Never ask questions one-by-one over dozens of tedious chat turns. Present questions in cohesive batches of 3-4 organized by phase.
- **Explicit Negative Scope**: Always list what *not* to build. Defining out-of-scope boundaries prevents 80% of agent hallucinated bloat.

---

## Verification & Testing

1. Run the clarifying interview state engine and specification generator test suite:
   ```bash
   python scripts/brave-man_helper.py
   ```
2. Test spec synthesis from synthetic project profiles:
   ```bash
   python scripts/clarifying_interview_engine.py --test-all
   ```
