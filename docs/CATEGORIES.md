# Skill Categories & Directory Map

Master navigation for **112** skills across structured domains, categories, and subcategories.

## Ai Engineering (17 skills)

### Agents (6 skills)
Category index: [`docs/categories/agents.md`](categories/agents.md)

- **Autogen** (1):
  - [multi-agent-debate-and-reflection](../skills/ai-engineering/agents/autogen/multi-agent-debate-and-reflection/SKILL.md) — Use this skill when designing, implementing, and evaluating multi-agent debate, reflection, and self-correction workflows. It guides the agent through constructing multi-turn debate topologies (Proposer, Critic, Reflector), consensus scoring mechanisms, majority voting, eliminating groupthink and confirmation bias, and improving reasoning accuracy on complex tasks.
- **Benchmarking** (1):
  - [ai-agent-benchmark-evaluation](../skills/ai-engineering/agents/benchmarking/ai-agent-benchmark-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and grading autonomous AI agents across multi-step execution tasks. It guides the agent through establishing reproducible mock environments, measuring task completion rates, analyzing tool calling trajectory efficiency, computing hallucination indices, and detecting regression degradation across model releases.
- **Fault Injection** (1):
  - [ai-agent-chaos-testing-and-fault-injection](../skills/ai-engineering/agents/fault-injection/ai-agent-chaos-testing-and-fault-injection/SKILL.md) — Use this skill when stress-testing, chaos-testing, and verifying the fault-tolerance of autonomous AI agents and tool-calling pipelines. It guides the agent through simulating tool API failures, network timeouts, corrupt JSON payloads, context window truncation, and verifying agent self-healing and recovery strategies.
- **Memory** (1):
  - [agent-project-memory](../skills/ai-engineering/agents/memory/agent-project-memory/SKILL.md) — Use this skill when designing, maintaining, or recovering persistent memory and architectural context across long-running AI agent sessions. It establishes structured memory stores, state serialization protocols, session recovery checkpoints, and active context pruning to prevent context loss during complex projects.
- **Orchestration** (1):
  - [multi-agent-consensus-protocol](../skills/ai-engineering/agents/orchestration/multi-agent-consensus-protocol/SKILL.md) — Use this skill when designing, orchestrating, and coordinating multi-agent systems requiring consensus, debate, and validation. It guides the agent through role-specialized multi-agent topologies (Generator-Critic, Committee Voting, Delphi Consensus), conflict resolution protocols, shared scratchpad synchronization, and infinite circular argument prevention.
- **Process Management** (1):
  - [multi-agent-tmux-process-orchestrator](../skills/ai-engineering/agents/process-management/multi-agent-tmux-process-orchestrator/SKILL.md) — Use this skill when managing, supervising, and coordinating multiple autonomous CLI coding agents and subprocesses across detached terminal sessions using tmux. It covers automated tmux session and pane lifecycle management, sending keystrokes and instructions (send-keys), monitoring stdout/stderr activity buffers, and auto-restarting stalled agent workers.

### Context (1 skills)
Category index: [`docs/categories/context.md`](categories/context.md)

- **Optimization** (1):
  - [context-window-engineering](../skills/ai-engineering/context/optimization/context-window-engineering/SKILL.md) — Use this skill when managing, structuring, and compressing context windows for LLMs and autonomous agents. It enforces prompt caching alignment, 'lost in the middle' attention optimization, dynamic token budget allocation, semantic pruning, and multi-turn message compaction to maximize reasoning accuracy while minimizing latency and token costs.

### Evaluation (3 skills)
Category index: [`docs/categories/evaluation.md`](categories/evaluation.md)

- **Deepeval** (1):
  - [deepeval-unit-testing-llm-apps](../skills/ai-engineering/evaluation/deepeval/deepeval-unit-testing-llm-apps/SKILL.md) — Use this skill when designing, authoring, and automating CI/CD unit testing suites for Large Language Model applications using DeepEval. It guides the agent through defining LLM test cases (LLMTestCase), configuring G-Eval custom criteria metrics, hallucination and answer relevancy scoring, integrating with pytest, and setting regression assertions.
- **Promptfoo** (1):
  - [promptfoo-llm-eval-benchmarking](../skills/ai-engineering/evaluation/promptfoo/promptfoo-llm-eval-benchmarking/SKILL.md) — Use this skill when designing, executing, and automating LLM prompt evaluations and adversarial red-teaming benchmarks using promptfoo. It guides the agent through defining test matrices (providers x prompts x variables), configuring deterministic and LLM-as-a-judge assertions, running red-team vulnerability scans, and integrating evaluations into CI/CD pipelines.
- **Ragas Rag Evaluation** (1):
  - [ragas-rag-triad-evaluation](../skills/ai-engineering/evaluation/ragas-rag-evaluation/ragas-rag-triad-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and auditing Retrieval-Augmented Generation (RAG) pipelines using RAGAS and the RAG Triad framework. It guides the agent through calculating Faithfulness (hallucination detection), Answer Relevance, Context Precision, and Context Recall, building synthetic evaluation datasets, and CI automated regression gating.

### Fine Tuning (1 skills)
Category index: [`docs/categories/fine-tuning.md`](categories/fine-tuning.md)

- **Peft Lora** (1):
  - [llm-lora-fine-tuning-pipeline](../skills/ai-engineering/fine-tuning/peft-lora/llm-lora-fine-tuning-pipeline/SKILL.md) — Use this skill when designing, training, and evaluating parameter-efficient fine-tuning (PEFT) pipelines for Large Language Models using LoRA and QLoRA. It guides the agent through 4-bit/8-bit quantization via bitsandbytes, LoRA hyperparameter configuration (rank r, alpha, target modules), dataset preparation and token masking, SFTTrainer orchestration, and adapter weight merging.

### Guardrails (1 skills)
Category index: [`docs/categories/guardrails.md`](categories/guardrails.md)

- **Input Output Moderation** (1):
  - [llm-guardrails-input-output-moderation](../skills/ai-engineering/guardrails/input-output-moderation/llm-guardrails-input-output-moderation/SKILL.md) — Use this skill when designing, implementing, and deploying enterprise safety guardrails for Large Language Model applications. It guides the agent through prompt injection detection, sensitive PII redaction (Presidio), toxic output moderation (Llama Guard), strict JSON schema validation, and fallback circuit breaking.

### Inference Optimization (1 skills)
Category index: [`docs/categories/inference-optimization.md`](categories/inference-optimization.md)

- **Vllm** (1):
  - [vllm-high-throughput-inference-serving](../skills/ai-engineering/inference-optimization/vllm/vllm-high-throughput-inference-serving/SKILL.md) — Use this skill when architecting, configuring, and deploying high-throughput LLM serving infrastructure using vLLM. It guides the agent through PagedAttention memory management, continuous dynamic batching, tensor parallelism for multi-GPU distribution, prefix caching for long prompts, and hosting OpenAI-compatible API servers.

### Quantization (1 skills)
Category index: [`docs/categories/quantization.md`](categories/quantization.md)

- **Gguf Llama Cpp** (1):
  - [llm-quantization-gguf-and-awq](../skills/ai-engineering/quantization/gguf-llama-cpp/llm-quantization-gguf-and-awq/SKILL.md) — Use this skill when quantizing, optimizing, and compressing Large Language Models for efficient CPU and GPU inference using GGUF (llama.cpp) and AWQ (Activation-aware Weight Quantization). It guides the agent through GGUF k-quant selection (Q4_K_M vs Q5_K_M vs Q8_0), AWQ 4-bit tensor calibration, perplexity evaluation against WikiText-2, and benchmark testing.

### Rag (1 skills)
Category index: [`docs/categories/rag.md`](categories/rag.md)

- **Evaluation** (1):
  - [rag-retrieval-evaluation](../skills/ai-engineering/rag/evaluation/rag-retrieval-evaluation/SKILL.md) — Use this skill when evaluating, benchmarking, and optimizing the retrieval quality of a Retrieval-Augmented Generation (RAG) system. It guides the agent through calculating Recall@K, Precision@K, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG), and context relevance to eliminate hallucinations caused by poor context retrieval.

### Synthetic Data (1 skills)
Category index: [`docs/categories/synthetic-data.md`](categories/synthetic-data.md)

- **Synth Data Pipeline** (1):
  - [llm-synthetic-data-generation-pipeline](../skills/ai-engineering/synthetic-data/synth-data-pipeline/llm-synthetic-data-generation-pipeline/SKILL.md) — Use this skill when designing, orchestrating, and validating synthetic data generation pipelines for training, evaluating, and fine-tuning Large Language Models. It covers Self-Instruct seed bootstrapping, Evol-Instruct complexity expansion (in-breadth and in-depth), vector embedding semantic deduplication, and automated quality filtering using frontier LLM judges.

### Vector Databases (1 skills)
Category index: [`docs/categories/vector-databases.md`](categories/vector-databases.md)

- **Indexing** (1):
  - [vector-database-rag-indexing](../skills/ai-engineering/vector-databases/indexing/vector-database-rag-indexing/SKILL.md) — Use this skill when architecting, building, and optimizing high-scale vector database indexing pipelines for Retrieval-Augmented Generation (RAG). It guides the agent through chunking strategies, dense embedding generation, approximate nearest neighbor (ANN) index selection (HNSW vs IVF vs ScaNN), payload metadata schema design, hybrid dense-sparse search, and index warm-up.

## Backend (14 skills)

### Api Design (1 skills)
Category index: [`docs/categories/api-design.md`](categories/api-design.md)

- **Rate Limiting** (1):
  - [api-rate-limiting-and-throttling](../skills/backend/api-design/rate-limiting/api-rate-limiting-and-throttling/SKILL.md) — Use this skill when designing, implementing, and tuning API rate limiters and request throttling systems. It guides the agent through algorithm selection (Token Bucket, Leaky Bucket, Sliding Window Counter), distributed synchronization with Redis, HTTP 429 response formatting, Tier-based limits, and atomic Lua script execution to prevent race conditions.

### Background Tasks (1 skills)
Category index: [`docs/categories/background-tasks.md`](categories/background-tasks.md)

- **Celery** (1):
  - [celery-distributed-task-processing](../skills/backend/background-tasks/celery/celery-distributed-task-processing/SKILL.md) — Use this skill when designing, configuring, and operating asynchronous distributed task queues using Celery in Python. It covers broker connection tuning (Redis/RabbitMQ), exponential backoff retry strategies, task canvas workflows (chains, groups, chords), task deduplication, and worker concurrency optimization.

### Caching (1 skills)
Category index: [`docs/categories/caching.md`](categories/caching.md)

- **Redis Streams** (1):
  - [redis-streams-event-processing](../skills/backend/caching/redis-streams/redis-streams-event-processing/SKILL.md) — Use this skill when architecting, implementing, and operating event-driven stream processing systems using Redis Streams. It guides the agent through appending events with XADD, managing competing Consumer Groups with XREADGROUP, tracking the Pending Entries List (PEL), dead-lettering abandoned messages via XAUTOCLAIM, and stream memory trimming with MAXLEN.

### Database Drivers (2 skills)
Category index: [`docs/categories/database-drivers.md`](categories/database-drivers.md)

- **Drizzle** (1):
  - [drizzle-orm-schema-and-relational-queries](../skills/backend/database-drivers/drizzle/drizzle-orm-schema-and-relational-queries/SKILL.md) — Use this skill when designing database schemas, managing type-safe migrations, and querying SQL databases with Drizzle ORM in TypeScript. It guides the agent through pgTable declarations, relations API (1:1, 1:N, M:N), Drizzle Kit migrations (generate/migrate), prepared statements for maximum performance, and serverless pooling.
- **Sqlalchemy** (1):
  - [sqlalchemy-async-session-management](../skills/backend/database-drivers/sqlalchemy/sqlalchemy-async-session-management/SKILL.md) — Use this skill when architecting asynchronous database access layers in Python using SQLAlchemy 2.0+ and asyncpg. It guides the agent through AsyncEngine configuration, connection pooling with pool_pre_ping, scoped async session lifecycles, eager loading strategies (selectinload vs joinedload), and atomic transaction context managers.

### Database Migrations (1 skills)
Category index: [`docs/categories/database-migrations.md`](categories/database-migrations.md)

- **Alembic** (1):
  - [alembic-zero-downtime-migrations](../skills/backend/database-migrations/alembic/alembic-zero-downtime-migrations/SKILL.md) — Use this skill when designing, authoring, and executing online zero-downtime PostgreSQL schema migrations using Alembic and SQLAlchemy. It guides the agent through the Expand and Contract pattern, non-blocking asynchronous index creation with CREATE INDEX CONCURRENTLY, adding NOT NULL columns safely, and managing lock timeouts.

### Fastapi (1 skills)
Category index: [`docs/categories/fastapi.md`](categories/fastapi.md)

- **Async Architecture** (1):
  - [fastapi-async-api-design](../skills/backend/fastapi/async-architecture/fastapi-async-api-design/SKILL.md) — Use this skill when building high-performance, asynchronous REST APIs with FastAPI, Pydantic v2, and async database drivers. It guides the agent through dependency injection patterns, async/await event loop blocking prevention, structured error handlers, lifespan context managers, and OpenAPI schema generation.

### Graphql (2 skills)
Category index: [`docs/categories/graphql.md`](categories/graphql.md)

- **Federation** (1):
  - [apollo-federation-subgraph-architecture](../skills/backend/graphql/federation/apollo-federation-subgraph-architecture/SKILL.md) — Use this skill when designing, composing, and operating distributed GraphQL schemas using Apollo Federation v2. It guides the agent through defining entity keys (@key), entity resolvers (__resolveReference), sharing types (@shareable), migrating fields across subgraphs (@override), schema composition with Rover CLI, and Gateway/Router routing.
- **Schema Design** (1):
  - [graphql-schema-evolution](../skills/backend/graphql/schema-design/graphql-schema-evolution/SKILL.md) — Use this skill when designing, versioning, and evolving GraphQL schemas without breaking existing mobile and web clients. It guides the agent through schema-first SDL design, non-breaking deprecation directives (@deprecated), resolving the N+1 query problem using DataLoader, input union patterns, and automated breaking-change detection in CI.

### Grpc (1 skills)
Category index: [`docs/categories/grpc.md`](categories/grpc.md)

- **Services** (1):
  - [grpc-service-implementation](../skills/backend/grpc/services/grpc-service-implementation/SKILL.md) — Use this skill when designing, compiling, and implementing high-performance gRPC microservices with Protocol Buffers (proto3). It guides the agent through defining .proto service contracts, bidirectional streaming, gRPC interceptors for auth/logging, deadline/cancellation propagation, HTTP/2 multiplexing, and gRPC status code error handling.

### Message Queues (1 skills)
Category index: [`docs/categories/message-queues.md`](categories/message-queues.md)

- **Rabbitmq** (1):
  - [rabbitmq-reliable-messaging-patterns](../skills/backend/message-queues/rabbitmq/rabbitmq-reliable-messaging-patterns/SKILL.md) — Use this skill when designing, building, and operating mission-critical message queuing architectures with RabbitMQ (AMQP 0-9-1). It guides the agent through publisher confirms (ACK/NACK), queue and message durability, dead letter exchanges (DLX) for poisoned messages, consumer manual acknowledgments with prefetch limits, and consumer idempotency.

### Messaging (1 skills)
Category index: [`docs/categories/messaging.md`](categories/messaging.md)

- **Kafka** (1):
  - [kafka-event-driven-architecture](../skills/backend/messaging/kafka/kafka-event-driven-architecture/SKILL.md) — Use this skill when designing, implementing, and tuning event-driven architectures with Apache Kafka. It guides the agent through partition key selection, consumer group rebalance minimization, exactly-once processing semantics (EOS), schema evolution with Avro/Protobuf, dead letter queues (DLQ), and producer idempotency.

### Realtime (1 skills)
Category index: [`docs/categories/realtime.md`](categories/realtime.md)

- **Websocket** (1):
  - [websocket-realtime-communication](../skills/backend/realtime/websocket/websocket-realtime-communication/SKILL.md) — Use this skill when designing, building, and scaling bi-directional real-time WebSocket applications. It guides the agent through WebSocket handshake upgrade, heartbeat ping/pong keepalive frames, horizontal clustering using Redis Pub/Sub backplanes, reconnection backoff with message replay buffers, and binary frame optimization.

### Resilience (1 skills)
Category index: [`docs/categories/resilience.md`](categories/resilience.md)

- **Rate Limiter Token Bucket** (1):
  - [distributed-rate-limiting-token-bucket](../skills/backend/resilience/rate-limiter-token-bucket/distributed-rate-limiting-token-bucket/SKILL.md) — Use this skill when designing, implementing, and deploying high-performance distributed rate limiters using the Token Bucket and Sliding Window algorithms with Redis and Lua. It guides the agent through atomic Redis Lua script execution, burst handling, tier-based limits (per IP, per API key, per tenant), and standard HTTP 429 response headers (X-RateLimit-* and Retry-After).

## Business (3 skills)

### Finance (1 skills)
Category index: [`docs/categories/finance.md`](categories/finance.md)

- **Audit Controls** (1):
  - [internal-financial-audit-and-controls](../skills/business/finance/audit-controls/internal-financial-audit-and-controls/SKILL.md) — Use this skill when designing, testing, and automating internal financial accounting controls, journal entry audit trails, and reconciliation workflows compliant with SOX 404, GAAP, and IFRS. It guides the agent through general ledger reconciliation, manual journal entry approval thresholds, segregation of duties in treasury, and anomaly detection.

### Human Resources (1 skills)
Category index: [`docs/categories/human-resources.md`](categories/human-resources.md)

- **Performance Management** (1):
  - [employee-360-feedback-review-system](../skills/business/human-resources/performance-management/employee-360-feedback-review-system/SKILL.md) — Use this skill when designing, configuring, and operating multi-rater 360-degree performance feedback systems. It guides the agent through peer reviewer nomination workflows, role-specific competency rubrics, anonymous vs attributed visibility rules, cognitive bias mitigation (recency and halo effects), and synthesis reporting.

### Procurement (1 skills)
Category index: [`docs/categories/procurement.md`](categories/procurement.md)

- **Software Selection** (1):
  - [enterprise-software-selection-and-rfp](../skills/business/procurement/software-selection/enterprise-software-selection-and-rfp/SKILL.md) — Use this skill when evaluating, scoring, and selecting commercial-off-the-shelf (COTS) and SaaS software solutions through evidence-backed scoring matrices and Request for Proposal (RFP) processes. It covers requirements weighting, compliance auditing (SOC2, HIPAA, GDPR), Total Cost of Ownership (TCO) modeling, security reviews, and vendor pilot proof-of-concepts.

## Data Analytics (4 skills)

### Dashboards (1 skills)
Category index: [`docs/categories/dashboards.md`](categories/dashboards.md)

- **Operational Metrics** (1):
  - [real-time-operational-metrics-dashboard](../skills/data-analytics/dashboards/operational-metrics/real-time-operational-metrics-dashboard/SKILL.md) — Use this skill when designing, building, and instrumenting real-time operational metrics registers and analytics dashboards. It establishes strict KPI naming schemas, SQL/semantic definitions, data refresh intervals, target/threshold alerting, and integration with Grafana, Superset, or Metabase.

### Data Pipelines (1 skills)
Category index: [`docs/categories/data-pipelines.md`](categories/data-pipelines.md)

- **Polars** (1):
  - [polars-high-throughput-data-pipeline](../skills/data-analytics/data-pipelines/polars/polars-high-throughput-data-pipeline/SKILL.md) — Use this skill when processing, transforming, and analyzing large tabular datasets exceeding memory limits using Polars. It guides the agent through lazy evaluation (LazyFrame), streaming execution, predicate/projection pushdown, memory-mapped Parquet I/O, and Apache Arrow zero-copy transformations.

### Data Warehouse (1 skills)
Category index: [`docs/categories/data-warehouse.md`](categories/data-warehouse.md)

- **Snowflake** (1):
  - [snowflake-data-warehouse-modeling](../skills/data-analytics/data-warehouse/snowflake/snowflake-data-warehouse-modeling/SKILL.md) — Use this skill when architecting, modeling, and optimizing enterprise data warehouses in Snowflake. It guides the agent through multi-cluster virtual warehouse sizing, micro-partition clustering keys, zero-copy cloning for staging environments, time travel data recovery, and continuous ingestion with Snowpipe.

### Experimentation (1 skills)
Category index: [`docs/categories/experimentation.md`](categories/experimentation.md)

- **Ab Testing** (1):
  - [ab-test-experiment-design](../skills/data-analytics/experimentation/ab-testing/ab-test-experiment-design/SKILL.md) — Use this skill when designing, sizing, and analyzing A/B and multivariate split experiments. It guides the agent through statistical hypothesis formulation, sample size calculation via power analysis, minimum detectable effect (MDE) estimation, guardrail metric tracking, CUPED variance reduction, and p-value significance evaluation.

## Databases (11 skills)

### Clickhouse (1 skills)
Category index: [`docs/categories/clickhouse.md`](categories/clickhouse.md)

- **Time Series** (1):
  - [clickhouse-time-series-analytics](../skills/databases/clickhouse/time-series/clickhouse-time-series-analytics/SKILL.md) — Use this skill when designing, partitioning, and querying massive time-series event logs and telemetry in ClickHouse. It guides the agent through selecting MergeTree table engines, primary key and sorting key design, TTL data aging policies, materialized views for real-time aggregations, and high-throughput batched ingestion.

### Duckdb (1 skills)
Category index: [`docs/categories/duckdb.md`](categories/duckdb.md)

- **Analytics** (1):
  - [duckdb-embedded-analytics](../skills/databases/duckdb/analytics/duckdb-embedded-analytics/SKILL.md) — Use this skill when embedding DuckDB for high-speed local analytical queries (OLAP) directly inside Python or Node.js runtimes. It guides the agent through querying remote Parquet files on S3/HTTP without downloading, executing fast vectorized window aggregations, zero-copy Apache Arrow integration, and replacing heavy database infrastructure for medium-data analytics.

### Migrations (1 skills)
Category index: [`docs/categories/migrations.md`](categories/migrations.md)

- **Zero Downtime** (1):
  - [database-migration-safety](../skills/databases/migrations/zero-downtime/database-migration-safety/SKILL.md) — Use this skill when authoring, reviewing, and applying database schema migrations in high-traffic production environments without downtime. It enforces the Expand and Contract pattern, non-blocking lock acquisition, safe column additions, asynchronous backfills, reversible rollbacks, and zero-downtime schema evolution.

### Nosql (2 skills)
Category index: [`docs/categories/nosql.md`](categories/nosql.md)

- **Neo4J** (1):
  - [neo4j-graph-data-modeling-and-cypher](../skills/databases/nosql/neo4j/neo4j-graph-data-modeling-and-cypher/SKILL.md) — Use this skill when designing, indexing, and querying labeled property graphs using Neo4j 5+ and Cypher query language. It guides the agent through node and relationship property modeling, index and constraint declarations, variable-length path traversal, aggregation with WITH clauses, and optimizing Cypher queries using PROFILE and EXPLAIN.
- **Scylladb** (1):
  - [scylladb-high-throughput-nosql-architecture](../skills/databases/nosql/scylladb/scylladb-high-throughput-nosql-architecture/SKILL.md) — Use this skill when architecting, modeling, and operating distributed, ultra-low-latency NoSQL databases with ScyllaDB (Apache Cassandra compatible). It guides the agent through shard-per-core asynchronous architecture, CQL partition and clustering key design, tuning consistency levels (LOCAL_QUORUM), tombstone prevention, and driver connection pooling.

### Orm (1 skills)
Category index: [`docs/categories/orm.md`](categories/orm.md)

- **Prisma** (1):
  - [prisma-schema-migration-and-relations](../skills/databases/orm/prisma/prisma-schema-migration-and-relations/SKILL.md) — Use this skill when architecting database schemas, managing relational migrations, and optimizing database queries using Prisma ORM (TypeScript/Node.js). It covers complex relationship modeling (1:1, 1:N, M:N explicit join tables), zero-downtime migration workflows (`prisma migrate dev/deploy`), connection pooling with PgBouncer, and avoiding N+1 query traps.

### Postgresql (1 skills)
Category index: [`docs/categories/postgresql.md`](categories/postgresql.md)

- **Performance** (1):
  - [postgres-query-performance-analysis](../skills/databases/postgresql/performance/postgres-query-performance-analysis/SKILL.md) — Use this skill when diagnosing, analyzing, and optimizing slow PostgreSQL queries. It guides the agent through running and interpreting EXPLAIN (ANALYZE, BUFFERS), identifying sequential table scans, resolving missing indexes, fixing high buffer reads, eliminating N+1 query patterns, and tuning query planner configurations.

### Redis (1 skills)
Category index: [`docs/categories/redis.md`](categories/redis.md)

- **Caching** (1):
  - [redis-caching-patterns](../skills/databases/redis/caching/redis-caching-patterns/SKILL.md) — Use this skill when designing, implementing, and optimizing caching strategies using Redis. It guides the agent through selecting appropriate patterns (Cache-Aside, Write-Through, Write-Behind), mitigating cache stampedes (dogpiling) using probabilistic early expiration (XFetch) or mutex locks, avoiding cache penetration with Bloom filters, and configuring TTL jitter.

### Search (2 skills)
Category index: [`docs/categories/search.md`](categories/search.md)

- **Elasticsearch** (1):
  - [elasticsearch-dsl-search-and-aggregations](../skills/databases/search/elasticsearch/elasticsearch-dsl-search-and-aggregations/SKILL.md) — Use this skill when architecting, indexing, and querying complex search and analytical systems using Elasticsearch 8+ and Elasticsearch-DSL. It guides the agent through explicit index mapping design (analyzers, keyword vs text fields), boolean compound queries (must, filter, should), multi-match cross-field queries, and multi-level nested aggregations.
- **Meilisearch** (1):
  - [meilisearch-full-text-search-integration](../skills/databases/search/meilisearch/meilisearch-full-text-search-integration/SKILL.md) — Use this skill when designing, indexing, and querying lightning-fast, typo-tolerant full-text search systems using Meilisearch. It guides the agent through index configuration, searchable vs filterable attributes, custom ranking rules, document batching, faceted navigation, and building search-as-you-type frontend experiences.

### Time Series (1 skills)
Category index: [`docs/categories/time-series.md`](categories/time-series.md)

- **Timescaledb** (1):
  - [timescaledb-hypertables-and-retention](../skills/databases/time-series/timescaledb/timescaledb-hypertables-and-retention/SKILL.md) — Use this skill when architecting, partitioning, and optimizing high-throughput time-series databases with TimescaleDB on PostgreSQL. It guides the agent through hypertable creation, chunk time interval sizing, continuous aggregates with automatic refresh policies, column-oriented compression policies, and data retention drops.

## Devops (16 skills)

### Ci Cd (1 skills)
Category index: [`docs/categories/ci-cd.md`](categories/ci-cd.md)

- **Optimization** (1):
  - [github-actions-ci-pipeline-optimization](../skills/devops/ci-cd/optimization/github-actions-ci-pipeline-optimization/SKILL.md) — Use this skill when auditing, accelerating, and optimizing GitHub Actions CI/CD workflows. It guides the agent through dependency caching strategies (actions/cache), matrix test parallelization, path filtering triggers, Docker layer caching in CI, artifact retention policies, and security hardening (minimal GITHUB_TOKEN permissions).

### Container Orchestration (1 skills)
Category index: [`docs/categories/container-orchestration.md`](categories/container-orchestration.md)

- **Helm** (1):
  - [helm-chart-architecture-and-lifecycle](../skills/devops/container-orchestration/helm/helm-chart-architecture-and-lifecycle/SKILL.md) — Use this skill when architecting, authoring, and managing production-grade Kubernetes packages with Helm 3+. It guides the agent through chart file structures, named template helpers (_helpers.tpl), strict values schema validation using values.schema.json, dependency subcharts, test suites (helm test), and semantic versioning release workflows.

### Containers (1 skills)
Category index: [`docs/categories/containers.md`](categories/containers.md)

- **Optimization** (1):
  - [docker-container-optimization](../skills/devops/containers/optimization/docker-container-optimization/SKILL.md) — Use this skill when auditing, shrinking, and hardening Docker container images. It guides the agent through multi-stage builds, cache-efficient layer ordering, non-root user enforcement, minimal distroless/alpine base images, and vulnerability scanning with Trivy/Docker Scout.

### Continuous Delivery (1 skills)
Category index: [`docs/categories/continuous-delivery.md`](categories/continuous-delivery.md)

- **Flagger** (1):
  - [flagger-canary-progressive-delivery](../skills/devops/continuous-delivery/flagger/flagger-canary-progressive-delivery/SKILL.md) — Use this skill when designing, configuring, and automating canary progressive delivery on Kubernetes using Flagger and service meshes (Istio/Linkerd). It covers Canary CRD resource declarations, automated metric analysis (request success rate, P99 latency via Prometheus), progressive traffic stepping (10% to 50%), automated rollback on anomalies, and webhook alerting.

### Continuous Integration (1 skills)
Category index: [`docs/categories/continuous-integration.md`](categories/continuous-integration.md)

- **Github Reusable Workflows** (1):
  - [github-actions-reusable-workflows-and-composite-actions](../skills/devops/continuous-integration/github-reusable-workflows/github-actions-reusable-workflows-and-composite-actions/SKILL.md) — Use this skill when designing, architecting, and standardizing enterprise CI/CD pipelines using GitHub Actions Reusable Workflows (workflow_call) and Composite Actions. It covers modular parameter passing, secret inheritance, matrix job fan-out, action packaging with action.yaml, and cross-repository pipeline governance.

### Gitops (1 skills)
Category index: [`docs/categories/gitops.md`](categories/gitops.md)

- **Argo Cd** (1):
  - [argocd-gitops-continuous-delivery](../skills/devops/gitops/argo-cd/argocd-gitops-continuous-delivery/SKILL.md) — Use this skill when designing, configuring, and operating GitOps continuous delivery workflows on Kubernetes using Argo CD. It guides the agent through Application and ApplicationSet CRD declarations, automated self-healing and pruning sync policies, sync waves and resource hooks, multi-tenant RBAC, and repository secrets integration.

### Iac (1 skills)
Category index: [`docs/categories/iac.md`](categories/iac.md)

- **Terraform** (1):
  - [terraform-infrastructure-as-code](../skills/devops/iac/terraform/terraform-infrastructure-as-code/SKILL.md) — Use this skill when writing, refactoring, and maintaining Infrastructure as Code (IaC) using Terraform / OpenTofu. It guides the agent through remote state management with S3/DynamoDB locking, modular component design, variable validation rules, drift detection, resource tagging standards, and blast radius containment.

### Infrastructure As Code (2 skills)
Category index: [`docs/categories/infrastructure-as-code.md`](categories/infrastructure-as-code.md)

- **Ansible** (1):
  - [ansible-idempotent-configuration-management](../skills/devops/infrastructure-as-code/ansible/ansible-idempotent-configuration-management/SKILL.md) — Use this skill when designing, authoring, and executing automated server configuration management playbooks and roles using Ansible. It guides the agent through enforcing strict task idempotency, structuring reusable Ansible roles, managing encrypted secrets with Ansible Vault, organizing inventory variables, and testing with Molecule.
- **Terraform Modules** (1):
  - [terraform-module-design-and-testing](../skills/devops/infrastructure-as-code/terraform-modules/terraform-module-design-and-testing/SKILL.md) — Use this skill when architecting, authoring, and testing reusable Infrastructure as Code (IaC) modules with Terraform and OpenTofu. It guides the agent through root and child module contracts, custom input variable validations, structured outputs, dynamic blocks, version pinning, and automated integration testing using Terratest in Go.

### Kubernetes (1 skills)
Category index: [`docs/categories/kubernetes.md`](categories/kubernetes.md)

- **Troubleshooting** (1):
  - [kubernetes-crashloop-debugging](../skills/devops/kubernetes/troubleshooting/kubernetes-crashloop-debugging/SKILL.md) — Use this skill when diagnosing and recovering Kubernetes Pods stuck in CrashLoopBackOff, Error, OOMKilled, or Pending states. It guides the agent through inspecting exit codes, previous container logs, describe events, resource limits, readiness/liveness probe misconfigurations, and volume mount failures.

### Monitoring (2 skills)
Category index: [`docs/categories/monitoring.md`](categories/monitoring.md)

- **Prometheus** (2):
  - [prometheus-grafana-observability](../skills/devops/monitoring/prometheus/prometheus-grafana-observability/SKILL.md) — Use this skill when designing, instrumenting, and deploying application monitoring stacks using Prometheus metrics and Grafana dashboards. It guides the agent through the Four Golden Signals (Latency, Traffic, Errors, Saturation), metric type selection (Counter, Gauge, Histogram, Summary), PromQL query authoring, and actionable Alertmanager alerting rules.
  - [prometheus-metrics-instrumentation](../skills/devops/monitoring/prometheus/prometheus-metrics-instrumentation/SKILL.md) — Use this skill when instrumenting backend microservices with Prometheus metrics. It guides the agent through selecting metric types (Counter, Gauge, Histogram, Summary), enforcing the RED and USE monitoring methods, label cardinality management to avoid memory exhaustion, and authoring alerting rules (PromQL).

### Observability (3 skills)
Category index: [`docs/categories/observability.md`](categories/observability.md)

- **Grafana Loki** (1):
  - [grafana-loki-log-aggregation](../skills/devops/observability/grafana-loki/grafana-loki-log-aggregation/SKILL.md) — Use this skill when designing, configuring, and querying horizontally scalable log aggregation systems using Grafana Loki and Promtail / Grafana Alloy. It guides the agent through label cardinality management to prevent index explosion, authoring LogQL queries and metric extractions, configuring structured metadata, and creating LogQL alerting rules.
- **Opentelemetry** (1):
  - [opentelemetry-distributed-tracing](../skills/devops/observability/opentelemetry/opentelemetry-distributed-tracing/SKILL.md) — Use this skill when designing, instrumenting, and troubleshooting end-to-end distributed tracing across microservices using OpenTelemetry (OTel). It covers W3C tracecontext propagation, OTLP gRPC/HTTP exporters, head-based and tail-based sampling strategies, span attributes standardization (semantic conventions), and collector deployment.
- **Opentelemetry Collector** (1):
  - [opentelemetry-collector-pipeline-routing](../skills/devops/observability/opentelemetry-collector/opentelemetry-collector-pipeline-routing/SKILL.md) — Use this skill when architecting, configuring, and scaling OpenTelemetry (OTel) Collector pipelines. It guides the agent through defining receivers (OTLP gRPC/HTTP), core processors (memory_limiter, batch, filter, transform), routing connectors (routing connector), multi-backend exporters (Prometheus, Jaeger, Tempo, Loki), and tuning collector throughput.

### Service Mesh (1 skills)
Category index: [`docs/categories/service-mesh.md`](categories/service-mesh.md)

- **Istio** (1):
  - [istio-service-mesh-traffic-routing](../skills/devops/service-mesh/istio/istio-service-mesh-traffic-routing/SKILL.md) — Use this skill when implementing advanced traffic management, security policies, and canary deployments using the Istio Service Mesh. It guides the agent through VirtualService routing rules, DestinationRule subset definitions, mutual TLS (mTLS) PeerAuthentication enforcement, fault injection, and Envoy sidecar proxy tuning.

## Frontend (5 skills)

### 3D Graphics (1 skills)
Category index: [`docs/categories/3d-graphics.md`](categories/3d-graphics.md)

- **Threejs** (1):
  - [threejs-3d-web-experience](../skills/frontend/3d-graphics/threejs/threejs-3d-web-experience/SKILL.md) — Use this skill when designing, implementing, and optimizing interactive 3D web experiences using Three.js and React Three Fiber (R3F). It guides the agent through scene graph architecture, GLTF/GLB model loading and compression (Draco/Meshopt), custom GLSL shaders, camera controls (OrbitControls), lighting and shadows, and 60 FPS mobile performance optimization.

### Accessibility (1 skills)
Category index: [`docs/categories/accessibility.md`](categories/accessibility.md)

- **Wcag** (1):
  - [wcag-accessibility-audit](../skills/frontend/accessibility/wcag/wcag-accessibility-audit/SKILL.md) — Use this skill when auditing, testing, and remediating web interfaces for compliance with WCAG 2.2 AA standards. It guides the agent through automated scanning with axe-core, keyboard focus trapping, ARIA roles, color contrast ratio verification, accessible forms, screen reader announcement trees, and responsive zoom testing.

### Nextjs (1 skills)
Category index: [`docs/categories/nextjs.md`](categories/nextjs.md)

- **Architecture** (1):
  - [nextjs-app-router-architecture](../skills/frontend/nextjs/architecture/nextjs-app-router-architecture/SKILL.md) — Use this skill when architecting and developing full-stack web applications with Next.js App Router (version 14+ / 15+). It guides the agent through React Server Components (RSC) vs Client Components boundaries, Server Actions with Zod validation, streaming SSR with Suspense boundaries, parallel and intercepting routes, dynamic segment caching, and revalidation (ISR).

### React (1 skills)
Category index: [`docs/categories/react.md`](categories/react.md)

- **Architecture** (1):
  - [react-component-architecture](../skills/frontend/react/architecture/react-component-architecture/SKILL.md) — Use this skill when designing, refactoring, and structuring scalable React component hierarchies. It enforces clean separation of concerns between presentational components and stateful containers, headless UI patterns, compound components, strict TypeScript prop contracts, and memoization boundaries.

### State Management (1 skills)
Category index: [`docs/categories/state-management.md`](categories/state-management.md)

- **Zustand** (1):
  - [zustand-state-management-patterns](../skills/frontend/state-management/zustand/zustand-state-management-patterns/SKILL.md) — Use this skill when designing, structuring, and optimizing global client-side state in React applications using Zustand. It guides the agent through the slice pattern for modular domain separation, persistent middleware (localStorage/IndexedDB), selector optimization with shallow equality, DevTools debugging, and async action flows.

## Marketing (2 skills)

### Creative (1 skills)
Category index: [`docs/categories/creative.md`](categories/creative.md)

- **Ad Creative** (1):
  - [high-converting-ad-creative-design](../skills/marketing/creative/ad-creative/high-converting-ad-creative-design/SKILL.md) — Use this skill to research, generate, test, and optimize high-converting multi-platform ad copy, creative variations, hooks, angles, and CTA matrices for Google Search/Display, Meta (Facebook/Instagram), LinkedIn B2B, and TikTok campaigns. It enforces strict platform character constraints, psychological hook archetypes, and creative fatigue rotation policies.

### Paid Advertising (1 skills)
Category index: [`docs/categories/paid-advertising.md`](categories/paid-advertising.md)

- **Campaign Analytics** (1):
  - [cross-channel-ad-campaign-analytics](../skills/marketing/paid-advertising/campaign-analytics/cross-channel-ad-campaign-analytics/SKILL.md) — Use this skill when analyzing, attributing, and optimizing multi-channel paid advertising campaigns across Google Ads, Meta Ads, LinkedIn, and programmatic channels. It guides the agent through calculating Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), attribution modeling (First-Touch, Last-Touch, Data-Driven Markov), statistical significance in spend allocation, and budget rebalancing.

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

## Mobile (1 skills)

### Ios (1 skills)
Category index: [`docs/categories/ios.md`](categories/ios.md)

- **App Clips** (1):
  - [ios-app-clip-architecture](../skills/mobile/ios/app-clips/ios-app-clip-architecture/SKILL.md) — Use this skill when designing, building, and configuring iOS App Clips for on-demand, lightweight app experiences without full App Store installations. It guides the agent through Apple App Clip target creation in Xcode/Expo, bundle size optimization (< 15MB or 50MB on iOS 17+), Associated Domains configuration (appclips:), Apple Pay and Sign in with Apple integration, and App Clip code invocation.

## Programming Languages (2 skills)

### Golang (1 skills)
Category index: [`docs/categories/golang.md`](categories/golang.md)

- **Concurrency** (1):
  - [golang-goroutine-concurrency-patterns](../skills/programming-languages/golang/concurrency/golang-goroutine-concurrency-patterns/SKILL.md) — Use this skill when designing, implementing, and debugging concurrent systems in Go. It guides the agent through worker pool patterns, context cancellation propagation (context.Context), channel synchronization (buffered vs unbuffered), race condition prevention using the Go race detector (-race), errgroup error aggregation, and graceful shutdown.

### Rust (1 skills)
Category index: [`docs/categories/rust.md`](categories/rust.md)

- **Memory Safety** (1):
  - [rust-memory-safety-and-lifetimes](../skills/programming-languages/rust/memory-safety/rust-memory-safety-and-lifetimes/SKILL.md) — Use this skill when designing, writing, and refactoring Rust code to navigate the borrow checker, manage explicit lifetimes ('a), prevent allocations through zero-copy borrowing, handle interior mutability (RefCell/Mutex), and structure safe concurrency without data races.

## Security (22 skills)

### Ai Security (1 skills)
Category index: [`docs/categories/ai-security.md`](categories/ai-security.md)

- **Defense** (1):
  - [prompt-injection-defense](../skills/security/ai-security/defense/prompt-injection-defense/SKILL.md) — Use this skill when auditing, hardening, and protecting LLM applications and agent pipelines against direct and indirect prompt injection attacks. It guides the agent through untrusted data boundary separation, XML tagging, dual-model verification, output validation guardrails, and tool execution privilege sandboxing.

### Application Security (2 skills)
Category index: [`docs/categories/application-security.md`](categories/application-security.md)

- **Cors Csrf** (1):
  - [cors-csrf-web-security-hardening](../skills/security/application-security/cors-csrf/cors-csrf-web-security-hardening/SKILL.md) — Use this skill when designing, implementing, and auditing Cross-Origin Resource Sharing (CORS) and Cross-Site Request Forgery (CSRF) defenses for web APIs and single-page applications. It guides the agent through strict origin allowlists, preflight OPTION request caching, SameSite cookie strategies, double-submit cookie patterns, and Sec-Fetch-* metadata header verification.
- **Security Headers** (1):
  - [http-security-headers-hardening](../skills/security/application-security/security-headers/http-security-headers-hardening/SKILL.md) — Use this skill when auditing, configuring, and hardening HTTP security headers for web applications and APIs. It guides the agent through Content-Security-Policy (CSP) with dynamic cryptographic nonces, Strict-Transport-Security (HSTS), X-Content-Type-Options, Permissions-Policy, Referrer-Policy, and Cross-Origin Resource isolation headers (COOP, COEP, CORP).

### Architecture (1 skills)
Category index: [`docs/categories/architecture.md`](categories/architecture.md)

- **Zero Trust** (1):
  - [zero-trust-network-architecture](../skills/security/architecture/zero-trust/zero-trust-network-architecture/SKILL.md) — Use this skill when designing, assessing, and enforcing Zero Trust Network Architecture (ZTNA) across distributed services. It guides the agent through eliminating implicit perimeter trust, mutual TLS (mTLS) service mesh identity, ephemeral device attestation, microsegmentation policies, and continuous context-aware authorization.

### Authentication (1 skills)
Category index: [`docs/categories/authentication.md`](categories/authentication.md)

- **Oauth2** (1):
  - [oauth2-jwt-authentication-flow](../skills/security/authentication/oauth2/oauth2-jwt-authentication-flow/SKILL.md) — Use this skill when designing, implementing, and securing OAuth 2.1 and OpenID Connect (OIDC) authentication flows with JSON Web Tokens (JWT). It enforces Authorization Code Flow with PKCE, asymmetric RS256 signature verification, refresh token rotation with reuse detection, claims validation, and centralized revocation blacklists.

### Authorization (1 skills)
Category index: [`docs/categories/authorization.md`](categories/authorization.md)

- **Rbac** (1):
  - [rbac-access-matrix-policy-design](../skills/security/authorization/rbac/rbac-access-matrix-policy-design/SKILL.md) — Use this skill when designing, auditing, and implementing Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) permission matrices. It guides the agent through defining fine-grained permission scopes (resource:action), modeling roles vs groups, resolving permission conflicts, detecting privilege escalation risks, and enforcing policy gates in middleware.

### Code Review (1 skills)
Category index: [`docs/categories/code-review.md`](categories/code-review.md)

- **Github** (1):
  - [github-pr-security-review](../skills/security/code-review/github/github-pr-security-review/SKILL.md) — Use this skill when reviewing a GitHub pull request for security vulnerabilities, exposed secrets, unsafe dependencies, injection risks, authentication flaws, or insecure CI/CD modifications. It guides the agent through systematic threat modeling, diff inspection, risk severity classification, and remediation generation.

### Cryptography (1 skills)
Category index: [`docs/categories/cryptography.md`](categories/cryptography.md)

- **Envelope Encryption** (1):
  - [envelope-encryption-kms-pattern](../skills/security/cryptography/envelope-encryption/envelope-encryption-kms-pattern/SKILL.md) — Use this skill when architecting and implementing cryptographic envelope encryption for sensitive data at rest using cloud Key Management Services (AWS KMS, GCP KMS, Azure Key Vault) or HashiCorp Vault. It guides the agent through two-tier key hierarchies (KEK and DEK), AES-256-GCM authenticated encryption, DEK caching with TTL limits, and key rotation.

### Identity Governance (2 skills)
Category index: [`docs/categories/identity-governance.md`](categories/identity-governance.md)

- **Access Review** (1):
  - [identity-access-review-and-certification](../skills/security/identity-governance/access-review/identity-access-review-and-certification/SKILL.md) — Use this skill when designing, automating, and conducting periodic Identity Access Reviews, user entitlement certifications, and least-privilege compliance audits. It covers generating access certification campaigns, flagging dormant accounts, detecting toxic permission combinations (Segregation of Duties - SoD), and producing audit evidence for SOC2/ISO27001.
- **Admin Register** (1):
  - [privileged-access-and-admin-account-register](../skills/security/identity-governance/admin-register/privileged-access-and-admin-account-register/SKILL.md) — Use this skill when cataloging, auditing, and enforcing governance policies over privileged administrator accounts and break-glass emergency credentials across SaaS, cloud infrastructure, and internal systems. It guides the agent through structuring an Admin Access Register, enforcing mandatory MFA/WebAuthn, designated backup owners, and access justification logs.

### Incident Response (1 skills)
Category index: [`docs/categories/incident-response.md`](categories/incident-response.md)

- **Triage** (1):
  - [incident-response-and-triage](../skills/security/incident-response/triage/incident-response-and-triage/SKILL.md) — Use this skill when triaging, containing, and investigating active production security incidents and data breaches. It guides the agent through the PICERL framework (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned), evidence preservation without anti-forensic contamination, forensic log isolation, and root-cause analysis.

### Network Security (1 skills)
Category index: [`docs/categories/network-security.md`](categories/network-security.md)

- **Wireguard** (1):
  - [wireguard-site-to-site-mesh-vpn](../skills/security/network-security/wireguard/wireguard-site-to-site-mesh-vpn/SKILL.md) — Use this skill when designing, configuring, and maintaining secure site-to-site and point-to-point mesh VPN networks using WireGuard. It covers Curve25519 cryptographic key generation, wg-quick configuration files, AllowedIPs routing tables, persistent keepalives behind NAT, and network firewall forwarding rules.

### Penetration Testing (1 skills)
Category index: [`docs/categories/penetration-testing.md`](categories/penetration-testing.md)

- **Active Directory** (1):
  - [active-directory-security-assessment](../skills/security/penetration-testing/active-directory/active-directory-security-assessment/SKILL.md) — Use this skill when auditing, assessing, and hardening Microsoft Active Directory (AD) and hybrid Azure AD/Entra ID environments against common identity attack vectors. It guides the agent through identifying Kerberoasting vulnerabilities, AS-REP roasting, BloodHound attack path mapping, DCSync credential dumping risks, and Active Directory Certificate Services (ADCS) misconfigurations.

### Secret Management (1 skills)
Category index: [`docs/categories/secret-management.md`](categories/secret-management.md)

- **Detection** (1):
  - [secret-leak-detection-and-remediation](../skills/security/secret-management/detection/secret-leak-detection-and-remediation/SKILL.md) — Use this skill when detecting, containing, revoking, and purging secrets committed to Git repositories or build artifacts. It guides the agent through scanning history with TruffleHog/Gitleaks, executing emergency credential revocation, rewriting Git history with git-filter-repo, and installing pre-commit guardrails.

### Secrets (1 skills)
Category index: [`docs/categories/secrets.md`](categories/secrets.md)

- **Vault** (1):
  - [vault-secrets-management](../skills/security/secrets/vault/vault-secrets-management/SKILL.md) — Use this skill when architecting and managing enterprise secrets using HashiCorp Vault. It guides the agent through dynamic database credentials generation, lease management and renewal, Kubernetes ServiceAccount authentication, PKI on-demand certificate issuance, transit encryption, and disaster recovery replication.

### Supply Chain (1 skills)
Category index: [`docs/categories/supply-chain.md`](categories/supply-chain.md)

- **Cosign** (1):
  - [cosign-container-image-signing](../skills/security/supply-chain/cosign/cosign-container-image-signing/SKILL.md) — Use this skill when designing, implementing, and enforcing cryptographic container image signing and verification using Sigstore Cosign. It covers keyless signing via OIDC (GitHub Actions/GitLab CI), public/private keypair signing, SBOM attestation attachment, and enforcing Kubernetes admission policies with Kyverno or Gatekeeper.

### Threat Modeling (1 skills)
Category index: [`docs/categories/threat-modeling.md`](categories/threat-modeling.md)

- **Stride** (1):
  - [stride-threat-modeling-and-security-audit](../skills/security/threat-modeling/stride/stride-threat-modeling-and-security-audit/SKILL.md) — Use this skill when performing comprehensive threat modeling, architectural attack surface analysis, and security auditing using the STRIDE and PASTA methodologies. It guides the agent through data flow diagramming (DFDs), threat enumeration across trust boundaries, mitigations mapping to OWASP standards, and risk scoring.

### Vulnerability Management (1 skills)
Category index: [`docs/categories/vulnerability-management.md`](categories/vulnerability-management.md)

- **Dependency Check** (1):
  - [software-supply-chain-sbom-audit](../skills/security/vulnerability-management/dependency-check/software-supply-chain-sbom-audit/SKILL.md) — Use this skill when auditing, generating, and verifying Software Bill of Materials (SBOM) and scanning software supply chains for CVE vulnerabilities and non-compliant open-source licenses. It guides the agent through generating CycloneDX/SPDX SBOMs with Syft, scanning for known exploits with Grype, validating software licenses, and enforcing CI/CD gates.

### Vulnerability Scanning (1 skills)
Category index: [`docs/categories/vulnerability-scanning.md`](categories/vulnerability-scanning.md)

- **Trivy** (1):
  - [container-vulnerability-scanning-trivy](../skills/security/vulnerability-scanning/trivy/container-vulnerability-scanning-trivy/SKILL.md) — Use this skill when auditing, scanning, and enforcing security policies across container images, filesystems, and Software Bill of Materials (SBOM) using Aqua Security Trivy. It guides the agent through CI/CD gate automation, severity threshold enforcement (CRITICAL/HIGH), CVE filtering via .trivyignore, and generating CycloneDX SBOMs.

### Zero Trust (3 skills)
Category index: [`docs/categories/zero-trust.md`](categories/zero-trust.md)

- **Boundary** (1):
  - [hashicorp-boundary-secure-remote-access](../skills/security/zero-trust/boundary/hashicorp-boundary-secure-remote-access/SKILL.md) — Use this skill when designing, configuring, and operating identity-aware secure remote access architectures using HashiCorp Boundary. It guides the agent through defining Scopes (Global, Org, Project), dynamic host catalogs (AWS/K8s), targets (SSH, PostgreSQL, Kubernetes), credential brokering with Vault, and session recording.
- **Mfa Webauthn** (1):
  - [webauthn-fido2-passkey-authentication](../skills/security/zero-trust/mfa-webauthn/webauthn-fido2-passkey-authentication/SKILL.md) — Use this skill when designing, implementing, and securing passwordless authentication and multi-factor authentication (MFA) using WebAuthn, FIDO2, and Passkeys. It covers registration and authentication ceremony state machines, cryptographic challenge verification, public key credential storage, authenticator attestation, and signature counter verification.
- **Spiffe Spire** (1):
  - [spiffe-spire-workload-identity](../skills/security/zero-trust/spiffe-spire/spiffe-spire-workload-identity/SKILL.md) — Use this skill when designing and deploying cryptographic zero-trust workload identities across heterogeneous cloud and Kubernetes environments using SPIFFE and SPIRE. It covers SPIFFE ID naming conventions, SPIRE Server and Agent architecture, node attestation (AWS/K8s PSAT), Workload Attestation, and automated X.509 SVID issuance and rotation.

## Software Engineering (9 skills)

### Architecture (2 skills)
Category index: [`docs/categories/architecture.md`](categories/architecture.md)

- **Hexagonal** (1):
  - [hexagonal-ports-and-adapters-architecture](../skills/software-engineering/architecture/hexagonal/hexagonal-ports-and-adapters-architecture/SKILL.md) — Use this skill when architecting backend systems using Hexagonal Architecture (Ports and Adapters / Clean Architecture). It guides the agent through domain model isolation, designing driving (inbound) and driven (outbound) port interfaces, implementing swappable adapters (FastAPI, CLI, PostgreSQL, Mock), and structuring dependency injection.
- **Interfaces** (1):
  - [api-and-interface-design](../skills/software-engineering/architecture/interfaces/api-and-interface-design/SKILL.md) — Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles.

### Code Review (1 skills)
Category index: [`docs/categories/code-review.md`](categories/code-review.md)

- **Pr Feedback** (1):
  - [github-pr-review-feedback-resolver](../skills/software-engineering/code-review/pr-feedback/github-pr-review-feedback-resolver/SKILL.md) — Use this skill when processing, triage-categorizing, and systematically addressing code review feedback and comments on pull requests. It guides the agent through parsing inline diff suggestions, verifying requested changes locally with test suites, pushing atomic fix commits, replying to reviewers with context, and resolving comment threads.

### Debugging (1 skills)
Category index: [`docs/categories/debugging.md`](categories/debugging.md)

- **Recovery** (1):
  - [debugging-and-error-recovery](../skills/software-engineering/debugging/recovery/debugging-and-error-recovery/SKILL.md) — Use this skill when diagnosing obscure bugs, production failures, memory leaks, race conditions, or unhandled exceptions. It enforces scientific hypothesis-driven debugging, minimal reproduction synthesis, stack trace isolation, binary search bisecting, and permanent regression test installation.

### Design Patterns (2 skills)
Category index: [`docs/categories/design-patterns.md`](categories/design-patterns.md)

- **Event Sourcing** (1):
  - [event-sourcing-and-cqrs-architecture](../skills/software-engineering/design-patterns/event-sourcing/event-sourcing-and-cqrs-architecture/SKILL.md) — Use this skill when architecting and implementing Event Sourcing and Command Query Responsibility Segregation (CQRS) systems. It guides the agent through aggregate root design, immutable append-only event streams, optimistic concurrency control via sequence numbers, read model projections, and snapshotting strategies.
- **Saga Pattern** (1):
  - [distributed-saga-orchestration-pattern](../skills/software-engineering/design-patterns/saga-pattern/distributed-saga-orchestration-pattern/SKILL.md) — Use this skill when designing, implementing, and coordinating multi-service distributed transactions across microservices using the Saga Pattern (Orchestrator and Choreography). It guides the agent through defining forward actions, reliable compensating rollback transactions, state machine persistence, outbox pattern integration, and handling network partitions.

### Modernization (1 skills)
Category index: [`docs/categories/modernization.md`](categories/modernization.md)

- **Migration** (1):
  - [legacy-system-strangler-migration](../skills/software-engineering/modernization/migration/legacy-system-strangler-migration/SKILL.md) — Use this skill when incrementally modernizing, decomposing, and replacing legacy monoliths or deprecated backend systems without risky all-at-once cutovers. It guides the agent through the Strangler Fig pattern, reverse proxy intercept routing, parallel run shadow verification, database synchronization, and progressive decommission.

### Refactoring (1 skills)
Category index: [`docs/categories/refactoring.md`](categories/refactoring.md)

- **Simplification** (1):
  - [code-simplification](../skills/software-engineering/refactoring/simplification/code-simplification/SKILL.md) — Use this skill when simplifying convoluted code, eliminating accidental complexity, unwinding deeply nested conditionals, and removing speculative abstractions. It guides the agent through guard clauses, cyclomatic complexity reduction, dead code pruning, and establishing transparent data flow.

### Resilience (1 skills)
Category index: [`docs/categories/resilience.md`](categories/resilience.md)

- **Circuit Breaker** (1):
  - [microservices-resilience-circuit-breaker](../skills/software-engineering/resilience/circuit-breaker/microservices-resilience-circuit-breaker/SKILL.md) — Use this skill when designing, implementing, and tuning resilience patterns for distributed microservices. It guides the agent through Circuit Breaker state machines (Closed, Open, Half-Open), sliding window error rate calculation, exponential backoff with full jitter, bulkheads, fallback degradation, and health check probe integration.

## Testing (4 skills)

### Acceptance Testing (1 skills)
Category index: [`docs/categories/acceptance-testing.md`](categories/acceptance-testing.md)

- **Bdd Orchestration** (1):
  - [e2e-acceptance-testing-orchestrator](../skills/testing/acceptance-testing/bdd-orchestration/e2e-acceptance-testing-orchestrator/SKILL.md) — Use this skill when orchestrating end-to-end acceptance testing pipelines, behavior-driven development (BDD) workflows, and automated issue acceptance verification. It guides the agent through converting user stories into executable Gherkin specifications, integrating Playwright and Behave/Cucumber, managing test data fixtures, and enforcing release acceptance criteria.

### Component (1 skills)
Category index: [`docs/categories/component.md`](categories/component.md)

- **Cypress** (1):
  - [cypress-component-testing](../skills/testing/component/cypress/cypress-component-testing/SKILL.md) — Use this skill when authoring, running, and debugging isolated component tests using Cypress Component Testing for React, Vue, or Angular. It guides the agent through mounting components in real browser DOMs, asserting visual states, stubbing network requests via cy.intercept, simulating user events, and verifying CSS animations without firing up full backend environments.

### E2E (1 skills)
Category index: [`docs/categories/e2e.md`](categories/e2e.md)

- **Playwright** (1):
  - [playwright-e2e-testing](../skills/testing/e2e/playwright/playwright-e2e-testing/SKILL.md) — Use this skill when authoring, debugging, and maintaining end-to-end (E2E) automated browser test suites using Playwright. It guides the agent through resilient locator strategies (user-facing role/text), page object models, network mocking, authenticated session caching, parallel execution, and flaky test elimination.

### Load Testing (1 skills)
Category index: [`docs/categories/load-testing.md`](categories/load-testing.md)

- **K6** (1):
  - [k6-api-load-testing](../skills/testing/load-testing/k6/k6-api-load-testing/SKILL.md) — Use this skill when designing, executing, and analyzing performance and stress load test suites for backend APIs using Grafana k6. It guides the agent through defining Virtual User (VU) ramping stages, establishing SLA performance thresholds (P95/P99 latency, error rate), simulating realistic traffic patterns, and identifying database concurrency bottlenecks.
