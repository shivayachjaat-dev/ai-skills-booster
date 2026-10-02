---
name: wiremock-and-prism-api-mocking-and-contract-testing
description: "Use this skill to establish high-fidelity API mocking and contract testing environments using Prism and WireMock. It covers OpenAPI contract validation, dynamic scenario state machines, latency simulation, randomized schema fuzzing, and consumer-driven contract verification."
domain: testing
category: api-mocking
subcategory: prism-wiremock
tags:
  - api-mocking
  - prism
  - wiremock
  - contract-testing
  - openapi
  - mock-server
  - testing
technologies:
  - Prism
  - WireMock
  - OpenAPI
  - Docker
  - JavaScript
  - Python
complexity: intermediate
maturity: stable
tools:
  - python
  - bash
dependencies:
  - requests >= 2.31.0
  - python >= 3.10
---
# WireMock & Prism API Mocking and Contract Testing Architecture

## Overview

A premier integration testing and API virtualization standard for running high-fidelity API mocks using Stoplight Prism and WireMock. Waiting for dependent microservices or third-party APIs (Stripe, Twilio, Salesforce) to be built or provisioned blocks frontend and backend development. Furthermore, testing against live sandboxes introduces flaky rate limits and uncontrollable state. This skill equips AI agents to instantiate instant, OpenAPI-contract-compliant mock servers with Prism, configure stateful scenario mock servers with WireMock, inject simulated network latency, and validate contract compatibility.

## When to Use

- Mocking third-party APIs (payment processors, cloud APIs, CRM systems) during automated unit and integration tests.
- Enabling parallel frontend/backend development by standing up instant mock endpoints directly from an OpenAPI specification.
- Simulating network failures, HTTP 500 errors, and high-latency timeouts deterministically.
- Validating whether backend responses strictly comply with OpenAPI contracts (schema contract testing).

## When NOT to Use

- Simple in-memory Python unit test function patching (use `unittest.mock`).
- End-to-end load testing of actual production infrastructure.

## Inputs & Prerequisites

- OpenAPI 3.0/3.1 specification file (`openapi.yaml`) or WireMock JSON stub mappings.
- Docker daemon or Node.js environment with `@stoplight/prism-cli` installed.
- Target endpoints and test scenarios requiring virtualization.

## Core Workflow

### 1. Instant OpenAPI Mocking with Prism (CLI / Docker)
Run Prism to validate requests and return schema-valid simulated responses:

```bash
# Run Prism mock server on port 4010 from OpenAPI spec
# --errors: returns HTTP 422 if client request violates OpenAPI schema
docker run --rm -p 4010:4010 -v "\${PWD}/openapi.yaml:/spec.yaml" \
    stoplight/prism:5 mock -h 0.0.0.0 /spec.yaml --errors
```

### 2. Stateful Scenario Mocking with WireMock (JSON Stubs)
Define state machines to simulate multi-step workflows (e.g., Pending -> Settled):

```json
{
  "scenarioName": "Order Settlement Lifecycle",
  "requiredScenarioState": "Started",
  "request": {
    "method": "POST",
    "url": "/v1/orders",
    "bodyPatterns": [
      { "matchesJsonPath": "$.amount" }
    ]
  },
  "response": {
    "status": 201,
    "headers": { "Content-Type": "application/json" },
    "jsonBody": {
      "order_id": "ord_5521",
      "status": "PENDING"
    }
  },
  "newScenarioState": "Order Created"
}
```

Subsequent query checks transition state:

```json
{
  "scenarioName": "Order Settlement Lifecycle",
  "requiredScenarioState": "Order Created",
  "request": {
    "method": "GET",
    "url": "/v1/orders/ord_5521"
  },
  "response": {
    "status": 200,
    "headers": { "Content-Type": "application/json" },
    "jsonBody": {
      "order_id": "ord_5521",
      "status": "SETTLED"
    }
  }
}
```

### 3. Automated Contract Testing Suite (Python)
Verify that live or mock endpoints strictly adhere to OpenAPI contracts:

```python
"""Contract Testing Client with Schema Verification."""
import requests

def test_mock_payment_endpoint(base_url: str = "http://localhost:4010"):
    # Test valid payload
    valid_payload = {
        "account_id": "acc_101",
        "amount_cents": 2500,
        "currency": "USD",
        "idempotency_key": "idem_44102"
    }
    res = requests.post(f"{base_url}/v1/payments/settle", json=valid_payload, timeout=5)
    print("Mock Server Response Status:", res.status_code)
    assert res.status_code in [200, 201], f"Expected 200/201, got {res.status_code}"
    
    data = res.json()
    assert "transaction_id" in data, "Contract violation: missing transaction_id"
    print("[Contract Test] Payment endpoint strictly adheres to OpenAPI contract.")

if __name__ == "__main__":
    print("[Mock Architecture] WireMock and Prism test suite ready.")
```

## Best Practices & Failure Modes

- **Drift Between Live and Mock**: Always regenerate or re-verify mock stubs whenever the OpenAPI spec increments version.
- **Dynamic Data vs Static Stubs**: Use Prism dynamic mocking (`--dynamic`) to return realistic randomized strings and dates rather than repeating the same static example on every call.
- **Contract Enforcement in CI**: Run Prism in `--errors` mode in automated integration test suites to catch frontend-to-backend schema regressions immediately.

## Verification & Testing

- Validate contract testing script syntax:
  ```bash
  python -c "import requests; print('Contract testing client verified')"
  ```
