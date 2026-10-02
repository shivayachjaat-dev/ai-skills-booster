---
name: owasp-api-security-top-10-hardening
description: "Use this skill to audit and harden REST and GraphQL APIs against the OWASP API Security Top 10 vulnerabilities. It covers Broken Object Level Authorization (BOLA), Broken Authentication, Unrestricted Resource Consumption, Broken Function Level Authorization (BFLA), and Server-Side Request Forgery (SSRF)."
domain: security
category: api-security
subcategory: owasp-top-10
tags:
  - api-security
  - owasp-top-10
  - bola
  - bfla
  - authentication
  - rate-limiting
  - security
technologies:
  - Python
  - FastAPI
  - OWASP API Top 10
  - JWT
  - Security Auditing
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - fastapi >= 0.100.0
  - pydantic >= 2.5.0
  - python >= 3.10
---
# OWASP API Security Top 10 Audit & Hardening Architecture

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
"""OWASP API1 (BOLA) Defense Pattern in FastAPI."""
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
"""OWASP API3 (Mass Assignment) Defense with Explicit DTOs."""
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
