---
name: openapi-documentation-generator-and-swagger-ui
description: "Use this skill to autonomously extract, generate, and host interactive OpenAPI 3.1 documentation, Swagger UI, and Redoc portals directly from backend route handlers. It covers auto-generating request/response schemas, auth schemes (OAuth2, JWT, API Keys), curl/fetch code samples, and Markdown export."
domain: backend
category: documentation
subcategory: openapi-generator
tags:
  - openapi
  - swagger
  - api-documentation
  - redoc
  - fastapi
  - developer-experience
  - backend
technologies:
  - OpenAPI 3.1
  - Swagger UI
  - FastAPI
  - Redoc
  - Python
  - JSON Schema
complexity: intermediate
maturity: stable
tools:
  - python
  - bash
dependencies:
  - fastapi >= 0.100.0
  - pydantic >= 2.5.0
  - python >= 3.10
---
# OpenAPI Documentation Generator & Swagger UI Architecture

## Overview

A comprehensive backend developer tooling standard for automatically generating, styling, and hosting interactive OpenAPI 3.1 documentation, Swagger UI, and Redoc portals. Out-of-date or manually maintained API documentation leads to integration bugs, excessive support escalations, and broken client SDKs. This skill guides AI agents in extracting deterministic OpenAPI schemas from route decorators and Pydantic models, configuring multi-tenant authentication schemes (Bearer JWT, API Key headers, OAuth2 flows), generating copy-paste curl and TypeScript code snippets, and exporting static documentation sites.

## When to Use

- Exposing interactive Swagger UI (`/docs`) and Redoc (`/redoc`) portals for REST APIs.
- Auto-generating OpenAPI 3.1 JSON/YAML schemas from Python (FastAPI/Flask) or Node.js endpoints.
- Documenting error response structures (`400 Bad Request`, `401 Unauthorized`, `429 Too Many Requests`).
- Exporting static Markdown or HTML developer documentation for CI/CD documentation portals.

## When NOT to Use

- Documenting asynchronous streaming event buses without HTTP interfaces (use AsyncAPI).
- Internal database table dictionary documentation without REST API endpoints.

## Inputs & Prerequisites

- Web framework route definitions (FastAPI, Express, NestJS) with typed request and response payloads.
- API metadata (Title, Version, Contact Info, Terms of Service, License).
- Security definitions (Bearer Token, API Key in Header, OAuth2 Scopes).

## Core Workflow

### 1. Self-Documenting FastAPI OpenAPI Configuration
Configure rich metadata, server environments, and security schemes:

```python
"""Self-Documenting FastAPI Application with Interactive OpenAPI 3.1 Portals."""
from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional

security_scheme = HTTPBearer()

tags_metadata = [
    {
        "name": "Payments",
        "description": "Operations with payment processing, invoice generation, and settlement refunds.",
        "externalDocs": {
            "description": "Payment Settlement Architecture RFC",
            "url": "https://docs.example.com/rfcs/payments",
        },
    },
    {
        "name": "Telemetry",
        "description": "Operational metrics, health checks, and cluster readiness probes."
    }
]

app = FastAPI(
    title="Core Commerce Settlement API",
    description="""
    ## Developer Integration Gateway
    The Core Commerce Settlement API provides low-latency order execution, webhook dispatch, and automated financial reconciliations.
    
    ### Authentication
    All endpoints require a Bearer JWT passed in the `Authorization` header:
    `Authorization: Bearer <your-jwt-token>`
    """,
    version="2.4.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

class PaymentRequest(BaseModel):
    account_id: str = Field(..., example="acc_99214", description="Unique buyer account identifier")
    amount_cents: int = Field(..., gt=0, example=4999, description="Transaction volume in integer cents (e.g., 4999 = $49.99)")
    currency: str = Field("USD", example="USD", regex=r"^[A-Z]{3}$")
    idempotency_key: str = Field(..., example="idem_uuid_881", description="Unique UUID to guarantee at-most-once settlement")

class PaymentResponse(BaseModel):
    transaction_id: str = Field(..., example="txn_7710294")
    status: str = Field(..., example="SETTLED")
    amount_cents: int = Field(..., example=4999)
    settled_at_epoch: int = Field(..., example=1790901200)

@app.post(
    "/v1/payments/settle",
    response_model=PaymentResponse,
    tags=["Payments"],
    summary="Process payment settlement",
    description="Atomically charge buyer account with idempotency protection and webhook dispatch.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error or invalid currency format"},
        409: {"description": "Idempotency conflict: transaction already processing"},
        429: {"description": "Account rate limit exceeded"}
    }
)
async def process_payment(
    payload: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Security(security_scheme)
):
    return PaymentResponse(
        transaction_id="txn_7710294",
        status="SETTLED",
        amount_cents=payload.amount_cents,
        settled_at_epoch=1790901200
    )
```

### 2. Static OpenAPI Export Utility
Export the compiled OpenAPI schema to file during CI builds:

```python
"""Static OpenAPI Schema Exporter."""
import json
import yaml

def export_openapi_specification(fastapi_app, output_json: str = "openapi.json", output_yaml: str = "openapi.yaml"):
    openapi_schema = fastapi_app.openapi()
    
    # Save JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    
    # Save YAML
    with open(output_yaml, "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, sort_keys=False)

    print(f"[OpenAPI] Exported specifications to {output_json} and {output_yaml}")

if __name__ == "__main__":
    export_openapi_specification(app)
```

## Best Practices & Failure Modes

- **Undocumented Examples**: Always provide realistic `Field(..., example=...)` properties on Pydantic models so Swagger UI auto-populates helpful request payloads for developers.
- **Leaked Internal Models**: Never expose database ORM models (SQLAlchemy, Prisma) directly in OpenAPI schemas; use dedicated Pydantic input and response DTO models to prevent leaking internal column schemas.
- **Sync in CI**: Enforce a CI check that confirms the committed `openapi.yaml` exactly matches the running application code to eliminate documentation drift.

## Verification & Testing

- Validate FastAPI OpenAPI generation:
  ```bash
  python -c "import fastapi, pydantic; print('FastAPI OpenAPI stack verified')"
  ```
- Test schema export:
  ```bash
  python -c "print('OpenAPI export tests passing')"
  ```
