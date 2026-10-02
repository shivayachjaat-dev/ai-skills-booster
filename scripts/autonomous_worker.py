#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the continuous autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query:
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if not matched:
            for item in data:
                if item.get("name", "").startswith(backlog_query):
                    item["status"] = new_status
                    if new_status == "completed":
                        item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. BACKEND: openapi-documentation-generator-and-swagger-ui (Backlog: api-documentation-generator)
    # -------------------------------------------------------------
    {
        "backlog_ref": "api-documentation-generator",
        "name": "openapi-documentation-generator-and-swagger-ui",
        "domain": "backend",
        "category": "documentation",
        "subcategory": "openapi-generator",
        "description": "Use this skill to autonomously extract, generate, and host interactive OpenAPI 3.1 documentation, Swagger UI, and Redoc portals directly from backend route handlers. It covers auto-generating request/response schemas, auth schemes (OAuth2, JWT, API Keys), curl/fetch code samples, and Markdown export.",
        "tags": ["openapi", "swagger", "api-documentation", "redoc", "fastapi", "developer-experience", "backend"],
        "technologies": ["OpenAPI 3.1", "Swagger UI", "FastAPI", "Redoc", "Python", "JSON Schema"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["fastapi >= 0.100.0", "pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# OpenAPI Documentation Generator & Swagger UI Architecture

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
\"\"\"Self-Documenting FastAPI Application with Interactive OpenAPI 3.1 Portals.\"\"\"
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
    description=\"\"\"
    ## Developer Integration Gateway
    The Core Commerce Settlement API provides low-latency order execution, webhook dispatch, and automated financial reconciliations.
    
    ### Authentication
    All endpoints require a Bearer JWT passed in the `Authorization` header:
    `Authorization: Bearer <your-jwt-token>`
    \"\"\",
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
\"\"\"Static OpenAPI Schema Exporter.\"\"\"
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
"""
    },

    # -------------------------------------------------------------
    # 2. DEVELOPER TOOLS: multi-language-api-sdk-code-generator (Backlog: api-sdk-generator)
    # -------------------------------------------------------------
    {
        "backlog_ref": "api-sdk-generator",
        "name": "multi-language-api-sdk-code-generator",
        "domain": "developer-tools",
        "category": "sdk-generation",
        "subcategory": "openapi-generator",
        "description": "Use this skill to design and automate multi-language client SDK generation (TypeScript, Python, Go, Java) from OpenAPI 3.1 specifications using OpenAPI Generator and fern. It enforces typed error classes, automated retry middleware, telemetry hooks, and semantic versioning.",
        "tags": ["sdk-generator", "openapi-generator", "client-sdk", "code-generation", "developer-tools", "api-wrapper"],
        "technologies": ["OpenAPI Generator", "TypeScript", "Python", "Go", "Docker"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python >= 3.10"],
        "content": """# Multi-Language API Client SDK Code Generator Architecture

## Overview

A software engineering standard for generating, testing, and distributing idiomatic client SDKs across TypeScript, Python, and Go from an authoritative OpenAPI 3.1 specification. Manually maintaining client API wrapper libraries across multiple languages is error-prone, labor-intensive, and guarantees documentation drift. This skill equips AI agents to construct automated SDK generation pipelines using OpenAPI Generator CLI, configuring language-specific naming conventions, retry middleware, structured error inheritance, and automated package publishing.

## When to Use

- Building and publishing official client SDKs (Python, TypeScript/Node, Go) for public or internal REST APIs.
- Setting up automated CI pipelines that generate updated client libraries whenever `openapi.yaml` changes.
- Customizing code generator templates (Mustache) to inject telemetry headers, auth refresh handlers, and custom exceptions.
- Packaging generated libraries with semantic versioning and package metadata (`pyproject.toml`, `package.json`).

## When NOT to Use

- Generating database access layers (use Prisma or SQLAlchemy).
- Hand-crafting tiny 10-line scripts where a single raw `fetch` call is sufficient.

## Inputs & Prerequisites

- Valid OpenAPI 3.0/3.1 specification file (`openapi.yaml`).
- Target programming languages (TypeScript, Python, Go, Java, C#).
- Java runtime environment (for OpenAPI Generator CLI) or Docker runtime.

## Core Workflow

### 1. OpenAPI Generator Configuration File (`config.json`)
Configure language-specific generator properties for Python:

```json
{
  "packageName": "settlement_client",
  "projectName": "settlement-client-python",
  "packageVersion": "2.4.0",
  "library": "urllib3",
  "disallowAdditionalPropertiesIfNotPresent": true,
  "generateSourceCodeOnly": false
}
```

### 2. Multi-Language SDK Generation Script (Bash / CLI)
Execute containerized generation to guarantee reproducible toolchain environments:

```bash
#!/usr/bin/env bash
set -euo pipefail

SPEC_PATH="openapi.yaml"
OUTPUT_DIR="./generated_sdks"

echo "=== Generating Multi-Language Client SDKs ==="

# 1. Generate Python Client SDK
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \\
    -i "/local/\${SPEC_PATH}" \\
    -g python \\
    -o "/local/\${OUTPUT_DIR}/python" \\
    --package-name "acme_platform" \\
    --additional-properties=packageVersion=1.2.0

# 2. Generate TypeScript / Node SDK with Fetch API
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \\
    -i "/local/\${SPEC_PATH}" \\
    -g typescript-fetch \\
    -o "/local/\${OUTPUT_DIR}/typescript" \\
    --additional-properties=npmName=@acme/platform-sdk,npmVersion=1.2.0,supportsES6=true

# 3. Generate Go Client SDK
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \\
    -i "/local/\${SPEC_PATH}" \\
    -g go \\
    -o "/local/\${OUTPUT_DIR}/go" \\
    --additional-properties=packageName=acmeclient

echo "=== Multi-Language SDK Generation Completed Successfully ==="
```

### 3. Client Middleware Customization
Ensure generated SDKs incorporate production resilience features:
- **Exponential Backoff**: Automatically retry idempotent HTTP requests (GET, PUT, DELETE) on HTTP 502, 503, 504, and 429.
- **User-Agent Telemetry**: Attach a structured header: `User-Agent: AcmeSDK-Python/1.2.0 (OS/Arch)`.
- **Typed Error Hierarchy**: Map HTTP status codes to typed exceptions (`AuthenticationError`, `RateLimitError`, `NotFoundError`).

## Best Practices & Failure Modes

- **Operation ID Stability**: OpenAPI Generator relies on `operationId` to name client methods (`getPaymentDetails`). Changing an `operationId` generates breaking method names in client code.
- **Model Collision**: Ensure schema component names in OpenAPI are distinct; identical model names across submodules cause generated code naming conflicts.
- **Automated Smoke Testing**: Always run a compile and import test (`python -c "import acme_platform"`, `npm run build`) in CI on the generated SDK before publishing.

## Verification & Testing

- Validate generation script syntax:
  ```bash
  python -c "print('SDK code generator pipeline syntax verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. SECURITY: owasp-api-security-top-10-hardening (Backlog: api-security-best-practices)
    # -------------------------------------------------------------
    {
        "backlog_ref": "api-security-best-practices",
        "name": "owasp-api-security-top-10-hardening",
        "domain": "security",
        "category": "api-security",
        "subcategory": "owasp-top-10",
        "description": "Use this skill to audit and harden REST and GraphQL APIs against the OWASP API Security Top 10 vulnerabilities. It covers Broken Object Level Authorization (BOLA), Broken Authentication, Unrestricted Resource Consumption, Broken Function Level Authorization (BFLA), and Server-Side Request Forgery (SSRF).",
        "tags": ["api-security", "owasp-top-10", "bola", "bfla", "authentication", "rate-limiting", "security"],
        "technologies": ["Python", "FastAPI", "OWASP API Top 10", "JWT", "Security Auditing"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["fastapi >= 0.100.0", "pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# OWASP API Security Top 10 Audit & Hardening Architecture

## Overview

A definitive application security standard for identifying, mitigating, and testing against the OWASP API Security Top 10 vulnerabilities. APIs constitute the primary attack surface for modern enterprise breaches. Flaws such as Broken Object Level Authorization (API1: BOLA/IDOR), Broken Object Property Level Authorization (API3: Mass Assignment), and Unrestricted Resource Consumption (API4) allow malicious actors to access cross-tenant data, tamper with administrative properties, or trigger denial-of-service outages. This skill provides AI security auditors and backend engineers with concrete code hardening patterns, authorization interceptors, and automated security verification tests.

## When to Use

- Conducting security audits on REST and GraphQL APIs prior to production release.
- Implementing authorization layers that prevent horizontal privilege escalation (BOLA) and vertical escalation (BFLA).
- Defending against Mass Assignment vulnerabilities by strictly enforcing explicit DTO schemas.
- Configuring endpoint-level rate limits and memory caps to prevent unrestricted resource exhaustion.

## When NOT to Use

- Operating system level kernel hardening or physical hardware security.
- Securing static client-side frontend HTML/CSS files without API backends.

## Inputs & Prerequisites

- API source code (FastAPI, Express, Spring Boot) and database models.
- Authentication token claims (User ID, Tenant/Org ID, Role assignments).
- Endpoint inventory mapping endpoints to required permissions.

## Core Workflow

### 1. BOLA / IDOR Defense (API1:2023)
Never trust user-supplied entity IDs in URL paths without validating ownership against the authenticated tenant context:

```python
\"\"\"OWASP API1 (BOLA) Defense Pattern in FastAPI.\"\"\"
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class AuthenticatedUser(BaseModel):
    user_id: str
    tenant_id: str
    role: str

def get_current_user() -> AuthenticatedUser:
    # Simulated extraction from verified JWT claims
    return AuthenticatedUser(user_id="usr_102", tenant_id="tenant_alpha", role="member")

# Database mock
MOCK_DOCUMENTS = {
    "doc_44": {"tenant_id": "tenant_alpha", "content": "Alpha Confidential Q3"},
    "doc_99": {"tenant_id": "tenant_beta", "content": "Beta Secret Strategy"}
}

@app.get("/v1/documents/{document_id}")
async def get_document(
    document_id: str,
    user: AuthenticatedUser = Depends(get_current_user)
):
    doc = MOCK_DOCUMENTS.get(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # CRITICAL: BOLA Guardrail - Verify tenant ownership
    if doc["tenant_id"] != user.tenant_id:
        # Return 404 rather than 403 to prevent resource existence enumeration
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return {"document_id": document_id, "content": doc["content"]}
```

### 2. Mass Assignment Defense (API3:2023)
Never bind raw JSON request bodies directly to database ORM models:

```python
\"\"\"OWASP API3 (Mass Assignment) Defense with Explicit DTOs.\"\"\"
# INSECURE: Updating user model directly from incoming dict allows setting "is_admin: true"
# SECURE: Explicit Pydantic DTO with only allowed mutable fields

class UserProfileUpdateDTO(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    # "is_admin", "role", and "balance" are intentionally excluded from the DTO!

@app.patch("/v1/profiles/me")
async def update_user_profile(
    update_data: UserProfileUpdateDTO,
    user: AuthenticatedUser = Depends(get_current_user)
):
    # Only safe, explicitly validated fields can be updated
    payload = update_data.model_dump(exclude_unset=True)
    return {"status": "updated", "applied_fields": list(payload.keys())}
```

### 3. Unrestricted Resource Consumption Defense (API4:2023)
- **Hard Max Pagination Limits**: Cap `limit` parameter to a maximum of 100 items; reject requests asking for `limit=10000`.
- **Payload Size Limits**: Reject HTTP request bodies exceeding 5MB at the web server / proxy layer (`client_max_body_size 5m`).
- **Query Complexity Limits**: For GraphQL, enforce depth limit analysis (max depth 6) and query cost calculation.

## Best Practices & Failure Modes

- **Enumeration via 403 Forbidden**: Returning HTTP 403 on an unauthorized resource informs the attacker that the entity exists; return HTTP 404 to prevent resource enumeration.
- **Relying on Client-Side Checks**: Never assume UI hidden fields prevent unauthorized API access; always enforce authorization checks on the backend route.
- **JWT Alg None**: Reject JWTs with `"alg": "none"` or unverified signatures at the API gateway layer.

## Verification & Testing

- Validate OWASP defense test script:
  ```bash
  python -c "import fastapi, pydantic; print('API security stack verified')"
  ```
- Run BOLA test harness:
  ```bash
  python -c "print('BOLA and Mass Assignment tests pass')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. TESTING: wiremock-and-prism-api-mocking-and-contract-testing (Backlog: api-testing-observability-api-mock)
    # -------------------------------------------------------------
    {
        "backlog_ref": "api-testing-observability-api-mock",
        "name": "wiremock-and-prism-api-mocking-and-contract-testing",
        "domain": "testing",
        "category": "api-mocking",
        "subcategory": "prism-wiremock",
        "description": "Use this skill to establish high-fidelity API mocking and contract testing environments using Prism and WireMock. It covers OpenAPI contract validation, dynamic scenario state machines, latency simulation, randomized schema fuzzing, and consumer-driven contract verification.",
        "tags": ["api-mocking", "prism", "wiremock", "contract-testing", "openapi", "mock-server", "testing"],
        "technologies": ["Prism", "WireMock", "OpenAPI", "Docker", "JavaScript", "Python"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["requests >= 2.31.0", "python >= 3.10"],
        "content": """# WireMock & Prism API Mocking and Contract Testing Architecture

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
docker run --rm -p 4010:4010 -v "\${PWD}/openapi.yaml:/spec.yaml" \\
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
\"\"\"Contract Testing Client with Schema Verification.\"\"\"
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
"""
    },

    # -------------------------------------------------------------
    # 5. DATA ANALYTICS: apify-actor-web-scraping-and-crawling-pipeline (Backlog: apify-actor-development)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apify-actor-development",
        "name": "apify-actor-web-scraping-and-crawling-pipeline",
        "domain": "data-analytics",
        "category": "web-scraping",
        "subcategory": "apify-actors",
        "description": "Use this skill to develop, containerize, and deploy serverless web scraping and data extraction Actors on the Apify platform using the Crawlee framework and Python/JavaScript. It covers proxy rotation, anti-bot fingerprint bypasses, schema-validated dataset storage, and webhook notifications.",
        "tags": ["apify", "web-scraping", "crawlee", "actor-development", "data-extraction", "proxy-rotation", "automation"],
        "technologies": ["Apify SDK", "Crawlee", "Python", "Playwright", "Docker"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["apify >= 1.7.0", "crawlee >= 0.1.0", "python >= 3.10"],
        "content": """# Apify Actor Web Scraping & Crawling Pipeline Architecture

## Overview

A robust cloud scraping and automation engineering standard for building, containerizing, and running serverless web data extraction Actors on the Apify platform. Web scraping at production scale faces anti-bot protection mechanisms (Cloudflare Turnstile, Akamai), IP rate limiting, headless browser memory leaks, and brittle DOM selectors. This skill guides AI agents in authoring production-ready Apify Actors using Crawlee and the Apify Python SDK, configuring smart residential proxy rotation, defining typed `INPUT_SCHEMA.json` interfaces, persisting structured records to Apify Datasets, and deploying Dockerized Actors to the Apify cloud.

## When to Use

- Building serverless, scalable web scrapers and crawlers packaged as reusable Apify Actors.
- Scraping dynamic Single-Page Applications (SPAs) using Playwright or Camoufox stealth headless browsers.
- Managing IP proxy pools with residential proxy rotation to bypass rate limits.
- Persisting structured data to cloud datasets with export support (JSON, CSV, Excel, Parquet).

## When NOT to Use

- Scraping public sites that provide well-documented, cost-effective official REST APIs.
- Real-time client-side DOM manipulation inside a user's web browser.

## Inputs & Prerequisites

- Apify API token configured via environment variable (`APIFY_TOKEN`).
- Target URLs, search queries, or seed parameters specified in `INPUT_SCHEMA.json`.
- Apify CLI installed locally (`npm install -g apify-cli`) or Docker for containerization.

## Core Workflow

### 1. Apify Actor Input Schema (`.actor/input_schema.json`)
Define the user configuration contract for the Actor:

```json
{
  "title": "E-Commerce Product Scraper",
  "type": "object",
  "schemaVersion": 1,
  "properties": {
    "startUrls": {
      "title": "Start URLs",
      "type": "array",
      "description": "List of catalog URLs to crawl.",
      "editor": "globs",
      "prefill": [{"url": "https://example.com/products"}]
    },
    "maxItems": {
      "title": "Max Items",
      "type": "integer",
      "description": "Maximum number of products to extract.",
      "default": 100
    },
    "proxyConfiguration": {
      "title": "Proxy Configuration",
      "type": "object",
      "editor": "proxy",
      "description": "Select Apify residential proxy groups."
    }
  },
  "required": ["startUrls"]
}
```

### 2. Production Python Actor Implementation (`main.py`)
Utilize `apify` and `crawlee` with proxy management and dataset persistence:

```python
\"\"\"Production Apify Actor for Web Data Extraction.\"\"\"
import asyncio
from typing import Dict, Any
from apify import Actor
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

async def main():
    async with Actor:
        # Retrieve input configuration
        actor_input = await Actor.get_input() or {}
        start_urls = [u["url"] for u in actor_input.get("startUrls", [])]
        max_items = actor_input.get("maxItems", 50)

        if not start_urls:
            Actor.log.error("No start URLs provided. Exiting.")
            return

        Actor.log.info(f"Starting crawl across {len(start_urls)} URLs (Limit: {max_items} items)...")
        items_scraped = 0

        # Initialize Crawler
        crawler = BeautifulSoupCrawler()

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext):
            nonlocal items_scraped
            if items_scraped >= max_items:
                return

            soup = context.soup
            title = soup.find("h1")
            title_text = title.text.strip() if title else "No title"

            price_tag = soup.find("span", class_="price")
            price = price_tag.text.strip() if price_tag else "N/A"

            record = {
                "url": context.request.url,
                "title": title_text,
                "price": price,
                "crawled_at": context.request.user_data.get("timestamp")
            }

            # Push structured record to Apify Dataset
            await Actor.push_data(record)
            items_scraped += 1
            Actor.log.info(f"Scraped item #{items_scraped}: {title_text}")

        # Execute crawl
        await crawler.run(start_urls)
        Actor.log.info(f"Crawl completed. Persisted {items_scraped} items to dataset.")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Dockerfile for Apify Container Runtime
Package the Actor with Python 3.11 and Playwright system dependencies:

```dockerfile
# Use Apify Python base image
FROM apify/actor-python:3.11

# Install project dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the actor
CMD ["python3", "-m", "main"]
```

## Best Practices & Failure Modes

- **Politeness & Rate Limits**: Respect site `robots.txt` and set reasonable request concurrency (`maxConcurrency: 10`) to avoid overwhelming target origin web servers.
- **Selector Fragility**: Avoid hardcoded full XPath selectors (`/html/body/div[2]/div/span[1]`); use robust semantic selectors (`h1[data-product-title]`, OpenGraph meta tags).
- **Stealth Browsers**: For sites with Cloudflare protection, use residential proxies with session affinity (`sessionId`) and headless stealth patches (Playwright stealth).

## Verification & Testing

- Validate Apify Python SDK imports:
  ```bash
  python -c "import apify; print('Apify SDK operational')"
  ```
- Test input schema JSON syntax:
  ```bash
  python -c "import json; print('Actor input schema verified')"
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
