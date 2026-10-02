---
name: graphql-schema-evolution
description: "Use this skill when designing, versioning, and evolving GraphQL schemas without breaking existing mobile and web clients. It guides the agent through schema-first SDL design, non-breaking deprecation directives (@deprecated), resolving the N+1 query problem using DataLoader, input union patterns, and automated breaking-change detection in CI."
domain: backend
category: graphql
subcategory: schema-design
tags:
  - graphql
  - schema-design
  - backend
  - api
  - dataloader
  - typescript
technologies:
  - GraphQL
  - TypeScript
  - DataLoader
  - Apollo Server
  - GraphQL Yoga
complexity: advanced
maturity: stable
tools:
  - node
  - npm
  - graphql-inspector
dependencies:
  - graphql >= 16.0
  - dataloader
---
# GraphQL Schema Evolution

## Overview

A guide for designing robust, evolvable, and performant GraphQL schemas. Unlike REST APIs that frequently resort to hard URL versioning (`/v1/`, `/v2/`), GraphQL APIs evolve continuously within a single graph. This skill instructs AI agents on non-breaking schema design, resolver optimization with DataLoader, and automated breaking-change CI gating.

## When to Use

- Designing new GraphQL types, queries, and mutations for web or mobile consumption.
- Adding fields or modifying existing GraphQL schemas consumed by deployed mobile apps that cannot be forcibly upgraded.
- Solving severe database query amplification caused by GraphQL nested resolution (the N+1 problem).
- Deprecating legacy fields safely using `@deprecated` metadata directives.

## When NOT to Use

- Flat simple microservices where gRPC or standard REST is preferable.
- Pure file upload/download binary streaming endpoints.

## Inputs & Prerequisites

- GraphQL schema definition file (`schema.graphql` or code-first schema definitions).
- GraphQL server runtime (Apollo Server, GraphQL Yoga, Mercurius, or Strawberry).
- Node.js or Python environment with DataLoader support.

## Core Workflow

### 1. Non-Breaking Schema Evolution Principles
- **Never rename a field in place**: Renaming breaks every deployed mobile app that requests that field.
- **Never change a field's return type**: Changing from `String` to `[String]` breaks deserializers.
- **Never make an optional argument non-null (`!`):** Existing clients omitting the argument will receive validation errors.
- **Always add, never remove immediately**: Add the new field alongside the old field, deprecate the old field, and monitor telemetry until usage drops to zero.

### 2. Graceful Deprecation with `@deprecated`
Mark obsolete fields and enum values with explicit deprecation directives and replacement guidance:
```graphql
type User {
  id: ID!
  # Obsolete: Use displayName instead
  fullName: String @deprecated(reason: "Use 'displayName' which supports customized naming preferences.")
  displayName: String!
  avatarUrl: String
}
```

### 3. Solving the N+1 Problem with DataLoader
GraphQL resolvers execute independently. Querying 50 users and their orders triggers 1 query for users + 50 queries for orders (N+1 queries). Batch and cache database requests using DataLoader:
```typescript
import DataLoader from "dataloader";

// Batches 50 individual user ID queries into a single SQL: WHERE user_id IN (1, 2, 3...)
export const orderLoader = new DataLoader(async (userIds: readonly string[]) => {
  const orders = await db.query(
    "SELECT * FROM orders WHERE user_id = ANY($1)",
    [userIds]
  );
  
  // Group orders by userId and return in matching array order
  const orderMap = new Map<string, Order[]>();
  orders.forEach(order => {
    const list = orderMap.get(order.userId) || [];
    list.push(order);
    orderMap.set(order.userId, list);
  });
  
  return userIds.map(id => orderMap.get(id) || []);
});

// Resolver: Runs in O(1) database queries instead of O(N)
export const resolvers = {
  User: {
    orders: (parent, args, context) => context.loaders.orderLoader.load(parent.id)
  }
};
```

### 4. Mutation Design: Single Input Object & Payload Pattern
Always wrap mutation arguments in a single `input` object and return a dedicated payload type:
```graphql
input CreateProjectInput {
  name: String!
  description: String
  clientMutationId: String
}

type CreateProjectPayload {
  project: Project
  userErrors: [UserError!]!
}

type Mutation {
  createProject(input: CreateProjectInput!): CreateProjectPayload!
}
```
This guarantees you can add optional input parameters or return additional response metadata in the future without breaking existing callers.

### 5. Automated Breaking-Change CI Check
Enforce schema backwards compatibility in pull request workflows using GraphQL Inspector:
```bash
npx @graphql-inspector/cli diff schema-master.graphql schema-branch.graphql
```
Fails CI if breaking changes (removed fields, changed nullability) are detected.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Malicious deeply nested queries (DoS vulnerability) | Implement query depth limiting (e.g. max depth: 6) and query complexity analysis before query execution. |
| Inconsistent database ordering in DataLoader | DataLoader requires the returned array to strictly match the order and length of the input keys array; missing entries must return `null` or empty array at the corresponding index. |
| Paginated collections | Use the standard Relay Cursor Connections specification (`edges`, `node`, `pageInfo`, `cursor`) rather than raw unbounded arrays. |

## Validation & Acceptance Criteria

- [ ] Schema diff passes automated breaking-change detection in CI.
- [ ] Nested relational resolvers utilize DataLoader to prevent N+1 query loops.
- [ ] Mutations follow the single input object and payload return pattern.
- [ ] Deprecated fields supply clear reasoning and alternative replacement field names.
- [ ] Query depth and complexity limiters active in GraphQL server config.

## Failure Handling & Recovery

- If DataLoader returns mismatch array lengths, throw an internal resolver exception and verify database query grouping logic.

## Expected Output & Artifacts

- Clean, evolvable GraphQL SDL schema file (`schema.graphql`).
- DataLoader batching implementation module.
- CI pipeline step configuration for breaking change detection.

## Related Skills

- `api-and-interface-design`
- `postgres-query-performance-analysis`
- `fastapi-async-api-design`
