---
name: timescaledb-hypertables-and-retention
description: "Use this skill when architecting, partitioning, and optimizing high-throughput time-series databases with TimescaleDB on PostgreSQL. It guides the agent through hypertable creation, chunk time interval sizing, continuous aggregates with automatic refresh policies, column-oriented compression policies, and data retention drops."
domain: databases
category: time-series
subcategory: timescaledb
tags:
  - timescaledb
  - postgresql
  - time-series
  - database
  - analytics
  - sql
  - iot
technologies:
  - TimescaleDB
  - PostgreSQL
  - SQL
  - Python asyncpg
  - Docker
complexity: advanced
maturity: stable
tools:
  - psql
  - python
dependencies:
  - timescaledb >= 2.13.0
---
# TimescaleDB Hypertables & Continuous Aggregates Architecture

## Overview

A definitive production engineering guide for handling petabyte-scale time-series workloads with TimescaleDB on PostgreSQL. This skill instructs AI agents on converting relational tables into partitioned Hypertables, sizing chunk time intervals to fit in RAM, configuring automated real-time Continuous Aggregates, enforcing column-oriented compression policies that reduce storage by 90%+, and automating data lifecycle retention policies.

## When to Use

- Ingesting massive streams of financial ticks, IoT sensor readings, DevOps server metrics, or application clickstreams.
- Querying time-range data (`time_bucket('5 minutes', time)`) across billions of rows with sub-second latency.
- Maintaining full PostgreSQL SQL capabilities (JOINs, secondary indexes, foreign keys) alongside time-series optimizations.
- Dramatically reducing storage footprint via native chunk compression.

## When NOT to Use

- Pure non-time-series transactional OLTP workloads with few timestamps.
- Unstructured distributed text search (use Meilisearch or Elasticsearch).

## Inputs & Prerequisites

- PostgreSQL 15+ with TimescaleDB extension enabled: `CREATE EXTENSION IF NOT EXISTS timescaledb;`.
- Access via `psql` or PostgreSQL client library.

## Core Workflow

### 1. Hypertables & Optimal Chunk Interval Sizing
Create a partitioned hypertable with 1-day chunks so each active chunk fits in memory:

```sql
-- 1. Standard PostgreSQL table definition
CREATE TABLE IF NOT EXISTS device_telemetry (
    recorded_at TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(32) NOT NULL,
    location_id VARCHAR(16) NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    battery_level INT
);

-- 2. Convert to Hypertable with 1-day chunk time interval
SELECT create_hypertable(
    'device_telemetry',
    by_range('recorded_at', INTERVAL '1 day'),
    if_not_exists => TRUE
);

-- 3. Composite Index for device query filtering
CREATE INDEX IF NOT EXISTS idx_telemetry_device_time 
ON device_telemetry (device_id, recorded_at DESC);
```

### 2. Continuous Aggregates with Automated Refresh
Materialize downsampled time-bucketed aggregates incrementally in the background:

```sql
-- Materialized view computing hourly averages
CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_device_stats
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', recorded_at) AS bucket,
    device_id,
    AVG(temperature) AS avg_temperature,
    MAX(temperature) AS max_temperature,
    MIN(temperature) AS min_temperature,
    COUNT(*) AS reading_count
FROM device_telemetry
GROUP BY bucket, device_id
WITH NO DATA;

-- Automated Refresh Policy: Refresh hourly for data older than 2 hours to allow for late-arriving data
SELECT add_continuous_aggregate_policy(
    'hourly_device_stats',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

### 3. Columnar Compression & Data Retention
Compress historical chunks older than 7 days, and drop raw chunks older than 90 days:

```sql
-- 1. Enable TimescaleDB Columnar Compression
ALTER TABLE device_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id',
    timescaledb.compress_orderby = 'recorded_at DESC'
);

-- 2. Add automated compression policy for chunks older than 7 days
SELECT add_compression_policy('device_telemetry', INTERVAL '7 days');

-- 3. Add automated retention policy to drop raw chunks older than 90 days
SELECT add_retention_policy('device_telemetry', INTERVAL '90 days');
```

## Best Practices & Failure Modes

1. **Chunk Sizing Mistakes**: Chunks that are too large (e.g. 1 year) exceed available RAM, destroying write performance and query caching. Chunks that are too small (e.g. 5 minutes) produce thousands of tiny partitions, adding planning overhead. Target active chunks to consume roughly 25% of available RAM.
2. **Mutations on Compressed Chunks**: Updating or deleting rows in compressed chunks incurs decompression overhead. Handle corrections before chunks are compressed or schedule compression after data is finalized.
3. **Missing `by_range` Parameter**: In TimescaleDB 2.13+, use `by_range('recorded_at', INTERVAL '1 day')` rather than deprecated positional parameters to ensure clean schema definitions.

## Verification & Testing

- Inspect chunk partition metadata and compression ratios:
  ```sql
  SELECT chunk_name, range_start, range_end, is_compressed
  FROM timescaledb_information.chunks
  WHERE hypertable_name = 'device_telemetry';
  ```
- Check compression space savings:
  ```sql
  SELECT * FROM hypertable_compression_stats('device_telemetry');
  -- Verifies uncompressed vs compressed bytes
  ```
- Test query using time_bucket:
  ```sql
  SELECT time_bucket('15 minutes', recorded_at) AS five_min, AVG(temperature)
  FROM device_telemetry
  WHERE recorded_at >= NOW() - INTERVAL '6 hours'
  GROUP BY five_min
  ORDER BY five_min DESC;
  ```
