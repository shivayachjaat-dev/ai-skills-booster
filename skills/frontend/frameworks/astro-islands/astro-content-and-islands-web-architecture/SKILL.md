---
name: astro-content-and-islands-web-architecture
description: "Use this skill to design, build, and optimize content-driven websites and web applications using Astro 4/5 Islands Architecture. It covers zero-JS by default rendering, selective client hydration (client:load, client:idle, client:visible), type-safe Content Collections with Zod schemas, View Transitions API, hybrid SSR adapter configuration, and SEO optimization."
domain: frontend
category: frameworks
subcategory: astro-islands
tags:
  - frontend
  - astro
  - islands-architecture
  - ssg
  - ssr
  - typescript
  - content-collections
  - web-performance
technologies:
  - Astro
  - TypeScript
  - Zod
  - Vite
  - Node.js
  - Tailwind CSS
complexity: advanced
maturity: stable
tools:
  - astro
  - npm
  - node
dependencies:
  - astro@^4.0.0
  - typescript@^5.0.0
  - zod@^3.22.0
---
# Astro Content Collections & Islands Architecture

## Overview

A modern web engineering guide for architecting high-performance, content-first websites and hybrid web applications using Astro (v4/v5). By enforcing a "Zero JavaScript by default" baseline, Astro compiles UI templates (Astro, React, Vue, Svelte, Preact) to static HTML at build time, while hydrating interactive components ("islands") independently on demand. This skill guides software engineers and AI coding agents in designing robust Astro architectures, configuring type-safe Content Collections with Zod schema validation, implementing client-side routing with the native View Transitions API, and deploying hybrid server-side rendering (SSR) via edge adapters.

```
+------------------------------------------------------------------------+
|                          Astro Static Shell (0kb JS)                  |
|                                                                        |
|  +---------------------+  +---------------------+  +----------------+  |
|  | Header & Hero       |  | Markdown Article    |  | Static Footer  |  |
|  | (Static HTML/CSS)   |  | Content Collection  |  | (Pure HTML)    |  |
|  +---------------------+  +---------------------+  +----------------+  |
|                                                                        |
|  Interactive Component Islands:                                        |
|  +-----------------------+     +-----------------------+               |
|  | Search Dialog (React) |     | Comments Widget (Vue) |               |
|  | client:idle           |     | client:visible        |               |
|  +-----------------------+     +-----------------------+               |
+------------------------------------------------------------------------+
```

## When to Use

- Developing documentation sites, tech blogs, marketing portfolios, and editorial publishing platforms requiring near-perfect Google Core Web Vitals (LCP < 1.2s, CLS = 0).
- Building multi-framework hybrid applications where different teams use React, Vue, or Svelte components inside a single unified shell.
- Structuring large collections of Markdown or MDX documents requiring strict frontmatter validation and schema integrity.
- Implementing fast multi-page applications (MPA) with SPA-like animated page transitions using Astro View Transitions.

## When NOT to Use

- Highly dynamic, single-page state-intensive web apps (e.g., Figma-like canvas editors, live trading dashboards) where every single element requires client-side state synchronization.
- Pure REST API backends or microservices without front-facing HTML markup.

## Inputs & Prerequisites

- Node.js 18.17.1+ or 20.x, npm / pnpm / yarn package manager.
- Basic familiarity with TypeScript, HTML/CSS, and JSX or template syntaxes.
- Target project repository initialized with `astro` dependencies.

## Core Workflow

### Step 1: Content Collection Schema Modeling
Define strongly typed schemas in `src/content/config.ts` using Astro's built-in `defineCollection` and `z` (Zod).

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content', // 'content' for Markdown/MDX, 'data' for JSON/YAML
  schema: ({ image }) => z.object({
    title: z.string().max(80),
    description: z.string().min(20).max(160),
    pubDate: z.date(),
    updatedDate: z.date().optional(),
    author: z.string().default('Core Engineering Team'),
    tags: z.array(z.string()).nonempty(),
    coverImage: image().refine((img) => img.width >= 720, {
      message: 'Cover image must be at least 720px wide',
    }).optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = {
  blog: blogCollection,
};
```

### Step 2: Dynamic Route Generation
Create static routes with parameter validation using `getStaticPaths` in `src/pages/blog/[...slug].astro`.

```astro
---
// src/pages/blog/[...slug].astro
import { getCollection, type CollectionEntry } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => {
    return import.meta.env.PROD ? !data.draft : true;
  });

  return posts.map((post) => ({
    params: { slug: post.slug },
    props: { post },
  }));
}

interface Props {
  post: CollectionEntry<'blog'>;
}

const { post } = Astro.props;
const { Content, headings } = await post.render();
---

<BaseLayout title={post.data.title} description={post.data.description}>
  <article class="prose prose-slate max-w-3xl mx-auto py-12 px-4">
    <header class="mb-8">
      <h1 class="text-4xl font-extrabold tracking-tight">{post.data.title}</h1>
      <p class="text-sm text-slate-500">
        Published on {post.data.pubDate.toLocaleDateString('en-US', { dateStyle: 'long' })}
      </p>
    </header>
    
    <div class="content-body">
      <Content />
    </div>
  </article>
</BaseLayout>
```

### Step 3: Island Hydration Strategy Selection
Apply explicit `client:*` hydration directives based on real user interaction requirements:

| Directive | Execution Condition | Best Use Case |
|---|---|---|
| *(none)* | Rendered to static HTML, 0kb JS loaded | Headers, footers, articles, static cards |
| `client:load` | Hydrates immediately on page load | Critical interactive elements (primary navigation, cart modal) |
| `client:idle` | Hydrates once browser reaches `requestIdleCallback` | Search bars, newsletter subscription forms, theme toggles |
| `client:visible` | Hydrates when element intersects viewport (`IntersectionObserver`) | Heavy comments widgets, interactive charts, media players |
| `client:media` | Hydrates only when CSS media query matches (`client:media="(max-width: 50em)"`) | Mobile-only slideout menus |
| `client:only="react"`| Skips server-side rendering entirely, runs on client | Canvas tools, browser-storage dependent UI |

### Step 4: Seamless View Transitions Integration
Enable persistent state and fluid navigation animations across page switches:

```astro
---
// src/layouts/BaseLayout.astro
import { ViewTransitions } from 'astro:transitions';
interface Props {
  title: string;
  description: string;
}
const { title, description } = Astro.props;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <ViewTransitions fallback="swap" />
  </head>
  <body class="bg-white text-slate-900 min-h-screen">
    <slot />
  </body>
</html>
```

## Best Practices & Failure Modes

- **Never Over-Hydrate**: Avoid putting `client:load` on components below the fold; prefer `client:visible` or `client:idle` to maintain zero First Input Delay (FID) and Low Interaction to Next Paint (INP).
- **Zod Schema Evolution**: When adding required fields to content schemas, provide default values (`.default(...)`) or mark them `.optional()` to prevent breaking legacy markdown files.
- **Islands Isolation**: Remember that islands do not share UI state automatically across different frameworks. Use lightweight nanostores (`@nanostores/core`) or browser custom events for cross-island reactivity.
- **Environment Variables**: Use `PUBLIC_*` prefix only for variables safe to expose to client bundles; private API keys must be accessed in server endpoints or `.astro` frontmatter.

## Verification & Testing

1. Run schema validation: `npx astro check` to verify TypeScript and Content Collection types.
2. Build static output: `npx astro build` to confirm zero broken links and valid asset hashes.
3. Audit client JS bundle: Confirm page payloads in `dist/` contain 0kb client script bundles for purely informational pages.
4. Preview production artifacts: `npx astro preview` and verify Core Web Vitals using Lighthouse.
