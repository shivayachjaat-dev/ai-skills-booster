---
name: postgres-query-performance-analysis
description: "Use this skill when diagnosing, analyzing, and optimizing slow PostgreSQL queries. It guides the agent through running and interpreting EXPLAIN (ANALYZE, BUFFERS), identifying sequential table scans, resolving missing indexes, fixing high buffer reads, eliminating N+1 query patterns, and tuning query planner configurations."
domain: databases
category: postgresql
subcategory: performance
tags:
  - postgresql
  - databases
  - performance
  - query-optimization
  - indexing
  - sql
technologies:
  - PostgreSQL
  - SQL
  - pg_stat_statements
complexity: advanced
maturity: stable
tools:
  - psql
  - python
dependencies:
  - postgresql >= 12
---
# PostgreSQL Query Performance Analysis

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
