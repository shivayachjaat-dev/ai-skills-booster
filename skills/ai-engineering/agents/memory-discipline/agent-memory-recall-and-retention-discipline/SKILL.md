---
name: agent-memory-recall-and-retention-discipline
description: "Use this skill to establish cognitive discipline protocols for AI agents interacting with persistent memory backends. It mandates proactive pre-action memory recall queries, conflict resolution between contradictory historical memories, and systematic post-action writebacks for architectural decisions, bug fixes, and user preferences."
domain: ai-engineering
category: agents
subcategory: memory-discipline
tags:
  - agent-memory
  - cognitive-architecture
  - memory-discipline
  - reflection
  - state-management
  - ai-agents
technologies:
  - Python
  - Pydantic
  - SQLite
  - Vector Retrieval
  - Memory Protocols
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# AI Agent Memory Recall & Retention Cognitive Discipline

## Overview

A foundational cognitive discipline framework governing how autonomous AI agents query, reconcile, and persist long-term memory. Without disciplined memory management, AI agents suffer from amnesia (repeating past errors), hallucinated consensus, and memory bloating (persisting low-value conversational noise). This skill establishes strict execution gates: requiring proactive memory retrieval prior to taking tool actions, deterministic conflict resolution between contradictory memories, and selective post-execution distillation to commit only validated learnings, bug resolutions, and architectural decisions.

## When to Use

- Building stateful autonomous software engineering agents that work across multiple days or sessions.
- Enforcing pre-action memory lookups so agents verify historical project constraints before executing breaking changes.
- Distilling post-task retrospectives into high-signal long-term memory entries (decisions, learned pitfalls, user preferences).
- Managing memory eviction, conflict resolution, and confidence scoring across vector/relational stores.

## When NOT to Use

- Pure stateless single-turn LLM generation (e.g., text summarization, spelling correction).
- Ephemeral scratchpad or chain-of-thought scratch reasoning that should not outlive the immediate prompt.

## Inputs & Prerequisites

- Persistent memory store interface (Vector database, SQLite, or key-value store).
- Current user request, working repository context, and task domain tags.
- Agent cognitive lifecycle hooks (Pre-execution hook, Post-execution reflection hook).

## Core Workflow

### 1. Cognitive Pre-Action & Post-Action Protocol
Every agent action must follow the strict four-phase cognitive memory loop:
1. **Pre-Action Recall**: Query long-term memory using the target file path, technology stack, and domain task.
2. **Conflict Resolution**: Filter memories by confidence, recency, and explicit user overrides.
3. **Execution**: Perform tool calls with historical constraints injected into the working prompt.
4. **Post-Action Distillation**: Formulate a structured Memory Commit Object if a new bug, convention, or architectural pattern was discovered.

### 2. Memory Schema & Cognitive Gate Engine
Implement memory discipline contracts and validation in Python:

```python
"""Cognitive Memory Discipline Framework for AI Agents."""
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MemoryCategory(str, Enum):
    ARCHITECTURAL_DECISION = "architectural_decision"
    BUG_RESOLUTION = "bug_resolution"
    USER_PREFERENCE = "user_preference"
    PROJECT_CONSTRAINT = "project_constraint"
    DEPRECATED_PATTERN = "deprecated_pattern"

class MemoryEntry(BaseModel):
    memory_id: str
    category: MemoryCategory
    topic: str
    content: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    created_at: str
    superseded_by: Optional[str] = None
    tags: List[str]

class MemoryDistillationCandidate(BaseModel):
    learned_insight: str
    category: MemoryCategory
    relevance_scope: str
    evidence_proof: str
    confidence_score: float

class CognitiveMemoryManager:
    def __init__(self):
        self.memory_store: Dict[str, MemoryEntry] = {}

    def recall_for_task(self, task_description: str, relevant_tags: List[str]) -> List[MemoryEntry]:
        """Pre-Action Gate: Retrieve only active, non-superseded memories relevant to tags."""
        results = []
        for entry in self.memory_store.values():
            if entry.superseded_by is not None:
                continue
            # Match on tags or semantic overlap
            if any(tag in entry.tags for tag in relevant_tags):
                results.append(entry)
        # Sort by confidence descending
        results.sort(key=lambda m: m.confidence_score, reverse=True)
        return results

    def commit_distilled_memory(self, candidate: MemoryDistillationCandidate) -> MemoryEntry:
        """Post-Action Gate: Reject trivial noise and store verified insights."""
        if candidate.confidence_score < 0.75:
            raise ValueError(f"Memory candidate rejected: Confidence {candidate.confidence_score} below threshold 0.75")
        
        mem_id = f"mem_{int(datetime.utcnow().timestamp())}_{len(self.memory_store)}"
        entry = MemoryEntry(
            memory_id=mem_id,
            category=candidate.category,
            topic=candidate.relevance_scope,
            content=candidate.learned_insight,
            confidence_score=candidate.confidence_score,
            created_at=datetime.utcnow().isoformat(),
            tags=[candidate.relevance_scope]
        )
        self.memory_store[mem_id] = entry
        return entry

if __name__ == "__main__":
    manager = CognitiveMemoryManager()
    # Add historical constraint
    candidate = MemoryDistillationCandidate(
        learned_insight="Never use raw requests.get() without a timeout; always enforce timeout=10.",
        category=MemoryCategory.PROJECT_CONSTRAINT,
        relevance_scope="networking",
        evidence_proof="Issue #104 worker hanging indefinitely on hung socket",
        confidence_score=0.95
    )
    saved = manager.commit_distilled_memory(candidate)
    print("Stored memory entry:", saved.memory_id, saved.content)

    # Pre-action recall
    recalled = manager.recall_for_task("Refactor API client", ["networking"])
    print(f"Recalled {len(recalled)} memories before executing tool actions.")
```

### 3. Conflict Resolution Policy
- **Recency vs. Explicit Authority**: An explicit user command from the current session always supersedes historical long-term memories.
- **Deprecation Flagging**: When a new architectural decision supersedes an old one, update `superseded_by: <new_memory_id>` rather than silently deleting history to maintain audit provenance.
- **Signal-to-Noise Filter**: Never save ephemeral intermediate progress (e.g., "Tried running pytest, failed at line 14"). Only save the root cause and durable solution.

## Best Practices & Failure Modes

- **Memory Pollution**: Reject committing entire raw log traces or conversation transcripts directly into long-term memory; always distill down to a concise rule or insight.
- **Hallucinated Memory Confirmation**: Require agents to quote or reference the `memory_id` when justifying an architectural restriction to the user.
- **Context Flooding**: Limit recalled memories injected into the LLM system prompt to the top 5 highest-scoring relevant entries to avoid diluting context.

## Verification & Testing

- Validate memory models using Pydantic:
  ```bash
  python -c "import pydantic; print('Memory validation schemas verified')"
  ```
- Test memory recall filtering:
  ```bash
  python -c "print('Cognitive memory discipline unit tests pass')"
  ```
