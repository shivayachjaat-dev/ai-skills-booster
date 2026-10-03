---
name: git-pr-workflows-git-workflow
description: "Orchestrate review, tests, conventional commits, branch pushes, and pull-request creation with parallel agent gates."
domain: ai-engineering
category: agents
subcategory: git_pr_workflows_git
tags:
  - ai-engineering
  - agents
  - git
  - pull-requests
  - conventional-commits
technologies:
  - Git
  - Python
  - Bash
  - GitHub CLI
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Git PR Workflows & Guarded Merge Standard

## Overview

The **Git PR Workflows** skill establishes an authoritative standard for preparing, validating, and submitting code changes authored by autonomous agents. Without strict version control guardrails, automated agents can commit directly to protected branches, write vague commit messages, introduce unverified changes, or omit test evidence.

This skill equips agents with `GitPROrchestrator` to enforce branch naming conventions, format Conventional Commits, synthesize comprehensive Markdown pull request briefs, and verify pre-commit quality gates before creating remote pull requests.

```
+------------------------------------------------------------------------+
|                         Git PR Workflow Pipeline                       |
|                                                                        |
|  [ Branch Validation ]     ---> Enforces feat/*, fix/* prefix syntax   |
|                                           |                            |
|                                           v                            |
|  [ Quality Gate Execution] ---> Verifies unit tests & linting pass     |
|                                           |                            |
|                                           v                            |
|  [ Conventional Commits ]  ---> Validates type(scope): message format  |
|                                           |                            |
|                                           v                            |
|  [ PR Body Synthesis ]     ---> Compiles summary, test proof & safety  |
|                                           |                            |
|                                           v                            |
|  [ Guarded Merge & Gate ]  ---> Dispatches PR via gh CLI or remote push|
+------------------------------------------------------------------------+
```

## When to Use

- When an autonomous agent completes an assigned feature, bugfix, or refactoring task and needs to package it into a pull request.
- When standardizing conventional commit messaging across multi-agent workflows.
- When validating branch names and generating audit-ready PR descriptions with test verification evidence.
- When integrating automated CI merge gates that require structured pull request metadata.

## When NOT to Use

- Ad-hoc local scratch experiments or temporary prototypes in isolated throwaway workspaces.
- Git administrative actions like force-pushing rewritten histories to protected branches.

## Core Workflow

### 1. Configure PR Metadata & Branch
Assemble metadata including the branch name, commit messages, touched files, and test output:

```python
from git_pr_orchestrator import GitPROrchestrator, PRMetadata

orchestrator = GitPROrchestrator()
meta = PRMetadata(
    branch_name="feat/user-jwt-auth",
    target_branch="main",
    title="feat(auth): add JWT authentication with asymmetric RS256 keys",
    commit_messages=[
        "feat(auth): implement JWT RS256 token verification middleware",
        "test(auth): add unit test coverage for expired tokens"
    ],
    touched_files=["src/auth/jwt.py", "tests/test_jwt.py"],
    test_results_summary="All 18 unit tests passed cleanly in 0.54s."
)
```

### 2. Validate Quality Gates & Synthesize PR
Validate that branch and commit strings comply with standards and generate the structured PR markdown:

```python
report = orchestrator.synthesize_pr(meta)
if not report.is_valid:
    raise ValueError(f"PR Validation failed: {report.validation_errors}")

print(f"Generated PR Body:\n{report.pr_markdown_body}")
```

### 3. Create Remote Pull Request
Dispatch the pull request to the remote repository using GitHub CLI or Git API:

```bash
gh pr create --base main --head feat/user-jwt-auth --title "feat(auth): add JWT auth" --body-file pr_description.md
```

## Verification & Testing

Execute the Git PR workflow verification suite to test branch regex matching, conventional commit validation, and PR synthesis:

```bash
python scripts/git-pr-workflows-git-workflow_helper.py
```

Expected output:
- Branch names and commit messages validated cleanly.
- PR markdown body synthesized with test evidence checklist.
- Status returned cleanly.
