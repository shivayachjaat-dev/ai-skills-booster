# Skill Categories & Directory Map

Master navigation for **8** skills across structured domains, categories, and subcategories.

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

## Devops (1 skills)

### Containers (1 skills)
Category index: [`docs/categories/containers.md`](categories/containers.md)

- **Optimization** (1):
  - [docker-container-optimization](../skills/devops/containers/optimization/docker-container-optimization/SKILL.md) — Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout.

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

## Security (1 skills)

### Code Review (1 skills)
Category index: [`docs/categories/code-review.md`](categories/code-review.md)

- **Github** (1):
  - [github-pr-security-review](../skills/security/code-review/github/github-pr-security-review/SKILL.md) — Use this skill when reviewing a GitHub pull request for security vulnerabilities, exposed secrets, unsafe dependencies, injection risks, authentication flaws, or insecure CI/CD modifications. It guides the agent through systematic threat modeling, diff inspection, risk severity classification, and remediation generation.

## Software Engineering (1 skills)

### Architecture (1 skills)
Category index: [`docs/categories/architecture.md`](categories/architecture.md)

- **Interfaces** (1):
  - [api-and-interface-design](../skills/software-engineering/architecture/interfaces/api-and-interface-design/SKILL.md) — Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles.
