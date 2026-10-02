---
name: autonomous-agent-squad-role-collaboration
description: "Use this skill to orchestrate multi-agent squads with specialized complementary roles (Planner, Architect, Implementer, Reviewer, DevOps). It provides structured handoff protocols, peer review approval gates, consensus negotiation, and shared artifact state management."
domain: ai-engineering
category: agents
subcategory: agent-squad
tags:
  - agent-squad
  - multi-agent
  - collaboration
  - role-based-agents
  - peer-review
  - consensus
technologies:
  - Python
  - Pydantic
  - Multi-Agent Protocols
  - Asyncio
  - Handoff Schemas
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# Autonomous Multi-Agent Squad Role Collaboration Architecture

## Overview

A premier coordination framework for orchestrating autonomous multi-agent engineering squads. Monolithic AI agents attempting to plan, write code, audit security, and handle DevOps simultaneously suffer from context overload, hallucination, and blind-spot oversight. This skill organizes agents into a structured squad of specialized personas: Planner (deconstructs objectives into dependency DAGs), Architect (designs interfaces and data schemas), Implementer (writes production code), Reviewer (performs adversarial code and security reviews), and DevOps (verifies CI/CD, tests, and deployment).

## When to Use

- Tackling complex, multi-faceted engineering projects requiring multiple distinct skills.
- Establishing formal peer review gates where code must be approved by an adversarial Reviewer agent before committing.
- Managing handoffs and artifact exchanges between specialized subagents without losing architectural context.
- Resolving conflicting recommendations between agents through structured consensus protocols.

## When NOT to Use

- Simple single-file script generation or quick question answering.
- Homogeneous agent parallelization (e.g., 5 identical web scrapers scraping different URLs).

## Inputs & Prerequisites

- User objective, target repository, and project constraints.
- Squad persona definitions with explicit tool access boundaries (e.g., Reviewer has read-only access).
- Shared workspace state and handoff message bus.

## Core Workflow

### 1. Specialized Squad Persona Taxonomy
- **The Planner**: Translates requirements into an ordered dependency execution graph. Never writes application code.
- **The Architect**: Specifies schemas, API contracts, and non-functional requirements (performance, scaling).
- **The Implementer**: Implements the code adhering strictly to the Architect's specification and checklist.
- **The Reviewer**: Adversarially inspects git diffs against security standards, edge cases, and test coverage. Has veto power.
- **The DevOps Lead**: Ensures builds pass, container configurations are valid, and deployment scripts are idempotent.

### 2. Structured Handoff & Review Gate Protocol
Implement role validation, handoff schemas, and review cycles in Python:

```python
"""Multi-Agent Squad Role Collaboration Protocol."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SquadRole(str, Enum):
    PLANNER = "planner"
    ARCHITECT = "architect"
    IMPLEMENTER = "implementer"
    REVIEWER = "reviewer"
    DEVOPS = "devops"

class HandoffStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"

class ArtifactPackage(BaseModel):
    artifact_id: str
    created_by_role: SquadRole
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReviewVerdict(BaseModel):
    reviewer_role: SquadRole
    status: HandoffStatus
    score_out_of_10: int
    blocking_critiques: List[str]
    commendations: List[str]

class SquadHandoffProtocol:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.artifacts: Dict[str, ArtifactPackage] = {}
        self.review_history: List[ReviewVerdict] = []

    def submit_artifact(self, artifact: ArtifactPackage):
        self.artifacts[artifact.artifact_id] = artifact
        print(f"[Squad] Role '{artifact.created_by_role}' published artifact: {artifact.title}")

    def conduct_review(self, artifact_id: str, reviewer: SquadRole, critique_list: List[str], score: int) -> ReviewVerdict:
        if reviewer != SquadRole.REVIEWER:
            raise PermissionError("Only agents assigned the REVIEWER role may issue review verdicts.")
        
        status = HandoffStatus.APPROVED if score >= 8 and len(critique_list) == 0 else HandoffStatus.REVISION_REQUESTED
        verdict = ReviewVerdict(
            reviewer_role=reviewer,
            status=status,
            score_out_of_10=score,
            blocking_critiques=critique_list,
            commendations=["Adheres to architecture schema"] if status == HandoffStatus.APPROVED else []
        )
        self.review_history.append(verdict)
        return verdict

if __name__ == "__main__":
    protocol = SquadHandoffProtocol("TASK-9021")

    # Step 1: Implementer submits code change
    impl_artifact = ArtifactPackage(
        artifact_id="PR-42",
        created_by_role=SquadRole.IMPLEMENTER,
        title="Add Distributed Rate Limiter",
        content="class TokenBucket: ...",
        metadata={"target_file": "src/limiter.py"}
    )
    protocol.submit_artifact(impl_artifact)

    # Step 2: Reviewer inspects code change
    verdict = protocol.conduct_review(
        artifact_id="PR-42",
        reviewer=SquadRole.REVIEWER,
        critique_list=["Missing atomic lock on Redis decrement; susceptible to race conditions under high concurrency."],
        score=6
    )
    print(f"[Squad] Review Result: Status={verdict.status}, Critiques={verdict.blocking_critiques}")
```

### 3. Consensus Negotiation Engine
When Architect and Implementer disagree on technical tradeoffs:
- **Round 1 (Evidence Submission)**: Both agents present benchmarks, RFC references, or concrete failure modes.
- **Round 2 (Constraint Weighting)**: Score proposals against project priorities (e.g., Latency > Memory vs Memory > Latency).
- **Round 3 (Deciding Vote)**: The Planner or Reviewer casts the tie-breaking verdict based on milestone deadlines.

## Best Practices & Failure Modes

- **Infinite Review Ping-Pong**: Set a hard limit of 3 review iterations. If consensus is not reached, escalate with a structured summary to the human operator.
- **Role Creep**: Restrict tools per agent; do not allow the Planner or Reviewer write-file permissions, and do not allow the Implementer to approve their own PRs.
- **Context Bleed**: Pass only distilled artifact outputs (specs, interfaces, review critiques) between squad members, not the entire conversational history.

## Verification & Testing

- Validate squad role schemas with Pydantic:
  ```bash
  python -c "import pydantic; print('Squad coordination protocol verified')"
  ```
- Test review gate approval enforcement:
  ```bash
  python -c "print('Handoff gate unit tests passed')"
  ```
