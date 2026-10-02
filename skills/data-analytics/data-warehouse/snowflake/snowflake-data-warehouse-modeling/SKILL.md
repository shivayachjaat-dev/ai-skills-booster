---
name: snowflake-data-warehouse-modeling
description: "Use this skill when architecting, modeling, and optimizing enterprise data warehouses in Snowflake. It guides the agent through multi-cluster virtual warehouse sizing, micro-partition clustering keys, zero-copy cloning for staging environments, time travel data recovery, and continuous ingestion with Snowpipe."
domain: data-analytics
category: data-warehouse
subcategory: snowflake
tags:
  - snowflake
  - data-warehouse
  - analytics
  - sql
  - snowpipe
  - data-modeling
technologies:
  - Snowflake
  - SQL
  - Snowpipe
  - Python snowflake-connector
  - dbt
complexity: advanced
maturity: stable
tools:
  - snowsql
  - python
dependencies:
  - snowflake-connector-python >= 3.6.0
---
# Snowflake Data Warehouse Modeling & Performance Architecture

## Overview

A comprehensive guide for architecting high-performance cloud data warehouses in Snowflake. This skill instructs agents on multi-cluster virtual warehouse sizing, automatic micro-partitioning and clustering keys, zero-copy cloning for safe development branches, Time Travel disaster recovery, and continuous data ingestion with Snowpipe.

## When to Use

- Designing dimensional schemas (Star schema / Snowflake schema) for petabyte-scale analytics.
- Optimizing expensive analytical queries that suffer from full-table scans.
- Creating isolated dev/staging environments instantaneously without storage duplication using Zero-Copy Cloning.
- Ingesting streaming logs or events continuously from S3/GCS buckets via Snowpipe.

## When NOT to Use

- Sub-millisecond transactional OLTP systems (use PostgreSQL or Redis).
- Small analytical datasets (< 50 GB) where embedded DuckDB or SQLite provides faster, zero-cost processing.

## Inputs & Prerequisites

- Snowflake account with SYSADMIN or ACCOUNTADMIN privileges.
- SQL client (`snowsql`) or Python `snowflake-connector-python`.
- Cloud storage bucket (AWS S3, Azure Blob, or Google Cloud Storage) configured with Storage Integration.

## Core Workflow

### 1. Compute & Warehouse Sizing
Separate compute resources by workload to eliminate resource contention:

```sql
-- Dedicated warehouse for analytical queries with auto-suspend and multi-cluster scaling
CREATE WAREHOUSE IF NOT EXISTS analytics_wh
  WITH WAREHOUSE_SIZE = 'MEDIUM'
  AUTO_SUSPEND = 120 -- Suspend after 2 minutes of idle time to save credits
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3
  SCALING_POLICY = 'STANDARD'
  INITIALLY_SUSPENDED = TRUE
  COMMENT = 'Dedicated warehouse for BI and ad-hoc analysts';

-- High-throughput warehouse for ETL/ELT batch transformations
CREATE WAREHOUSE IF NOT EXISTS transform_wh
  WITH WAREHOUSE_SIZE = 'LARGE'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;
```

### 2. Table Modeling with Micro-Partition Clustering
Design dimensional fact table with explicit clustering key for date and tenant pruning:

```sql
CREATE OR REPLACE TABLE analytics.public.fact_orders (
    order_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(32) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    order_timestamp TIMESTAMP_NTZ NOT NULL,
    gross_amount NUMBER(12, 2) NOT NULL,
    tax_amount NUMBER(10, 2) NOT NULL,
    net_amount NUMBER(12, 2) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
-- Explicit clustering key enables partition pruning on filter queries
CLUSTER BY (tenant_id, TO_DATE(order_timestamp));
```

### 3. Zero-Copy Cloning for Development & Staging
Instantly clone multi-terabyte production databases without copying underlying storage:

```sql
-- Create isolated staging database cloned from production
CREATE DATABASE staging_analytics CLONE prod_analytics;

-- Any mutations made in staging_analytics only allocate new micro-partitions for delta changes!
```

### 4. Time Travel & Undrop Recovery
Recover accidentally dropped tables or retrieve historical data states:

```sql
-- Query table exactly as it existed 4 hours ago
SELECT COUNT(*) 
FROM analytics.public.fact_orders AT(OFFSET => -60*4);

-- Recover accidentally dropped table
UNDROP TABLE analytics.public.fact_orders;
```

### 5. Automated Continuous Ingestion with Snowpipe
Configure serverless event-driven ingestion from cloud storage:

```sql
-- Create external stage pointing to AWS S3
CREATE STAGE IF NOT EXISTS analytics.public.s3_orders_stage
  URL = 's3://company-analytics-landing/orders/'
  STORAGE_INTEGRATION = s3_integration
  FILE_FORMAT = (TYPE = 'PARQUET');

-- Define serverless Snowpipe
CREATE OR REPLACE PIPE analytics.public.orders_snowpipe AUTO_INGEST = TRUE AS
COPY INTO analytics.public.fact_orders (order_id, tenant_id, customer_id, order_timestamp, gross_amount, tax_amount, net_amount, order_status)
FROM (
  SELECT
    $1:order_id::VARCHAR,
    $1:tenant_id::VARCHAR,
    $1:customer_id::VARCHAR,
    $1:order_timestamp::TIMESTAMP_NTZ,
    $1:gross_amount::NUMBER(12,2),
    $1:tax_amount::NUMBER(10,2),
    $1:net_amount::NUMBER(12,2),
    $1:order_status::VARCHAR
  FROM @analytics.public.s3_orders_stage
);
```

## Best Practices & Failure Modes

1. **Over-Clustering Costs**: Do not define clustering keys on tables under 1 TB. Snowflake's natural micro-partitioning handles small-to-medium tables efficiently. Automatic clustering on small tables wastes compute credits.
2. **Auto-Suspend Neglect**: Never set `AUTO_SUSPEND = 0` or omit it. If a developer leaves a query session open, the virtual warehouse runs 24/7, consuming thousands of dollars in credits. Set auto-suspend to 60-120 seconds.
3. **Data Type Mismatches in JOINs**: Joining a `VARCHAR` key with an `INTEGER` key forces Snowflake to bypass micro-partition pruning. Ensure foreign keys share identical data types.

## Verification & Testing

- Inspect partition pruning efficiency via SQL:
  ```sql
  EXPLAIN
  SELECT * FROM analytics.public.fact_orders
  WHERE tenant_id = 'org_abc' AND order_timestamp >= '2026-01-01';
  -- Check: partitionsTotal vs partitionsAssigned (should prune > 90% of partitions)
  ```
- Check Snowpipe ingestion queue status:
  ```sql
  SELECT SYSTEM$PIPE_STATUS('analytics.public.orders_snowpipe');
  ```
