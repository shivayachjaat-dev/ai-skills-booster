---
name: database-migration-safety
description: "Use this skill when authoring, reviewing, and applying database schema migrations in high-traffic production environments without downtime. It enforces the Expand and Contract pattern, non-blocking lock acquisition, safe column additions, asynchronous backfills, reversible rollbacks, and zero-downtime schema evolution."
domain: databases
category: migrations
subcategory: zero-downtime
tags:
  - databases
  - migrations
  - zero-downtime
  - postgresql
  - mysql
  - sql
  - devops
technologies:
  - PostgreSQL
  - MySQL
  - SQL
  - Liquibase
  - Prisma
complexity: advanced
maturity: stable
tools:
  - psql
  - python
dependencies:
  - postgresql >= 12 or mysql >= 8.0
---
# Database Migration Safety

## Overview

A zero-downtime database migration methodology for production relational databases. Instructs AI agents on executing schema changes without taking table-exclusive locks, avoiding API query timeouts, applying the Expand and Contract pattern for breaking changes, and deploying non-blocking data backfills.

## When to Use

- Writing or reviewing DDL migrations on tables containing > 100,000 rows.
- Renaming columns, changing column data types, or adding non-null constraints to existing tables.
- Creating or dropping indexes on production databases under active read/write load.
- Establishing migration safety guidelines and automated CI/CD migration linters.

## When NOT to Use

- Brand-new greenfield databases prior to production launch with zero user traffic.
- Analytical data warehouses (Snowflake, BigQuery) where transactional table locks do not apply.

## Inputs & Prerequisites

- Target SQL migration script.
- Target database engine (PostgreSQL, MySQL).
- Estimated table row count and read/write QPS.

## Core Workflow

### 1. The Expand and Contract Pattern for Breaking Changes
Never alter, rename, or drop a column in a single deployment:
1. **Phase 1 (Expand)**: Add the new column as nullable.
2. **Phase 2 (Dual-Write)**: Deploy application code that reads from the old column but writes to both old and new columns.
3. **Phase 3 (Backfill)**: Run an asynchronous background script to copy historical data from old column to new column in batches.
4. **Phase 4 (Read New)**: Deploy application code to read from the new column. Stop writing to the old column.
5. **Phase 5 (Contract)**: Drop the old column in a future migration once all services have transitioned.

### 2. Safe Column Additions with Defaults
In older PostgreSQL/MySQL versions, adding a column with a default value rewrote the entire table, holding an exclusive lock for minutes:
- In modern PostgreSQL (11+): `ALTER TABLE orders ADD COLUMN status_code VARCHAR DEFAULT 'pending';` is safe (metadata-only update).
- If adding `NOT NULL`: Add as nullable first, populate data, then add `NOT NULL` with a constraint check:
  ```sql
  -- Step 1: Add check constraint without validating existing rows
  ALTER TABLE orders ADD CONSTRAINT check_status_not_null CHECK (status_code IS NOT NULL) NOT VALID;
  -- Step 2: Validate concurrently without blocking reads or writes
  ALTER TABLE orders VALIDATE CONSTRAINT check_status_not_null;
  ```

### 3. Non-Blocking Index Operations
- **PostgreSQL**: ALWAYS use `CREATE INDEX CONCURRENTLY` and `DROP INDEX CONCURRENTLY`. Standard `CREATE INDEX` acquires an `ACCESS EXCLUSIVE` lock, halting all writes until index builds complete.
- Note: `CREATE INDEX CONCURRENTLY` cannot run inside a multi-statement transaction block (`BEGIN ... COMMIT`).

### 4. Lock Timeout Guards
Every migration script must set a strict lock timeout. If the migration cannot acquire the required table lock within 3 seconds, it must abort immediately rather than queuing up behind slow queries and blocking the entire connection pool:
```sql
SET lock_timeout = '3s';
SET statement_timeout = '30s';
ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE;
```

### 5. Batched Data Backfills
When migrating millions of rows, never run `UPDATE orders SET new_col = old_col;` in one transaction. This blows up WAL logs and causes severe replication lag. Backfill in indexed batches:
```sql
-- Batch 10,000 rows at a time
UPDATE orders
SET new_col = old_col
WHERE id BETWEEN 1 AND 10000;
-- Sleep 100ms between batches to allow replicas to catch up
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Migration aborts with lock timeout | Do not increase lock timeout. Investigate long-running transactions blocking the table and reschedule during lowest traffic window. |
| Concurrent index creation fails | Check index status: `SELECT indexrelid::regclass, indisvalid FROM pg_index WHERE ...`. If `indisvalid = false`, drop concurrently and recreate. |
| Foreign key addition | Add constraint with `NOT VALID`, then validate in a separate step: `ALTER TABLE ... VALIDATE CONSTRAINT ...`. |

## Validation & Acceptance Criteria

- [ ] Lock timeout set on all DDL statements (`SET lock_timeout = '3s'`).
- [ ] No `CREATE INDEX` statements without `CONCURRENTLY` flag.
- [ ] Breaking column changes follow multi-phase Expand and Contract protocol.
- [ ] Data backfills run in bounded batches (< 10,000 rows per batch).
- [ ] Down migration / rollback script authored and verified.

## Failure Handling & Recovery

- If a migration script locks up connections, cancel the migration immediately (`SELECT pg_cancel_backend(pid);`) to restore service availability.

## Expected Output & Artifacts

- Phase-separated SQL migration scripts.
- Asynchronous batch backfill script.
- Reversible rollback migration script.

## Related Skills

- `postgres-query-performance-analysis`
- `api-and-interface-design`
- `ci-cd-and-automation`
