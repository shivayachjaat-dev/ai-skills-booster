---
name: prisma-schema-migration-and-relations
description: "Use this skill when architecting database schemas, managing relational migrations, and optimizing database queries using Prisma ORM (TypeScript/Node.js). It covers complex relationship modeling (1:1, 1:N, M:N explicit join tables), zero-downtime migration workflows (`prisma migrate dev/deploy`), connection pooling with PgBouncer, and avoiding N+1 query traps."
domain: databases
category: orm
subcategory: prisma
tags:
  - prisma
  - orm
  - typescript
  - database
  - migrations
  - postgresql
technologies:
  - Prisma
  - TypeScript
  - Node.js
  - PostgreSQL
  - PgBouncer
complexity: intermediate
maturity: stable
tools:
  - npx prisma
  - npm
dependencies:
  - @prisma/client >= 5.10.0
  - prisma >= 5.10.0
---
# Prisma Schema Modeling & Relational Migration Architecture

## Overview

A production guide for data modeling, migration lifecycle management, and high-performance querying using Prisma ORM. This skill instructs agents on establishing normalized database schemas, configuring explicit many-to-many relationship join tables, applying non-destructive zero-downtime migrations in CI/CD, configuring transaction isolation, and preventing N+1 query bottlenecks.

## When to Use

- Designing relational data models in modern TypeScript/Node.js full-stack systems.
- Executing version-controlled database schema migrations (`prisma migrate`).
- Connecting Prisma to PostgreSQL through serverless connection poolers (PgBouncer, Supabase, Neon).
- Constructing type-safe queries with deep relation inclusion and pagination.

## When NOT to Use

- Applications requiring raw micro-optimized SQL where full query builder control is necessary (use Kysely or raw SQL drivers).
- Highly dynamic document data with arbitrary untyped JSON structures (use MongoDB or document stores).

## Inputs & Prerequisites

- Node.js 18+ runtime with TypeScript.
- PostgreSQL, MySQL, or SQLite database available.
- Prisma CLI installed (`npm install prisma @prisma/client`).

## Core Workflow

### 1. Robust Schema Design (`schema.prisma`)
Define explicit relations, indexes, and PgBouncer direct URL configuration:

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")      // Pooled connection URL (e.g. port 6543)
  directUrl = env("DIRECT_URL")        // Direct connection URL for migrations (e.g. port 5432)
}

generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["relationJoins"]
}

enum Role {
  USER
  ADMIN
  MAINTAINER
}

model User {
  id           String        @id @default(uuid())
  email        String        @unique
  name         String?
  role         Role          @default(USER)
  createdAt    DateTime      @default(now()) @map("created_at")
  updatedAt    DateTime      @updatedAt @map("updated_at")
  memberships  Membership[]

  @@index([role])
  @@map("users")
}

model Organization {
  id          String        @id @default(uuid())
  slug        String        @unique
  name        String
  createdAt   DateTime      @default(now()) @map("created_at")
  memberships Membership[]

  @@map("organizations")
}

// Explicit Many-to-Many Join Table with Metadata
model Membership {
  id             String       @id @default(uuid())
  userId         String       @map("user_id")
  organizationId String       @map("organization_id")
  role           String       @default("member")
  joinedAt       DateTime     @default(now()) @map("joined_at")

  user           User         @relation(fields: [userId], references: [id], onDelete: Cascade)
  organization   Organization @relation(fields: [organizationId], references: [id], onDelete: Cascade)

  @@unique([userId, organizationId])
  @@index([organizationId])
  @@map("memberships")
}
```

### 2. CI/CD Migration Execution Workflow
Never run `prisma migrate dev` in staging or production. Follow the strict pipeline:

```bash
# In local development: generate migration file and apply locally
npx prisma migrate dev --name add_organization_memberships

# In CI / Production deployment pipelines: apply pending migrations only
npx prisma migrate deploy

# Generate Prisma Client artifact
npx prisma generate
```

### 3. Avoiding N+1 Query Traps & Safe Transactions
Use `relationJoins` or explicit includes, and wrap mutations in transactions:

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

// Single SQL Query with JOIN instead of multiple roundtrips
export async function getOrganizationWithMembers(orgSlug: string) {
  return await prisma.organization.findUnique({
    where: { slug: orgSlug },
    include: {
      memberships: {
        include: {
          user: {
            select: { id: true, name: true, email: true },
          },
        },
        orderBy: { joinedAt: 'asc' },
      },
    },
  });
}

// Atomic Multi-Table Mutation via Transaction
export async function createOrgWithAdmin(
  userId: string,
  orgData: { slug: string; name: string }
) {
  return await prisma.$transaction(async (tx) => {
    const org = await tx.organization.create({
      data: orgData,
    });

    const membership = await tx.membership.create({
      data: {
        userId,
        organizationId: org.id,
        role: 'owner',
      },
    });

    return { org, membership };
  });
}
```

## Best Practices & Failure Modes

1. **PgBouncer Prepared Statement Collision**: When connecting Prisma to PgBouncer in Transaction Pooling mode, Prisma's default prepared statements will fail. Append `?pgbouncer=true` to `DATABASE_URL` and configure a separate unpooled `directUrl` for migrations.
2. **Implicit Many-to-Many Limitations**: Avoid Prisma implicit many-to-many tables (`User[]` <-> `Organization[]`) in production schemas because you cannot add audit attributes (`role`, `invited_by`, `joined_at`) without dropping and recreating the tables. Use explicit join models.
3. **Client Instantiation Leaks**: Instantiating `new PrismaClient()` inside request handlers or serverless lambdas quickly exhausts PostgreSQL connections. Always use a global singleton pattern in Next.js/Node.js.

## Verification & Testing

- Validate Prisma schema syntax:
  ```bash
  npx prisma validate
  ```
- Check migration synchronization status against live database:
  ```bash
  npx prisma migrate status
  ```
- Inspect generated SQL without executing:
  ```bash
  npx prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script
  ```
