# Skill Categories & Directory Map

Master navigation for **15** skills across structured domains, categories, and subcategories.

## Ai Engineering (2 skills)

### Agents (1 skills)
Category index: [`docs/categories/agents.md`](categories/agents.md)

- **Memory** (1):
  - [agent-project-memory](../skills/ai-engineering/agents/memory/agent-project-memory/SKILL.md) — Use this skill when designing, maintaining, or recovering persistent memory and architectural context across long-running AI agent sessions. It establishes structured memory stores, state serialization protocols, session recovery checkpoints, and active context pruning to prevent context loss during complex projects.

### Rag (1 skills)
Category index: [`docs/categories/rag.md`](categories/rag.md)

- **Evaluation** (1):
  - [rag-retrieval-evaluation](../skills/ai-engineering/rag/evaluation/rag-retrieval-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and optimizing the retrieval quality of a Retrieval-Augmented Generation (RAG) system. It guides the agent through calculating Recall@K, Precision@K, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG), and context relevance to eliminate hallucinations caused by poor context retrieval.

## Databases (1 skills)

### Postgresql (1 skills)
Category index: [`docs/categories/postgresql.md`](categories/postgresql.md)

- **Performance** (1):
  - [postgres-query-performance-analysis](../skills/databases/postgresql/performance/postgres-query-performance-analysis/SKILL.md) — Use this skill when diagnosing, analyzing, and optimizing slow PostgreSQL queries. It guides the agent through running and interpreting EXPLAIN (ANALYZE, BUFFERS), identifying sequential table scans, resolving missing indexes, fixing high buffer reads, eliminating N+1 query patterns, and tuning query planner configurations.

## Devops (2 skills)

### Containers (1 skills)
Category index: [`docs/categories/containers.md`](categories/containers.md)

- **Optimization** (1):
  - [docker-container-optimization](../skills/devops/containers/optimization/docker-container-optimization/SKILL.md) — Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout.

### Kubernetes (1 skills)
Category index: [`docs/categories/kubernetes.md`](categories/kubernetes.md)

- **Troubleshooting** (1):
  - [kubernetes-crashloop-debugging](../skills/devops/kubernetes/troubleshooting/kubernetes-crashloop-debugging/SKILL.md) — Use this skill when diagnosing and recovering Kubernetes Pods stuck in CrashLoopBackOff, Error, OOMKilled, or Pending states. It guides the agent through inspecting exit codes, previous container logs, describe events, resource limits, readiness/liveness probe misconfigurations, and volume mount failures.

## Frontend (1 skills)

### React (1 skills)
Category index: [`docs/categories/react.md`](categories/react.md)

- **Architecture** (1):
  - [react-component-architecture](../skills/frontend/react/architecture/react-component-architecture/SKILL.md) — Use this skill when designing, refactoring, and structuring scalable React component hierarchies. It enforces clean separation of concerns between presentational components and stateful containers, headless UI patterns, compound components, strict TypeScript prop contracts, and memoization boundaries.

## Mcp (1 skills)

### Server Development (1 skills)
Category index: [`docs/categories/server-development.md`](categories/server-development.md)

- **Scaffolding** (1):
  - [mcp-server-scaffold](../skills/mcp/server-development/scaffolding/mcp-server-scaffold/SKILL.md) — Use this skill when scaffolding, implementing, and validating a Model Context Protocol (MCP) server from scratch using TypeScript or Python. It guides the agent through configuring tool schemas, resource providers, prompt templates, stdio/SSE transports, error boundaries, and integration tests.

## Meta (1 skills)

### Ecosystem (1 skills)
Category index: [`docs/categories/ecosystem.md`](categories/ecosystem.md)

- **Creation** (1):
  - [skill-creator](../skills/meta/ecosystem/creation/skill-creator/SKILL.md) — Use this skill when designing, authoring, and structuring new Agent Skills for AI coding agents. It guides the agent through problem formulation, three-level taxonomy classification, frontmatter schema validation, step-by-step workflow authoring, edge case identification, and automated evaluation generation.

## Security (3 skills)

### Ai Security (1 skills)
Category index: [`docs/categories/ai-security.md`](categories/ai-security.md)

- **Defense** (1):
  - [prompt-injection-defense](../skills/security/ai-security/defense/prompt-injection-defense/SKILL.md) — Use this skill when auditing, hardening, and protecting LLM applications and agent pipelines against direct and indirect prompt injection attacks. It guides the agent through untrusted data boundary separation, XML tagging, dual-model verification, output validation guardrails, and tool execution privilege sandboxing.

### Code Review (1 skills)
Category index: [`docs/categories/code-review.md`](categories/code-review.md)

- **Github** (1):
  - [github-pr-security-review](../skills/security/code-review/github/github-pr-security-review/SKILL.md) — Use this skill when reviewing a GitHub pull request for security vulnerabilities, exposed secrets, unsafe dependencies, injection risks, authentication flaws, or insecure CI/CD modifications. It guides the agent through systematic threat modeling, diff inspection, risk severity classification, and remediation generation.

### Secret Management (1 skills)
Category index: [`docs/categories/secret-management.md`](categories/secret-management.md)

- **Detection** (1):
  - [secret-leak-detection-and-remediation](../skills/security/secret-management/detection/secret-leak-detection-and-remediation/SKILL.md) — Use this skill when detecting, containing, revoking, and purging secrets committed to Git repositories or build artifacts. It guides the agent through scanning history with TruffleHog/Gitleaks, executing emergency credential revocation, rewriting Git history with git-filter-repo, and installing pre-commit guardrails.

## Software Engineering (3 skills)

### Architecture (1 skills)
Category index: [`docs/categories/architecture.md`](categories/architecture.md)

- **Interfaces** (1):
  - [api-and-interface-design](../skills/software-engineering/architecture/interfaces/api-and-interface-design/SKILL.md) — Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles.

### Debugging (1 skills)
Category index: [`docs/categories/debugging.md`](categories/debugging.md)

- **Recovery** (1):
  - [debugging-and-error-recovery](../skills/software-engineering/debugging/recovery/debugging-and-error-recovery/SKILL.md) — Use this skill when diagnosing obscure bugs, production failures, memory leaks, race conditions, or unhandled exceptions. It enforces scientific hypothesis-driven debugging, minimal reproduction synthesis, stack trace isolation, binary search bisecting, and permanent regression test installation.

### Refactoring (1 skills)
Category index: [`docs/categories/refactoring.md`](categories/refactoring.md)

- **Simplification** (1):
  - [code-simplification](../skills/software-engineering/refactoring/simplification/code-simplification/SKILL.md) — Use this skill when simplifying convoluted code, eliminating accidental complexity, unwinding deeply nested conditionals, and removing speculative abstractions. It guides the agent through guard clauses, cyclomatic complexity reduction, dead code pruning, and establishing transparent data flow.

## Testing (1 skills)

### E2E (1 skills)
Category index: [`docs/categories/e2e.md`](categories/e2e.md)

- **Playwright** (1):
  - [playwright-e2e-testing](../skills/testing/e2e/playwright/playwright-e2e-testing/SKILL.md) — Use this skill when authoring, debugging, and maintaining end-to-end (E2E) automated browser test suites using Playwright. It guides the agent through resilient locator strategies (user-facing role/text), page object models, network mocking, authenticated session caching, parallel execution, and flaky test elimination.
