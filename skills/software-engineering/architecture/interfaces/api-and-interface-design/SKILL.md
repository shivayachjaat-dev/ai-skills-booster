---
name: api-and-interface-design
description: "Use this skill when designing public APIs, module boundaries, database interfaces, or component props. It enforces Hyrum's Law awareness, backwards compatibility, strict contract specification, defensive schema validation, explicit error hierarchies, and graceful deprecation lifecycles."
domain: software-engineering
category: architecture
subcategory: interfaces
tags:
  - api-design
  - architecture
  - interface-contracts
  - rest
  - graphql
  - typescript
technologies:
  - REST
  - GraphQL
  - TypeScript
  - OpenAPI
  - JSON Schema
complexity: advanced
maturity: stable
tools:
  - tsc
  - curl
dependencies:
  - typescript >= 4.5
---
# API and Interface Design

## Overview

Design resilient, stable, and well-documented interfaces that are easy to use correctly and hard to misuse. Good interfaces make the right thing easy and the wrong thing hard. This applies to REST APIs, GraphQL schemas, internal module contracts, component props, and SDK public surfaces.

## When to Use

- Designing new public HTTP REST, gRPC, or GraphQL endpoints.
- Defining module boundaries or contracts between distributed teams or microservices.
- Establishing database access layer interfaces or repository patterns.
- Creating component prop contracts in frontend libraries.
- Changing or refactoring existing public interfaces with backwards compatibility requirements.

## When NOT to Use

- Quick, one-off internal helper scripts intended for immediate disposal.
- Internal private implementations hidden completely behind an existing stable interface.

## Inputs & Prerequisites

- High-level business requirements and entity models.
- Target transport protocol (REST, gRPC, TypeScript interface, GraphQL).
- Existing consumer constraints and backwards compatibility commitments.

## Core Workflow

### 1. Hyrum's Law Analysis & Surface Minimization
> "With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody, regardless of what you promise in the contract."

1. Expose the minimum necessary surface area.
2. Never leak internal implementation details (e.g. database column names, internal IDs, third-party vendor types).
3. Keep internal helper types unexported.

### 2. Contract Specification (Schema First)
Write the strict contract before writing implementation code:
- For REST: Produce OpenAPI 3.1 specification.
- For TypeScript: Define explicit input, output, and error types:
```typescript
export interface CreateOrderRequest {
  readonly customerId: string;
  readonly items: ReadonlyArray<{
    readonly productId: string;
    readonly quantity: number;
  }>;
  readonly idempotencyKey: string;
}

export type CreateOrderResult =
  | { readonly success: true; readonly orderId: string; readonly totalAmountCents: number }
  | { readonly success: false; readonly error: OrderCreationError };
```

### 3. Idempotency & Safe Mutation
For any non-idempotent operation (e.g. billing, order placement, message sending):
- Require an `Idempotency-Key` HTTP header or parameter.
- Cache operation results keyed by the idempotency key for at least 24 hours to prevent duplicate processing during network retries.

### 4. Explicit Error Hierarchy
Never return generic `500 Internal Server Error` without structured error taxonomy:
- Define machine-readable error codes: `INVALID_INPUT`, `RESOURCE_NOT_FOUND`, `RATE_LIMITED`, `UNAUTHORIZED`.
- Include safe user-facing message, machine code, and correlation ID:
```json
{
  "error": {
    "code": "PAYMENT_FAILED",
    "message": "The transaction was declined by the issuing bank.",
    "correlation_id": "req_8f1b2c3d"
  }
}
```

### 5. Evolution & Deprecation Strategy
- Never make breaking changes to an existing active version.
- Add optional fields rather than modifying or removing existing fields.
- When deprecating, mark fields with `@deprecated` in schemas and return `Sunset` HTTP headers.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Breaking change required | Introduce a new API version (e.g. `/v2/`) or new module interface, supporting the old version concurrently during a transition period. |
| Large dataset queries | Mandate cursor-based pagination (`cursor` & `limit`) rather than offset pagination to avoid performance degradation on deep scans. |
| Timezone ambiguity | Enforce ISO 8601 UTC timestamps (`YYYY-MM-DDTHH:MM:SSZ`) across all inputs and outputs. |

## Validation & Acceptance Criteria

- [ ] Schema is strictly typed and validates all edge-case inputs.
- [ ] Error scenarios return structured, predictable error payloads with machine-readable codes.
- [ ] Mutations support idempotency keys to prevent duplicate execution.
- [ ] Documentation includes complete request/response examples and failure scenarios.

## Failure Handling & Recovery

- If a consumer breaks due to an unintended change in timing or ordering, assess whether the behavior was an undocumented quirk, and apply compensating adapter layers.

## Expected Output & Artifacts

- OpenAPI YAML specification or TypeScript contract definition file.
- Comprehensive request/response fixtures for positive and negative test cases.

## Related Skills

- `code-review-and-quality`
- `deprecation-and-migration`
- `owasp-api-security-top-10`
