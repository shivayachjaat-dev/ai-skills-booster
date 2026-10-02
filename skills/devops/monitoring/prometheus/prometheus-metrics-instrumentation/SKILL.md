---
name: prometheus-metrics-instrumentation
description: "Use this skill when instrumenting backend microservices with Prometheus metrics. It guides the agent through selecting metric types (Counter, Gauge, Histogram, Summary), enforcing the RED and USE monitoring methods, label cardinality management to avoid memory exhaustion, and authoring alerting rules (PromQL)."
domain: devops
category: monitoring
subcategory: prometheus
tags:
  - prometheus
  - metrics
  - monitoring
  - promql
  - observability
  - grafana
technologies:
  - Prometheus
  - PromQL
  - Python prometheus_client
  - Grafana
  - Go prometheus/client_golang
complexity: advanced
maturity: stable
tools:
  - promtool
  - curl
dependencies:
  - prometheus-client >= 0.19.0
---
# Prometheus Metrics Instrumentation & PromQL Architecture

## Overview

A definitive production standard for application metrics collection and alerting using Prometheus. This skill equips agents with principles for instrumenting web services, selecting appropriate metric primitives (Counter, Gauge, Histogram, Summary), structuring labels according to the RED (Rate, Errors, Duration) method, preventing high-cardinality time series explosion, and writing PromQL alerting rules.

## When to Use

- Instrumenting HTTP APIs, background task queues, and batch jobs with real-time operational telemetry.
- Defining Golden Signals: latency, traffic, errors, and saturation.
- Creating production Grafana dashboards powered by PromQL queries.
- Authoring Prometheus Alertmanager alerting rules with duration thresholds (`for: 5m`).

## When NOT to Use

- High-cardinality transaction tracing where unique IDs must be recorded per event (use `opentelemetry-distributed-tracing`).
- Long-term raw event archiving where message schemas evolve continuously.

## Inputs & Prerequisites

- Prometheus server scraping endpoints (`/metrics`).
- Prometheus client library (`prometheus_client` in Python or `client_golang` in Go).
- Web application framework (FastAPI, Flask, Express, or Go standard HTTP).

## Core Workflow

### 1. Metric Primitives Selection & RED Method Instrumentation
Define the core metrics using Python's official Prometheus client:

```python
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
import time

app = FastAPI()

# 1. RED - Rate & Errors: Total HTTP requests received
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by endpoint and status code.",
    ["method", "endpoint", "status_code"]
)

# 2. RED - Duration: Request latency distribution in seconds
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 3. Saturation: In-flight concurrent requests currently processing
IN_FLIGHT_REQUESTS = Gauge(
    "http_in_flight_requests",
    "Number of HTTP requests currently being processed.",
    ["endpoint"]
)

@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    endpoint = request.url.path
    method = request.method

    # Normalize dynamic route parameters to prevent high cardinality
    if endpoint.startswith("/api/v1/orders/"):
        endpoint = "/api/v1/orders/{order_id}"

    IN_FLIGHT_REQUESTS.labels(endpoint=endpoint).inc()
    start_time = time.perf_counter()
    
    try:
        response = await call_next(request)
        status_code = str(response.status_code)
        return response
    except Exception as e:
        status_code = "500"
        raise e
    finally:
        latency = time.perf_counter() - start_time
        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            endpoint=endpoint
        ).observe(latency)
        IN_FLIGHT_REQUESTS.labels(endpoint=endpoint).dec()

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

### 2. PromQL Alerting Rules
Author production alert rules evaluated by Prometheus:

```yaml
# prometheus-alerts.yaml
groups:
  - name: api-operational-alerts
    rules:
      # Alert when HTTP 5xx error rate exceeds 2% over 5 minutes
      - alert: HighHttpErrorRate
        expr: |
          (
            sum(rate(http_requests_total{status_code=~"5.."}[5m]))
            /
            sum(rate(http_requests_total[5m]))
          ) * 100 > 2.0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High HTTP error rate on {{ $labels.endpoint }}"
          description: "Endpoint {{ $labels.endpoint }} has error rate of {{ $value | printf "%.2f" }}% over 5m."

      # Alert when p99 latency exceeds 1.5 seconds
      - alert: HighHttpP99Latency
        expr: |
          histogram_quantile(
            0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
          ) > 1.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P99 latency exceeding 1.5s on {{ $labels.endpoint }}"
```

## Best Practices & Failure Modes

1. **Cardinality Bomb Disaster**: Putting unbounded dynamic values (`user_id`, `email`, `timestamp`, `uuid`) into metric labels causes Prometheus memory usage to explode exponentially, leading to Prometheus OOM crashes. Metric labels must strictly have low, bounded sets of possible values.
2. **Missing Normalization**: If endpoint paths are logged raw (`/customers/1`, `/customers/2`), every customer ID creates a separate time series. Always normalize path templates (`/customers/{id}`).
3. **Histogram Bucket Misconfiguration**: Using default buckets for microsecond-level services produces useless distributions where 99% of samples fall into the first bucket. Tailor bucket boundaries to realistic target latencies.

## Verification & Testing

- Validate alerting rules using `promtool`:
  ```bash
  promtool check rules prometheus-alerts.yaml
  ```
- Scrape local metrics endpoint:
  ```bash
  curl -s http://localhost:8000/metrics | grep http_requests_total
  ```
