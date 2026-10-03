---
name: ditto
description: "Mine and update a private, evidence-backed developer profile from local Claude Code, Gemini, Copilot, or OpenCode sessions."
domain: ai-engineering
category: agents
subcategory: ditto
tags:
  - ai-engineering
  - agents
  - developer-profiling
  - privacy
  - behavioral-analytics
technologies:
  - Python
  - Bash
  - JSON Schema
  - Regex Sanitization
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Ditto Architecture & Implementation Standard

## Overview

The **Ditto** skill establishes an enterprise standard for mining, maintaining, and synthesizing privacy-preserving developer work profiles from local AI coding tool sessions. As developers collaborate with conversational coding agents (such as Claude Code, GitHub Copilot CLI, Gemini, and OpenCode), significant signal regarding preferred architectural styles, testing patterns, and language proficiencies is generated.

Ditto ingests local interaction transcripts, executes deterministic credential redaction, extracts behavioral metrics (including Test-Driven Development indices and tool frequencies), and generates an evidence-backed persona without exfiltrating private code or API tokens.

```
+------------------------------------------------------------------------+
|                         Ditto Mining Pipeline                          |
|                                                                        |
|  [ Transcript Ingestion ]   ---> Reads local coding agent event logs   |
|                                           |                            |
|                                           v                            |
|  [ Secret Sanitization ]    ---> Strips API keys, passwords, and tokens|
|                                           |                            |
|                                           v                            |
|  [ Behavioral Profiling ]   ---> Calculates TDD index & command ratios |
|                                           |                            |
|                                           v                            |
|  [ Persona Synthesis ]      ---> Emits structured developer profile    |
+------------------------------------------------------------------------+
```

## When to Use

- When tailoring autonomous AI agent prompts to match a developer's specific coding conventions and preferences.
- When generating evidence-backed developer summaries from local engineering history.
- When evaluating test-driven discipline and command-line tool usage patterns.
- When team onboarding requires understanding local repo conventions without manual surveys.

## When NOT to Use

- When operating on shared public CI environments where session logs belong to multiple anonymous contributors.
- When handling unredacted HIPAA, PCI, or strictly confidential production databases without prior data governance authorization.

## Core Workflow

### 1. Ingest and Sanitize Agent Session Logs
Load raw interaction events from local session transcripts and pass them through Ditto's redaction filter:

```python
from ditto_profiler import DittoProfiler

profiler = DittoProfiler()
raw_events = [
    {"event_type": "command", "content": "git commit -m 'feat: auth'"},
    {"event_type": "file_edit", "content": "Updated src/services/user_service.py"},
    {"event_type": "command", "content": "pytest tests/ --cov=src"}
]
profiler.ingest_session_events(raw_events)
```

### 2. Extract Behavioral Metrics & Archetype
Execute the profiling engine to compute developer archetypes and language affinities:

```python
profile = profiler.extract_profile()
print(f"Developer Archetype: {profile.archetype}")
print(f"Primary Languages: {profile.primary_languages}")
print(f"TDD Index: {profile.work_metrics['tdd_ratio']}")
```

### 3. Persist Local Developer Profile
Export the sanitized profile for consumption by IDE extensions or agent custom instructions:

```python
import json

with open(".ditto-profile.json", "w", encoding="utf-8") as f:
    json.dump(profile.__dict__, f, indent=2)
```

## Verification & Testing

Execute the profile mining verification suite to validate redaction and archetype calculation:

```bash
python scripts/ditto_helper.py
```

Expected output:
- Credential redaction verified with zero secret disclosure.
- Archetype computed successfully.
- Operational status returned cleanly.
