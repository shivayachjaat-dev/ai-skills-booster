---
name: ai-loop
description: "Use this skill to orchestrate bounded, stateful autonomous development loops structured across Specification, Implementation (Build), and Automated Verification (Review). It enforces formal iteration budgets, stop conditions, deterministic diff bounding, and human approval gates for high-risk operations."
domain: ai-engineering
category: models
subcategory: ai_loop
tags:
  - autonomous-coding
  - spec-driven-development
  - agentic-loop
  - verification-gates
  - software-synthesis
  - bounded-execution
technologies:
  - Python
  - Git
  - Pytest
  - AST
  - JSON-Schema
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

# Autonomous Development Loop (Spec-Build-Review) Standard

## Overview

The `ai-loop` skill provides a formal, state-machine-driven framework for executing autonomous software development lifecycles. Unconstrained autonomous coding agents frequently suffer from context drift, speculative scope expansion, infinite retry loops, and undetected code regressions. This skill enforces rigorous bounded execution by separating every coding task into three decoupled phases: **Specification (Spec)**, **Implementation (Build)**, and **Verification (Review)**, bound by strict iteration limits and explicit human approval triggers.

```
+-----------------------------------------------------------------------------------+
|                        Autonomous Spec-Build-Review Loop                          |
|                                                                                   |
|     +-------------------+                                                         |
|     |  User Objective   |                                                         |
|     +-------------------+                                                         |
|               |                                                                   |
|               v                                                                   |
|     +-------------------+                                                         |
|     |   PHASE 1: SPEC   | <--- Solicit constraints, define scope & "Done"         |
|     |  (specs/<feat>.md)|                                                         |
|     +-------------------+                                                         |
|               |                                                                   |
|               +-----------------------+                                           |
|               |                       |                                           |
|               v                       v                                           |
|     +-------------------+    [Approval Required?] ---> [ HUMAN GATE ]             |
|     |  PHASE 2: BUILD   |                                     |                   |
|     | (Code strictly    | <-----------------------------------+ (Approved)        |
|     |  within scope)    |                                                         |
|     +-------------------+                                                         |
|               |                                                                   |
|               v                                                                   |
|     +-------------------+                                                         |
|     |  PHASE 3: REVIEW  |                                                         |
|     |  (Test & verify   |                                                         |
|     |   against spec)   |                                                         |
|     +-------------------+                                                         |
|          /         \                                                              |
|   [All Passed]   [Failures & Budget Left]                                         |
|        /             \                                                            |
|       v               v                                                           |
|   +--------+    +----------------------------+                                    |
|   |  DONE  |    | Loop back to BUILD with    |                                    |
|   +--------+    | targeted defect diagnostics|                                    |
|                 +----------------------------+                                    |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When developing new modules, features, or bug fixes autonomously where requirements must be strictly verified.
- When an agent is tasked with end-to-end implementation with high autonomy but needs deterministic termination guarantees.
- When modifying legacy or mission-critical code requiring automated regression verification and scope confinement.

## When NOT to Use

- For trivial, single-step operations (e.g., renaming a variable, updating a docstring) where the overhead of a full formal spec loop is unwarranted.
- Open-ended, exploratory research spikes without definable success criteria or verification commands.
- Tasks requiring irreversible operations without pre-configured human approval hooks.

---

## Inputs & Prerequisites

1. **Target Feature / Defect Description**: Natural language statement of the goal.
2. **Iteration Budget**: Hard limit on maximum build-review cycles (default: 3 to 5 iterations).
3. **Verification Command**: Automated test command or deterministic validation script (e.g. `pytest tests/test_feature.py`).
4. **Permitted Scope**: Explicit whitelist of allowed files and directories that the agent may modify.

---

## Core Workflow

### Phase 1: Specification & Contract Definition
The agent analyzes requirements, identifies edge cases, determines the test harness, and generates a structured specification document before touching any implementation code:

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LoopSpecification:
    objective: str
    requirements: List[str]
    allowed_file_patterns: List[str]
    verification_command: str
    max_iterations: int = 5
    definition_of_done: List[str] = field(default_factory=list)
    requires_human_approval: bool = False
```

### Phase 2: Bounded Implementation (Build)
The agent executes modifications strictly constrained to the `allowed_file_patterns`. Any modification attempt outside the designated boundary is blocked:

```python
import fnmatch
import os

def validate_scope(modified_files: List[str], allowed_patterns: List[str]) -> bool:
    """Verifies that every modified file falls within the permitted scope boundary."""
    for path in modified_files:
        norm_path = path.replace("\\", "/")
        match = any(fnmatch.fnmatch(norm_path, pattern) for pattern in allowed_patterns)
        if not match:
            raise PermissionError(f"Out-of-scope modification rejected: {path}")
    return True
```

### Phase 3: Verification & Loop Evaluation (Review)
Run verification commands, capture stdout/stderr, and calculate delta towards goal completion:

```python
import subprocess

def execute_verification(verification_cmd: str) -> tuple[bool, str]:
    """Executes the deterministic verification suite and returns status and output."""
    res = subprocess.run(verification_cmd, shell=True, capture_output=True, text=True)
    passed = (res.returncode == 0)
    output = res.stdout if passed else (res.stdout + "\n" + res.stderr)
    return passed, output
```

### Phase 4: Termination & Safety Thresholds
The loop terminates upon any of the following mutually exclusive conditions:
1. **Goal Completion**: All spec requirements and verification commands pass.
2. **Budget Exhaustion**: Iteration counter reaches `max_iterations` without passing. Agent emits a structured diagnostic report and halts.
3. **Escalation Trigger**: A high-risk event (database schema migration, external API write, scope creep) is encountered, requiring explicit user confirmation.

---

## Best Practices & Failure Modes

- **Never Combine Spec and Build**: Writing code before committing the spec leads to confirmation bias where tests are tailored to what was written rather than what was required.
- **Diff Confinement**: Measure git diff size at each iteration. If diff exceeds 500 lines for a targeted bugfix, trigger human escalation.
- **Flaky Test Guard**: If a test flips between pass and fail across iterations without related code changes, quarantine the test as non-deterministic.

---

## Verification & Testing

1. Run the autonomous loop state-machine test suite:
   ```bash
   python scripts/ai-loop_helper.py
   ```
2. Verify loop constraint enforcement with simulated budget exhaustion and scope boundary violations:
   ```bash
   python scripts/ai_loop_orchestrator.py --test-all
   ```
