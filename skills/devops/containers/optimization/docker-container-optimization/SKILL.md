---
name: docker-container-optimization
description: "Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout."
domain: devops
category: containers
subcategory: optimization
tags:
  - docker
  - containers
  - devops
  - image-optimization
  - security-hardening
  - ci-cd
technologies:
  - Docker
  - Docker Compose
  - Linux
  - Trivy
complexity: intermediate
maturity: stable
tools:
  - docker
  - docker-compose
dependencies:
  - docker >= 20.10
---
# Docker Container Optimization

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
- Application codebase and dependency manifests.
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
