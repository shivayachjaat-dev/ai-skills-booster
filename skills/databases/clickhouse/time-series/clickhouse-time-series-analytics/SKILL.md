---
name: clickhouse-time-series-analytics
description: "Use this skill when designing, partitioning, and querying massive time-series event logs and telemetry in ClickHouse. It guides the agent through selecting MergeTree table engines, primary key and sorting key design, TTL data aging policies, materialized views for real-time aggregations, and high-throughput batched ingestion."
domain: databases
category: clickhouse
subcategory: time-series
tags:
  - clickhouse
  - databases
  - time-series
  - olap
  - analytics
  - sql
  - telemetry
technologies:
  - ClickHouse
  - SQL
  - MergeTree
  - Docker
  - Python
complexity: advanced
maturity: stable
tools:
  - clickhouse-client
  - python
dependencies:
  - clickhouse-connect or clickhouse-driver
---
# ClickHouse Time-Series Analytics

## Overview

A guide for architecting, partitioning, and querying massive time-series logs, financial ticks, and IoT telemetry using ClickHouse. Delivers sub-second query performance across billions of rows through columnar compression (LZ4/ZSTD), sparse primary key indexing, and background MergeTree data part compaction.

## When to Use

- Ingesting and querying event telemetry, API access logs, or clickstreams exceeding 100 million events per day.
- Real-time time-series aggregations (e.g. 5-minute metric rollups, percentile latencies, user session lengths).
- Replacing slow, expensive relational database log queries with an optimized columnar OLAP store.
- Implementing automatic cold-data aging and tiering using TTL policies.

## When NOT to Use

- Single-row transactional point updates (`UPDATE table SET val = 1 WHERE id = 42`) or transactional ACID locking (use PostgreSQL).
- Ephemeral in-memory analytics under 50GB (use DuckDB).

## Inputs & Prerequisites

- Running ClickHouse server instance (native binary, Docker container, or ClickHouse Cloud).
- Telemetry event schema (timestamp, tenant ID, device ID, metrics).

## Core Workflow

### 1. Table Engine & Sorting Key Selection
In ClickHouse, the `ORDER BY` tuple determines physical on-disk data sorting and primary index construction:
```sql
CREATE TABLE telemetry_events (
    timestamp DateTime64(3, 'UTC'),
    tenant_id UInt32,
    service_name LowCardinality(String),
    event_type LowCardinality(String),
    duration_ms Float32,
    attributes Map(String, String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (tenant_id, service_name, event_type, timestamp)
TTL timestamp + INTERVAL 90 DAY DELETE;
```
- **Order of columns in `ORDER BY`**: Order by cardinality (lowest cardinality first: `tenant_id` $\rightarrow$ `service_name` $\rightarrow$ `timestamp`). This maximizes compression and range pruning.
- **Partition Key**: Partition by month (`toYYYYMM`) or day. Never partition by high-cardinality fields (like `tenant_id` or `timestamp` directly), as this creates millions of tiny data parts and crashes the server.

### 2. High-Throughput Batched Ingestion
> ClickHouse is NOT an OLTP database. Sending 1 row per `INSERT` statement creates thousands of unmerged parts and triggers `Too many parts` exceptions.
- **Batch Rule**: Always buffer writes on the client or broker side and insert in batches of **10,000 to 100,000 rows** (or every 1 to 3 seconds):
```python
import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=8123)

# Batched insert of tuples
client.insert('telemetry_events', batch_data, column_names=['timestamp', 'tenant_id', 'service_name', 'event_type', 'duration_ms'])
```

### 3. Real-Time Pre-Aggregations (Materialized Views)
Avoid scanning billions of raw rows for dashboard graphs. Use Materialized Views with `SummingMergeTree` or `AggregatingMergeTree`:
```sql
CREATE TABLE hourly_service_stats (
    hour DateTime,
    tenant_id UInt32,
    service_name LowCardinality(String),
    request_count SimpleAggregateFunction(sum, UInt64),
    total_duration_ms SimpleAggregateFunction(sum, Float64)
) ENGINE = SummingMergeTree()
ORDER BY (tenant_id, service_name, hour);

CREATE MATERIALIZED VIEW mv_hourly_service_stats TO hourly_service_stats AS
SELECT
    toStartOfHour(timestamp) as hour,
    tenant_id,
    service_name,
    count() as request_count,
    sum(duration_ms) as total_duration_ms
FROM telemetry_events
GROUP BY hour, tenant_id, service_name;
```

### 4. Advanced Analytical Functions
Utilize ClickHouse vectorized built-in functions:
- Quantiles / Percentiles: `quantilesExactWeighted(0.50, 0.95, 0.99)(duration_ms, 1)`.
- Funnel Analysis: `windowFunnel(86400)(timestamp, event_type = 'view', event_type = 'add_cart', event_type = 'purchase')`.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Repetitive string values (e.g. country codes, log levels) | Wrap in `LowCardinality(String)` to dictionary-encode strings into 1-byte integers, slashing storage and RAM. |
| Ingestion triggers `Too many parts` error | Increase client batch sizes (minimum 10,000 rows per insert) or deploy Vector / Kafka Connect buffers in front of ClickHouse. |
| Need deduplication of incoming events | Use `ReplacingMergeTree(version)` engine to collapse duplicate rows during background merges. |

## Validation & Acceptance Criteria

- [ ] Ingestion executes in batches (> 10,000 rows per insert).
- [ ] `ORDER BY` tuple ordered by low-cardinality filters first.
- [ ] Partitioning strategy generates < 1,000 total data parts across table.
- [ ] Materialized Views configured for high-frequency dashboard queries.
- [ ] TTL policies configured for automatic aging and disk pruning.

## Failure Handling & Recovery

- If background merges fall behind, monitor `system.parts` and temporarily throttle client ingestion rate to allow MergeTree engines to compact parts.

## Expected Output & Artifacts

- Optimized ClickHouse DDL table schema.
- Materialized View aggregation definitions.
- High-throughput Python/Go batch ingestion client module.

## Related Skills

- `duckdb-embedded-analytics`
- `kafka-event-driven-architecture`
- `prometheus-grafana-observability`
