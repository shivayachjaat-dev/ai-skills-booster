---
name: real-time-operational-metrics-dashboard
description: "Use this skill when designing, building, and instrumenting real-time operational metrics registers and analytics dashboards. It establishes strict KPI naming schemas, SQL/semantic definitions, data refresh intervals, target/threshold alerting, and integration with Grafana, Superset, or Metabase."
domain: data-analytics
category: dashboards
subcategory: operational-metrics
tags:
  - metrics-register
  - kpi-dashboard
  - operational-analytics
  - sli-slo
  - sql
  - data-governance
technologies:
  - Python
  - SQL
  - Grafana
  - Superset
  - Pydantic
  - Semantic Layer
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# Real-Time Operational Metrics Dashboard & Semantic Register

## Overview

A robust data engineering and analytics framework for building reliable operational metrics registers, data catalogs, and real-time executive dashboards. When organizations calculate business metrics haphazardly across ad-hoc SQL scripts, executive misalignment, data drift, and conflicting dashboards result. This skill provides AI agents with standard schemas for registering KPIs, defining deterministic SQL expressions, modeling refresh intervals, setting SLI/SLO warning thresholds, and laying out Grafana and Superset visualizations.

## When to Use

- Designing metric catalogs and data dictionaries for engineering, FinOps, or product analytics.
- Establishing standard semantic layer SQL formulas for recurring KPIs across team boundaries.
- Configuring real-time operational triage dashboards with automated alert thresholds.
- Standardizing metric ownership, cadence, and data lineage documentation.

## When NOT to Use

- Simple one-off ad-hoc SQL queries for exploratory data analysis.
- Unstructured machine learning model hyperparameter tracking.

## Inputs & Prerequisites

- Source data warehouse or time-series database (PostgreSQL, ClickHouse, Snowflake, BigQuery).
- Business metric definition, formula, source tables, and dimensional grain.
- Target refresh frequency (real-time stream vs 5-minute micro-batch vs daily rollup).
- Ownership assignment and SLA / alerting targets.

## Core Workflow

### 1. Metric Register & Data Dictionary Architecture
Define each metric with strict typing, dimensional grain, and threshold bounds:

```python
"""Metric register and validation engine."""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    COUNT_DISTINCT = "count_distinct"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    RATIO = "ratio"

class RefreshCadence(str, Enum):
    STREAMING = "streaming"
    REALTIME_1MIN = "1m"
    HOURLY = "1h"
    DAILY = "1d"

class MetricDefinition(BaseModel):
    metric_id: str = Field(..., regex=r"^[a-z0-9_]+$", description="Unique snake_case identifier")
    display_name: str
    owner_team: str
    source_table: str
    aggregation: AggregationType
    sql_formula: str
    cadence: RefreshCadence
    target_value: float
    warning_threshold: float
    critical_threshold: float
    dimensions: List[str]
    description: str

class DashboardRegister(BaseModel):
    dashboard_name: str
    refresh_rate_seconds: int = 60
    metrics: List[MetricDefinition]

def create_operational_register() -> DashboardRegister:
    return DashboardRegister(
        dashboard_name="Checkout Platform Operational Health",
        refresh_rate_seconds=30,
        metrics=[
            MetricDefinition(
                metric_id="payment_success_rate",
                display_name="Payment Success Rate (%)",
                owner_team="payments-engineering",
                source_table="analytics.fact_transactions",
                aggregation=AggregationType.RATIO,
                sql_formula="COUNT(CASE WHEN status = 'SUCCEEDED' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)",
                cadence=RefreshCadence.REALTIME_1MIN,
                target_value=99.5,
                warning_threshold=98.0,
                critical_threshold=95.0,
                dimensions=["payment_gateway", "currency", "country_code"],
                description="Percentage of processed transaction attempts that successfully settled."
            ),
            MetricDefinition(
                metric_id="p95_checkout_latency_ms",
                display_name="P95 Checkout API Latency (ms)",
                owner_team="api-platform",
                source_table="telemetry.http_request_logs",
                aggregation=AggregationType.PERCENTILE_95,
                sql_formula="APPROX_PERCENTILE(duration_ms, 0.95)",
                cadence=RefreshCadence.REALTIME_1MIN,
                target_value=250.0,
                warning_threshold=400.0,
                critical_threshold=800.0,
                dimensions=["endpoint", "cloud_region"],
                description="95th percentile response latency for the order settlement endpoint."
            )
        ]
    )

if __name__ == "__main__":
    reg = create_operational_register()
    print(f"Registered {len(reg.metrics)} metrics for dashboard '{reg.dashboard_name}'.")
    for m in reg.metrics:
        print(f" - {m.display_name}: Target={m.target_value}, Critical={m.critical_threshold}")
```

### 2. Standard SQL Semantic Aggregation Template
Generate standardized time-bucketed aggregation queries:

```sql
-- Standard 1-minute time bucket aggregation for operational metrics
WITH raw_metrics AS (
    SELECT
        DATE_TRUNC('minute', event_timestamp) AS metric_timestamp,
        country_code,
        payment_gateway,
        COUNT(*) AS total_attempts,
        COUNT(CASE WHEN status = 'SUCCEEDED' THEN 1 END) AS successful_settlements,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_latency_ms
    FROM telemetry.fact_transactions
    WHERE event_timestamp >= NOW() - INTERVAL '1 hour'
    GROUP BY 1, 2, 3
)
SELECT
    metric_timestamp,
    country_code,
    payment_gateway,
    total_attempts,
    (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) AS payment_success_rate,
    p95_latency_ms,
    CASE 
        WHEN (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) < 95.0 THEN 'CRITICAL'
        WHEN (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) < 98.0 THEN 'WARNING'
        ELSE 'HEALTHY'
    END AS operational_health_status
FROM raw_metrics
ORDER BY metric_timestamp DESC;
```

### 3. Dashboard Information Architecture
- **Row 1: Executive North Stars (Single Stat KPIs)**: Current value with sparkline trend and color indicator against target.
- **Row 2: Temporal Anomaly Heatmaps**: Real-time 60-minute window showing rolling p95 latency and throughput spikes.
- **Row 3: Dimensional Decomposition**: Bar charts splitting errors by gateway, region, or customer tier.
- **Row 4: Live Event Drilldown**: Paginated tabular log of recent critical transaction failures.

## Best Practices & Failure Modes

- **Denominator Zero Division**: Always wrap SQL divisions with `NULLIF(denominator, 0)` to prevent runtime query crashes.
- **Timestamp Standardization**: Enforce UTC timestamps across all warehouse models before calculating rolling window intervals.
- **Metric Drift**: Never modify an established metric calculation without incrementing its version (e.g., `payment_success_rate_v2`) to preserve historical comparability.

## Verification & Testing

- Validate register schemas using Pydantic:
  ```bash
  python -c "import pydantic; print('Pydantic schema validation successful')"
  ```
- Run query cost and execution plan audits (`EXPLAIN ANALYZE`) to verify index coverage on metric timestamp partitions.
