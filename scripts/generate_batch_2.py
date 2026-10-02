#!/usr/bin/env python3
"""
generate_batch_2.py - Second batch of high-value Agent Skills.
Enforces: ONE COMPLETED SKILL = ONE GIT COMMIT + ONE GITHUB PUSH.
"""

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BATCH_2 = [
    # -------------------------------------------------------------
    # 1. DEVOPS: docker-container-optimization
    # -------------------------------------------------------------
    {
        "name": "docker-container-optimization",
        "domain": "devops",
        "category": "containers",
        "subcategory": "optimization",
        "description": "Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout.",
        "tags": ["docker", "containers", "devops", "image-optimization", "security-hardening", "ci-cd"],
        "technologies": ["Docker", "Docker Compose", "Linux", "Trivy"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["docker", "docker-compose"],
        "dependencies": ["docker >= 20.10"],
        "content": """# Docker Container Optimization

## Overview

A comprehensive container engineering workflow designed to reduce image footprint by up to 80%, accelerate CI/CD build caching, and eliminate root privileges and vulnerable binaries from production deployment artifacts.

## When to Use

- Production container image size exceeds 500MB.
- CI/CD build and push times are excessively slow due to poor layer caching.
- Security scanners (Trivy, Snyk, Docker Scout) flag critical vulnerabilities in underlying OS packages.
- Hardening containers for enterprise Kubernetes deployment (enforcing non-root users and read-only filesystems).

## When NOT to Use

- Local development ephemeral containers where hot-reloading compilers and debuggers are required.
- Virtual machine image generation (use Packer).

## Inputs & Prerequisites

- Existing `Dockerfile` or `compose.yml`.
- Application source repository and dependency manifests.
- Docker daemon running locally or in CI runner.

## Core Workflow

### 1. Multi-Stage Build Architecture
Separate build-time dependencies (compilers, devDependencies, header files) from runtime execution:
```dockerfile
# Stage 1: Build & Dependencies
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

# Stage 2: Minimal Production Runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
USER appuser
EXPOSE 3000
ENTRYPOINT ["node", "dist/index.js"]
```

### 2. Cache-Optimized Layer Ordering
Order Dockerfile instructions from least-frequently-changing to most-frequently-changing:
1. Base image (`FROM`)
2. System packages (`apk add ...` or `apt-get install ...`)
3. Dependency manifests (`package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`)
4. Dependency install steps (`RUN npm ci`, `RUN go mod download`)
5. Application source code (`COPY . .`)
6. Build commands (`RUN npm run build`)

### 3. Layer Minimization & Cleanup
- Chain `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` into a single `RUN` layer.
- Use `.dockerignore` to strictly exclude `.git`, `node_modules`, `tests`, `docs`, and local environment files (`.env`).

### 4. Non-Root Security Hardening
- Explicitly create a non-root group and user.
- Switch to the non-root user via `USER <name>` before the `ENTRYPOINT`.
- Set container security flags in orchestrators (`readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`).

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Native C-extension compilation required (e.g. Python packages) | Build wheels in a heavyweight `builder` stage with gcc/make, and copy only the compiled wheels into a lightweight `slim` runtime stage. |
| Alpine DNS issues in Kubernetes | Switch from Alpine to Debian Slim (`python:3.12-slim` or `node:20-bookworm-slim`) to avoid musl libc DNS resolution quirks. |
| Read-only root filesystem prevents temporary file creation | Mount an ephemeral in-memory `tmpfs` volume at `/tmp`. |

## Validation & Acceptance Criteria

- [ ] Multi-stage build implemented.
- [ ] Image size reduced by at least 40% compared to unoptimized build.
- [ ] Container runs successfully under non-root UID.
- [ ] `.dockerignore` prevents leakage of `.git` and `.env` files.
- [ ] Container boots cleanly and passes health check (`HEALTHCHECK CMD curl -f http://localhost:3000/health || exit 1`).

## Failure Handling & Recovery

- If application crashes with permission denied errors upon container boot, verify that runtime directories requiring write access (e.g. log paths, cache dirs) are chowned to the non-root user during the build stage.

## Expected Output & Artifacts

- Optimized `Dockerfile`.
- Comprehensive `.dockerignore`.
- Image size and vulnerability scan comparison report.

## Related Skills

- `kubernetes-crashloop-debugging`
- `container-security-hardening`
- `github-actions-ci-pipeline-optimization`
"""
    },

    # -------------------------------------------------------------
    # 2. DEVOPS: kubernetes-crashloop-debugging
    # -------------------------------------------------------------
    {
        "name": "kubernetes-crashloop-debugging",
        "domain": "devops",
        "category": "kubernetes",
        "subcategory": "troubleshooting",
        "description": "Use this skill when diagnosing and recovering Kubernetes Pods stuck in CrashLoopBackOff, Error, OOMKilled, or Pending states. It guides the agent through inspecting exit codes, previous container logs, describe events, resource limits, readiness/liveness probe misconfigurations, and volume mount failures.",
        "tags": ["kubernetes", "devops", "troubleshooting", "debugging", "k8s", "containers", "observability"],
        "technologies": ["Kubernetes", "kubectl", "Docker", "Linux"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["kubectl"],
        "dependencies": ["kubectl >= 1.24"],
        "content": """# Kubernetes CrashLoop Debugging

## Overview

A systematic root-cause diagnosis and resolution workflow for Kubernetes workloads stuck in failure loops. Guides the agent through decoding termination exit codes, inspecting prior crashed instance logs (`--previous`), triaging cluster events, resolving resource limit bottlenecks (OOMKilled), and fixing probe misconfigurations.

## When to Use

- A Kubernetes Pod reports `CrashLoopBackOff`, `Error`, or repeated restarts.
- Pod is killed immediately with exit code `137` (OOMKilled) or `1` (Application Exception).
- A deployment rollout stalls because new replica pods fail readiness checks.
- Pod remains stuck in `Pending` due to scheduling constraints or PVC binding errors.

## When NOT to Use

- Managing underlying physical cluster node hardware or cloud provider control plane upgrades (use `kubernetes-cluster-administration`).
- Initial Helm chart authoring from scratch (use `helm-chart-scaffold`).

## Inputs & Prerequisites

- `kubectl` CLI configured with cluster access and relevant namespace context.
- Target pod name, deployment name, or namespace.

## Core Workflow

### 1. Pod Status & Event Inspection
Query pod state and termination metadata:
```bash
kubectl get pod <POD_NAME> -n <NAMESPACE> -o wide
kubectl describe pod <POD_NAME> -n <NAMESPACE>
```
Inspect the `Last State` and `Events` sections at the bottom of the describe output:
- `Exit Code: 0`: Application finished execution prematurely (process daemon didn't stay in foreground).
- `Exit Code: 1`: Uncaught runtime application exception or syntax error.
- `Exit Code: 137`: Process terminated by SIGKILL, almost always due to OOM (Out Of Memory). Check `OOMKilled: true`.
- `Exit Code: 143`: Process terminated by SIGTERM (graceful shutdown requested or probe failure).

### 2. Previous Container Log Extraction
Extract logs from the crashed container instance before the restart:
```bash
kubectl logs <POD_NAME> -n <NAMESPACE> --previous --tail=100
```
If multiple containers reside in the pod:
```bash
kubectl logs <POD_NAME> -c <CONTAINER_NAME> -n <NAMESPACE> --previous --tail=100
```

### 3. Triage & Fix by Failure Class

#### A. OOMKilled (Exit Code 137)
- Inspect memory limit in the pod spec (`resources.limits.memory`).
- Verify whether the application leaks memory or simply requires a higher baseline limit.
- Patch deployment with an adjusted limit:
  ```bash
  kubectl set resources deployment/<DEPLOYMENT_NAME> -n <NAMESPACE> --limits=memory=1Gi --requests=memory=512Mi
  ```

#### B. Liveness / Readiness Probe Failure
- Inspect probe configuration: `initialDelaySeconds`, `timeoutSeconds`, `periodSeconds`, `httpGet.path`.
- If the application takes 45 seconds to initialize but `initialDelaySeconds` is set to 10s, Kubernetes will kill the pod while it is still starting.
- Increase `initialDelaySeconds` or implement a `startupProbe` to accommodate slow initialization.

#### C. Missing Secrets or ConfigMaps
- In `kubectl describe pod`, check for events like: `MountVolume.SetUp failed for volume "secret-vol" : secret "app-secret" not found`.
- Verify required Secret/ConfigMap exists in the target namespace.

#### D. Foreground Process Missing
- Containers terminate when PID 1 exits. If the entrypoint script runs a background daemon (`nginx &`), the script completes and the container exits with code 0.
- Ensure the main process runs in the foreground (`nginx -g 'daemon off;'`).

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Pod restarts too fast to capture logs | Run an ephemeral debug container with an overridden entrypoint (`sleep 3600`) to inspect filesystem state: `kubectl debug <POD_NAME> -it --image=busybox --target=<CONTAINER>`. |
| Pending status with Unschedulable | Check node resources and nodeSelectors: `kubectl describe node` to verify memory and CPU allocatable headroom. |
| PersistentVolumeClaim unbound | Check storage class provisioner and access modes (`ReadWriteOnce` vs `ReadWriteMany`). |

## Validation & Acceptance Criteria

- [ ] Root cause identified from logs or describe events.
- [ ] Corrective patch applied to Deployment manifest.
- [ ] Pod transitions to `Running` state with `1/1` Ready containers.
- [ ] Zero restarts observed over a 5-minute monitoring window (`kubectl get pod -w`).

## Failure Handling & Recovery

- If new deployment version continues crashing, perform an immediate emergency rollback:
  ```bash
  kubectl rollout undo deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>
  ```

## Expected Output & Artifacts

- Triage diagnostic summary report with root cause analysis.
- Remediation patch manifest (YAML).
- Verification log showing healthy pod restart count.

## Related Skills

- `docker-container-optimization`
- `github-actions-ci-pipeline-optimization`
- `observability-and-instrumentation`
"""
    },

    # -------------------------------------------------------------
    # 3. FRONTEND: react-component-architecture
    # -------------------------------------------------------------
    {
        "name": "react-component-architecture",
        "domain": "frontend",
        "category": "react",
        "subcategory": "architecture",
        "description": "Use this skill when designing, refactoring, and structuring scalable React component hierarchies. It enforces clean separation of concerns between presentational components and stateful containers, headless UI patterns, compound components, strict TypeScript prop contracts, and memoization boundaries.",
        "tags": ["react", "frontend", "component-architecture", "typescript", "ui-patterns", "design-systems"],
        "technologies": ["React", "TypeScript", "Tailwind CSS", "shadcn/ui"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["tsc", "npm"],
        "dependencies": ["react >= 18.0", "typescript >= 4.5"],
        "content": """# React Component Architecture

## Overview

A structured architectural guide for designing modular, accessible, testable, and high-performance React component trees. Establishes clean boundaries between business state and presentation, implements reusable compound component patterns, and prevents common re-rendering bottlenecks.

## When to Use

- Architecting new UI features or reusable design system component libraries.
- Refactoring bloated "god components" (monolithic files with 500+ lines mixing hooks, API calls, and JSX).
- Standardizing component props, polymorphic rendering (`asChild` pattern), and compound components.
- Fixing cascading re-render performance issues across deep component trees.

## When NOT to Use

- Pure backend Node.js services or CLI tools.
- Static HTML sites with zero client-side interactive state.

## Inputs & Prerequisites

- React 18+ and TypeScript development environment.
- Component requirements including interactive states (loading, empty, error, disabled, active).
- Design system tokens or styling framework (Tailwind CSS, CSS Modules).

## Core Workflow

### 1. Component Role Separation (Container vs Presenter)
Separate data orchestration from visual rendering:
- **Presenter Components**: Pure functions of props. Zero network side effects. Highly reusable and easily unit-tested in Storybook.
- **Container / Feature Hooks**: Encapsulate data fetching, mutations, and local state machines (`useUserProfile`).

### 2. Compound Component Pattern for Complex Interfaces
For flexible multi-part widgets (e.g. Modals, Dropdowns, Tabs, Accordions), use compound components sharing React Context:
```tsx
import React, { createContext, useContext, useState } from "react";

interface TabsContextType {
  activeTab: string;
  setActiveTab: (id: string) => void;
}
const TabsContext = createContext<TabsContextType | null>(null);

export function Tabs({ defaultValue, children }: { defaultValue: string; children: React.ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs-container">{children}</div>
    </TabsContext.Provider>
  );
}

export function TabTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("TabTrigger must be used within Tabs");
  const isActive = ctx.activeTab === value;
  return (
    <button
      role="tab"
      aria-selected={isActive}
      className={isActive ? "tab-active" : "tab-inactive"}
      onClick={() => ctx.setActiveTab(value)}
    >
      {children}
    </button>
  );
}
```

### 3. Strict Prop Contracts & Invariants
- Use explicit TypeScript interfaces.
- Avoid passing entire raw domain entities when only 2 fields are displayed (pass primitives or narrow interfaces to enable memoization).
- Use discriminating unions for mutually exclusive states:
```tsx
type ButtonProps =
  | { variant: "link"; href: string; onClick?: never }
  | { variant: "button"; href?: never; onClick: () => void };
```

### 4. Render Optimization & Boundary Isolation
- Push state down: Colocate state as close as possible to the leaves that consume it.
- Lift content up: Pass heavy child components as `children` prop so their re-render is decoupled from parent state updates.
- Wrap expensive calculations in `useMemo` and callbacks passed to memoized children in `useCallback`.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Deep prop drilling across > 3 layers | Introduce a scoped React Context or lightweight atomic state store (Zustand/Jotai). |
| Polymorphic rendering needed | Use Radix UI `Slot` / `asChild` pattern to compose functionality onto custom child elements without wrapper DOM pollution. |
| Server Components (Next.js App Router) | Default to Server Components for data fetching. Mark files with `'use client'` only where browser APIs, hooks, or event listeners are required. |

## Validation & Acceptance Criteria

- [ ] Components adhere to single-responsibility principle (< 200 lines per file).
- [ ] Strict TypeScript prop interfaces with zero `any` types.
- [ ] ARIA roles and keyboard navigation implemented for interactive elements.
- [ ] No unwanted re-rendering of siblings when typing in input controls.

## Failure Handling & Recovery

- If React renders in an infinite loop, check `useEffect` dependency arrays for objects or arrays instantiated inline inside the component body without `useMemo`.

## Expected Output & Artifacts

- Clean, modular component source files.
- Exported TypeScript type definitions.
- Unit and accessibility tests using React Testing Library.

## Related Skills

- `react-accessibility-audit`
- `browser-performance-profiling`
- `playwright-e2e-testing`
"""
    },

    # -------------------------------------------------------------
    # 4. TESTING: playwright-e2e-testing
    # -------------------------------------------------------------
    {
        "name": "playwright-e2e-testing",
        "domain": "testing",
        "category": "e2e",
        "subcategory": "playwright",
        "description": "Use this skill when authoring, debugging, and maintaining end-to-end (E2E) automated browser test suites using Playwright. It guides the agent through resilient locator strategies (user-facing role/text), page object models, network mocking, authenticated session caching, parallel execution, and flaky test elimination.",
        "tags": ["playwright", "testing", "e2e", "browser-automation", "qa", "ci-cd"],
        "technologies": ["Playwright", "TypeScript", "Node.js", "Chromium"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["npx", "playwright", "node"],
        "dependencies": ["@playwright/test >= 1.35"],
        "content": """# Playwright E2E Testing

## Overview

A production-grade methodology for writing robust, maintainable, and deterministic end-to-end browser tests using Microsoft Playwright. Eliminates test flakiness through auto-waiting, resilient role-based locators, authenticated storage state caching, and comprehensive trace inspection.

## When to Use

- Writing automated regression test suites for critical user journeys (signup, checkout, onboarding, settings).
- Debugging intermittent test failures or race conditions in CI pipelines.
- Establishing test fixtures with pre-authenticated sessions or seeded database states.
- Running multi-browser cross-platform matrix testing (Chromium, Firefox, WebKit, Mobile).

## When NOT to Use

- Isolated pure function logic or algorithmic unit tests (use Vitest / Jest).
- Backend unit testing of database queries without UI involvement.

## Inputs & Prerequisites

- Node.js project with `@playwright/test` installed.
- Running application server or baseURL configured in `playwright.config.ts`.

## Core Workflow

### 1. Resilient Locator Strategy
Always prefer user-visible locators over fragile CSS selectors or XPath:
```typescript
// GOOD: Resilient, accessible locators
page.getByRole("button", { name: "Submit Order" });
page.getByLabel("Email Address");
page.getByTestId("checkout-summary"); // Safe fallback when semantic roles are ambiguous

// BAD: Fragile, brittle selectors that break on style changes
page.locator(".btn-primary.submit-btn");
page.locator("div > div:nth-child(3) > button");
```

### 2. Page Object Model (POM) Design
Encapsulate page interactions inside reusable classes:
```typescript
import { type Page, type Locator, expect } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.submitButton = page.getByRole("button", { name: "Sign In" });
  }

  async goto() {
    await this.page.goto("/login");
  }

  async login(email: string, pass: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(pass);
    await this.submitButton.click();
    await expect(this.page).toHaveURL(/.*dashboard/);
  }
}
```

### 3. Authenticated Session Caching (Storage State)
Avoid logging in through the UI before every test. Authenticate once in a setup project and reuse saved cookies and localStorage:
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: "setup", testMatch: /.*\\.setup\\.ts/ },
    {
      name: "e2e tests",
      use: { storageState: "playwright/.auth/user.json" },
      dependencies: ["setup"],
    },
  ],
});
```

### 4. Flakiness Elimination & Auto-Waiting
- Never use arbitrary `page.waitForTimeout(5000)` sleeps.
- Rely on Playwright's built-in auto-waiting (`click`, `fill`, `check` automatically wait for element visibility, stability, and actionable state).
- Use web-first assertions with automatic retry:
  ```typescript
  await expect(page.getByText("Welcome back")).toBeVisible({ timeout: 10000 });
  ```

### 5. Network Mocking & API Interception
Mock unpredictable third-party APIs (Stripe, Twilio, analytics):
```typescript
await page.route("**/api/payments/charge", async (route) => {
  await route.fulfill({
    status: 200,
    contentType: "application/json",
    body: JSON.stringify({ success: true, transactionId: "mock_tx_123" }),
  });
});
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Test fails only in headless CI environment | Enable trace recording on retry (`trace: 'on-first-retry'`) and inspect trace using `npx playwright show-trace trace.zip`. |
| Flaky timing on dynamic animations | Disable animations in Playwright config or wait for specific network requests (`page.waitForResponse(...)`). |
| Multi-tab or popup windows | Listen for popup event: `const [popup] = await Promise.all([page.waitForEvent('popup'), page.getByRole('button').click()]);`. |

## Validation & Acceptance Criteria

- [ ] Tests run successfully in headless mode across all target browsers.
- [ ] No arbitrary sleeps (`waitForTimeout`) present in test code.
- [ ] Authentication setup isolates user sessions efficiently.
- [ ] CI pipeline captures screenshots and traces on test failure.

## Failure Handling & Recovery

- If a test fails intermittently, run it in repeat-each mode: `npx playwright test --repeat-each=20` to reproduce and isolate race conditions.

## Expected Output & Artifacts

- Clean test specification files (`tests/e2e/*.spec.ts`).
- Modular Page Object Model files (`tests/models/*.ts`).
- HTML test execution reports (`playwright-report/`).

## Related Skills

- `browser-testing-with-devtools`
- `react-component-architecture`
- `ci-cd-and-automation`
"""
    },

    # -------------------------------------------------------------
    # 5. SECURITY: secret-leak-detection-and-remediation
    # -------------------------------------------------------------
    {
        "name": "secret-leak-detection-and-remediation",
        "domain": "security",
        "category": "secret-management",
        "subcategory": "detection",
        "description": "Use this skill when detecting, containing, revoking, and purging secrets committed to Git repositories or build artifacts. It guides the agent through scanning history with TruffleHog/Gitleaks, executing emergency credential revocation, rewriting Git history with git-filter-repo, and installing pre-commit guardrails.",
        "tags": ["security", "secrets", "git", "credential-hygiene", "devsecops", "incident-response"],
        "technologies": ["Git", "Gitleaks", "TruffleHog", "git-filter-repo"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["git", "gitleaks", "python"],
        "dependencies": ["git >= 2.30"],
        "content": """# Secret Leak Detection and Remediation

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
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Sequential Skill Factory Deployment - Batch 2 ({len(BATCH_2)} skills)")
    print("=" * 70)

    for idx, skill in enumerate(BATCH_2, 1):
        print(f"\n[{idx}/{len(BATCH_2)}] Processing skill: {skill['name']} ({skill['domain']}/{skill['category']})")
        success = create_and_ship_skill(skill)
        if not success:
            print(f"ERROR: Failed processing skill {skill['name']}. Aborting sequence.")
            sys.exit(1)
        time.sleep(1)

    print("\n" + "=" * 70)
    print("Batch 2 successfully manufactured, validated, committed, and pushed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
