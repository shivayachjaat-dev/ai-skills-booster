---
name: github-pr-security-review
description: "Use this skill when reviewing a GitHub pull request for security vulnerabilities, exposed secrets, unsafe dependencies, injection risks, authentication flaws, or insecure CI/CD modifications. It guides the agent through systematic threat modeling, diff inspection, risk severity classification, and remediation generation."
domain: security
category: code-review
subcategory: github
tags:
  - github
  - security
  - pull-request
  - code-review
  - devsecops
technologies:
  - GitHub
  - Git
  - GitHub Actions
complexity: advanced
maturity: stable
tools:
  - git
  - gh
dependencies:
  - git >= 2.30
  - gh >= 2.20
---
# GitHub PR Security Review

## Overview

A structured, defense-in-depth security review workflow for GitHub pull requests. This skill instructs the agent to audit incoming pull requests for exposed secrets, injection vectors, broken authentication or authorization, insecure third-party dependencies, malicious CI/CD workflows, and risky configuration changes before code is merged into protected branches.

## When to Use

- Conducting pre-merge security reviews on any GitHub pull request.
- Reviewing pull requests that modify authentication, authorization, or session logic.
- Reviewing PRs that introduce new external dependencies or bump dependency manifests.
- Reviewing changes to `.github/workflows/`, deployment scripts, or cloud infrastructure definitions.
- Inspecting contributions from external, untrusted, or newly onboarded contributors.

## When NOT to Use

- Pure styling, formatting, or documentation changes where zero executable logic, dependencies, or workflows are touched (use standard `code-review-and-quality`).
- Full external black-box dynamic penetration testing (requires dedicated dynamic DAST tools).
- Live cloud infrastructure compliance audits (use `cloud-infrastructure-compliance-audit`).

## Inputs & Prerequisites

- Git repository checked out locally or accessible via GitHub CLI (`gh`).
- Target branch name and PR branch name, or PR number via `gh pr view <number>`.
- Full diff output obtained via `git diff origin/main...HEAD` or `gh pr diff <number>`.

## Core Workflow

### 1. Diff Scoping & Threat Profiling
1. Extract the complete file list modified in the PR:
   ```bash
   gh pr diff --name-only <PR_NUMBER>
   ```
2. Identify high-risk target files:
   - Workflow files: `.github/workflows/*.yml`
   - Auth/crypto code: `**/auth/**`, `**/crypto/**`, `**/security/**`, `**/tokens/**`
   - Manifests: `package.json`, `Cargo.toml`, `go.mod`, `requirements.txt`, `pom.xml`
   - Infrastructure as Code: `Dockerfile`, `terraform/**`, `k8s/**`, `helm/**`
   - Entry points and routers: `routes/**`, `api/**`, `controllers/**`

### 2. Secret & Credential Detection
Scan the entire diff for high-entropy tokens, private keys, API secrets, and webhook secrets:
- Search for patterns: `Bearer [A-Za-z0-9_-]{20,}`, `BEGIN PRIVATE KEY`, `ghp_`, `AKIA[0-9A-Z]{16}`.
- Verify whether added `.env` or sample configuration files contain real production values.
- Verify that `.gitignore` prevents committing newly introduced local state or credentials.

### 3. Dependency & Supply Chain Verification
For every new or updated dependency:
- Check for typosquatting (e.g. `lodsh` instead of `lodash`, `reqeusts` instead of `requests`).
- Check if version constraints are pinning vulnerable legacy releases.
- Ensure lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`) are updated synchronously with the manifest.

### 4. Vulnerability & Injection Analysis
Inspect added and modified lines for standard OWASP vulnerabilities:
- **SQL/NoSQL Injection**: Ensure queries use parameterized statements rather than string concatenation or formatted templates.
- **Command Injection**: Check calls to `exec()`, `spawn()`, `subprocess.Popen(..., shell=True)`, `system()`. Ensure inputs are sanitized and arguments passed as arrays.
- **Cross-Site Scripting (XSS)**: Check for raw HTML injections (`dangerouslySetInnerHTML`, `v-html`, unescaped template tags).
- **Broken Access Control**: Confirm authorization checks execute before database operations and sensitive data retrieval.
- **SSRF (Server-Side Request Forgery)**: Verify external URLs requested by backend services are validated against an allowlist and do not resolve to loopback/link-local IPs (`127.0.0.1`, `169.254.169.254`).

### 5. CI/CD & Pipeline Integrity
Inspect `.github/workflows/` changes:
- Ensure untrusted user inputs (like `github.event.issue.title` or `github.head_ref`) are not evaluated directly inside `run:` shell blocks.
- Verify actions are pinned to full commit SHAs with comments rather than mutable tags (`@main`).
- Verify secret access is restricted to required jobs only.

### 6. Report Generation
Compile findings into a structured markdown report categorized by severity: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, and `INFORMATIONAL`.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Plaintext secret detected in diff | Mark as `CRITICAL BLOCKER`. Instruct author to immediately revoke the exposed credential, rotate keys, and rewrite Git history using `git-filter-repo`. |
| Dependency version has known CVE | Mark as `HIGH`. Require upgrading to the patched minimum version or providing an architectural justification with compensating controls. |
| Insecure CI/CD shell interpolation | Mark as `HIGH`. Require passing context data via environment variables rather than direct inline bash interpolation `${{ github.event... }}`. |
| Potential false positive secret | Verify entropy and test context. If it is a dummy test fixture, require explicit renaming (e.g. `DUMMY_TEST_KEY_NOT_REAL`). |

## Validation & Acceptance Criteria

- [ ] All modified lines in the pull request diff have been scanned.
- [ ] No plaintext secrets or active authentication tokens are present in any commit.
- [ ] Dependency lockfiles match package manifests with zero untrusted sources.
- [ ] Every API endpoint modified verifies caller authorization.
- [ ] Every finding in the generated report contains an exact line reference and a concrete remediation diff.

## Failure Handling & Recovery

- If `gh` CLI lacks authorization or network access, obtain the diff via standard local Git commands (`git diff origin/main...HEAD`).
- If the diff exceeds context window limits (> 2,000 lines), chunk the review by subdirectories, auditing `auth` and `workflows` first before general application logic.

## Expected Output & Artifacts

A structured security audit report:
```markdown
### Security Review Summary: [PASSED | BLOCKED]

- **Total Files Audited**: X
- **Risk Level**: [Low | Medium | High | Critical]

#### Findings
1. **[CRITICAL] SQL Injection in UserRepository.ts (L45-L52)**
   - **Vulnerability**: Unsanitized user parameter concatenated directly into raw query.
   - **Remediation**: Use parameterized query: `db.query('SELECT * FROM users WHERE id = $1', [userId])`.
```

## Related Skills

- `secret-leak-detection-and-remediation`
- `dependency-vulnerability-audit`
- `owasp-api-security-top-10`
- `github-pr-code-review`
