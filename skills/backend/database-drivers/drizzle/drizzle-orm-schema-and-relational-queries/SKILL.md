---
name: drizzle-orm-schema-and-relational-queries
description: "Use this skill when designing database schemas, managing type-safe migrations, and querying SQL databases with Drizzle ORM in TypeScript. It guides the agent through pgTable declarations, relations API (1:1, 1:N, M:N), Drizzle Kit migrations (generate/migrate), prepared statements for maximum performance, and serverless pooling."
domain: backend
category: database-drivers
subcategory: drizzle
tags:
  - drizzle-orm
  - typescript
  - postgresql
  - database
  - orm
  - drizzle-kit
  - sql
technologies:
  - Drizzle ORM
  - Drizzle Kit
  - TypeScript
  - PostgreSQL
  - Node.js
complexity: intermediate
maturity: stable
tools:
  - npx drizzle-kit
  - npm
dependencies:
  - drizzle-orm >= 0.29.0
  - drizzle-kit >= 0.20.0
---
# Drizzle ORM Schema Architecture & Relational Querying

## Overview

A definitive production engineering reference for developing zero-overhead, type-safe database layers using Drizzle ORM in TypeScript. Unlike traditional heavy ORMs with runtime query compilation and hidden reflection overhead, Drizzle acts as a lightweight TypeScript-to-SQL compiler with near-zero runtime latency. This skill instructs AI agents on declaring schema tables, modeling explicit relationships, executing migrations via Drizzle Kit, optimizing queries using the Relational Query API, and preparing statements.

## When to Use

- Building low-latency, edge-ready, or serverless TypeScript microservices (Cloudflare Workers, Vercel, Node.js).
- Demanding absolute SQL transparency without hidden queries or N+1 magic.
- Enforcing end-to-end type safety between database schema definitions and application code.
- Managing database migrations with pure SQL scripts generated directly from TypeScript schemas.

## When NOT to Use

- Legacy projects locked to Python, Go, or Java.
- Rapid prototyping where high-level automatic schema generation without understanding SQL is preferred (use Prisma).

## Inputs & Prerequisites

- Node.js 18+ or Bun runtime with TypeScript.
- PostgreSQL database accessible via connection URI.
- Dependencies: `npm install drizzle-orm postgres` and `npm install -D drizzle-kit`.

## Core Workflow

### 1. Declarative Schema Definition (`schema.ts`)
Declare tables, composite keys, indexes, and relations:

```typescript
// db/schema.ts
import { pgTable, uuid, varchar, timestamp, integer, pgEnum } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const customerRoleEnum = pgEnum('customer_role', ['member', 'admin', 'owner']);

export const customers = pgTable('customers', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: varchar('email', { length: 255 }).notNull().unique(),
  fullName: varchar('full_name', { length: 128 }).notNull(),
  role: customerRoleEnum('role').default('member').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const orders = pgTable('orders', {
  id: uuid('id').defaultRandom().primaryKey(),
  customerId: uuid('customer_id')
    .notNull()
    .references(() => customers.id, { onDelete: 'cascade' }),
  totalCents: integer('total_cents').notNull(),
  status: varchar('status', { length: 32 }).default('pending').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Relational Definitions for Drizzle Relational Queries API
export const customersRelations = relations(customers, ({ many }) => ({
  orders: many(orders),
}));

export const ordersRelations = relations(orders, ({ one }) => ({
  customer: one(customers, {
    fields: [orders.customerId],
    references: [customers.id],
  }),
}));
```

### 2. Drizzle Kit Configuration & Migration Lifecycle
Configure migration generator in `drizzle.config.ts`:

```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './db/schema.ts',
  out: './drizzle/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.DATABASE_URL || '',
  },
} satisfies Config;
```

```bash
# Generate pure SQL migration diff from TypeScript schema
npx drizzle-kit generate:pg

# Apply pending SQL migrations to target database
npx drizzle-kit push:pg
```

### 3. High-Performance Relational Querying & Prepared Statements
Execute nested relational queries with sub-millisecond execution times:

```typescript
// db/queries.ts
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';
import { eq, sql } from 'drizzle-orm';

const queryClient = postgres(process.env.DATABASE_URL!);
export const db = drizzle(queryClient, { schema });

// 1. Relational Queries API (automatically executes optimal JOIN/batching)
export async function getCustomerWithRecentOrders(customerId: string) {
  return await db.query.customers.findFirst({
    where: eq(schema.customers.id, customerId),
    with: {
      orders: {
        limit: 5,
        orderBy: (orders, { desc }) => [desc(orders.createdAt)],
      },
    },
  });
}

// 2. Prepared Statement (compiled once on PostgreSQL server)
export const preparedCustomerById = db.query.customers
  .findFirst({
    where: eq(schema.customers.id, sql.placeholder('targetId')),
  })
  .prepare('customer_by_id_prep');

export async function executeFastLookup(id: string) {
  return await preparedCustomerById.execute({ targetId: id });
}
```

## Best Practices & Failure Modes

1. **Missing Schema in Drizzle Initialization**: If `{ schema }` is omitted when calling `drizzle(client, { schema })`, `db.query` will be undefined at runtime. Always pass the exported schema object.
2. **Connection Leak in Serverless**: Creating `postgres(connectionString)` inside serverless functions opens a new TCP connection on every invocation, exhausting PostgreSQL connection limits. Use connection poolers (Neon serverless driver, Supabase pooler, PgBouncer).
3. **N+1 Avoidance**: Avoid looping over records and querying relationships sequentially. Use the Relational Query API (`db.query.customers.findMany({ with: { orders: true } })`) which issues a single consolidated query.

## Verification & Testing

- Validate schema types and check for TypeScript errors:
  ```bash
  npx tsc --noEmit
  ```
- Test migration dry-run:
  ```bash
  npx drizzle-kit check:pg
  ```
