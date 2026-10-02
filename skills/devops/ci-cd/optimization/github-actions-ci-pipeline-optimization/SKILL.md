---
name: github-actions-ci-pipeline-optimization
description: "Use this skill when auditing, accelerating, and optimizing GitHub Actions CI/CD workflows. It guides the agent through dependency caching strategies (actions/cache), matrix test parallelization, path filtering triggers, Docker layer caching in CI, artifact retention policies, and security hardening (minimal GITHUB_TOKEN permissions)."
domain: devops
category: ci-cd
subcategory: optimization
tags:
  - github-actions
  - ci-cd
  - devops
  - automation
  - workflow-optimization
  - build-speed
technologies:
  - GitHub Actions
  - YAML
  - Docker
  - npm
  - Git
complexity: advanced
maturity: stable
tools:
  - git
  - gh
dependencies:
  - git >= 2.30
  - gh >= 2.20
---
# GitHub Actions CI Pipeline Optimization

## Overview

A guide for auditing, securing, and accelerating GitHub Actions workflows. Slashes CI build times by up to 70%, cuts runner compute costs, eliminates redundant pipeline triggers, and hardens workflow files against supply-chain attacks and privilege escalation.

## When to Use

- CI builds take > 15 minutes, blocking developer pull request merge velocity.
- Workflows run unnecessarily on pure documentation, markdown, or asset edits.
- Dependency installation (`npm install`, `cargo build`, `pip install`) repeats from scratch on every run.
- Auditing repository workflows for GitHub Actions security vulnerabilities and token permissions.

## When NOT to Use

- Managing local git hooks prior to push (use pre-commit).
- Multi-cloud orchestration across non-GitHub CI servers (use Jenkins or GitLab CI).

## Inputs & Prerequisites

- Repository with `.github/workflows/*.yml` workflow definitions.
- Write permissions to modify workflow files.

## Core Workflow

### 1. Intelligent Trigger Filtering (Path Filtering)
Never trigger full build-and-test matrix suites when a developer only modifies a README or documentation:
```yaml
on:
  push:
    branches: [main]
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.gitignore'
  pull_request:
    branches: [main]
    paths:
      - 'src/**'
      - 'package*.json'
      - '.github/workflows/ci.yml'
```

### 2. Dependency & Build Caching
Use cache actions with lockfile content hashes to eliminate redundant downloads:
```yaml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: 'npm' # Built-in caching for package-lock.json

# Or manual caching for heavy compiler artifacts
- name: Cache Cargo Build Artifacts
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/bin/
      ~/.cargo/registry/index/
      ~/.cargo/registry/cache/
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

### 3. Test Matrix Parallelization
Split large test suites across multiple parallel runner nodes:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - name: Run Test Shard
        run: npm test -- --shard=${{ matrix.shard }}/4
```

### 4. Concurrency Cancellation
Cancel stale in-flight workflow runs when a developer pushes new commits to an open PR:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
This frees up runner queues immediately without wasting compute minutes on obsolete commits.

### 5. Security Hardening & Principle of Least Privilege
Set explicit top-level `permissions` to block token theft:
```yaml
# Strict default: read-only access for GITHUB_TOKEN
permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      # Pinned actions to immutable commit SHAs, NOT mutable tags
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Large Docker build in CI | Use `docker/build-push-action` with GitHub Actions cache backend (`cache-from: type=gha`, `cache-to: type=gha,mode=max`). |
| Secret leakage via untrusted PRs | Never run workflows on `pull_request_target` with write permissions or secret access on fork contributions. |
| Cache size limits exceeded (> 10GB per repo) | Prune intermediate compiler build directories and cache only final dependency trees. |

## Validation & Acceptance Criteria

- [ ] Path filters configured to skip CI on documentation-only commits.
- [ ] Concurrency groups cancel superseded pull request runs automatically.
- [ ] Dependencies restored from cache; zero redundant clean installs.
- [ ] Default `permissions: contents: read` enforced at top level of every workflow.
- [ ] External actions pinned to immutable commit SHAs.

## Failure Handling & Recovery

- If cache becomes corrupted, bust the cache by updating the cache key version prefix (e.g. `key: v2-${{ runner.os }}...`).

## Expected Output & Artifacts

- Optimized `.github/workflows/ci.yml` pipeline manifest.
- Pipeline execution time benchmark report (before vs after).

## Related Skills

- `docker-container-optimization`
- `playwright-e2e-testing`
- `github-pr-security-review`
