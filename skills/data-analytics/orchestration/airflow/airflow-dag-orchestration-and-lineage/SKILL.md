---
name: airflow-dag-orchestration-and-lineage
description: "Use this skill to design, write, test, and deploy production-grade Apache Airflow DAGs with data lineage tracking, idempotent task execution, dynamic task mapping, OpenLineage metadata emission, and robust error retry strategies."
domain: data-analytics
category: orchestration
subcategory: airflow
tags:
  - airflow
  - data-pipelines
  - dag
  - openlineage
  - taskflow-api
  - orchestration
technologies:
  - Apache Airflow >= 2.8.0
  - Python
  - OpenLineage
  - PostgreSQL
  - Docker
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - apache-airflow >= 2.8.0
  - openlineage-airflow >= 1.0.0
  - python >= 3.10
---
# Apache Airflow DAG Orchestration & OpenLineage Architecture

## Overview

A definitive data engineering standard for developing resilient, idempotent, and observable Apache Airflow data pipelines. In distributed data architectures, pipeline failures stemming from non-deterministic backfills, unversioned dependencies, hidden schema drift, and invisible data provenance cost engineering teams countless debugging hours. This skill provides AI agents with modern Airflow 2.8+ TaskFlow API standards, dynamic task mapping, OpenLineage metadata emission, and automated unit testing for DAG integrity.

## When to Use

- Writing enterprise batch ETL/ELT pipelines in Apache Airflow using the modern TaskFlow API (`@task`, `@dag`).
- Implementing dynamic task fan-out and fan-in workflows using `.expand()` and `.partial()`.
- Capturing automated data lineage, dataset inputs/outputs, and quality assertions via OpenLineage and Marquez.
- Designing idempotent DAGs safe for historical partition backfills and concurrent catchup runs.

## When NOT to Use

- Sub-second low-latency streaming event processing (use Apache Flink or Kafka Streams).
- Simple linear bash shell cron jobs without dependency orchestration needs.

## Inputs & Prerequisites

- Apache Airflow environment (>= 2.8.0) with PostgreSQL metadata database.
- Target data systems (S3/GCS data lake, Snowflake, BigQuery, Postgres).
- OpenLineage backend URL (e.g., Marquez server) if lineage tracking is enabled.

## Core Workflow

### 1. Modern TaskFlow DAG with Dynamic Task Mapping
Implement typed tasks with dynamic fan-out and error retries:

```python
"""Production TaskFlow DAG with Dynamic Mapping and Lineage."""
from datetime import datetime, timedelta
from typing import List, Dict
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain

DEFAULT_ARGS = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}

@dag(
    dag_id="ecommerce_order_settlement_pipeline",
    default_args=DEFAULT_ARGS,
    description="Processes daily partition settlements with OpenLineage tracking",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=2,
    tags=["finance", "settlements", "openlineage"]
)
def order_settlement_pipeline():

    @task
    def discover_active_regions() -> List[str]:
        """Discovers active operational regions for dynamic task fan-out."""
        return ["us-east", "eu-west", "ap-southeast"]

    @task
    def extract_and_transform_region(region: str, ds: str = None) -> Dict[str, Any]:
        """Idempotent extraction per region using execution date partition."""
        print(f"Processing region {region} for partition date {ds}")
        # Deterministic extraction logic partitioned by ds
        return {
            "region": region,
            "partition_date": ds,
            "settled_count": 1420,
            "settled_volume_usd": 128500.50
        }

    @task
    def aggregate_global_summary(regional_metrics: List[Dict[str, Any]], ds: str = None) -> Dict[str, Any]:
        """Reduces dynamically mapped regional metrics into consolidated report."""
        total_volume = sum(m["settled_volume_usd"] for m in regional_metrics)
        total_count = sum(m["settled_count"] for m in regional_metrics)
        print(f"Global Summary for {ds}: Volume=${total_volume:,.2f}, Transactions={total_count}")
        return {"date": ds, "total_volume": total_volume, "total_count": total_count}

    # Pipeline Topology
    regions = discover_active_regions()
    # Dynamic Task Mapping fan-out
    transformed = extract_and_transform_region.expand(region=regions)
    # Fan-in reduction
    summary = aggregate_global_summary(transformed)

pipeline = order_settlement_pipeline()
```

### 2. OpenLineage Integration Configuration
Configure automatic lineage emission in `airflow.cfg` or environment variables:

```ini
[lineage]
backend = openlineage
transport = {"type": "http", "url": "http://marquez:5000/api/v1/lineage"}

[openlineage]
namespace = production_airflow_cluster
extractors = airflow.providers.openlineage.extractors.bash.BashExtractor;airflow.providers.openlineage.extractors.python.PythonExtractor
```

### 3. Automated DAG Integrity Unit Test
Validate syntax, cycle freedom, and SLA configuration in CI:

```python
"""DAG Integrity & Unit Test Suite."""
import pytest
from airflow.models import DagBag

@pytest.fixture(scope="module")
def dag_bag():
    return DagBag(dag_folder="dags/", include_examples=False)

def test_dag_import_errors(dag_bag):
    """Verify that zero DAGs contain syntax errors or import crashes."""
    assert len(dag_bag.import_errors) == 0, f"Import errors detected: {dag_bag.import_errors}"

def test_dag_retries_configured(dag_bag):
    """Enforce that all production DAGs have retry policies defined."""
    for dag_id, dag in dag_bag.dags.items():
        assert dag.default_args.get("retries", 0) >= 1, f"DAG {dag_id} missing retries"

def test_dag_no_cycles(dag_bag):
    """Confirm DAGs are strictly acyclic."""
    for dag_id, dag in dag_bag.dags.items():
        assert not dag.has_cycle(), f"DAG {dag_id} contains a cyclic dependency loop"
```

## Best Practices & Failure Modes

- **Never Use Non-Deterministic Defaults**: Avoid calling `datetime.now()` inside task parameters. Always rely on templated execution date parameters (`ds`, `ts`, `logical_date`).
- **Catchup Run Bombardment**: Set `catchup=False` unless intentionally running historical backfills with constrained `max_active_runs`.
- **Top-Level Code Latency**: Never run heavy database queries or network HTTP calls in top-level DAG script code; this blocks the Airflow Scheduler heartbeat loop.

## Verification & Testing

- Validate DAG syntax with the Airflow CLI:
  ```bash
  airflow dags list-import-errors
  ```
- Run local pytest test suite:
  ```bash
  pytest tests/test_dag_integrity.py
  ```
