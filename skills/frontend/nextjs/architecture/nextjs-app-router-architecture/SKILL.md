---
name: nextjs-app-router-architecture
description: "Use this skill when architecting and developing full-stack web applications with Next.js App Router (version 14+ / 15+). It guides the agent through React Server Components (RSC) vs Client Components boundaries, Server Actions with Zod validation, streaming SSR with Suspense boundaries, parallel and intercepting routes, dynamic segment caching, and revalidation (ISR)."
domain: frontend
category: nextjs
subcategory: architecture
tags:
  - nextjs
  - react
  - app-router
  - server-components
  - server-actions
  - ssr
technologies:
  - Next.js 14+
  - React 19
  - TypeScript
  - Zod
  - TailwindCSS
complexity: advanced
maturity: stable
tools:
  - npm
  - pnpm
  - node
dependencies:
  - next >= 14.2.0
  - react >= 18.3.0
---
# Next.js App Router Enterprise Architecture

## Overview

A comprehensive guide for architecting production web applications using the Next.js App Router paradigm. This skill instructs agents on establishing clean boundaries between React Server Components (RSC) and Client Components (`use client`), executing mutations via Server Actions with type-safe schema validation, streaming async UI with React Suspense, and managing Next.js cache lifecycles (Data Cache, Full Route Cache, Router Cache).

## When to Use

- Building modern full-stack TypeScript applications with Next.js 14 or 15.
- Transitioning legacy Pages Router (`pages/`) codebases to App Router (`app/`).
- Architecting low-latency dashboards with progressive streaming rendering.
- Implementing form submissions and backend mutations directly via Server Actions.

## When NOT to Use

- Pure Client-Side Single Page Applications (SPAs) where server rendering and Node.js hosting are not used (use standard Vite + React).
- Backend-only REST or GraphQL APIs with no frontend UI (use `fastapi-async-api-design` or `grpc-service-implementation`).

## Inputs & Prerequisites

- Node.js 18.17+ or 20+.
- Next.js 14+ initialized with TypeScript and TailwindCSS.
- Knowledge of React Server Components (RSC) execution model.

## Core Workflow

### 1. Server Component vs Client Component Composition
Keep data fetching in Server Components and push interactivity to leaf Client Components:

```tsx
// app/dashboard/page.tsx (Server Component by default)
import { Suspense } from 'react';
import { MetricsGrid } from '@/components/dashboard/metrics-grid';
import { MetricsSkeleton } from '@/components/dashboard/metrics-skeleton';
import { InteractiveFilter } from '@/components/dashboard/interactive-filter'; // Client Component

interface PageProps {
  searchParams: { period?: string };
}

export default async function DashboardPage({ searchParams }: PageProps) {
  const period = searchParams.period || '7d';

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Analytics Overview</h1>
        <InteractiveFilter initialPeriod={period} />
      </div>

      <Suspense fallback={<MetricsSkeleton />}>
        <MetricsGrid period={period} />
      </Suspense>
    </div>
  );
}
```

```tsx
// components/dashboard/interactive-filter.tsx
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useTransition } from 'react';

export function InteractiveFilter({ initialPeriod }: { initialPeriod: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();

  const handlePeriodChange = (newPeriod: string) => {
    const params = new URLSearchParams(searchParams);
    params.set('period', newPeriod);
    
    startTransition(() => {
      router.push(`?${params.toString()}`);
    });
  };

  return (
    <div className="flex gap-2">
      {['24h', '7d', '30d'].map((p) => (
        <button
          key={p}
          disabled={isPending}
          onClick={() => handlePeriodChange(p)}
          className={`px-3 py-1 text-sm rounded ${initialPeriod === p ? 'bg-blue-600 text-white' : 'bg-gray-100'}`}
        >
          {p}
        </button>
      ))}
    </div>
  );
}
```

### 2. Type-Safe Server Actions with Zod Validation
Handle mutations securely on the server with cache revalidation:

```typescript
// app/actions/create-project.ts
'use server';

import { z } from 'zod';
import { revalidatePath, revalidateTag } from 'next/cache';
import { redirect } from 'next/navigation';
import { db } from '@/lib/db';

const CreateProjectSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters").max(100),
  description: z.string().optional(),
  department: z.enum(['engineering', 'design', 'marketing']),
});

export type ActionState = {
  errors?: Record<string, string[]>;
  message?: string;
};

export async function createProjectAction(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  const rawData = {
    title: formData.get('title'),
    description: formData.get('description'),
    department: formData.get('department'),
  };

  const validation = CreateProjectSchema.safeParse(rawData);
  if (!validation.success) {
    return {
      errors: validation.error.flatten().fieldErrors,
      message: 'Validation failed. Please correct the fields.',
    };
  }

  try {
    const project = await db.project.create({
      data: validation.data,
    });
    
    // Invalidate cached project list
    revalidateTag('projects');
    revalidatePath('/dashboard/projects');
  } catch (error) {
    return {
      message: 'Database error: Unable to create project.',
    };
  }

  redirect('/dashboard/projects');
}
```

### 3. Route Handlers for External APIs
Build secure Edge/Node Route Handlers:

```typescript
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const signature = request.headers.get('stripe-signature');
  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  const rawBody = await request.text();
  // Verify webhook signature and process event...

  return NextResponse.json({ received: true });
}
```

## Best Practices & Failure Modes

1. **Unintentional Client Component Bleed**: Marking a high-level layout or page with `'use client'` disables Server Component optimizations for all nested children. Keep `'use client'` strictly at the leaves.
2. **Environment Variable Exposure**: Never expose private API keys in client components. Variables prefixed with `NEXT_PUBLIC_` are bundled into the browser JavaScript. Keep secrets in Server Components and Server Actions.
3. **Uncontrolled Caching**: Next.js 14 aggressively caches fetch requests by default. For real-time data, explicitly specify `fetch(url, { cache: 'no-store' })` or `export const dynamic = 'force-dynamic'`.

## Verification & Testing

- Run production build to verify Server/Client boundary compliance:
  ```bash
  npm run build
  ```
- Check route output manifest:
  - `○ (Static)`: prerendered as static HTML
  - `ƒ (Dynamic)`: server-rendered on demand
- Test server action form submission with invalid inputs and verify inline validation feedback renders without page reload.
