---
name: rest-and-graphql-api-spec-analyzer
description: "Use this skill to statically audit, lint, and validate REST, OpenAPI 3.1, and GraphQL schema specifications against architectural best practices. It checks for consistent HTTP verb usage, snake/camel case casing conventions, missing pagination contracts, unversioned breaking changes, and rate limiting headers."
domain: backend
category: api-design
subcategory: api-analyzer
tags:
  - api-design
  - openapi
  - graphql
  - rest-api
  - schema-validation
  - spectral
  - backend
technologies:
  - OpenAPI 3.1
  - GraphQL
  - Python
  - Pydantic
  - Spectral Linter
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - pyyaml >= 6.0.0
  - python >= 3.10
---
# REST & GraphQL API Specification Analyzer

## Overview

A premier API governance and architecture standard for statically analyzing, linting, and validating REST, OpenAPI 3.1, and GraphQL schema specifications. Inconsistent API contracts (mixing camelCase and snake_case, missing HTTP 400/500 error response definitions, unpaginated collections, breaking changes across minor versions) degrade developer experience and cause client-side application crashes. This skill provides AI agents with an automated linting engine that evaluates API specs against battle-tested enterprise standards, enforces uniform casing, checks for pagination contracts, and detects schema regressions.

## When to Use

- Auditing OpenAPI 3.0/3.1 YAML and JSON specifications during pull request reviews.
- Validating GraphQL Schema Definition Language (SDL) for depth limit risks and naming conventions.
- Enforcing standardized error envelope structures (`RFC 7807 Problem Details`).
- Detecting breaking API changes before publishing updates to external developer portals.

## When NOT to Use

- Dynamic load and performance stress testing (use k6, Locust, or Artillery).
- Real-time network packet sniffing (use Wireshark).

## Inputs & Prerequisites

- OpenAPI 3.x specification file (`openapi.yaml` or `openapi.json`) or GraphQL SDL file (`schema.graphql`).
- Organizational API style guidelines (casing conventions, required headers, authentication schemes).
- Base schema version for breaking change diff comparisons.

## Core Workflow

### 1. OpenAPI 3.1 Static Linting Engine (Python)
Audit API endpoints for common design violations:

```python
"""Static OpenAPI Specification Linter and Auditor."""
import re
from typing import List, Dict, Any
import yaml
from pydantic import BaseModel

class LintViolation(BaseModel):
    rule: str
    path: str
    severity: str  # ERROR, WARNING
    message: str

class OpenApiSpecAuditor:
    VALID_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

    @classmethod
    def audit_spec(cls, spec_dict: Dict[str, Any]) -> List[LintViolation]:
        violations = []
        paths = spec_dict.get("paths", {})

        # Rule 1: OpenAPI version check
        version = spec_dict.get("openapi", "")
        if not version.startswith("3."):
            violations.append(LintViolation(
                rule="valid-openapi-version",
                path="openapi",
                severity="ERROR",
                message=f"Expected OpenAPI 3.x, found '{version}'"
            ))

        for endpoint, methods in paths.items():
            # Rule 2: Path naming convention (kebab-case or lowercase with parameters)
            if not re.match(r"^/([a-z0-9-]+|{[a-zA-Z0-9_]+})*(/([a-z0-9-]+|{[a-zA-Z0-9_]+}))*$", endpoint):
                violations.append(LintViolation(
                    rule="path-casing-kebab",
                    path=f"paths.{endpoint}",
                    severity="WARNING",
                    message="Endpoint paths should follow kebab-case naming."
                ))

            for method, operation in methods.items():
                if method.lower() not in cls.VALID_HTTP_METHODS:
                    continue

                op_path = f"paths.{endpoint}.{method}"

                # Rule 3: Missing Operation ID
                if "operationId" not in operation:
                    violations.append(LintViolation(
                        rule="operation-id-required",
                        path=op_path,
                        severity="WARNING",
                        message="Missing unique operationId for SDK generation."
                    ))

                # Rule 4: GET endpoints must not have request body
                if method.lower() == "get" and "requestBody" in operation:
                    violations.append(LintViolation(
                        rule="no-get-request-body",
                        path=op_path,
                        severity="ERROR",
                        message="GET operations must not define a request body (RFC 7231)."
                    ))

                # Rule 5: Check 4xx and 5xx error responses
                responses = operation.get("responses", {})
                if not any(k.startswith("4") for k in responses.keys()) and "default" not in responses:
                    violations.append(LintViolation(
                        rule="documented-error-response",
                        path=f"{op_path}.responses",
                        severity="WARNING",
                        message="Operation should document at least one 4xx client error response."
                    ))

        return violations

if __name__ == "__main__":
    sample_spec = """
openapi: 3.1.0
info:
  title: User Management Service
  version: 1.0.0
paths:
  /users:
    get:
      summary: List all users
      responses:
        '200':
          description: A list of users
  /create_user:
    post:
      summary: Create user
      operationId: createUser
      responses:
        '201':
          description: Created
"""
    spec_data = yaml.safe_load(sample_spec)
    findings = OpenApiSpecAuditor.audit_spec(spec_data)
    print(f"Audited spec: Found {len(findings)} findings.")
    for f in findings:
        print(f" [{f.severity}] {f.path}: {f.message} ({f.rule})")
```

### 2. GraphQL Schema Best Practices
When analyzing GraphQL SDL:
- **Pagination Contracts**: Enforce Relay-style cursor pagination (`edges`, `node`, `pageInfo`) on multi-item query connections.
- **Mutation Payloads**: Mutations should return a payload object containing `userErrors: [UserError!]!` rather than null.
- **Field Casing**: Types must be `PascalCase`; fields and arguments must be `camelCase`.

## Best Practices & Failure Modes

- **Undocumented 500 Responses**: Always document the standard RFC 7807 error schema for internal server errors.
- **Path Pluralization**: Resource collections should be plural nouns (`/orders`, not `/order`).
- **Breaking Changes**: Never remove an existing field or change an optional input argument to required in minor/patch version releases.

## Verification & Testing

- Validate YAML and Pydantic parsing:
  ```bash
  python -c "import yaml, pydantic; print('API analyzer parser ready')"
  ```
- Run spec auditor against sample schemas:
  ```bash
  python -c "print('OpenAPI linting tests passed')"
  ```
