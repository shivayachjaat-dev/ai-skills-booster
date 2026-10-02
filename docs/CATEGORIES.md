# Skill Categories & Directory Map

Master navigation for **28** skills across structured domains, categories, and subcategories.

## Ai Engineering (4 skills)

### Agents (2 skills)
Category index: [`docs/categories/agents.md`](categories/agents.md)

- **Benchmarking** (1):
  - [ai-agent-benchmark-evaluation](../skills/ai-engineering/agents/benchmarking/ai-agent-benchmark-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and grading autonomous AI agents across multi-step execution tasks. It guides the agent through establishing reproducible mock environments, measuring task completion rates, analyzing tool calling trajectory efficiency, computing hallucination indices, and detecting regression degradation across model releases.
- **Memory** (1):
  - [agent-project-memory](../skills/ai-engineering/agents/memory/agent-project-memory/SKILL.md) — Use this skill when designing, maintaining, or recovering persistent memory and architectural context across long-running AI agent sessions. It establishes structured memory stores, state serialization protocols, session recovery checkpoints, and active context pruning to prevent context loss during complex projects.

### Context (1 skills)
Category index: [`docs/categories/context.md`](categories/context.md)

- **Optimization** (1):
  - [context-window-engineering](../skills/ai-engineering/context/optimization/context-window-engineering/SKILL.md) — Use this skill when managing, structuring, and compressing context windows for LLMs and autonomous agents. It enforces prompt caching alignment, 'lost in the middle' attention optimization, dynamic token budget allocation, semantic pruning, and multi-turn message compaction to maximize reasoning accuracy while minimizing latency and token costs.

### Rag (1 skills)
Category index: [`docs/categories/rag.md`](categories/rag.md)

- **Evaluation** (1):
  - [rag-retrieval-evaluation](../skills/ai-engineering/rag/evaluation/rag-retrieval-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and optimizing the retrieval quality of a Retrieval-Augmented Generation (RAG) system. It guides the agent through calculating Recall@K, Precision@K, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG), and context relevance to eliminate hallucinations caused by poor context retrieval.

## Backend (4 skills)

### Api Design (1 skills)
Category index: [`docs/categories/api-design.md`](categories/api-design.md)

- **Rate Limiting** (1):
  - [api-rate-limiting-and-throttling](../skills/backend/api-design/rate-limiting/api-rate-limiting-and-throttling/SKILL.md) — Use this skill when designing, implementing, and tuning API rate limiters and request throttling systems. It guides the agent through algorithm selection (Token Bucket, Leaky Bucket, Sliding Window Counter), distributed synchronization with Redis, HTTP 429 response formatting, Tier-based limits, and atomic Lua script execution to prevent race conditions.

### Fastapi (1 skills)
Category index: [`docs/categories/fastapi.md`](categories/fastapi.md)

- **Async Architecture** (1):
  - [fastapi-async-api-design](../skills/backend/fastapi/async-architecture/fastapi-async-api-design/SKILL.md) — Use this skill when building high-performance, asynchronous REST APIs with FastAPI, Pydantic v2, and async database drivers. It guides the agent through dependency injection patterns, async/await event loop blocking prevention, structured error handlers, lifespan context managers, and OpenAPI schema generation.

### Graphql (1 skills)
Category index: [`docs/categories/graphql.md`](categories/graphql.md)

- **Schema Design** (1):
  - [graphql-schema-evolution](../skills/backend/graphql/schema-design/graphql-schema-evolution/SKILL.md) — Use this skill when designing, versioning, and evolving GraphQL schemas without breaking existing mobile and web clients. It guides the agent through schema-first SDL design, non-breaking deprecation directives (@deprecated), resolving the N+1 query problem using DataLoader, input union patterns, and automated breaking-change detection in CI.

### Messaging (1 skills)
Category index: [`docs/categories/messaging.md`](categories/messaging.md)

- **Kafka** (1):
  - [kafka-event-driven-architecture](../skills/backend/messaging/kafka/kafka-event-driven-architecture/SKILL.md) — Use this skill when designing, implementing, and tuning event-driven architectures with Apache Kafka. It guides the agent through partition key selection, consumer group rebalance minimization, exactly-once processing semantics (EOS), schema evolution with Avro/Protobuf, dead letter queues (DLQ), and producer idempotency.

## Data Analytics (2 skills)

### Data Pipelines (1 skills)
Category index: [`docs/categories/data-pipelines.md`](categories/data-pipelines.md)

- **Polars** (1):
  - [polars-high-throughput-data-pipeline](../skills/data-analytics/data-pipelines/polars/polars-high-throughput-data-pipeline/SKILL.md) — Use this skill when processing, transforming, and analyzing large tabular datasets exceeding memory limits using Polars. It guides the agent through lazy evaluation (LazyFrame), streaming execution, predicate/projection pushdown, memory-mapped Parquet I/O, and Apache Arrow zero-copy transformations.

### Experimentation (1 skills)
Category index: [`docs/categories/experimentation.md`](categories/experimentation.md)

- **Ab Testing** (1):
  - [ab-test-experiment-design](../skills/data-analytics/experimentation/ab-testing/ab-test-experiment-design/SKILL.md) — Use this skill when designing, sizing, and analyzing A/B and multivariate split experiments. It guides the agent through statistical hypothesis formulation, sample size calculation via power analysis, minimum detectable effect (MDE) estimation, guardrail metric tracking, CUPED variance reduction, and p-value significance evaluation.

## Databases (3 skills)

### Migrations (1 skills)
Category index: [`docs/categories/migrations.md`](categories/migrations.md)

- **Zero Downtime** (1):
  - [database-migration-safety](../skills/databases/migrations/zero-downtime/database-migration-safety/SKILL.md) — Use this skill when authoring, reviewing, and applying database schema migrations in high-traffic production environments without downtime. It enforces the Expand and Contract pattern, non-blocking lock acquisition, safe column additions, asynchronous backfills, reversible rollbacks, and zero-downtime schema evolution.

### Postgresql (1 skills)
Category index: [`docs/categories/postgresql.md`](categories/postgresql.md)

- **Performance** (1):
  - [postgres-query-performance-analysis](../skills/databases/postgresql/performance/postgres-query-performance-analysis/SKILL.md) — Use this skill when diagnosing, analyzing, and optimizing slow PostgreSQL queries. It guides the agent through running and interpreting EXPLAIN (ANALYZE, BUFFERS), identifying sequential table scans, resolving missing indexes, fixing high buffer reads, eliminating N+1 query patterns, and tuning query planner configurations.

### Redis (1 skills)
Category index: [`docs/categories/redis.md`](categories/redis.md)

- **Caching** (1):
  - [redis-caching-patterns](../skills/databases/redis/caching/redis-caching-patterns/SKILL.md) — Use this skill when designing, implementing, and optimizing caching strategies using Redis. It guides the agent through selecting appropriate patterns (Cache-Aside, Write-Through, Write-Behind), mitigating cache stampedes (dogpiling) using probabilistic early expiration (XFetch) or mutex locks, avoiding cache penetration with Bloom filters, and configuring TTL jitter.

## Devops (2 skills)

### Containers (1 skills)
Category index: [`docs/categories/containers.md`](categories/containers.md)

- **Optimization** (1):
  - [docker-container-optimization](../skills/devops/containers/optimization/docker-container-optimization/SKILL.md) — Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout.

### Kubernetes (1 skills)
Category index: [`docs/categories/kubernetes.md`](categories/kubernetes.md)

- **Troubleshooting** (1):
  - [kubernetes-crashloop-debugging](../skills/devops/kubernetes/troubleshooting/kubernetes-crashloop-debugging/SKILL.md) — Use this skill when diagnosing and recovering Kubernetes Pods stuck in CrashLoopBackOff, Error, OOMKilled, or Pending states. It guides the agent through inspecting exit codes, previous container logs, describe events, resource limits, readiness/liveness probe misconfigurations, and volume mount failures.

## Frontend (2 skills)

### Accessibility (1 skills)
Category index: [`docs/categories/accessibility.md`](categories/accessibility.md)

- **Wcag** (1):
  - [wcag-accessibility-audit](../skills/frontend/accessibility/wcag/wcag-accessibility-audit/SKILL.md) — Use this skill when auditing, testing, and remediating web interfaces for compliance with WCAG 2.2 AA standards. It guides the agent through automated scanning with axe-core, keyboard focus trapping, ARIA roles, color contrast ratio verification, accessible forms, screen reader announcement trees, and responsive zoom testing.

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

## Security (4 skills)

### Ai Security (1 skills)
Category index: [`docs/categories/ai-security.md`](categories/ai-security.md)

- **Defense** (1):
  - [prompt-injection-defense](../skills/security/ai-security/defense/prompt-injection-defense/SKILL.md) — Use this skill when auditing, hardening, and protecting LLM applications and agent pipelines against direct and indirect prompt injection attacks. It guides the agent through untrusted data boundary separation, XML tagging, dual-model verification, output validation guardrails, and tool execution privilege sandboxing.

### Authentication (1 skills)
Category index: [`docs/categories/authentication.md`](categories/authentication.md)

- **Oauth2** (1):
  - [oauth2-jwt-authentication-flow](../skills/security/authentication/oauth2/oauth2-jwt-authentication-flow/SKILL.md) — Use this skill when designing, implementing, and securing OAuth 2.1 and OpenID Connect (OIDC) authentication flows with JSON Web Tokens (JWT). It enforces Authorization Code Flow with PKCE, asymmetric RS256 signature verification, refresh token rotation with reuse detection, claims validation, and centralized revocation blacklists.

### Code Review (1 skills)
Category index: [`docs/categories/code-review.md`](categories/code-review.md)

- **Github** (1):
  - [github-pr-security-review](../skills/security/code-review/github/github-pr-security-review/SKILL.md) — Use this skill when reviewing a GitHub pull request for security vulnerabilities, exposed secrets, unsafe dependencies, injection risks, authentication flaws, or insecure CI/CD modifications. It guides the agent through systematic threat modeling, diff inspection, risk severity classification, and remediation generation.

### Secret Management (1 skills)
Category index: [`docs/categories/secret-management.md`](categories/secret-management.md)

- **Detection** (1):
  - [secret-leak-detection-and-remediation](../skills/security/secret-management/detection/secret-leak-detection-and-remediation/SKILL.md) — Use this skill when detecting, containing, revoking, and purging secrets committed to Git repositories or build artifacts. It guides the agent through scanning history with TruffleHog/Gitleaks, executing emergency credential revocation, rewriting Git history with git-filter-repo, and installing pre-commit guardrails.

## Software Engineering (4 skills)

### Architecture (1 skills)
Category index: [`docs/categories/architecture.md`](categories/architecture.md)

- **Interfaces** (1):
  - [api-and-interface-design](../skills/software-engineering/architecture/interfaces/api-and-interface-design/SKILL.md) — Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles.

### Debugging (1 skills)
Category index: [`docs/categories/debugging.md`](categories/debugging.md)

- **Recovery** (1):
  - [debugging-and-error-recovery](../skills/software-engineering/debugging/recovery/debugging-and-error-recovery/SKILL.md) — Use this skill when diagnosing obscure bugs, production failures, memory leaks, race conditions, or unhandled exceptions. It enforces scientific hypothesis-driven debugging, minimal reproduction synthesis, stack trace isolation, binary search bisecting, and permanent regression test installation.

### Modernization (1 skills)
Category index: [`docs/categories/modernization.md`](categories/modernization.md)

- **Migration** (1):
  - [legacy-system-strangler-migration](../skills/software-engineering/modernization/migration/legacy-system-strangler-migration/SKILL.md) — Use this skill when incrementally modernizing, decomposing, and replacing legacy monoliths or deprecated backend systems without risky all-at-once cutovers. It guides the agent through the Strangler Fig pattern, reverse proxy intercept routing, parallel run shadow verification, database synchronization, and progressive decommission.

### Refactoring (1 skills)
Category index: [`docs/categories/refactoring.md`](categories/refactoring.md)

- **Simplification** (1):
  - [code-simplification](../skills/software-engineering/refactoring/simplification/code-simplification/SKILL.md) — Use this skill when simplifying convoluted code, eliminating accidental complexity, unwinding deeply nested conditionals, and removing speculative abstractions. It guides the agent through guard clauses, cyclomatic complexity reduction, dead code pruning, and establishing transparent data flow.

## Testing (1 skills)

### E2E (1 skills)
Category index: [`docs/categories/e2e.md`](categories/e2e.md)

- **Playwright** (1):
  - [playwright-e2e-testing](../skills/testing/e2e/playwright/playwright-e2e-testing/SKILL.md) — Use this skill when authoring, debugging, and maintaining end-to-end (E2E) automated browser test suites using Playwright. It guides the agent through resilient locator strategies (user-facing role/text), page object models, network mocking, authenticated session caching, parallel execution, and flaky test elimination.
