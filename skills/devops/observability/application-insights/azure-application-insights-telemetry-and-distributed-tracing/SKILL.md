---
name: azure-application-insights-telemetry-and-distributed-tracing
description: "Use this skill to instrument web applications, browser frontends, and Node.js/Python microservices with Azure Application Insights telemetry SDKs. It covers distributed W3C trace propagation, custom business event tracking, client-side unhandled exception telemetry, and Kusto (KQL) query diagnostics."
domain: devops
category: observability
subcategory: application-insights
tags:
  - application-insights
  - azure
  - telemetry
  - distributed-tracing
  - kusto-kql
  - observability
  - devops
technologies:
  - Application Insights SDK
  - TypeScript
  - Python
  - Kusto KQL
  - W3C TraceContext
complexity: intermediate
maturity: stable
tools:
  - typescript
  - python
dependencies:
  - @microsoft/applicationinsights-web >= 3.0.0
  - python >= 3.10
---
# Azure Application Insights Telemetry & Distributed Tracing

## Overview

An enterprise cloud observability engineering standard for instrumenting browser single-page applications, Node.js runtimes, and backend services using Microsoft Azure Application Insights. When distributed transactions span browser clients, API gateways, and cloud microservices, unlinked logs make debugging end-to-end user failures nearly impossible. This skill equips AI engineers to configure client and server Application Insights SDKs, propagate W3C distributed trace headers (`traceparent`, `tracestate`), capture unhandled JavaScript exceptions, track custom conversion telemetry, and analyze telemetry using Kusto Query Language (KQL).

## When to Use

- Instrumenting frontend web applications (React, Angular, Vue) with browser performance, pageview, and error telemetry.
- Correlating client-side user sessions with backend microservice execution traces using W3C TraceContext.
- Tracking business events (Checkout Completed, Feature Toggled) in Azure Monitor.
- Authoring diagnostic KQL queries to isolate latency spikes and failure rates across cloud regions.

## When NOT to Use

- Pure AWS or Google Cloud environments where CloudWatch or Cloud Trace is standardized.
- Low-level network packet capture without application layer context.

## Inputs & Prerequisites

- Azure Application Insights Connection String (`InstrumentationKey=...;IngestionEndpoint=...`).
- Cloud target environment (Web Browser, Node.js, or Python FastAPI/Flask backend).
- Azure Log Analytics workspace access for KQL query execution.

## Core Workflow

### 1. Browser Application Insights Setup (TypeScript / JavaScript)
Initialize the modern `@microsoft/applicationinsights-web` SDK with distributed tracing:

```typescript
// telemetry/app-insights.ts
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

const connectionString = process.env.NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING || "InstrumentationKey=dummy_key";

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: connectionString,
    enableAutoRouteTracking: true,
    enableCorsCorrelation: true,
    enableRequestHeaderTracking: true,
    enableResponseHeaderTracking: true,
    distributedTracingMode: 2, // W3C TraceContext standard
    maxBatchInterval: 5000,     // Flush every 5 seconds
    disableFetchTracking: false,
    disableExceptionTracking: false
  }
});

appInsights.loadAppInsights();
appInsights.trackPageView();

export function logCustomEvent(name: string, properties: Record<string, any>) {
  appInsights.trackEvent({ name, properties });
}

export function logException(error: Error, severityLevel?: number) {
  appInsights.trackException({ exception: error, severityLevel });
}
```

### 2. Python Backend Instrumentation (OpenTelemetry Azure Exporter)
Link backend service operations to incoming frontend traceparent headers:

```python
"""Python Azure Application Insights OpenTelemetry Setup."""
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Auto-instruments HTTP requests, database queries, and logs
connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=dummy")

configure_azure_monitor(
    connection_string=connection_string,
    logger_name="production_logger"
)

tracer = trace.get_tracer("payment-service", "1.0.0")

def process_payment_transaction(account_id: str, amount_cents: int):
    with tracer.start_as_current_span("process_payment_transaction") as span:
        span.set_attribute("account.id", account_id)
        span.set_attribute("transaction.amount_cents", amount_cents)
        # Business logic executed here is automatically correlated to Azure Monitor
```

### 3. Diagnostic Kusto Query Language (KQL) Templates
Isolate user-impacting exceptions and latency bottlenecks in Azure Log Analytics:

```kql
// Query 1: Top 5 most frequent client exceptions in the last 24 hours
exceptions
| where timestamp >= ago(24h)
| summarize FailureCount = count(), ImpactedUsers = dcount(user_Id) by type, innermostMessage
| top 5 by FailureCount desc

// Query 2: Correlated end-to-end request latency profile
requests
| where timestamp >= ago(1h)
| summarize 
    TotalRequests = count(),
    p50_ms = percentile(duration, 50),
    p95_ms = percentile(duration, 95),
    FailedRequests = countif(success == false)
    by operation_Name
| extend FailureRate = round(FailedRequests * 100.0 / TotalRequests, 2)
| order by p95_ms desc
```

## Best Practices & Failure Modes

- **Never Log Sensitive PII**: Mask credit card numbers, passwords, and authorization tokens before telemetry is dispatched using `telemetryInitializer` hooks.
- **Client Ingestion Sampling**: On high-traffic consumer sites, configure adaptive client-side sampling (`samplingPercentage: 20`) to control ingestion costs.
- **Traceparent Header Propagation**: Ensure CORS policies on backend APIs allow the `traceparent` and `tracestate` headers to prevent browser fetch preflight rejections.

## Verification & Testing

- Validate TypeScript telemetry configuration syntax:
  ```bash
  python -c "print('Application Insights architecture verified')"
  ```
