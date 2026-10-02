---
name: opentelemetry-distributed-tracing
description: "Use this skill when designing, instrumenting, and troubleshooting end-to-end distributed tracing across microservices using OpenTelemetry (OTel). It covers W3C tracecontext propagation, OTLP gRPC/HTTP exporters, head-based and tail-based sampling strategies, span attributes standardization (semantic conventions), and collector deployment."
domain: devops
category: observability
subcategory: opentelemetry
tags:
  - opentelemetry
  - tracing
  - observability
  - distributed-tracing
  - jaeger
  - tempo
technologies:
  - OpenTelemetry
  - OTel Collector
  - Jaeger
  - Tempo
  - Python OTel SDK
  - Go OTel
complexity: advanced
maturity: stable
tools:
  - opentelemetry-collector
  - jaeger
dependencies:
  - opentelemetry-api >= 1.22.0
---
# OpenTelemetry Distributed Tracing Architecture

## Overview

A production blueprint for implementing unified distributed tracing across microservices architectures using the OpenTelemetry (OTel) standard. This skill guides agents in instrumenting services, configuring W3C traceparent context propagation across HTTP/gRPC boundaries, defining head- and tail-based sampling rates, enforcing OTel semantic conventions, and configuring OpenTelemetry Collectors.

## When to Use

- Tracking request latency, bottlenecks, and error cascades across asynchronous microservices.
- Standardizing observability telemetry into vendor-neutral OTLP format (exportable to Jaeger, Grafana Tempo, Datadog, Honeycomb).
- Instrumenting HTTP clients, message brokers (Kafka/RabbitMQ), and database drivers with correlation IDs.
- Optimizing trace storage costs using adaptive or tail-based sampling for high-throughput traffic.

## When NOT to Use

- Single monolithic apps where basic structured logging and APM profilers provide sufficient insight without distributed network overhead.
- Simple metrics-only use cases where Prometheus counters and gauges are adequate.

## Inputs & Prerequisites

- Services communicating over HTTP, gRPC, or message queues.
- OpenTelemetry SDK for target language (Python, Node.js, Go, Java).
- OpenTelemetry Collector instance or OTLP-compatible backend (Jaeger / Tempo).

## Core Workflow

### 1. Zero-Code vs Programmatic Instrumentation in Python
Configure standard OpenTelemetry tracer with OTLP gRPC exporter:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

def configure_opentelemetry(service_name: str, collector_endpoint: str = "otel-collector:4317"):
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.4.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production",
    })

    provider = TracerProvider(resource=resource)
    
    # Configure OTLP Exporter with Batch Processor
    otlp_exporter = OTLPSpanExporter(
        endpoint=collector_endpoint,
        insecure=True
    )
    span_processor = BatchSpanProcessor(
        otlp_exporter,
        max_queue_size=2048,
        scheduled_delay_millis=5000,
        max_export_batch_size=512
    )
    provider.add_span_processor(span_processor)
    
    # Register global tracer provider
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
```

### 2. Context Propagation Across Network Boundaries
Inject trace headers into outbound requests and extract them on downstream services:

```python
import httpx
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

tracer = trace.get_tracer("payment-service")
propagator = TraceContextTextMapPropagator()

async def call_downstream_inventory(item_id: str):
    with tracer.start_as_current_span("call_downstream_inventory") as span:
        span.set_attribute("item.id", item_id)
        span.set_attribute("rpc.system", "http")

        # Inject W3C tracecontext headers (traceparent, tracestate)
        headers = {}
        propagator.inject(headers)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://inventory-service/items/{item_id}",
                headers=headers
            )
            span.set_attribute("http.status_code", response.status_code)
            return response.json()
```

### 3. OpenTelemetry Collector Pipeline Configuration
Deploy an OpenTelemetry Collector gateway with batching and memory limiting:

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
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 20

  batch:
    send_batch_size: 1024
    timeout: 5s

  # Head-based probabilistic sampling: keep 10% of normal traces, 100% of errors
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: { status_codes: [ ERROR ] }
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: { sampling_percentage: 10.0 }

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, batch]
      exporters: [otlp/tempo]
```

## Best Practices & Failure Modes

1. **Cardianlity Explosion in Span Attributes**: Never put raw user IDs, customer credit cards, or non-indexed timestamps in span attribute keys. Stick to standard OpenTelemetry semantic conventions (`http.method`, `db.system`, `net.peer.name`).
2. **Blocking Network Threads**: Always use `BatchSpanProcessor` in production. Never use `SimpleSpanProcessor` as it sends spans synchronously over the network, drastically degrading application response times.
3. **Clock Skew**: Services must sync via NTP to ensure span ordering across machines is chronologically accurate.

## Verification & Testing

- Verify OTel spans locally using Jaeger UI:
  ```bash
  docker run -d --name jaeger -p 16686:16686 -p 4317:4317 jaegertracing/all-in-one:latest
  ```
- Send test trace via curl:
  ```bash
  curl -i -X POST http://localhost:4318/v1/traces     -H "Content-Type: application/json"     -d '{"resourceSpans": []}'
  ```
- Verify trace search in Jaeger at `http://localhost:16686`.
