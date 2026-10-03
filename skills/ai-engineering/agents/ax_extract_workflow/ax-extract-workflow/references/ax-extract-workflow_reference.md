# Artifact Lineage & Workflow Reconstruction Technical Reference

## 1. Git Revision Forensics & Graph Traversal

A software repository's git commit DAG encodes the historical trajectory of implementation decisions:

```
[ Root Commit ] ---> [ Commit A: RFC & Schema ] ---> [ Commit B: Core Model ]
                                                             |
                                                             +---> [ Commit C: Fix ] ---> [ HEAD ]
```

### Forensic Anchors:
1. **Commit Hash Anchor**: Explicit SHA pointing directly to a mutation bundle.
2. **File Mutation History**: Utilizing `git log --follow --patch <path>` to trace revisions across file renames and structural refactorings.
3. **Diffstat Metrics**: Quantifying implementation surface area (insertions, deletions, affected subsystems).

---

## 2. Transcript & Event Trace Correlation

When autonomous coding agents execute workflows, raw git commits capture only the output state, not the intermediary reasoning or discarded attempts.

### Multi-Source Data Alignment:
- **Git Commits**: Ground truth code mutations and author metadata.
- **Session Transcripts**: Agent thought process, user intent clarifications, rejected alternatives.
- **Tool Traces**: Executed shell commands, compiler errors, unit test exit codes.

Aligning timestamps across these three sources yields an accurate timeline of problem-solving paths versus dead ends.

---

## 3. Standard Reproduction Recipe Structure

Extracted workflows must be formatted according to standard operational specifications:
1. **Prerequisites & Environment**: Runtime versions, dependencies, and environment configurations.
2. **Phase 1: Architecture & Contract Definition**: The foundational interfaces and schemas.
3. **Phase 2: Progressive Implementation**: Logical units in dependency order.
4. **Phase 3: Validation & Gate Checks**: Exact test commands and passing criteria.
5. **Phase 4: Defect Resolution**: Known pitfalls encountered during development and how they were resolved.
