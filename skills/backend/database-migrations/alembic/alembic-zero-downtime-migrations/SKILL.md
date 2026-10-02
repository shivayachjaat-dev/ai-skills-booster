---
name: alembic-zero-downtime-migrations
description: "Use this skill when designing, authoring, and executing online zero-downtime PostgreSQL schema migrations using Alembic and SQLAlchemy. It guides the agent through the Expand and Contract pattern, non-blocking asynchronous index creation with CREATE INDEX CONCURRENTLY, adding NOT NULL columns safely, and managing lock timeouts."
domain: backend
category: database-migrations
subcategory: alembic
tags:
  - alembic
  - sqlalchemy
  - migrations
  - zero-downtime
  - postgresql
  - python
technologies:
  - Alembic
  - SQLAlchemy
  - PostgreSQL
  - Python
complexity: advanced
maturity: stable
tools:
  - alembic
  - psql
  - python
dependencies:
  - alembic >= 1.13.0
  - sqlalchemy >= 2.0.0
---
# Alembic Zero-Downtime PostgreSQL Migrations Architecture

## Overview

A definitive production engineering reference for executing zero-downtime database schema migrations in PostgreSQL using Alembic. Traditional migrations that acquire exclusive table locks (`AccessExclusiveLock`) freeze incoming transactions, causing connection pool exhaustion and cascading HTTP 504 outages. This skill instructs AI agents on applying the Expand and Contract design pattern, creating indexes non-blocking via `CREATE INDEX CONCURRENTLY`, adding `NOT NULL` constraints safely, and enforcing lock timeouts.

## When to Use

- Migrating production PostgreSQL databases under active, high-volume transactional traffic.
- Adding non-blocking indexes to multi-million row tables.
- Renaming columns, dropping columns, or modifying data types without downtime.
- Adding mandatory (`NOT NULL`) columns without full table rewrites.

## When NOT to Use

- Greenfield development before launch where taking brief maintenance downtime is acceptable.
- Non-relational NoSQL databases (MongoDB, DynamoDB).

## Inputs & Prerequisites

- Python 3.10+ with `alembic` and `sqlalchemy` installed.
- PostgreSQL 14+ database.
- Database credentials with DDL privileges.

## Core Workflow

### 1. Enforcing Lock Timeouts (`env.py`)
Prevent migrations from blocking live application queries indefinitely:

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

def run_migrations_online():
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Enforce strict 2-second lock timeout: If an exclusive lock cannot be acquired
        # within 2 seconds, the migration fails fast rather than queueing and blocking traffic!
        connection.execute(connection.dialect.statement_compiler(None, None).process(
            "SET lock_timeout = '2s';"
        ))
        
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

### 2. Non-Blocking Index Creation (`CREATE INDEX CONCURRENTLY`)
Standard `CREATE INDEX` locks writes. Use `concurrently` within autocommit:

```python
# alembic/versions/xxxx_add_customer_email_idx.py
"""add customer email index concurrently

Revision ID: xxxx
Revises: wwww
Create Date: 2026-03-01
"""
from alembic import op

revision = 'xxxx'
down_revision = 'wwww'

def upgrade():
    # CONCURRENT index operations cannot execute inside a transactional block
    op.execute("COMMIT")
    op.execute(
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_email "
        "ON customers (email);"
    )

def downgrade():
    op.execute("COMMIT")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_customers_email;")
```

### 3. The Expand and Contract Pattern: Adding a `NOT NULL` Column
Never add `ALTER TABLE orders ADD COLUMN status VARCHAR NOT NULL DEFAULT 'pending'` on a table with 50M rows (rewrites table and locks it). Follow three decoupled phases:

```python
# Phase 1: Expand - Add column as NULLABLE (instant metadata update)
def upgrade():
    op.add_column("orders", sa.Column("status", sa.String(32), nullable=True))

# Phase 2: Application code writes to both old and new columns; backfill existing rows in batches
# UPDATE orders SET status = 'pending' WHERE status IS NULL LIMIT 5000;

# Phase 3: Contract - Add check constraint NOT VALID, validate it, and convert to NOT NULL
def upgrade():
    # Adding NOT VALID constraint requires only brief SHARE UPDATE EXCLUSIVE lock
    op.execute(
        "ALTER TABLE orders ADD CONSTRAINT chk_orders_status_not_null "
        "CHECK (status IS NOT NULL) NOT VALID;"
    )
    # Validates without blocking incoming reads/writes
    op.execute("ALTER TABLE orders VALIDATE CONSTRAINT chk_orders_status_not_null;")
```

## Best Practices & Failure Modes

1. **Transaction Queuing Disaster**: Running a migration without `SET lock_timeout` causes Alembic to wait for an active query. Behind Alembic, *all subsequent application reads and writes queue up*, exhausting connection pools within seconds. Always set `lock_timeout = '2s'`.
2. **Concurrently Inside Transaction**: Attempting `CREATE INDEX CONCURRENTLY` inside `with context.begin_transaction()` triggers `ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block`. Always break out via `op.execute("COMMIT")` or set `autocommit_block()`.
3. **Renaming Columns Directly**: Renaming a column (`ALTER TABLE t RENAME COLUMN a TO b`) immediately breaks running application containers expecting column `a`. Use Expand-and-Contract: create new column `b`, dual-write, backfill, migrate reads to `b`, then drop `a`.

## Verification & Testing

- Dry-run migration and inspect generated raw SQL:
  ```bash
  alembic upgrade head --sql
  ```
- Verify migration history and current database revision:
  ```bash
  alembic current
  alembic history --verbose
  ```
