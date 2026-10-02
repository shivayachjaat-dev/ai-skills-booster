---
name: github-pr-review-feedback-resolver
description: "Use this skill when processing, triage-categorizing, and systematically addressing code review feedback and comments on pull requests. It guides the agent through parsing inline diff suggestions, verifying requested changes locally with test suites, pushing atomic fix commits, replying to reviewers with context, and resolving comment threads."
domain: software-engineering
category: code-review
subcategory: pr-feedback
tags:
  - code-review
  - pull-request
  - github
  - git
  - collaboration
  - developer-experience
technologies:
  - GitHub API
  - Git
  - Python
  - Bash
complexity: intermediate
maturity: stable
tools:
  - gh
  - git
  - python
dependencies:
  - git >= 2.30.0
  - gh >= 2.40.0
---
# GitHub Pull Request Review Feedback Resolution Workflow

## Overview

A definitive software engineering standard for processing, implementing, and verifying code review feedback on GitHub pull requests. Effectively responding to code reviews requires more than applying mechanical suggestions; it demands understanding reviewer intent, testing side-effects locally, crafting atomic fixup commits, providing clear technical rationale for trade-offs, and marking comment threads resolved. This skill instructs AI agents on handling code review iterations systematically.

## When to Use

- Addressing reviewer comments and suggestions on open GitHub pull requests.
- Evaluating whether requested refactors break existing unit or integration tests.
- Formulating respectful, technically grounded rebuttals when a reviewer's suggestion has unintended drawbacks.
- Automating review comment triage and resolution via GitHub CLI (`gh`).

## When NOT to Use

- Creating new features from scratch before a pull request exists.
- Reviewing other developers' pull requests (use `github-pr-security-review`).

## Inputs & Prerequisites

- Local git branch tracking the open pull request.
- GitHub CLI (`gh`) authenticated with repository write access.
- Test suite configured locally to verify fixes before pushing.

## Core Workflow

### 1. Fetching Review Comments via GitHub CLI
Inspect pending review comments and unresolved review threads:

```bash
# View PR status and review comments
gh pr view --comments

# Fetch unresolved review discussion threads as structured JSON
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          comments(first: 5) {
            nodes {
              id
              path
              line
              body
              author { login }
            }
          }
        }
      }
    }
  }
}' -F owner='company-org' -F repo='app' -F pr=142
```

### 2. Review Comment Triage & Decision Matrix
Classify feedback into 4 actionable buckets:

1. **Typo / Formatting / Style**: Apply immediately without discussion.
2. **Bug / Edge Case**: Implement fix, add regression unit test, commit with clear message.
3. **Architectural Suggestion with Trade-offs**: Analyze impact; if agreeing, refactor; if disagreeing, present polite empirical evidence (benchmarks, complexity analysis).
4. **Out of Scope (Scope Creep)**: Acknowledge validity, create a separate tracking issue, and link it in the reply.

### 3. Pushing Fixes & Replying to Comments
Apply changes, run local test suite, push commits, and reply to threads:

```bash
# 1. Verify fix locally before pushing
pytest tests/
npm run typecheck

# 2. Commit atomic fix
git add src/payments.py tests/test_payments.py
git commit -m "fix(payments): handle null currency code in invoice calculation"

# 3. Push to PR branch
git push origin feature/payments-upgrade

# 4. Reply to specific review thread on GitHub
gh pr comment 142 --body "Addressed in commit $(git rev-parse --short HEAD). Added unit test covering null currency codes."
```

## Best Practices & Failure Modes

1. **Force-Pushing during Active Reviews**: Force-pushing (`git push --force`) wipes reviewer inline comment context from the GitHub UI, making it impossible for reviewers to see what changed between review rounds. Push incremental commits during review; squash-and-merge at the very end.
2. **Resolving Threads Without Replying**: Resolving a reviewer's comment without an explanation or commit reference leaves the reviewer wondering if their concern was addressed or ignored. Always comment with the commit SHA before resolving.
3. **Blindly Accepting Broken Suggestions**: GitHub's "Apply suggestion" button does not run test suites. Applying a suggestion that has a subtle syntax error or breaks type checking fails CI immediately. Always pull and run tests locally.

## Verification & Testing

- Check that all review threads are addressed and CI passes:
  ```bash
  gh pr checks
  # All status checks must report PASS
  ```
