---
name: handoff
description: "Compact the current multi-turn conversation into a standardized, loss-less handoff document for another agent or successor session."
domain: ai-engineering
category: agents
subcategory: handoff
tags:
  - ai-engineering
  - agents
  - handoff
  - context-compression
  - multi-agent
technologies:
  - Python
  - Markdown
  - Context Distillation
  - Agent Memory
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Agent Session Handoff Architecture Standard

## Overview

The **Handoff** skill provides a formalized methodology and automated tooling for compacting extended, multi-turn AI coding conversations into authoritative handoff briefs. As autonomous agent workflows tackle multi-hour implementations, raw session transcripts accumulate tens of thousands of tokens of intermediate command output, syntax errors, and temporary exploration paths.

This skill equips agents with `HandoffCompiler` to compress large session contexts by up to 20x while rigorously preserving acceptance criteria, discovered architectural invariants, modified file inventories, and the precise next operational step for successor agents.

```
+------------------------------------------------------------------------+
|                         Agent Handoff Pipeline                         |
|                                                                        |
|  [ Extended Conversation History ]                                     |
|                   |                                                    |
|                   v                                                    |
|  [ Invariant & Objective Extractor ]                                   |
|                   |                                                    |
|                   v                                                    |
|  [ Milestone & File State Inventory]                                   |
|                   |                                                    |
|                   v                                                    |
|  [ Directive Action Synthesizer ]                                      |
|                   |                                                    |
|                   v                                                    |
|  [ Compact HANDOFF.md Document ] ---> Ingested by Successor Agent      |
+------------------------------------------------------------------------+
```

## When to Use

- When approaching model context window boundaries and preparing to branch into a clean successor session.
- When transitioning an engineering task between specialized agents (e.g. Architect agent handing off to Implementer agent, or Implementer to QA tester).
- When preparing an end-of-task handover brief for human engineering review.
- When persisting checkpoint state across scheduled asynchronous background workers.

## When NOT to Use

- Short, single-turn interactions or trivial one-line code inquiries.
- When full raw session transcripts are required for compliance or forensic audits without summarization.

## Core Workflow

### 1. Capture Session State Snapshot
Assemble the session's original objective, completed milestones, touched files, and discovered constraints:

```python
from handoff_compiler import HandoffCompiler, SessionState

state = SessionState(
    session_id="sess-worker-402",
    original_objective="Upgrade database client to connection pool and add retry logic.",
    completed_tasks=["Implemented pool manager in src/db.py", "Added exponential backoff"],
    in_progress_task="Authoring unit tests for connection timeout",
    remaining_tasks=["Run integration tests with local Postgres", "Update deployment config"],
    modified_files=["src/db.py", "tests/test_db.py"],
    critical_invariants=["Max connections capped at 20", "Zero plain-text password logging"],
    next_immediate_step="pytest tests/test_db.py -k test_connection_timeout"
)
```

### 2. Compile Compressed Handoff Document
Compile the structured handoff markdown document and evaluate compression ratios:

```python
compiler = HandoffCompiler()
handoff = compiler.compile(state)

print(f"Compression: {handoff.token_compression_ratio}x")
print(f"Output Tokens: ~{handoff.output_estimated_tokens}")

with open("HANDOFF.md", "w", encoding="utf-8") as f:
    f.write(handoff.handoff_markdown)
```

### 3. Bootstrap Successor Agent
Initialize the successor agent session with `HANDOFF.md` prepended as its operational context.

## Verification & Testing

Execute the handoff compilation verification suite to test markdown generation and compression metrics:

```bash
python scripts/handoff_helper.py
```

Expected output:
- Session state distilled into standardized handoff document.
- Compression ratio exceeds 10x with zero invariant loss.
- Status returned cleanly.
