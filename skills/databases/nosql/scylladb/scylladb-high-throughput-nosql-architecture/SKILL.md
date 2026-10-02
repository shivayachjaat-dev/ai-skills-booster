---
name: scylladb-high-throughput-nosql-architecture
description: "Use this skill when architecting, modeling, and operating distributed, ultra-low-latency NoSQL databases with ScyllaDB (Apache Cassandra compatible). It guides the agent through shard-per-core asynchronous architecture, CQL partition and clustering key design, tuning consistency levels (LOCAL_QUORUM), tombstone prevention, and driver connection pooling."
domain: databases
category: nosql
subcategory: scylladb
tags:
  - scylladb
  - cassandra
  - cql
  - nosql
  - distributed-database
  - low-latency
  - big-data
technologies:
  - ScyllaDB
  - Apache Cassandra
  - CQL
  - Python scylla-driver
  - Go gocql
complexity: advanced
maturity: stable
tools:
  - cqlsh
  - nodetool
  - python
dependencies:
  - scylla-driver >= 3.25.0
---
# ScyllaDB High-Throughput NoSQL Architecture & Data Modeling

## Overview

A definitive production engineering reference for architecting ultra-low latency, horizontally scalable NoSQL systems with ScyllaDB. Written in C++ on the Seastar asynchronous engine using a shard-per-core architecture, ScyllaDB is a drop-in Apache Cassandra replacement delivering 10x higher throughput with predictable sub-millisecond P99 latencies without JVM garbage collection pauses. This skill instructs AI agents on designing query-driven Cassandra Query Language (CQL) schemas, primary key partitioning, tunable consistency levels, tombstone elimination, and connection pooling.

## When to Use

- Ingesting millions of writes per second with sub-millisecond P99 response times (time-series, gaming, IoT, real-time bidding).
- Replacing Apache Cassandra clusters suffering from unpredictable JVM garbage collection latency spikes.
- Multi-datacenter active-active distributed replication across geographic regions.
- Workloads requiring predictable linear horizontal scaling by adding nodes.

## When NOT to Use

- Relational data requiring multi-table JOINs, foreign key cascades, and ACID transactions across multiple partitions (use PostgreSQL).
- Small workloads (< 10,000 ops/sec) where managed serverless databases (DynamoDB or Firestore) require zero operational management.

## Inputs & Prerequisites

- ScyllaDB 5+ cluster running.
- CQL client (`cqlsh`) or shard-aware driver (`scylla-driver` for Python, `gocql` for Go).
- Understanding of distributed hash rings and partition tokens.

## Core Workflow

### 1. Query-First CQL Data Modeling
In ScyllaDB, tables are designed strictly to satisfy specific queries. A table must never require `ALLOW FILTERING`:

```sql
-- Create Keyspace with NetworkTopologyStrategy across two cloud regions
CREATE KEYSPACE IF NOT EXISTS sensor_telemetry WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'us-west': 3
};

-- Table designed for query: "Get sensor readings for a specific device over a time range"
-- Partition Key ((device_id, bucket_day)): Determines which cluster node/shard owns data.
-- Clustering Key (recorded_at): Determines physical on-disk sort order within the partition.
CREATE TABLE IF NOT EXISTS sensor_telemetry.readings_by_device (
    device_id UUID,
    bucket_day DATE,
    recorded_at TIMESTAMP,
    temperature FLOAT,
    voltage FLOAT,
    status_code INT,
    PRIMARY KEY ((device_id, bucket_day), recorded_at)
) WITH CLUSTERING ORDER BY (recorded_at DESC)
  AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
  };
```

### 2. Shard-Aware Python Driver Connection
Use the official Scylla shard-aware driver to route queries directly to the specific CPU core holding the partition:

```python
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.query import ConsistencyLevel
import uuid
import datetime

# Configure Token-Aware policy to send writes directly to replica node
profile = ExecutionProfile(
    load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy(local_dc="us-east")),
    consistency_level=ConsistencyLevel.LOCAL_QUORUM, # Strong consistency within local DC
    request_timeout=2.0
)

cluster = Cluster(
    contact_points=["10.0.1.10", "10.0.1.11", "10.0.1.12"],
    port=9042,
    execution_profiles={EXEC_PROFILE_DEFAULT: profile}
)
session = cluster.connect("sensor_telemetry")

# Prepared statements are compiled once on the cluster for microsecond execution
insert_stmt = session.prepare("""
    INSERT INTO readings_by_device (device_id, bucket_day, recorded_at, temperature, voltage, status_code)
    VALUES (?, ?, ?, ?, ?, ?)
""")

def record_reading(device_uuid: uuid.UUID, temp: float, volt: float, status: int):
    now = datetime.datetime.utcnow()
    today = now.date()
    session.execute(insert_stmt, (device_uuid, today, now, temp, volt, status))
```

### 3. Tunable Consistency Levels Strategy
- **`LOCAL_QUORUM` (Recommended)**: Requires response from a majority of replicas in the local datacenter `(N/2 + 1)`. Guarantees strong consistency without paying cross-datacenter WAN network latency.
- **`ONE`**: Fastest performance, suitable for non-critical telemetry metrics where dropping occasional packets is acceptable.
- **`ALL`**: Anti-pattern. If a single node is rebooting for maintenance, all writes fail.

## Best Practices & Failure Modes

1. **Hot Partition Bottlenecks**: Placing only `device_id` as the partition key causes devices that emit 1000 events/sec to create multi-gigabyte partitions on a single node. Bucketing with date (`(device_id, bucket_day)`) caps partition size to < 100 MB.
2. **Tombstone Saturation**: In Cassandra/ScyllaDB, executing `DELETE` or writing `null` values writes a tombstone marker. Reading across millions of tombstones causes query timeouts (`ReadFailureException: Scanned over 100000 tombstones`). Set TTLs on entire rows or model deletions via partition expiration.
3. **`ALLOW FILTERING` Anti-Pattern**: If a query requires `ALLOW FILTERING`, ScyllaDB must perform a full-cluster scan across every node. Redesign the table or create a Materialized View.

## Verification & Testing

- Inspect cluster ring status and node distribution:
  ```bash
  nodetool status
  ```
- Check partition histogram and tombstone metrics:
  ```bash
  nodetool cfhistograms sensor_telemetry readings_by_device
  ```
- Test low-latency query performance via `cqlsh`:
  ```bash
  cqlsh -e "TRACING ON; SELECT * FROM sensor_telemetry.readings_by_device WHERE device_id = 12345678-1234-5678-1234-567812345678 AND bucket_day = '2026-03-01' LIMIT 10;"
  ```
