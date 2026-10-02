---
name: github-actions-reusable-workflows-and-composite-actions
description: "Use this skill when designing, architecting, and standardizing enterprise CI/CD pipelines using GitHub Actions Reusable Workflows (workflow_call) and Composite Actions. It covers modular parameter passing, secret inheritance, matrix job fan-out, action packaging with action.yaml, and cross-repository pipeline governance."
domain: devops
category: continuous-integration
subcategory: github-reusable-workflows
tags:
  - github-actions
  - ci-cd
  - reusable-workflows
  - composite-actions
  - devops
  - automation
technologies:
  - GitHub Actions
  - YAML
  - Git
  - Docker
  - Node.js
complexity: advanced
maturity: stable
tools:
  - gh
  - git
dependencies:
  - github-actions >= 2.0.0
---
# GitHub Actions Reusable Workflows & Composite Actions Standard

## Overview

A definitive production engineering reference for standardizing CI/CD pipelines across enterprise repositories using GitHub Actions Reusable Workflows (`workflow_call`) and Composite Actions. This skill instructs AI agents on DRY pipeline architecture: encapsulating multi-step shell logic into Composite Actions, sharing multi-job release pipelines via Reusable Workflows, handling strict secret inheritance (`secrets: inherit`), and enforcing organization-wide security governance.

## When to Use

- Standardizing build, lint, scan, and deployment stages across dozens or hundreds of microservices.
- Eliminating copy-pasted workflow YAML files that diverge and create maintenance nightmares.
- Packaging multi-step shell commands into a single, clean custom action without publishing to public marketplace.
- Centralizing compliance gates (vulnerability scanning, signed releases) in a secured infrastructure repository.

## When NOT to Use

- Workflows that need to run outside GitHub infrastructure (use GitLab CI, Argo Workflows, or Jenkins).
- Single, unique one-off scripts with zero reuse across other jobs.

## Inputs & Prerequisites

- GitHub organization or repository with GitHub Actions enabled.
- Centralized workflow repository (e.g. `company-org/shared-workflows`).
- Understanding of GitHub Actions context variables (`github`, `inputs`, `secrets`, `matrix`).

## Core Workflow

### 1. Reusable Workflow (`.github/workflows/deploy-service.yaml`)
Define a parameterized workflow triggered via `workflow_call`:

```yaml
# company-org/shared-workflows/.github/workflows/deploy-service.yaml
name: Reusable Deploy Pipeline

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
        description: "Target environment (staging or production)"
      image_tag:
        required: true
        type: string
        description: "Docker image tag to deploy"
    secrets:
      DEPLOY_KEY:
        required: true
        description: "Deployment authentication token"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Validate Deployment Configuration
        run: |
          echo "Validating deployment of ${{ inputs.image_tag }} to ${{ inputs.environment }}"

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Execute Deployment
        env:
          TOKEN: ${{ secrets.DEPLOY_KEY }}
        run: |
          echo "Executing deployment to ${{ inputs.environment }} with tag ${{ inputs.image_tag }}"
```

### 2. Caller Workflow Consuming the Reusable Pipeline
Invoke the reusable workflow from application repositories:

```yaml
# my-app/.github/workflows/release.yaml
name: Release App

on:
  push:
    tags: ['v*']

jobs:
  call-deploy-staging:
    uses: company-org/shared-workflows/.github/workflows/deploy-service.yaml@main
    with:
      environment: staging
      image_tag: ${{ github.ref_name }}
    secrets: inherit

  call-deploy-production:
    needs: call-deploy-staging
    uses: company-org/shared-workflows/.github/workflows/deploy-service.yaml@main
    with:
      environment: production
      image_tag: ${{ github.ref_name }}
    secrets:
      DEPLOY_KEY: ${{ secrets.PROD_DEPLOY_KEY }}
```

### 3. Lightweight Custom Composite Action (`actions/setup-python-deps/action.yaml`)
Bundle repetitive setup steps (checkout, python setup, pip caching) into a composite action:

```yaml
# company-org/shared-workflows/actions/setup-python-deps/action.yaml
name: "Setup Python & Cached Virtualenv"
description: "Configures Python version and restores pip virtualenv cache."

inputs:
  python-version:
    description: "Target Python version"
    required: false
    default: "3.11"

runs:
  using: "composite"
  steps:
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: 'pip'

    - name: Install dependencies
      shell: bash
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
```

## Best Practices & Failure Modes

1. **Unpinned Workflow References**: Calling a reusable workflow via `@main` means any commit to `main` immediately affects production pipelines. Pin reusable workflows to immutable Git commit SHAs (`@a1b2c3d4...`) or release tags (`@v1.2.0`).
2. **Secret Inheritance Hazards (`secrets: inherit`)**: Blindly passing `secrets: inherit` exposes *all* caller repository secrets to the called workflow. For sensitive environments, pass only explicitly named secrets (`secrets: { KEY: secrets.KEY }`).
3. **Environment Secrets Scope**: Secrets defined inside GitHub Environments (e.g. `production`) are only accessible to jobs that explicitly declare `environment: production`.

## Verification & Testing

- Validate workflow syntax locally with `actionlint`:
  ```bash
  actionlint .github/workflows/*.yaml
  ```
- Dry-run workflows using `act`:
  ```bash
  act -n -j deploy
  ```
