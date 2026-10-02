---
name: prometheus-grafana-observability
description: "Use this skill when designing, instrumenting, and deploying application monitoring stacks using Prometheus metrics and Grafana dashboards. It guides the agent through the Four Golden Signals (Latency, Traffic, Errors, Saturation), metric type selection (Counter, Gauge, Histogram, Summary), PromQL query authoring, and actionable Alertmanager alerting rules."
domain: devops
category: monitoring
subcategory: prometheus
tags:
  - prometheus
  - grafana
  - observability
  - monitoring
  - devops
  - sre
  - metrics
technologies:
  - Prometheus
  - Grafana
  - PromQL
  - Docker
  - Alertmanager
complexity: advanced
maturity: stable
tools:
  - curl
  - docker
dependencies:
  - prometheus >= 2.45
---
# Prometheus and Grafana Observability

## Overview

A guide for instrumenting applications, authoring PromQL monitoring queries, and configuring alert rules using Prometheus and Grafana. Grounded in Google Site Reliability Engineering (SRE) principles, this skill instructs AI agents on tracking the Four Golden Signals, eliminating metric cardinality explosions, and writing actionable alerts with zero noise.

## When to Use

- Instrumenting backend applications with custom business and operational metrics.
- Authoring Grafana dashboards to monitor latency (P95/P99), error rates, throughput, and memory/CPU saturation.
- Creating Alertmanager rules that alert engineers on genuine user-impacting symptoms rather than noisy internal causes.
- Auditing Prometheus server memory consumption caused by runaway label cardinality.

## When NOT to Use

- Distributed request tracing across asynchronous microservice boundaries (use OpenTelemetry and Jaeger).
- Centralized raw text log aggregation (use Grafana Loki or Elasticsearch).

## Inputs & Prerequisites

- Prometheus server instance and Grafana dashboard endpoint.
- Application codebase equipped with Prometheus client SDK (e.g. `prom-client` for Node.js, `prometheus_client` for Python).

## Core Workflow

### 1. The Four Golden Signals
Structure metric instrumentation around Google's Four Golden Signals:
1. **Latency**: Time required to service a request (measured via Histogram).
2. **Traffic**: Demand placed on the system (e.g. HTTP requests/sec via Counter).
3. **Errors**: Rate of failed requests (e.g. HTTP 5xx responses via Counter).
4. **Saturation**: How full the service is (e.g. memory usage, threadpool queue depth via Gauge).

### 2. Metric Type Selection
Choose the appropriate metric primitive:
- **Counter**: Value only goes up (resets to 0 on restart). Use for request counts, error counts, bytes sent:
  `http_requests_total{method="POST", status="500"}`.
- **Gauge**: Value can fluctuate up or down. Use for current active connections, memory bytes, thread count:
  `jvm_memory_used_bytes{area="heap"}`.
- **Histogram**: Samples observations into configurable buckets. Use for request durations and response sizes:
  `http_request_duration_seconds_bucket{le="0.25"}`.

### 3. Avoiding Cardinality Explosions
> High-cardinality labels (labels with thousands or millions of unique values) destroy Prometheus memory and can crash monitoring servers!
- **NEVER use dynamic values as labels**: Never use `user_id`, `order_id`, `email`, `session_id`, or raw timestamps as metric labels.
- **Keep label sets bounded**: Labels should only contain finite enumerations: `method` (GET, POST), `status_code` (200, 404, 500), `route` (`/orders/{id}`).

### 4. Essential PromQL Query Patterns
- **Request Rate (QPS)**:
  `sum(rate(http_requests_total[5m])) by (service)`
- **Error Percentage**:
  `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100`
- **95th Percentile Latency (P95)**:
  `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`

### 5. Actionable Alerting Rules
Alert on user-visible symptoms, not transient spikes. Use `for: 5m` to prevent alert flap:
```yaml
groups:
- name: api-alerts
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "API Error rate exceeds 5% on {{ $labels.service }}"
      description: "Service {{ $labels.service }} error rate is currently {{ $value | humanizePercentage }}."
      runbook_url: "https://wiki.company.internal/runbooks/api-high-error-rate"
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Latency histogram bucket selection | Distribute buckets exponentially around your target SLA (e.g. `[0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]`). |
| Ephemeral batch jobs (cannot be scraped) | Use the **Prometheus Pushgateway** to push metrics before job exit. |
| Alert fatigue / noisy alerts | Consolidate alerts to SLO burn-rate alerts (Multi-Window Multi-Burn-Rate alerting per Google SRE book). |

## Validation & Acceptance Criteria

- [ ] `/metrics` endpoint exports valid Prometheus text exposition format.
- [ ] Zero high-cardinality labels (IDs, UUIDs) present in label keys.
- [ ] Grafana dashboard displays Four Golden Signals clearly.
- [ ] PromQL queries use `rate()` on Counters, not Gauges.
- [ ] Alert rules specify severity, runbook URLs, and `for` debounce duration.

## Failure Handling & Recovery

- If Prometheus crashes with Out Of Memory (OOM), inspect top-cardinality metrics using `tsdb analyze` and drop abusive labels in scrape configs.

## Expected Output & Artifacts

- Application Prometheus metrics client instrumentation module.
- Grafana dashboard JSON configuration.
- Prometheus alerting rules YAML file.

## Related Skills

- `k6-api-load-testing`
- `kubernetes-crashloop-debugging`
- `incident-response-and-triage`
