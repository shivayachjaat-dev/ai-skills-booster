---
name: secret-leak-detection-and-remediation
description: "Use this skill when detecting, containing, revoking, and purging secrets committed to Git repositories or build artifacts. It guides the agent through scanning history with TruffleHog/Gitleaks, executing emergency credential revocation, rewriting Git history with git-filter-repo, and installing pre-commit guardrails."
domain: security
category: secret-management
subcategory: detection
tags:
  - security
  - secrets
  - git
  - credential-hygiene
  - devsecops
  - incident-response
technologies:
  - Git
  - Gitleaks
  - TruffleHog
  - git-filter-repo
complexity: advanced
maturity: stable
tools:
  - git
  - gitleaks
  - python
dependencies:
  - git >= 2.30
---
# Secret Leak Detection and Remediation

## Overview

An emergency incident response and prevention workflow for handling exposed API keys, private tokens, passwords, and private cryptographic certificates. Instructs AI agents on rapid containment, credential revocation, surgical Git commit history rewriting, and configuring pre-commit blocking hooks.

## When to Use

- A developer or agent accidentally commits an `.env` file, private key, or API token to Git.
- An alert is received from GitHub Secret Scanning, GitGuardian, or an external cloud provider.
- Auditing repository history prior to open-sourcing a private codebase.
- Setting up pre-commit validation to block secret commits at the developer terminal.

## When NOT to Use

- Routine runtime environment variable configuration (use `environment-configuration-management`).
- General source code vulnerability scanning (use `github-pr-security-review`).

## Inputs & Prerequisites

- Git repository with write access to rewrite branches.
- Inventory of leaked secret identifiers (key name, token prefix, file path, commit hash).
- Credentials to access cloud provider console for immediate token revocation.

## Core Workflow

### 1. Immediate Containment & Key Revocation (PRIORITY ZERO)
> NEVER assume a leaked key was not scraped. Automated public scrapers consume exposed keys within 10 to 60 seconds of a push.

1. **Identify the exact secret**: Determine provider (AWS, Stripe, OpenAI, GitHub, Database).
2. **Revoke immediately**:
   - Access the provider dashboard or CLI.
   - Deactivate or delete the compromised credential.
   - Generate a fresh credential and deploy it to secure secrets managers (AWS Secrets Manager, HashiCorp Vault, GitHub Secrets).
3. **Audit Access Logs**: Check cloud audit logs (AWS CloudTrail, Stripe Audit Logs) for unauthorized actions taken during the window of exposure.

### 2. Comprehensive Repository Secret Audit
Scan entire repository and commit history using Gitleaks:
```bash
gitleaks detect --source . --verbose --report-path gitleaks-report.json
```
Review detected instances to classify true positives vs test mock strings.

### 3. Surgical Git History Purge
> Standard `git rm` or a new commit does NOT remove secrets from Git history. The secret remains fully accessible in historical commit objects.

Use `git-filter-repo` to permanently eradicate the file or secret string from all branches and tags:
```bash
# Option A: Purge an entire file across all historical commits
git filter-repo --path .env --invert-paths --force

# Option B: Replace a specific secret token with a redacted placeholder
echo "LEAKED_SECRET_STRING==>REDACTED_SECRET" > replace.txt
git filter-repo --replace-text replace.txt --force
```

### 4. Remote Force Push & Team Synchronization
1. Force push the rewritten history to the remote repository:
   ```bash
   git push origin --force --all
   git push origin --force --tags
   ```
2. Instruct all team members to re-clone the repository or reset local tracking branches to prevent accidentally re-pushing orphaned commits containing the secret.

### 5. Automated Prevention Guardrails
Install pre-commit hook preventing future secret commits:
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Secret was pushed to a public repository | Treat the key as completely compromised. Immediately invalidate it. Do NOT waste time rewriting history before revoking the key. |
| Leaked credential is a root or primary database password | Schedule immediate maintenance window to update connection strings across all running services before changing DB password. |
| Pull request contains secret | Close the PR, delete the branch on the remote fork, and revoke the secret immediately. |

## Validation & Acceptance Criteria

- [ ] Compromised secret is fully revoked at the service provider.
- [ ] Cloud provider audit logs verified for unauthorized calls.
- [ ] `gitleaks detect --source .` reports 0 detected secrets across full history.
- [ ] Pre-commit hook active in local repository.
- [ ] Fresh credentials deployed exclusively via secrets management.

## Failure Handling & Recovery

- If Git history rewriting breaks existing open PRs, rebase active branches onto the newly filtered `main` branch.

## Expected Output & Artifacts

- Incident report detailing exposure timeline, revocation confirmation, and audit findings.
- Clean Git repository with zero historical trace of the secret.
- Active pre-commit guardrail configuration.

## Related Skills

- `github-pr-security-review`
- `dependency-vulnerability-audit`
- `container-security-hardening`
