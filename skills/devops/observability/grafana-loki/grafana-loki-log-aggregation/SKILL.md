---
name: grafana-loki-log-aggregation
description: "Use this skill when designing, configuring, and querying horizontally scalable log aggregation systems using Grafana Loki and Promtail / Grafana Alloy. It guides the agent through label cardinality management to prevent index explosion, authoring LogQL queries and metric extractions, configuring structured metadata, and creating LogQL alerting rules."
domain: devops
category: observability
subcategory: grafana-loki
tags:
  - grafana-loki
  - loki
  - logql
  - logging
  - observability
  - promtail
  - devops
technologies:
  - Grafana Loki
  - Promtail
  - Grafana Alloy
  - LogQL
  - Kubernetes
complexity: advanced
maturity: stable
tools:
  - logcli
  - grafana
  - curl
dependencies:
  - loki >= 2.9.0
---
# Grafana Loki Log Aggregation & LogQL Architecture

## Overview

A comprehensive engineering guide for high-throughput, cost-effective log management using Grafana Loki. Unlike traditional log engines that index the full text of every message (leading to huge storage costs), Loki indexes only metadata labels and stores compressed chunks in object storage (S3/GCS). This skill instructs AI agents on optimizing label cardinality, configuring log collectors (Promtail/Alloy), querying logs with LogQL, extracting Prometheus-style metrics from unstructured logs, and authoring alerting rules.

## When to Use

- Aggregating container and system logs across Kubernetes clusters and microservices.
- Reducing log storage costs by 80%+ compared to Elasticsearch or Datadog.
- Correlating application logs directly with Prometheus metrics in Grafana using shared labels.
- Extracting real-time error rates and request count metrics from raw application text logs.

## When NOT to Use

- Full-text search across unstructured corporate documents with complex relevance ranking (use Elasticsearch or Meilisearch).
- Pure metric-only collection without log text (use Prometheus).

## Inputs & Prerequisites

- Grafana Loki 2.9+ server running (standalone or microservices mode).
- Log collector (Promtail or Grafana Alloy) scraping application logs.
- Grafana dashboard configured with Loki datasource.

## Core Workflow

### 1. Promtail Pipeline Configuration with Low-Cardinality Labels
Extract static stream labels while parsing JSON fields into structured metadata:

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

clients:
  - url: http://loki.monitoring.svc:3100/loki/api/v1/push

scrape_configs:
  - job_name: app-logs
    static_configs:
      - targets: [localhost]
        labels:
          job: app-production
          environment: production
          app: order-service
          __path__: /var/log/app/*.log

    pipeline_stages:
      # Parse JSON log lines
      - json:
          expressions:
            level: level
            request_path: path
            status: status_code
            latency_ms: duration

      # Promote 'level' to index label (low cardinality: debug, info, warn, error)
      - labels:
          level:

      # Store high-cardinality fields as structured metadata (NOT indexed labels)
      - structured_metadata:
          status:
          request_path:
```

### 2. LogQL Query Expressions
Query logs using LogQL stream selectors, filter expressions, and parsers:

```logql
# 1. Filter log stream for errors in order-service
{app="order-service", level="error"} |= "database timeout"

# 2. Parse JSON and filter by dynamic attribute without label indexing
{app="order-service"} 
  | json 
  | status_code >= 500 
  | line_format "{{.timestamp}} - [{{.level}}] - {{.message}} (Status: {{.status_code}})"
```

### 3. Metric Queries from Logs (LogQL Metric Extraction)
Derive real-time error rates directly from log streams:

```logql
# Calculate HTTP 5xx error rate per second over 5-minute window
sum(rate({app="order-service"} | json | status_code >= 500 [5m])) by (app)

# Compute 99th percentile request duration parsed from logs
quantile_over_time(0.99, {app="order-service"} | json | unwrap duration_ms [5m])
```

### 4. Loki Alerting Rule
Trigger alert notifications in Alertmanager based on log patterns:

```yaml
# loki-rules.yaml
groups:
  - name: application-log-alerts
    rules:
      - alert: HighApplicationErrorLogRate
        expr: |
          sum(rate({app=~".+", level="error"}[5m])) by (app) > 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Excessive error logs in {{ $labels.app }}"
          description: "Service {{ $labels.app }} generated over 10 error logs/sec in the last 5 minutes."
```

## Best Practices & Failure Modes

1. **High-Cardinality Label Explosion**: Putting `user_id`, `ip_address`, `request_id`, or `order_id` into Loki labels splits streams into millions of separate streams, causing memory exhaustion and catastrophic performance degradation. Labels must be strictly low-cardinality (< 100 distinct values).
2. **Missing Time Window on LogQL Quantiles**: Forgetting the `[5m]` window range in `quantile_over_time` causes query syntax errors.
3. **Unbounded Log Range Queries**: Running queries over 30 days without stream filters (`{}` without labels) forces full disk scans across terabytes of compressed chunks. Always restrict queries with specific stream labels (`{app="x", env="prod"}`).

## Verification & Testing

- Execute LogQL query using `logcli`:
  ```bash
  logcli query '{app="order-service", level="error"}' --limit=10 --since=1h
  ```
- Check Loki ready endpoint:
  ```bash
  curl -s http://localhost:3100/ready
  ```
