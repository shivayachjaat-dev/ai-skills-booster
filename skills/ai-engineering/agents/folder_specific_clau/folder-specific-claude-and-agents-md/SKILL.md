---
name: folder-specific-claude-and-agents-md
description: "Generate and maintain folder-scoped CLAUDE.md and AGENTS.md instruction files to provide specialized guidance for agents working in specific subsystems."
domain: ai-engineering
category: agents
subcategory: folder_specific_clau
tags:
  - ai-engineering
  - agents
  - monorepo
  - claude-md
  - agents-md
technologies:
  - Markdown
  - Python
  - Monorepo Architecture
  - Polyglot Toolchains
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Folder-Specific CLAUDE.md & AGENTS.md Standard

## Overview

The **Folder-Specific CLAUDE.md and AGENTS.md** skill provides an enterprise standard and automation harness for scoping AI agent operating instructions to specific directories, packages, or microservices within a repository. Monolithic root guidance files fail in polyglot monorepos where different subsystems have conflicting languages, test harnesses, and architecture boundaries.

This skill equips agents with `FolderGuidanceGenerator` to automatically detect subsystem tech stacks (e.g. TypeScript/React vs Python/FastAPI vs Rust), construct localized `AGENTS.md` and `CLAUDE.md` files, and enforce hierarchical inheritance rules that protect global repo invariants.

```
+------------------------------------------------------------------------+
|                     Folder Guidance Architecture                       |
|                                                                        |
|  [ Subsystem Probe ]      ---> Detects build tool, test runners & AST  |
|                                           |                            |
|                                           v                            |
|  [ Invariant Extraction ] ---> Identifies local architectural rules    |
|                                           |                            |
|                                           v                            |
|  [ File Synthesis ]       ---> Emits scoped AGENTS.md / CLAUDE.md      |
|                                           |                            |
|                                           v                            |
|  [ Inheritance Check ]    ---> Guarantees root compliance & boundaries |
+------------------------------------------------------------------------+
```

## When to Use

- When operating in monorepos or multi-package codebases with disparate languages (e.g. Next.js web frontend alongside a Rust backend).
- When a subdirectory requires specific localized testing commands (`npm test` vs `cargo test` vs `pytest`).
- When defining subsystem-specific architectural boundaries and prohibited import patterns.
- When minimizing agent context window bloat by loading only relevant local guidelines.

## When NOT to Use

- Small, single-language repositories where a single root `AGENTS.md` or `CLAUDE.md` captures all guidelines without ambiguity.
- Temporary or ephemeral scratch directories.

## Core Workflow

### 1. Probe Subsystem Directory
Inspect a package or subdirectory to determine language, build system, and testing runner:

```python
from folder_guidance_generator import FolderGuidanceGenerator

generator = FolderGuidanceGenerator(root_dir=".")
context = generator.probe_directory("packages/frontend-ui")
print(f"Detected: {context.detected_language} | Test Runner: {context.test_command}")
```

### 2. Generate Scoped Instruction Files
Synthesize a localized `AGENTS.md` or `CLAUDE.md` tailored specifically to the target folder:

```python
guidance_path = generator.generate_scoped_agents_md(
    target_dir="packages/frontend-ui",
    format_type="AGENTS.md"
)
print(f"Scoped guidance created: {guidance_path}")
```

### 3. Verify Inherited Boundaries
Ensure the scoped guidance adheres to parent directory constraints while defining strict boundaries:
- Local commands execute within the directory context.
- Cross-boundary imports of private sibling modules are forbidden.
- Root repository security rules (zero secret commits) remain in effect.

## Verification & Testing

Execute the folder guidance test suite to verify stack detection and instruction file generation:

```bash
python scripts/folder-specific-claude-and-agents-md_helper.py
```

Expected output:
- Subsystem directories probed and characterized cleanly.
- Frontend and backend scoped guidance files generated and verified.
- Status returned cleanly.
