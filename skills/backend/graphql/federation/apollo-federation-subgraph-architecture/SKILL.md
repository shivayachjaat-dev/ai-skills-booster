---
name: apollo-federation-subgraph-architecture
description: "Use this skill when designing, composing, and operating distributed GraphQL schemas using Apollo Federation v2. It guides the agent through defining entity keys (@key), entity resolvers (__resolveReference), sharing types (@shareable), migrating fields across subgraphs (@override), schema composition with Rover CLI, and Gateway/Router routing."
domain: backend
category: graphql
subcategory: federation
tags:
  - graphql
  - apollo-federation
  - subgraphs
  - api-gateway
  - distributed-systems
  - rover
technologies:
  - Apollo Federation v2
  - GraphQL
  - Rover CLI
  - Apollo Router
  - TypeScript
  - Node.js
complexity: advanced
maturity: stable
tools:
  - rover
  - npm
dependencies:
  - @apollo/subgraph >= 2.6.0
---
# Apollo Federation v2 Subgraph Architecture

## Overview

A definitive engineering standard for building modular, distributed GraphQL APIs using Apollo Federation v2. This skill instructs AI agents on partitioning domain schemas across autonomous service teams while presenting a single unified GraphQL supergraph to clients. It covers entity definition (`@key`), reference resolvers (`__resolveReference`), shared types (`@shareable`), progressive field migration (`@override`), and CI schema composition using Rover.

## When to Use

- Breaking a monolithic GraphQL API into independent, domain-oriented microservice subgraphs.
- Enabling multiple backend teams to contribute fields to common shared entities (e.g. `User`, `Product`, `Order`).
- Unifying separate GraphQL services behind a high-performance Rust-based Apollo Router gateway.
- Migrating fields between services without breaking client applications.

## When NOT to Use

- Small monolithic applications where a single schema and server suffice.
- REST or gRPC microservices without GraphQL requirements.

## Inputs & Prerequisites

- Node.js 18+ or TypeScript environment.
- Rover CLI installed (`npm install -g @apollo/rover`).
- Basic understanding of GraphQL schema definition language (SDL).

## Core Workflow

### 1. Defining Entities in Subgraphs
In the Users Subgraph, declare `User` as an entity with a primary `@key`:

```typescript
// subgraphs/accounts/schema.ts
import { gql } from 'graphql-tag';
import { buildSubgraphSchema } from '@apollo/subgraph';

export const typeDefs = gql`
  extend schema
    @link(url: "https://specs.apollo.dev/federation/v2.3", import: ["@key", "@shareable"])

  type User @key(fields: "id") {
    id: ID!
    email: String!
    username: String!
  }

  type Query {
    me: User
  }
`;

export const resolvers = {
  Query: {
    me: () => ({ id: "usr_100", email: "alice@example.com", username: "alice" }),
  },
  User: {
    // Entity Reference Resolver: Called when other subgraphs request User entity by id
    __resolveReference: (reference: { id: string }) => {
      return { id: reference.id, email: `${reference.id}@example.com`, username: reference.id };
    },
  },
};

export const schema = buildSubgraphSchema({ typeDefs, resolvers });
```

### 2. Extending Entities in Downstream Subgraphs
In the Reviews Subgraph, extend `User` to contribute review fields:

```typescript
// subgraphs/reviews/schema.ts
import { gql } from 'graphql-tag';
import { buildSubgraphSchema } from '@apollo/subgraph';

export const typeDefs = gql`
  extend schema
    @link(url: "https://specs.apollo.dev/federation/v2.3", import: ["@key"])

  type Review {
    id: ID!
    body: String!
    rating: Int!
    author: User!
  }

  # Reference the User entity without redefining its core fields
  type User @key(fields: "id") {
    id: ID!
    reviews: [Review!]!
  }
`;

export const resolvers = {
  User: {
    reviews: (user: { id: string }) => {
      return [
        { id: "rev_1", body: "Great service!", rating: 5, author: user },
      ];
    },
  },
};
```

### 3. Supergraph Composition via Rover CLI
Compose individual subgraphs into a unified supergraph configuration:

```yaml
# supergraph.yaml
federation_version: =2.3.0
subgraphs:
  users:
    routing_url: http://users-service:4001/graphql
    schema:
      file: ./subgraphs/accounts/schema.graphql
  reviews:
    routing_url: http://reviews-service:4002/graphql
    schema:
      file: ./subgraphs/reviews/schema.graphql
```

```bash
# Compose and validate supergraph schema locally
rover supergraph compose --config ./supergraph.yaml --output supergraph.graphql
```

## Best Practices & Failure Modes

1. **Missing `__resolveReference` Implementation**: If a subgraph references an entity with `@key(fields: "id")` but does not define `__resolveReference` for that type, any query that spans across subgraphs will fail at runtime with `Cannot resolve reference` errors.
2. **Conflicting Types Without `@shareable`**: In Federation v2, two subgraphs cannot declare the exact same type or field unless marked `@shareable`. Omitting `@shareable` causes Rover composition to fail.
3. **N+1 Entity Resolution**: When resolving entities across subgraphs, implement DataLoader within `__resolveReference` to batch multiple reference lookups into a single SQL/API call.

## Verification & Testing

- Validate subgraph schema syntax independently:
  ```bash
  rover subgraph check my-graph@prod --schema ./subgraphs/accounts/schema.graphql --name users
  ```
- Run Apollo Router with composed supergraph:
  ```bash
  apollo-router --supergraph supergraph.graphql
  ```
