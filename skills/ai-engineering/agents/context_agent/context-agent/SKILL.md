---
name: context-agent
description: "Use this skill to manage persistent session continuity, memory checkpointing, and cold-start briefing restoration across autonomous agent lifecycles. It compresses turn history, records architectural decisions and pending task states, and generates high-density initialization briefings without token dilution."
domain: ai-engineering
category: agents
subcategory: context_agent
tags:
  - session-continuity
  - agent-memory
  - context-checkpointing
  - memory-compaction
  - cold-start-briefing
  - task-state-persistence
technologies:
  - Python
  - SQLite
  - JSON
  - Markdown
  - Tokenizer
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

# Agent Session Continuity & Context Memory Standard

## Overview

The `context-agent` skill establishes the operational framework, state serialization schema, and briefing protocols for preserving context across autonomous agent sessions. In long-running development workflows, agents frequently hit context limits or are restarted in fresh processes. Without structured continuity management, newly launched agents suffer from cold-start amnesia: repeating already resolved errors, re-investigating previously decided architectural trade-offs, and losing track of unfinished tasks. This skill provides automated session checkpointing, structured `MEMORY.md` updates, and high-density initialization briefings.

```
+-----------------------------------------------------------------------------------+
|                        Agent Context Continuity Lifecycle                         |
|                                                                                   |
|  [ Concluding Agent Session ]                                                     |
|         |                                                                         |
|         v                                                                         |
|  [ Extract Session Delta ]                                                        |
|    - Architectural decisions locked in                                            |
|    - Modified file set (`git diff --name-only`)                                   |
|    - Unresolved errors & next steps                                               |
|         |                                                                         |
|         v                                                                         |
|  [ Context Compaction & Checkpoint Store ]                                        |
|    - Persist structured JSON snapshot to `.gemini/context_store.db`               |
|    - Append high-level milestones to `MEMORY.md`                                  |
|         |                                                                         |
|         v                                                                         |
|  [ Fresh Agent Session Start (Cold Start) ]                                       |
|         |                                                                         |
|         v                                                                         |
|  [ Inject High-Density Initialization Briefing ]                                  |
|    - Immediate awareness of current state without reading 100k raw tokens         |
|    - Seamless resumption of in-flight task queue                                  |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When concluding an agent session and preserving critical decisions, open bugs, and next steps for the next session.
- When starting a new session on an active project and restoring situational awareness without full context re-hydration.
- When an agent is approaching its context window budget and must compact historical turns into a durable summary.
- When multiple autonomous agents collaborate asynchronously across time boundaries.

## When NOT to Use

- For short, self-contained single-turn queries (e.g. "What is the syntax for a Python generator?").
- As a substitute for standard git version control (git commits track code; `context-agent` tracks intent, decisions, and uncommitted hypotheses).
- Storing high-security secrets, private keys, or passwords.

---

## Inputs & Prerequisites

1. **Session Artifacts**: Active chat trajectory, list of modified files, and user directives.
2. **Persistent Store Path**: Local checkpoint directory (e.g. `.context/` or `.gemini/`).
3. **Token Budget Target**: Maximum allowable tokens for cold-start briefings (default: $< 1200$ tokens).

---

## Core Workflow

### Step 1: Session State Extraction & Structuring
Extract the key delta elements from the current session:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class SessionCheckpoint:
    session_id: str
    timestamp: str
    decisions: List[str]
    modified_files: List[str]
    pending_tasks: List[str]
    unresolved_errors: List[str]
    technical_discoveries: List[str] = field(default_factory=list)
```

### Step 2: High-Density Initialization Briefing Synthesis
Generate a compact briefing tailored for cold-start injection:

```python
def generate_initialization_briefing(checkpoint: SessionCheckpoint) -> str:
    """Formats the latest checkpoint into a high-density cold-start briefing."""
    doc = [
        f"# Session Briefing: Resume State for {checkpoint.session_id}",
        f"**Checkpoint Timestamp**: {checkpoint.timestamp}",
        "",
        "## 1. Locked Architectural Decisions",
    ]
    for dec in checkpoint.decisions:
        doc.append(f"- {dec}")
        
    doc.append("\n## 2. Modified Working Files")
    for f in checkpoint.modified_files:
        doc.append(f"- `{f}`")
        
    doc.append("\n## 3. Active In-Flight Tasks (Pending)")
    for task in checkpoint.pending_tasks:
        doc.append(f"- [ ] {task}")
        
    if checkpoint.unresolved_errors:
        doc.append("\n## 4. Known Blockers & Unresolved Errors")
        for err in checkpoint.unresolved_errors:
            doc.append(f"- [!] {err}")
            
    return "\n".join(doc)
```

### Step 3: Rolling Memory Compaction
Prune older checkpoints when the archive exceeds storage limits, consolidating historic logs into permanent milestone records.

---

## Best Practices & Failure Modes

- **Never Log Secrets**: Scrub all API tokens, bearer keys, and environment passwords before serializing context checkpoints to disk.
- **Strict Token Limits**: Keep cold-start briefings under 1200 tokens. Bloated briefings defeat the purpose of session continuity.
- **Atomic File Writing**: Write checkpoints to temporary files before atomically renaming to prevent corruption if a process terminates abruptly.

---

## Verification & Testing

1. Run the session continuity manager test suite:
   ```bash
   python scripts/context-agent_helper.py
   ```
2. Verify checkpoint creation, briefing formatting, and compaction via CLI:
   ```bash
   python scripts/session_continuity_manager.py --test-all
   ```
