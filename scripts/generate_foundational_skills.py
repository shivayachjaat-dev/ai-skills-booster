#!/usr/bin/env python3
"""
generate_foundational_skills.py - Sequentially manufactures, validates,
indexes, commits, and pushes premier foundational skills across major domains.
Enforces: ONE COMPLETED SKILL = ONE GIT COMMIT + ONE GITHUB PUSH.
"""

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

SKILLS_QUEUE = [
    # -------------------------------------------------------------
    # 1. META SKILLS: skill-creator
    # -------------------------------------------------------------
    {
        "name": "skill-creator",
        "domain": "meta",
        "category": "ecosystem",
        "subcategory": "creation",
        "description": "Use this skill when designing, authoring, and structuring new Agent Skills for AI coding agents. It guides the agent through problem formulation, three-level taxonomy classification, frontmatter schema validation, step-by-step workflow authoring, edge case identification, and automated evaluation generation.",
        "tags": ["meta", "skill-creation", "agent-skills", "authoring", "taxonomy"],
        "technologies": ["Python", "Markdown", "YAML", "Git"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "git"],
        "dependencies": ["python >= 3.9"],
        "content": """# Skill Creator

## Overview

A meta-skill that guides AI coding agents in designing, generating, and verifying new, high-quality Agent Skills. It guarantees that new skills conform to the strict 3-level taxonomy (`domain/category/subcategory/skill-name`), possess complete YAML frontmatter, provide deterministic workflows with explicit decision trees, and include verifiable acceptance criteria.

## When to Use

- Creating a new agent skill to automate a distinct engineering or operational task.
- Refactoring legacy or informal prompts into structured, reproducible Agent Skills.
- Packaging repetitive multi-step coding or operational procedures for agent reuse.
- Expanding the AI Skills Booster catalog into new domains or subdomains.

## When NOT to Use

- Simply answering a one-off user coding question without intending to persist a reusable skill.
- Modifying general system instructions or global personality prompts.

## Inputs & Prerequisites

- Target problem statement and workflow description.
- Target domain, category, and subcategory according to the repository taxonomy.
- List of tools (e.g. `git`, `docker`, `python`) and dependencies required by the workflow.

## Core Workflow

### 1. Problem Formulation & Scope Verification
1. Define the exact user problem the skill solves.
2. Confirm that the skill is not a generic stub or trivial duplicate of an existing skill.
3. Formulate the skill name in strict kebab-case describing the action (e.g. `postgres-query-performance-analysis`).

### 2. Taxonomy & Directory Assignment
Assign the skill to the appropriate 3-level hierarchy:
`skills/<domain>/<category>/<subcategory>/<skill-name>/`
Ensure the directory structure matches the frontmatter fields.

### 3. Frontmatter Construction
Populate complete YAML frontmatter:
- `name`: kebab-case skill identifier
- `description`: Crisp, specific summary answering what it does, when to use it, and what problem it solves.
- `domain`, `category`, `subcategory`
- `tags`: 3 to 8 searchable keywords
- `technologies`: List of relevant technologies
- `complexity`: `beginner`, `intermediate`, `advanced`, or `expert`
- `maturity`: `experimental`, `stable`, or `advanced`
- `tools` and `dependencies`

### 4. Authoring Standard Sections
Structure the markdown content with mandatory sections:
1. `## Overview`
2. `## When to Use`
3. `## When NOT to Use`
4. `## Inputs & Prerequisites`
5. `## Core Workflow` (with step-by-step procedural commands)
6. `## Decision Points & Edge Cases`
7. `## Validation & Acceptance Criteria`
8. `## Failure Handling & Recovery`
9. `## Expected Output & Artifacts`
10. `## Related Skills`

### 5. Automated Verification
Run repository validator:
```bash
python scripts/validate.py
python scripts/detect_duplicates.py
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Overlap with existing skill | Check `scripts/detect_duplicates.py`. If scope overlaps > 70%, specialize the new skill or merge improvements into the existing one. |
| Complex multi-step scripts needed | Place executable helper code in `scripts/` inside the skill directory rather than bloating `SKILL.md`. |
| Complex reference data | Place extensive manuals, specifications, or schema documentation in `references/`. |

## Validation & Acceptance Criteria

- [ ] Directory path matches `skills/<domain>/<category>/<subcategory>/<name>/SKILL.md`.
- [ ] Description is at least 40 characters and clearly states triggers and outcomes.
- [ ] Frontmatter contains valid tags, complexity, maturity, and tools.
- [ ] `python scripts/validate.py` passes with zero errors.

## Failure Handling & Recovery

- If validation reports missing fields or naming mismatches, adjust frontmatter or directory naming immediately before proceeding to git commit.

## Expected Output & Artifacts

- Fully compliant `SKILL.md` in the target directory.
- Optional `scripts/` or `evals/` supporting files.

## Related Skills

- `skill-reviewer`
- `skill-validator`
- `skill-evaluator`
"""
    },

    # -------------------------------------------------------------
    # 2. AI ENGINEERING / AGENTS: agent-project-memory
    # -------------------------------------------------------------
    {
        "name": "agent-project-memory",
        "domain": "ai-engineering",
        "category": "agents",
        "subcategory": "memory",
        "description": "Use this skill when designing, maintaining, or recovering persistent memory and architectural context across long-running AI agent sessions. It establishes structured memory stores, state serialization protocols, session recovery checkpoints, and active context pruning to prevent context loss during complex projects.",
        "tags": ["ai-agents", "agent-memory", "context-management", "state-persistence", "llm-architecture"],
        "technologies": ["Python", "JSON", "SQLite", "Markdown"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "sqlite3"],
        "dependencies": ["python >= 3.9"],
        "content": """# Agent Project Memory

## Overview

Persistent project memory enables AI agents to maintain continuity, recall critical architecture decisions, and retain historical debugging context across long-running development workflows, context window resets, and multi-session collaborations.

## When to Use

- Managing multi-day or multi-agent development projects where context resets are inevitable.
- Capturing Architectural Decision Records (ADRs), user preferences, and dependency constraints.
- Resuming interrupted tasks where an agent must restore prior state, planned tasks, and completed milestones.
- Preventing catastrophic forgetting when agents generate thousands of lines of code across dozens of modules.

## When NOT to Use

- Short, single-turn query responses or ephemeral scratch tasks.
- Static application logging (use standard application logging frameworks like Winston or Loguru).

## Inputs & Prerequisites

- Local filesystem access to write project memory stores (`.gemini/memory/`, `.claude/context/`, or `.agent/memory.json`).
- Schema definition for persistent memory layers: Working Memory, Episodic Memory, and Semantic Project Memory.

## Core Workflow

### 1. Memory Layer Initialization
Establish a three-tier memory architecture in the repository:
```text
.agent/
├── memory/
│   ├── project-brief.json      # Semantic Memory: High-level vision, tech stack, rules
│   ├── decisions-log.jsonl     # Episodic Memory: Immutable append-only log of decisions
│   └── current-state.json      # Working Memory: Active task list, blockers, active branch
```

### 2. State Snapshotting Before Long-Running Operations
Before executing high-context operations (e.g. running 50 tests or large refactors), save the working state:
```json
{
  "timestamp": "2026-10-02T18:00:00Z",
  "active_task": "Refactor auth middleware to JWT v2",
  "completed_subtasks": ["Add token verification test", "Update interface"],
  "next_step": "Replace Express middleware in server.ts",
  "known_risks": ["Session cookies might invalidate existing users"]
}
```

### 3. Progressive Retrieval & Pruning
When restoring context after a session break:
1. Read `project-brief.json` for fixed invariants.
2. Read the last 5 records of `decisions-log.jsonl` to understand recent rationale.
3. Read `current-state.json` to resume the immediate next action.
4. Prune working memory records older than 14 days or compress completed tasks into summary milestones.

### 4. Conflict Resolution & Consistency Checks
If working memory contradicts current code on disk (e.g. code was modified by a human developer between agent runs):
1. Prioritize disk state (source code) as ground truth.
2. Update `current-state.json` to reflect current reality and append an entry to `decisions-log.jsonl` noting the reconciliation.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Memory file exceeds token budget (> 100KB) | Trigger memory summarization: summarize closed tasks and archive historical logs to `.agent/archive/`. |
| Concurrent agent writes | Use atomic write patterns (write to temporary file, then atomic rename) with POSIX file locks. |
| Memory contains sensitive secrets | Immediately redact secrets matching API key / token regexes before persisting to memory files. |

## Validation & Acceptance Criteria

- [ ] `.agent/memory/` structure exists with valid JSON schemas.
- [ ] No plaintext secrets or authorization tokens are persisted.
- [ ] The agent can successfully recover task state after a context restart without re-asking the user for baseline facts.

## Failure Handling & Recovery

- If memory files become corrupted, fall back to parsing `git log -n 10` and recent markdown notes, then regenerate clean memory files.

## Expected Output & Artifacts

- `.agent/memory/project-brief.json`
- `.agent/memory/decisions-log.jsonl`
- `.agent/memory/current-state.json`

## Related Skills

- `context-window-engineering`
- `agent-tool-use-reliability`
- `documentation-and-adrs`
"""
    },

    # -------------------------------------------------------------
    # 3. AI ENGINEERING / RAG: rag-retrieval-evaluation
    # -------------------------------------------------------------
    {
        "name": "rag-retrieval-evaluation",
        "domain": "ai-engineering",
        "category": "rag",
        "subcategory": "evaluation",
        "description": "Use this skill when evaluating, benchmarking, and optimizing the retrieval quality of a Retrieval-Augmented Generation (RAG) system. It guides the agent through calculating Recall@K, Precision@K, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG), and context relevance to eliminate hallucinations caused by poor context retrieval.",
        "tags": ["rag", "evaluation", "vector-search", "embeddings", "information-retrieval", "llm-benchmarking"],
        "technologies": ["Python", "Vector Databases", "Embeddings", "Ragas"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["python >= 3.9", "numpy"],
        "content": """# RAG Retrieval Evaluation

## Overview

A systematic evaluation and tuning workflow for Retrieval-Augmented Generation (RAG) systems. This skill enables agents to quantify retrieval accuracy, detect retrieval failures, diagnose embedding misalignment, and optimize chunking strategies to eliminate hallucinations caused by omitted or irrelevant context.

## When to Use

- Benchmarking retrieval performance of vector search, hybrid search, or dense retrieval pipelines.
- Investigating RAG hallucinations or evasive "I don't know" answers when documentation exists.
- Evaluating changes to chunk size, chunk overlap, embedding models, or re-ranking algorithms.
- Establishing automated CI/CD quality gates for enterprise search and RAG knowledge bases.

## When NOT to Use

- Pure generative style or tone evaluation (use `llm-output-quality-evaluation`).
- Vector database infrastructure scaling or cluster sharding (use `vector-database-performance-tuning`).

## Inputs & Prerequisites

- Ground-truth evaluation dataset containing: `query`, `ground_truth_context_ids`, and optional `ideal_answer`.
- Access to the retrieval function or vector search API endpoint.
- Python environment with NumPy or evaluation libraries (e.g. Ragas / TruLens).

## Core Workflow

### 1. Metric Selection & Target Thresholds
Establish core retrieval metrics:
- **Recall@K**: Proportion of relevant documents retrieved in top $K$ results (target: $\ge 0.85$ at $K=5$).
- **Precision@K**: Proportion of top $K$ retrieved documents that are actually relevant.
- **MRR (Mean Reciprocal Rank)**: Evaluates whether the primary correct document ranks at position 1.
- **NDCG@K**: Evaluates ranked order with graded relevance.
- **Context Relevance**: Measures the percentage of retrieved sentences that directly answer the query.

### 2. Retrieval Evaluation Execution
Run the evaluation test harness over the benchmark dataset:
```python
def evaluate_retrieval(query, retrieved_ids, ground_truth_ids, k=5):
    top_k = retrieved_ids[:k]
    relevant_retrieved = set(top_k).intersection(set(ground_truth_ids))
    recall = len(relevant_retrieved) / max(1, len(ground_truth_ids))
    precision = len(relevant_retrieved) / k
    reciprocal_rank = 0.0
    for idx, doc_id in enumerate(top_k):
        if doc_id in ground_truth_ids:
            reciprocal_rank = 1.0 / (idx + 1)
            break
    return {"recall@k": recall, "precision@k": precision, "mrr": reciprocal_rank}
```

### 3. Failure Mode Diagnosis
Categorize retrieval errors:
1. **Vocabulary Mismatch**: Query uses domain synonyms not captured in dense embeddings (Solution: Add BM25 hybrid search).
2. **Chunk Boundary Truncation**: Answer spans multiple chunks split by rigid character limits (Solution: Implement sentence-aware or semantic chunking with 20% overlap).
3. **Embedding Compression Loss**: Embedding fails to capture fine-grained numeric or entity details (Solution: Add metadata filtering or reciprocal rank fusion).
4. **Distractor Interference**: High similarity chunks containing outdated or conflicting policies rank above current data (Solution: Temporal decay weighting or reranking with cross-encoders).

### 4. Remediation & Tuning Plan
Execute step-by-step optimization:
- If Recall@5 < 0.70: Implement hybrid search (Dense vector + BM25 keyword).
- If Precision@5 < 0.50: Introduce a cross-encoder re-ranker (e.g. BGE-Reranker or Cohere Rerank) to filter noise.
- Re-run benchmark to verify metric improvement.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Synthetic test data generation needed | Use an LLM to generate diverse user queries (paraphrased, noisy, entity-specific) from raw source documents with labeled ground-truth chunks. |
| High retrieval latency | Limit cross-encoder reranking to top-20 retrieved candidates, returning top-5 to context window. |
| Mixed language queries | Evaluate cross-lingual embedding models (e.g. multilingual-e5) and inspect language identification steps. |

## Validation & Acceptance Criteria

- [ ] Benchmark test suite executed over at least 50 representative domain queries.
- [ ] Recall@K, Precision@K, and MRR quantified and logged.
- [ ] Failure analysis identifies root cause for every query scoring Recall < 0.50.
- [ ] Post-tuning benchmark proves measurable improvement over baseline.

## Failure Handling & Recovery

- If vector database connection drops during batch evaluation, checkpoint results after every 10 queries and resume automatically.

## Expected Output & Artifacts

- Evaluation scorecard report (`docs/rag-retrieval-benchmark.md`).
- Metric summary JSON (`metrics/retrieval-eval-results.json`).

## Related Skills

- `context-window-engineering`
- `llm-cost-and-latency-optimization`
- `model-evaluation-and-benchmarking`
"""
    },

    # -------------------------------------------------------------
    # 4. MCP: mcp-server-scaffold
    # -------------------------------------------------------------
    {
        "name": "mcp-server-scaffold",
        "domain": "mcp",
        "category": "server-development",
        "subcategory": "scaffolding",
        "description": "Use this skill when scaffolding, implementing, and validating a Model Context Protocol (MCP) server from scratch using TypeScript or Python. It guides the agent through configuring tool schemas, resource providers, prompt templates, stdio/SSE transports, error boundaries, and integration tests.",
        "tags": ["mcp", "model-context-protocol", "agent-tools", "typescript", "python", "api-integration"],
        "technologies": ["Model Context Protocol", "TypeScript", "Node.js", "Python"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["node", "npm", "python"],
        "dependencies": ["@modelcontextprotocol/sdk or mcp-python"],
        "content": """# MCP Server Scaffold

## Overview

A complete architectural guide for scaffolding, implementing, and validating Model Context Protocol (MCP) servers. Enables AI agents to expose clean, safe, and discoverable tools, resources, and prompt templates to client applications like Claude Code, Cursor, Windsurf, and Antigravity.

## When to Use

- Building a new custom MCP server to connect an agent to an internal API, database, or local utility.
- Exposing local system capabilities (filesystem, Git, docker, hardware) to an AI agent via standardized MCP schemas.
- Converting legacy CLI tools into standardized MCP tools with JSON schema validation.
- Establishing test harnesses and integration benchmarks for MCP servers.

## When NOT to Use

- Consuming an existing third-party MCP server (use `mcp-server-integration`).
- Building standard REST or GraphQL public web APIs (use `api-and-interface-design`).

## Inputs & Prerequisites

- Choice of runtime: TypeScript/Node.js (`@modelcontextprotocol/sdk`) or Python (`mcp`).
- Transport selection: `stdio` (for local CLI integration) or `SSE` (for remote network services).
- Tool definitions including JSON Schema specifications for inputs and return types.

## Core Workflow

### 1. Project Initialization & Dependencies
For TypeScript:
```bash
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
npx tsc --init
```

### 2. Server Architecture Setup
Create standard project layout:
```text
mcp-server/
├── src/
│   ├── index.ts          # Server initialization & transport binding
│   ├── tools/            # Individual tool implementations
│   ├── resources/        # Resource providers
│   └── schemas/          # Zod validation schemas
├── package.json
└── tsconfig.json
```

### 3. Tool Implementation with Strict Validation
Define tools using type-safe schemas:
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "custom-utility-server",
  version: "1.0.0"
});

server.tool(
  "query_database",
  "Executes a parameterized read-only SQL query against the application database",
  {
    query: z.string().describe("The SQL query to execute (SELECT only)"),
    params: z.array(z.any()).optional().describe("Query parameters")
  },
  async ({ query, params }) => {
    if (!query.trim().toUpperCase().startsWith("SELECT")) {
      return {
        isError: true,
        content: [{ type: "text", text: "Error: Only read-only SELECT queries are permitted." }]
      };
    }
    // Execution logic...
    return {
      content: [{ type: "text", text: JSON.stringify({ rows: [] }) }]
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
main().catch(console.error);
```

### 4. Resource & Prompt Registration
- Register resources using URI patterns (e.g. `system://metrics`, `repo://config`).
- Expose reusable prompt templates with parameterized arguments.

### 5. Transport Configuration & Verification
Verify that `stdio` transport does not write raw `console.log` messages to stdout, as this corrupts MCP JSON-RPC frames:
- Redirect internal debug logs to `stderr` (`console.error`).
- Test with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Large response payloads (> 100KB) | Paginate results or return a resource URI pointer instead of dumping large blobs into tool results. |
| Tool encounters runtime exception | Return `{ isError: true, content: [{ type: "text", text: error.message }] }` rather than crashing the MCP server process. |
| Stdio stdout corruption | Ensure all logging libraries are strictly configured to log to stderr or a disk file. |

## Validation & Acceptance Criteria

- [ ] MCP Server boots cleanly and connects over stdio without crashing.
- [ ] Tools correctly expose their JSON Schema definitions with field descriptions.
- [ ] Input validation rejects malformed parameters with clear error messages.
- [ ] No debug statements output to stdout.
- [ ] Verified compatible with MCP Inspector.

## Failure Handling & Recovery

- If client fails to discover tools, inspect `stderr` logs for schema validation failures during tool registration.

## Expected Output & Artifacts

- Complete runnable MCP server repository with package configs.
- Client configuration snippet (e.g. for `claude_desktop_config.json` or `antigravity.json`).

## Related Skills

- `mcp-server-debugging`
- `mcp-security-audit`
- `api-and-interface-design`
"""
    },

    # -------------------------------------------------------------
    # 5. SOFTWARE ENGINEERING: api-and-interface-design
    # -------------------------------------------------------------
    {
        "name": "api-and-interface-design",
        "domain": "software-engineering",
        "category": "architecture",
        "subcategory": "interfaces",
        "description": "Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles.",
        "tags": ["api-design", "architecture", "interface-contracts", "rest", "graphql", "typescript"],
        "technologies": ["REST", "GraphQL", "TypeScript", "OpenAPI", "JSON Schema"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["tsc", "curl"],
        "dependencies": ["typescript >= 4.5"],
        "content": """# API and Interface Design

## Overview

Design resilient, stable, and well-documented interfaces that are easy to use correctly and hard to misuse. Good interfaces make the right thing easy and the wrong thing hard. This applies to REST APIs, GraphQL schemas, internal module contracts, component props, and SDK public surfaces.

## When to Use

- Designing new public HTTP REST, gRPC, or GraphQL endpoints.
- Defining module boundaries or contracts between distributed teams or microservices.
- Establishing database access layer interfaces or repository patterns.
- Creating component prop contracts in frontend libraries.
- Changing or refactoring existing public interfaces with backwards compatibility requirements.

## When NOT to Use

- Quick, one-off internal helper scripts intended for immediate disposal.
- Internal private implementations hidden completely behind an existing stable interface.

## Inputs & Prerequisites

- High-level business requirements and entity models.
- Target transport protocol (REST, gRPC, TypeScript interface, GraphQL).
- Existing consumer constraints and backwards compatibility commitments.

## Core Workflow

### 1. Hyrum's Law Analysis & Surface Minimization
> "With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody, regardless of what you promise in the contract."

1. Expose the minimum necessary surface area.
2. Never leak internal implementation details (e.g. database column names, internal IDs, third-party vendor types).
3. Keep internal helper types unexported.

### 2. Contract Specification (Schema First)
Write the strict contract before writing implementation code:
- For REST: Produce OpenAPI 3.1 specification.
- For TypeScript: Define explicit input, output, and error types:
```typescript
export interface CreateOrderRequest {
  readonly customerId: string;
  readonly items: ReadonlyArray<{
    readonly productId: string;
    readonly quantity: number;
  }>;
  readonly idempotencyKey: string;
}

export type CreateOrderResult =
  | { readonly success: true; readonly orderId: string; readonly totalAmountCents: number }
  | { readonly success: false; readonly error: OrderCreationError };
```

### 3. Idempotency & Safe Mutation
For any non-idempotent operation (e.g. billing, order placement, message sending):
- Require an `Idempotency-Key` HTTP header or parameter.
- Cache operation results keyed by the idempotency key for at least 24 hours to prevent duplicate processing during network retries.

### 4. Explicit Error Hierarchy
Never return generic `500 Internal Server Error` without structured error taxonomy:
- Define machine-readable error codes: `INVALID_INPUT`, `RESOURCE_NOT_FOUND`, `RATE_LIMITED`, `UNAUTHORIZED`.
- Include safe user-facing message, machine code, and correlation ID:
```json
{
  "error": {
    "code": "PAYMENT_FAILED",
    "message": "The transaction was declined by the issuing bank.",
    "correlation_id": "req_8f1b2c3d"
  }
}
```

### 5. Evolution & Deprecation Strategy
- Never make breaking changes to an existing active version.
- Add optional fields rather than modifying or removing existing fields.
- When deprecating, mark fields with `@deprecated` in schemas and return `Sunset` HTTP headers.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Breaking change required | Introduce a new API version (e.g. `/v2/`) or new module interface, supporting the old version concurrently during a transition period. |
| Large dataset queries | Mandate cursor-based pagination (`cursor` & `limit`) rather than offset pagination to avoid performance degradation on deep scans. |
| Timezone ambiguity | Enforce ISO 8601 UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`) across all inputs and outputs. |

## Validation & Acceptance Criteria

- [ ] Schema is strictly typed and validates all edge-case inputs.
- [ ] Error scenarios return structured, predictable error payloads with machine-readable codes.
- [ ] Mutations support idempotency keys to prevent duplicate execution.
- [ ] Documentation includes complete request/response examples and failure scenarios.

## Failure Handling & Recovery

- If a consumer breaks due to an unintended change in timing or ordering, assess whether the behavior was an undocumented quirk, and apply compensating adapter layers.

## Expected Output & Artifacts

- OpenAPI YAML specification or TypeScript contract definition file.
- Comprehensive request/response fixtures for positive and negative test cases.

## Related Skills

- `code-review-and-quality`
- `deprecation-and-migration`
- `owasp-api-security-top-10`
"""
    },

    # -------------------------------------------------------------
    # 6. DATABASES: postgres-query-performance-analysis
    # -------------------------------------------------------------
    {
        "name": "postgres-query-performance-analysis",
        "domain": "databases",
        "category": "postgresql",
        "subcategory": "performance",
        "description": "Use this skill when diagnosing, analyzing, and optimizing slow PostgreSQL queries. It guides the agent through running and interpreting EXPLAIN (ANALYZE, BUFFERS), identifying sequential table scans, resolving missing indexes, fixing high buffer reads, eliminating N+1 query patterns, and tuning query planner configurations.",
        "tags": ["postgresql", "databases", "performance", "query-optimization", "indexing", "sql"],
        "technologies": ["PostgreSQL", "SQL", "pg_stat_statements"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["psql", "python"],
        "dependencies": ["postgresql >= 12"],
        "content": """# PostgreSQL Query Performance Analysis

## Overview

A systematic performance debugging and optimization guide for PostgreSQL. Enables AI agents to dissect execution plans using `EXPLAIN (ANALYZE, BUFFERS)`, identify memory and I/O bottlenecks, design targeted indexes, and rewrite pathological SQL queries to achieve sub-millisecond latencies.

## When to Use

- A production query exceeds latency budgets or causes API timeouts.
- CPU or I/O utilization spikes on the PostgreSQL database cluster.
- Reviewing new database migrations, views, or queries before merging to production.
- Auditing top slow queries identified by `pg_stat_statements`.

## When NOT to Use

- Hardware cluster failover, replication topology, or disk volume resizing (use `postgres-cluster-administration`).
- Non-relational key-value caching (use `redis-caching-patterns`).

## Inputs & Prerequisites

- Slow query SQL statement.
- Database connection via `psql` or application test harness.
- Execution plan output obtained with: `EXPLAIN (ANALYZE, BUFFERS, VERBOSE, SETTINGS) <query>;`.

## Core Workflow

### 1. Plan Extraction & Execution Metrics
Run the query wrapped in an explain block in a staging or read-replica environment:
```sql
EXPLAIN (ANALYZE, BUFFERS, COSTS, TIMING, SUMMARY)
SELECT u.id, u.email, count(o.id)
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at >= '2026-01-01'
GROUP BY u.id, u.email;
```

### 2. Plan Node Inspection & Bottleneck Triage
Examine the plan tree from innermost leaves to root:
1. **Sequential Scans (`Seq Scan`)**: Flag large tables scanned sequentially with high row counts.
2. **Buffer Hit Ratio**: Compare `Buffers: shared hit=X read=Y`. If `read` is high relative to `hit`, pages are being pulled from slow disk rather than RAM.
3. **Row Estimate Discrepancy**: Compare `rows=1` (estimated) with `actual rows=50000`. If disparate by orders of magnitude, database statistics are stale. Run: `ANALYZE <table>;`.
4. **Sort / Hash Spills**: Look for `Sort Method: external merge Disk`. This indicates `work_mem` is insufficient for in-memory sorting.

### 3. Targeted Index Engineering
Select the optimal index structure:
- **B-Tree**: Equality and range filters (`=`, `<`, `>`, `BETWEEN`).
- **Composite Index**: Multi-column filters. Order columns by: Equality first, then Range, then Sort (`WHERE status = 'active' AND date >= '2026-01-01' ORDER BY created_at`).
- **Covering Index (`INCLUDE`)**: Include selected columns to allow Index-Only Scans:
  ```sql
  CREATE INDEX CONCURRENTLY idx_users_created_at_covering
  ON users (created_at) INCLUDE (email);
  ```
- **Partial Index**: For heavily skewed boolean or status flags:
  ```sql
  CREATE INDEX CONCURRENTLY idx_orders_unprocessed
  ON orders (created_at) WHERE status = 'pending';
  ```

### 4. Query Rewriting Patterns
- Replace subqueries in `WHERE id IN (SELECT ...)` with `JOIN` or `EXISTS`.
- Eliminate `SELECT *` in favor of explicit required columns.
- Break massive monolithic queries using Common Table Expressions (`WITH`) or temporary staging tables.

### 5. Verification & Regression Check
1. Re-run `EXPLAIN (ANALYZE, BUFFERS)`.
2. Confirm the plan transitions from `Seq Scan` to `Index Scan` or `Index Only Scan`.
3. Verify total execution time and buffer read reductions.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| High production traffic during index creation | Always use `CREATE INDEX CONCURRENTLY` to prevent blocking concurrent writes. |
| Query planner ignores existing index | Check table size (planner prefers Seq Scan on small tables < 1000 rows). Check if column expression disables index (`WHERE LOWER(email) = ...` requires functional index). |
| Stale planner statistics | Run `ANALYZE <table>;` or increase `default_statistics_target` for frequently queried volatile columns. |

## Validation & Acceptance Criteria

- [ ] Query execution plan verified with `EXPLAIN (ANALYZE, BUFFERS)`.
- [ ] No unwanted Sequential Scans on tables exceeding 10,000 rows.
- [ ] No disk-based spills (`external merge Disk`).
- [ ] Index created with `CONCURRENTLY` flag in migration scripts.
- [ ] Query execution time reduced to target SLA (< 50ms for OLTP).

## Failure Handling & Recovery

- If creating an index concurrently fails or enters `INVALID` state, drop the invalid index (`DROP INDEX CONCURRENTLY <index>;`) and re-run after resolving table locks.

## Expected Output & Artifacts

- Diagnostic performance audit report.
- Safe SQL migration script with concurrent index definitions.
- Before-and-after execution plan metrics comparison.

## Related Skills

- `postgres-schema-migration-safety`
- `redis-caching-patterns`
- `api-and-interface-design`
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Sequential Skill Factory Deployment ({len(SKILLS_QUEUE)} skills)")
    print("=" * 70)

    for idx, skill in enumerate(SKILLS_QUEUE, 1):
        print(f"\n[{idx}/{len(SKILLS_QUEUE)}] Processing skill: {skill['name']} ({skill['domain']}/{skill['category']})")
        success = create_and_ship_skill(skill)
        if not success:
            print(f"ERROR: Failed processing skill {skill['name']}. Aborting sequence.")
            sys.exit(1)
        time.sleep(1)

    print("\n" + "=" * 70)
    print("All foundational skills successfully manufactured, validated, committed, and pushed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
