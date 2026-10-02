---
name: polars-high-throughput-data-pipeline
description: "Use this skill when processing, transforming, and analyzing large tabular datasets exceeding memory limits using Polars. It guides the agent through lazy evaluation (LazyFrame), streaming execution, predicate/projection pushdown, memory-mapped Parquet I/O, and Apache Arrow zero-copy transformations."
domain: data-analytics
category: data-pipelines
subcategory: polars
tags:
  - polars
  - data-analytics
  - data-pipelines
  - python
  - arrow
  - parquet
  - performance
technologies:
  - Polars
  - Python
  - Apache Arrow
  - Parquet
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - polars >= 0.20
  - pyarrow
---
# Polars High-Throughput Data Pipeline

## Overview

A high-performance data processing guide leveraging Polars for processing multi-gigabyte and multi-terabyte datasets on a single machine. Instructs AI agents on utilizing multithreaded Rust execution, lazy query optimization, streaming engines, and columnar Parquet storage to outperform traditional Pandas pipelines by 10x to 100x while consuming a fraction of RAM.

## When to Use

- Processing datasets between 1GB and 500GB on a single workstation or server.
- Existing Pandas workflows trigger Out-Of-Memory (OOM) errors or run unacceptably slow.
- Building high-throughput ETL/ELT data pipelines from Parquet, CSV, or Delta Lake tables.
- Requiring memory-efficient aggregations, window functions, and multi-key joins.

## When NOT to Use

- Massive multi-node distributed data processing exceeding 1TB where distributed clusters are mandatory (use Apache Spark).
- Low-latency real-time transactional ACID database updates (use PostgreSQL).

## Inputs & Prerequisites

- Python 3.9+ with `polars` installed (`pip install polars`).
- Raw data stored in columnar Parquet, CSV, or IPC format.

## Core Workflow

### 1. Lazy Evaluation Architecture (`LazyFrame`)
Never load entire files eagerly into memory using `read_csv` or `read_parquet`. Always build lazy query graphs using `scan_parquet` or `scan_csv`:
```python
import polars as pl

# Builds query plan without executing or loading data into memory
lazy_query = (
    pl.scan_parquet("data/transactions_*.parquet")
    .filter(pl.col("status") == "COMPLETED")
    .filter(pl.col("timestamp") >= pl.datetime(2026, 1, 1))
    .select(["customer_id", "amount_cents", "category", "timestamp"])
    .group_by(["customer_id", "category"])
    .agg([
        pl.col("amount_cents").sum().alias("total_spent"),
        pl.col("amount_cents").count().alias("transaction_count")
    ])
)
```

### 2. Query Plan Inspection (Pushdown Optimization)
Inspect the optimized query plan to ensure predicate and projection pushdowns are active:
```python
# View the graph to verify filters execute at the file reader level
print(lazy_query.explain())
```
- **Projection Pushdown**: Only the 4 requested columns are read from disk; unused columns are skipped entirely.
- **Predicate Pushdown**: Filter rows are evaluated during disk read, drastically reducing memory allocation.

### 3. Out-Of-Core Streaming Execution
For datasets that exceed total physical system RAM, execute the plan using the streaming engine:
```python
# Executes in chunks through memory without blowing RAM limits
result_df = lazy_query.collect(streaming=True)
```
Or write directly to Parquet sink without holding complete result in RAM:
```python
lazy_query.sink_parquet("output/aggregated_results.parquet")
```

### 4. Columnar Expressions & Anti-Patterns
- **NEVER iterate over rows** using `for row in df.iter_rows()` or `apply()`. This destroys performance by breaking columnar vectorization.
- Always use vector expressions:
```python
# Vectorized condition
df = df.with_columns(
    pl.when(pl.col("amount") > 1000)
    .then(pl.lit("VIP"))
    .otherwise(pl.lit("STANDARD"))
    .alias("customer_tier")
)
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Dataset contains many small CSV files | Convert raw CSVs to Parquet once with snappy/zstd compression before running analytical queries. |
| Join operation exceeds memory | Perform join on pre-sorted lazy frames or set `pl.Config.set_streaming_chunk_size(...)`. |
| Date parsing performance | Use `pl.col("date_str").str.to_datetime("%Y-%m-%d")` rather than custom Python lambda parsers. |

## Validation & Acceptance Criteria

- [ ] Query executes completely using `scan_*` and lazy query graphs.
- [ ] Memory consumption remains flat even on multi-gigabyte datasets (`streaming=True`).
- [ ] Zero row-wise Python loops present in transformation code.
- [ ] Output Parquet files validate with correct schema and row counts.

## Failure Handling & Recovery

- If streaming crashes due to complex non-streamable operations (e.g. certain window functions), partition data by date or category and process sequentially.

## Expected Output & Artifacts

- High-throughput Python ETL script.
- Optimized output Parquet files.
- Benchmark runtime and memory comparison report.

## Related Skills

- `postgres-query-performance-analysis`
- `docker-container-optimization`
- `observability-and-instrumentation`
