---
name: agent-project-memory
description: "Use this skill when designing, maintaining, or recovering persistent memory and architectural context across long-running AI agent sessions. It establishes structured memory stores, state serialization protocols, session recovery checkpoints, and active context pruning to prevent context loss during complex projects."
domain: ai-engineering
category: agents
subcategory: memory
tags:
  - ai-agents
  - agent-memory
  - context-management
  - state-persistence
  - llm-architecture
technologies:
  - Python
  - JSON
  - SQLite
  - Markdown
complexity: advanced
maturity: stable
tools:
  - python
  - sqlite3
dependencies:
  - python >= 3.9
---
# Agent Project Memory

## Overview

Persistent project memory enables AI agents to maintain continuity, recall critical architecture decisions, and retain historical debugging context across long-running development workflows, context window resets, and multi-session collaborations.

## When to Use

- Managing multi-day or multi-agent development projects where context resets are inevitable.
- Capturing Architectural Decision Records (ADRs), user preferences, and dependency constraints.
- Resuming interrupted tasks where an agent must restore prior state, planned tasks, and completed milestones.
- Preventing catastrophic forgetting when agents generate thousands of lines of code across dozens of modules.

## When NOT to Use

- Short, single-turn query responses or ephemeral scratch tasks.
- Static application logging (use standard application logging frameworks like Winston or Loguru).

## Inputs & Prerequisites

- Local filesystem access to write project memory stores (`.gemini/memory/`, `.claude/context/`, or `.agent/memory.json`).
- Schema definition for persistent memory layers: Working Memory, Episodic Memory, and Semantic Project Memory.

## Core Workflow

### 1. Memory Layer Initialization
Establish a three-tier memory architecture in the repository:
```text
.agent/
├── memory/
│   ├── project-brief.json      # Semantic Memory: High-level vision, tech stack, rules
│   ├── decisions-log.jsonl     # Episodic Memory: Immutable append-only log of decisions
│   └── current-state.json      # Working Memory: Active task list, blockers, active branch
```

### 2. State Snapshotting Before Long-Running Operations
Before executing high-context operations (e.g. running 50 tests or large refactors), save the working state:
```json
{
  "timestamp": "2026-10-02T18:00:00Z",
  "active_task": "Refactor auth middleware to JWT v2",
  "completed_subtasks": ["Add token verification test", "Update interface"],
  "next_step": "Replace Express middleware in server.ts",
  "known_risks": ["Session cookies might invalidate existing users"]
}
```

### 3. Progressive Retrieval & Pruning
When restoring context after a session break:
1. Read `project-brief.json` for fixed invariants.
2. Read the last 5 records of `decisions-log.jsonl` to understand recent rationale.
3. Read `current-state.json` to resume the immediate next action.
4. Prune working memory records older than 14 days or compress completed tasks into summary milestones.

### 4. Conflict Resolution & Consistency Checks
If working memory contradicts current code on disk (e.g. code was modified by a human developer between agent runs):
1. Prioritize disk state (source code) as ground truth.
2. Update `current-state.json` to reflect current reality and append an entry to `decisions-log.jsonl` noting the reconciliation.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Memory file exceeds token budget (> 100KB) | Trigger memory summarization: summarize closed tasks and archive historical logs to `.agent/archive/`. |
| Concurrent agent writes | Use atomic write patterns (write to temporary file, then atomic rename) with POSIX file locks. |
| Memory contains sensitive secrets | Immediately redact secrets matching API key / token regexes before persisting to memory files. |

## Validation & Acceptance Criteria

- [ ] `.agent/memory/` structure exists with valid JSON schemas.
- [ ] No plaintext secrets or authorization tokens are persisted.
- [ ] The agent can successfully recover task state after a context restart without re-asking the user for baseline facts.

## Failure Handling & Recovery

- If memory files become corrupted, fall back to parsing `git log -n 10` and recent markdown notes, then regenerate clean memory files.

## Expected Output & Artifacts

- `.agent/memory/project-brief.json`
- `.agent/memory/decisions-log.jsonl`
- `.agent/memory/current-state.json`

## Related Skills

- `context-window-engineering`
- `agent-tool-use-reliability`
- `documentation-and-adrs`
