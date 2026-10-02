---
name: k6-api-load-testing
description: "Use this skill when designing, executing, and analyzing performance and stress load test suites for backend APIs using Grafana k6. It guides the agent through defining Virtual User (VU) ramping stages, establishing SLA performance thresholds (P95/P99 latency, error rate), simulating realistic traffic patterns, and identifying database concurrency bottlenecks."
domain: testing
category: load-testing
subcategory: k6
tags:
  - k6
  - load-testing
  - performance
  - testing
  - benchmarking
  - backend
technologies:
  - Grafana k6
  - JavaScript
  - TypeScript
  - REST
  - HTTP/2
complexity: advanced
maturity: stable
tools:
  - k6
  - python
dependencies:
  - k6 >= 0.45
---
# k6 API Load Testing

## Overview

A performance engineering framework for designing, executing, and analyzing high-load stress tests on web APIs using Grafana k6. Enables AI agents to model realistic user journeys, define verifiable SLA performance thresholds, detect memory leaks under sustained load, and isolate database concurrency bottlenecks.

## When to Use

- Verifying backend capacity before major product launches or high-traffic events (e.g. Black Friday).
- Establishing automated performance regression gates in CI/CD pipelines.
- Stress testing systems to determine maximum breaking points and recovery behaviors.
- Benchmarking microservice latencies under concurrent load (100 to 50,000 requests/sec).

## When NOT to Use

- Client-side browser rendering and layout performance (use Lighthouse or `browser-performance-profiling`).
- Single-request functional unit tests (use Vitest or Pytest).

## Inputs & Prerequisites

- Grafana k6 CLI installed (`brew install k6` or downloaded binary).
- Target API base URL and test dataset (pre-seeded credentials or test accounts).
- Target Service Level Objectives (SLOs) (e.g. 99% of requests < 200ms at 1,000 VUs).

## Core Workflow

### 1. Test Script Architecture & Workload Modeling
Write k6 test scripts in JavaScript, structuring workload stages:
```javascript
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "1m", target: 50 },  // Ramp-up to 50 Virtual Users (VUs)
    { duration: "3m", target: 50 },  // Steady-state load
    { duration: "1m", target: 200 }, // Spike test to 200 VUs
    { duration: "1m", target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],              // Error rate must be under 1%
    http_req_duration: ["p(95)<250", "p(99)<500"] // 95% < 250ms, 99% < 500ms
  },
};

export default function () {
  const params = {
    headers: { "Content-Type": "application/json" },
  };
  
  const res = http.get("https://api.example.com/products?category=electronics", params);
  
  check(res, {
    "status is 200": (r) => r.status === 200,
    "response body not empty": (r) => r.body && r.body.length > 0,
  });

  sleep(1); // Realistic user think time
}
```

### 2. Test Topologies by Objective
- **Smoke Test**: Minimal load (1-2 VUs for 1 minute) to verify script syntax and basic endpoint health.
- **Load Test**: Steady target production volume (e.g. 500 VUs for 30 minutes) to evaluate normal behavior.
- **Stress Test**: Continuously increasing load until the system begins to fail, identifying the maximum throughput ceiling.
- **Spike Test**: Sudden massive surge from 10 to 1,000 VUs within 15 seconds, verifying auto-scaler and rate-limiter resilience.
- **Soak Test**: Moderate load over 4 to 12 hours, identifying slow memory leaks and database connection pool exhaustion.

### 3. Dynamic Test Data Parameterization
Avoid hitting the exact same URL parameter repeatedly, as caching layers will mask database bottlenecks. Parameterize test inputs:
```javascript
import { SharedArray } from "k6/data";

const testUsers = new SharedArray("users", function () {
  return JSON.parse(open("./fixtures/users.json"));
});

export default function () {
  const user = testUsers[Math.floor(Math.random() * testUsers.length)];
  // Use unique user credentials...
}
```

### 4. Metrics Dissection & Bottleneck Triage
Inspect k6 summary output:
- `http_req_waiting` (TTFB): Time spent waiting for server processing. High TTFB indicates database locking, slow queries, or CPU saturation.
- `http_req_connecting`: Time spent establishing TCP connections. High connecting time indicates threadpool starvation or port exhaustion.
- `http_req_duration`: End-to-end roundtrip latency.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Load generator CPU saturates at 100% | The bottleneck is the test machine itself, not the API. Distribute test execution across multiple k6 worker nodes or optimize script. |
| High rate of connection reset errors | Check load balancer / reverse proxy keepalive timeouts and connection limits (e.g. Nginx `worker_connections`). |
| Database connection pool exhaustion | Look for flat line latency spikes where requests queue up waiting for an available DB connection from the pool. |

## Validation & Acceptance Criteria

- [ ] All declared thresholds (P95, P99, error rate) evaluated programmatically.
- [ ] Test scripts include randomized user think times (`sleep(1)`).
- [ ] Test parameters randomized to prevent false cache-hit masking.
- [ ] Exit code 0 returned when all thresholds are met; non-zero on SLA violation.

## Failure Handling & Recovery

- If error rates spike over 50% during stress testing, immediately abort execution using threshold abort rules (`abortOnFail: true`) to avoid crashing shared staging databases.

## Expected Output & Artifacts

- Modular k6 test script.
- Performance execution summary report.
- CI/CD quality gate integration configuration.

## Related Skills

- `api-rate-limiting-and-throttling`
- `postgres-query-performance-analysis`
- `fastapi-async-api-design`
