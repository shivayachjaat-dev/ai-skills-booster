---
name: ax-extract-workflow
description: "Use this skill to inspect, reverse-engineer, and reconstruct the complete development workflow behind an existing software artifact, commit, or pull request. It analyzes git revision DAGs, commit deltas, agent tool-execution traces, and session transcripts to synthesize an authoritative operational lineage and reproducibility guide."
domain: ai-engineering
category: agents
subcategory: ax_extract_workflow
tags:
  - workflow-extraction
  - session-reconstruction
  - git-forensics
  - artifact-lineage
  - agent-observability
  - commit-analysis
technologies:
  - Python
  - Git
  - SQLite
  - JSONL
  - Regex
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

# Autonomous Workflow Reconstruction & Provenance Standard

## Overview

The `ax-extract-workflow` skill provides the methodology, tooling, and analytical procedures for reconstructing the exact sequence of engineering decisions, tool invocations, prompts, and code mutations that produced a specific software artifact (e.g. a pull request, feature commit, benchmark result, or architecture document). When teams or agents inherit complex legacy code or unfamiliar automated contributions, understanding *how* and *why* a change was made is critical for debugging, auditing, and continuous learning. This skill enables agents to inspect version control history, session logs, and tool execution traces to generate an authoritative "How this was built" reproduction guide.

```
+-----------------------------------------------------------------------------------+
|                        Workflow Reconstruction Pipeline                           |
|                                                                                   |
|  [ Anchor Input ] (Commit SHA, File Path, PR Number, or Date Window)              |
|         |                                                                         |
|         v                                                                         |
|  [ Git Revision Forensics ]                                                       |
|    - Commit log, diffstat, patch analysis, and parent DAG traversal               |
|         |                                                                         |
|         v                                                                         |
|  [ Session & Trace Correlation ]                                                  |
|    - Transcript logs, tool invocation records, test output captures               |
|         |                                                                         |
|         v                                                                         |
|  [ Action Chronology Synthesis ]                                                  |
|    1. Initial Exploration / Spec Phase                                            |
|    2. Core Implementation & Refactoring Passes                                    |
|    3. Verification & Bugfix Loop Cycles                                           |
|         |                                                                         |
|         v                                                                         |
|  [ Structured Reproduction Specification (specs/<artifact>_lineage.md) ]          |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When an engineer or user asks: "How was feature X built?", "What prompts or tools created this module?", or "Extract the workflow behind commit Y."
- When conducting post-mortem root-cause analysis on an automated agent regression.
- When creating reproducible step-by-step tutorials from a completed implementation.
- When extracting reusable agent workflow patterns from successful complex sessions.

## When NOT to Use

- For routine git log queries (e.g. `git log -n 5`) where a simple shell command suffices.
- When inspecting prospective plans for unbuilt software (use `ai-loop` or `plan` instead).
- When session or version control records have been purged and no trace evidence exists.

---

## Inputs & Prerequisites

1. **Target Artifact Anchor**: One or more of: Commit SHA, file path, branch name, or ISO timestamp.
2. **Access to Local Git Repository**: Initialized Git repository with reachable commit history.
3. **Session / Transcript Traces (Optional)**: JSONL execution logs or tool call records.

---

## Core Workflow

### Step 1: Resolve Target Anchor & Extract Git History
Extract the commit timeline, touched files, and diff statistics for the target anchor:

```python
import subprocess
from typing import List, Dict, Any

def extract_commit_lineage(anchor_sha: str, depth: int = 5) -> List[Dict[str, str]]:
    """Retrieves commit metadata and diff stats for a given git commit SHA."""
    cmd = ["git", "log", f"-n", str(depth), "--pretty=format:%H|%an|%ad|%s", "--date=iso", anchor_sha]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    commits = []
    for line in res.stdout.strip().splitlines():
        if not line:
            continue
        sha, author, date, subject = line.split("|", 3)
        commits.append({
            "sha": sha,
            "author": author,
            "date": date,
            "subject": subject
        })
    return commits
```

### Step 2: Chronological Action & Decision Mapping
Correlate git patches with tool actions (file writes, test executions, lint passes) into discrete phases:

```python
def synthesize_workflow_phases(commits: List[Dict[str, str]]) -> Dict[str, Any]:
    """Groups linear commit history into logical workflow phases."""
    phases = {
        "planning_and_spec": [],
        "implementation": [],
        "verification_and_hardening": []
    }
    
    for c in reversed(commits):
        sub = c["subject"].lower()
        if any(w in sub for w in ["test", "verify", "fix", "lint", "harden"]):
            phases["verification_and_hardening"].append(c)
        elif any(w in sub for w in ["spec", "doc", "design", "plan", "rfc"]):
            phases["planning_and_spec"].append(c)
        else:
            phases["implementation"].append(c)
            
    return phases
```

### Step 3: Emit Reproducibility Markdown Specification
Format the extracted findings into a structured report documenting:
1. Executive objective and scope.
2. Chronological step-by-step sequence of changes.
3. Key architectural decisions and trade-offs made.
4. Exact verification commands used to validate the output.

---

## Best Practices & Failure Modes

- **Missing Commit Context**: If squashed commits obscure the iteration history, inspect reflog or session transcript traces if available.
- **Hallucinating Intent**: Never invent reasons for code changes that are not supported by commit messages, PR descriptions, or diff content. State observed facts and qualify inferences.
- **Secret Scrubbing**: Before including tool call logs or diff snippets in the reconstructed workflow, verify that no credentials or private tokens are exposed.

---

## Verification & Testing

1. Run the workflow reconstruction engine self-tests:
   ```bash
   python scripts/ax-extract-workflow_helper.py
   ```
2. Reconstruct the lineage of recent repository commits:
   ```bash
   python scripts/workflow_reconstruction_engine.py --test-all
   ```
