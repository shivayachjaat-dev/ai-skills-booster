---
name: opentelemetry-collector-pipeline-routing
description: "Use this skill when architecting, configuring, and scaling OpenTelemetry (OTel) Collector pipelines. It guides the agent through defining receivers (OTLP gRPC/HTTP), core processors (memory_limiter, batch, filter, transform), routing connectors (routing connector), multi-backend exporters (Prometheus, Jaeger, Tempo, Loki), and tuning collector throughput."
domain: devops
category: observability
subcategory: opentelemetry-collector
tags:
  - opentelemetry
  - otel-collector
  - observability
  - metrics
  - traces
  - logging
  - devops
technologies:
  - OpenTelemetry Collector
  - OTLP
  - Kubernetes
  - Prometheus
  - Tempo
complexity: advanced
maturity: stable
tools:
  - otelcol
  - kubectl
dependencies:
  - otelcol-contrib >= 0.90.0
---
# OpenTelemetry Collector Pipeline Routing & Scaling Architecture

## Overview

A definitive production engineering reference for designing, configuring, and operating OpenTelemetry Collector gateways. The OpenTelemetry Collector is the vendor-agnostic proxy that receives, transforms, filters, and exports telemetry (traces, metrics, logs) at enterprise scale. This skill instructs AI agents on structuring pipeline components (Receivers, Processors, Exporters, Connectors), enforcing memory safety via `memory_limiter`, mutating attributes using the OpenTelemetry Transformation Language (OTTL), and routing telemetry across multiple specialized backends.

## When to Use

- Deploying a centralized telemetry gateway buffering and processing data from thousands of microservices.
- Scrubbing sensitive PII (credit cards, tokens, emails) from spans and logs before egress to third-party SaaS backends.
- Splitting or routing telemetry dynamically based on environment or tenant attributes using routing connectors.
- Converting spans to metrics (e.g. generating span metrics for latency and error counts).

## When NOT to Use

- Single-service prototypes where microservices can export directly to a local development Jaeger instance without proxy overhead.
- Raw network packet capture or kernel eBPF observability (use Cilium or Tetragon).

## Inputs & Prerequisites

- OpenTelemetry Collector Contrib binary or container (`otelcol-contrib:0.90.0+`).
- Configuration file in YAML format.
- Backend ingestion endpoints (Jaeger, Tempo, Prometheus, Loki, Datadog).

## Core Workflow

### 1. Hardened Production Configuration (`config.yaml`)
Configure memory limiting, batching, transformation, and routing connectors:

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  # 1. Memory Limiter MUST BE FIRST in pipeline to prevent OOM kills
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 20

  # 2. Batching reduces network roundtrips and optimizes backend compression
  batch:
    send_batch_size: 2048
    timeout: 2s
    send_batch_max_size: 4096

  # 3. Transform Processor using OTTL (OpenTelemetry Transformation Language)
  # Redacts sensitive authorization tokens from HTTP attribute spans
  transform:
    error_mode: ignore
    trace_statements:
      - context: span
        statements:
          - replace_pattern(attributes["http.request.headers.authorization"], "Bearer .*", "Bearer [REDACTED]")
          - set(attributes["environment"], "production") where attributes["environment"] == nil

  # 4. Filter out high-frequency health-check endpoint traces
  filter/drop_healthchecks:
    error_mode: ignore
    traces:
      span:
        - attributes["http.target"] == "/healthz"
        - attributes["http.target"] == "/ready"

exporters:
  otlp/tempo:
    endpoint: tempo.monitoring.svc:4317
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889
    namespace: otel

  logging:
    verbosity: basic

connectors:
  # Generates RED metrics (Request, Error, Duration) directly from span data!
  spanmetrics:
    histogram:
      explicit:
        buckets: [2ms, 5ms, 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s]
    dimensions:
      - name: http.status_code
      - name: http.method

service:
  telemetry:
    logs:
      level: info
    metrics:
      address: 0.0.0.0:8888 # Collector internal self-monitoring metrics

  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, filter/drop_healthchecks, transform, batch]
      exporters: [otlp/tempo, spanmetrics]

    metrics:
      receivers: [otlp, spanmetrics]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
```

### 2. Collector Deployment on Kubernetes
Deploy collector as an autoscaling Stateless Gateway Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: monitoring
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
        - name: collector
          image: otel/opentelemetry-collector-contrib:0.95.0
          args: ["--config=/etc/otelcol/config.yaml"]
          resources:
            limits:
              cpu: "2"
              memory: 2Gi
            requests:
              cpu: "500m"
              memory: 1Gi
          volumeMounts:
            - name: config
              mountPath: /etc/otelcol
      volumes:
        - name: config
          configMap:
            name: otel-collector-config
```

## Best Practices & Failure Modes

1. **Placing `memory_limiter` After `batch`**: If `memory_limiter` is placed after other processors, the collector buffers incoming data in memory before checking thresholds, crashing the process with OOM. Always place `memory_limiter` as the very first processor in every pipeline.
2. **Missing `spike_limit_percentage`**: Without spike limit protection, sudden bursts of traffic allocate heap memory faster than the check interval can react, resulting in container SIGKILL.
3. **Dropped Spans on Exporter Outage**: If backends (Tempo/Jaeger) go offline, an in-memory queue without persistent storage drops data. Configure `sending_queue.storage` with disk-backed buffers for mission-critical audit spans.

## Verification & Testing

- Validate collector configuration syntax:
  ```bash
  otelcol-contrib validate --config=otel-collector-config.yaml
  ```
- Query internal collector self-metrics:
  ```bash
  curl -s http://localhost:8888/metrics | grep otelcol_process_uptime
  ```
