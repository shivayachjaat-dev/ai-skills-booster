---
name: duckdb-embedded-analytics
description: "Use this skill when embedding DuckDB for high-speed local analytical queries (OLAP) directly inside Python or Node.js runtimes. It guides the agent through querying remote Parquet files on S3/HTTP without downloading, executing fast vectorized window aggregations, zero-copy Apache Arrow integration, and replacing heavy database infrastructure for medium-data analytics."
domain: databases
category: duckdb
subcategory: analytics
tags:
  - duckdb
  - databases
  - analytics
  - olap
  - sql
  - parquet
  - python
technologies:
  - DuckDB
  - Python
  - SQL
  - Parquet
  - Apache Arrow
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - duckdb >= 0.10
  - pyarrow
---
# DuckDB Embedded Analytics

## Overview

A guide for executing high-performance analytical queries (OLAP) directly within application processes using DuckDB. Often referred to as "the SQLite for Analytics", DuckDB utilizes columnar vectorized execution, parallel processing, and direct Parquet/Arrow querying to deliver sub-second analytical aggregations across millions of rows without requiring external database servers.

## When to Use

- Executing complex analytical SQL queries (aggregations, window functions, percentiles) inside Python, Node.js, or CLI tools.
- Querying remote Parquet, CSV, or JSON files directly from AWS S3, Cloudflare R2, or HTTP endpoints without downloading the entire dataset.
- Building embedded analytical dashboards, CLI reporting utilities, or data science notebooks.
- Analyzing datasets between 10MB and 100GB faster and with less memory than Pandas.

## When NOT to Use

- High-concurrency online transactional processing (OLTP) with thousands of concurrent small row-level writes (use PostgreSQL).
- Distributed petabyte-scale big data clusters (use Snowflake or BigQuery).

## Inputs & Prerequisites

- Python 3.9+ with `duckdb` installed (`pip install duckdb`).
- Tabular data files in Parquet, CSV, JSON, or in-memory Pandas/Polars DataFrames.

## Core Workflow

### 1. In-Memory vs Persistent Database Initialization
Connect in-memory for ephemeral processing, or attach to a local file for persistent storage:
```python
import duckdb

# In-memory database (zero disk footprint)
con = duckdb.connect(database=":memory:")

# Or persistent database file
con_disk = duckdb.connect(database="analytics.duckdb")
```

### 2. Direct Querying of External Parquet and CSV Files
Query files directly on disk or over S3 without prior import or table creation:
```python
# Direct SQL query over local Parquet wildcards
result = con.execute("""
    SELECT 
        customer_id,
        count(*) as total_orders,
        round(sum(amount_cents) / 100.0, 2) as total_spend_usd,
        percentile_cont(0.95) WITHIN GROUP (ORDER BY amount_cents) as p95_spend
    FROM read_parquet('data/orders_*.parquet')
    WHERE order_date >= '2026-01-01'
    GROUP BY customer_id
    HAVING count(*) >= 5
    ORDER BY total_spend_usd DESC
    LIMIT 20
""").fetchall()
```

### 3. Remote S3 Querying with Projection Pushdown
Configure the `httpfs` extension to read only required byte ranges from remote cloud buckets:
```python
con.execute("""
    INSTALL httpfs;
    LOAD httpfs;
    SET s3_region='us-east-1';
    SET s3_access_key_id='AKIA...';
    SET s3_secret_access_key='...';
""")

# DuckDB reads only the requested columns and metadata via HTTP Range Requests
df = con.execute("""
    SELECT country, avg(latency_ms) 
    FROM read_parquet('s3://my-telemetry-bucket/logs/*.parquet')
    GROUP BY country
""").df()
```

### 4. Zero-Copy Apache Arrow & Polars Interoperability
Pass data between DuckDB, Arrow, and Polars without expensive memory serialization:
```python
import polars as pl

# Convert DuckDB relation to Arrow table, then to Polars with zero copy
arrow_table = con.execute("SELECT * FROM large_table").arrow()
polars_df = pl.from_arrow(arrow_table)
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Querying millions of small JSON files | Use `read_ndjson_auto('*.json', union_by_name=True)` to handle slightly varying schemas across files. |
| RAM exhaustion on large joins | Set memory limit to prevent OS killer: `SET max_memory='8GB'; SET preserve_insertion_order=false;`. DuckDB will spill cleanly to disk. |
| Multiple threads accessing same DuckDB file | DuckDB supports multiple readers but only one active writer per file. For multi-process writing, use separate databases or memory instances. |

## Validation & Acceptance Criteria

- [ ] Query executes without prior data ingestion using `read_parquet` or `read_csv`.
- [ ] Memory limit configured explicitly to prevent host Out-Of-Memory exceptions.
- [ ] Analytical aggregations (window functions, percentiles) execute in sub-second timeframes.
- [ ] Zero-copy Arrow export validated without intermediate CSV/JSON conversions.

## Failure Handling & Recovery

- If DuckDB runs out of memory on complex queries, configure disk spilling: `SET temp_directory='/tmp/duckdb_temp';`.

## Expected Output & Artifacts

- Embedded DuckDB analytical script.
- Compact analytical results DataFrame or JSON payload.
- Query benchmark metrics comparison.

## Related Skills

- `polars-high-throughput-data-pipeline`
- `postgres-query-performance-analysis`
- `fastapi-async-api-design`
