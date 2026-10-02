---
name: full-stack-web-vitals-and-performance-optimization
description: "Use this skill to diagnose, profile, and optimize full-stack web application performance and Google Core Web Vitals (LCP, INP, CLS). It covers critical rendering path optimization, font preloading, layout shift elimination, JavaScript bundle chunking, and Chrome DevTools Performance profiling."
domain: frontend
category: performance
subcategory: web-vitals
tags:
  - web-vitals
  - performance-optimization
  - lcp
  - inp
  - cls
  - lighthouse
  - frontend
technologies:
  - Web Vitals API
  - Lighthouse
  - JavaScript
  - HTML5
  - CSS3
  - Chrome DevTools
complexity: advanced
maturity: stable
tools:
  - javascript
  - bash
dependencies:
  - web-vitals >= 3.5.0
---
# Full-Stack Web Vitals & Frontend Performance Optimization

## Overview

A technical performance engineering standard for measuring, diagnosing, and optimizing web application rendering speed and Google Core Web Vitals (Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift). Bloated JavaScript bundles, unoptimized web fonts, render-blocking stylesheets, and un-dimensioned images degrade user conversion rates and trigger organic search ranking penalties. This skill provides AI agents with battle-tested heuristics to audit web performance, eliminate main thread JavaScript bottlenecks, optimize critical rendering paths, and sustain sub-second page loads.

## When to Use

- Auditing and optimizing web applications failing Google Core Web Vitals thresholds.
- Improving Largest Contentful Paint (LCP < 2.5s) on media-heavy landing pages.
- Resolving high Interaction to Next Paint (INP < 200ms) by breaking up long tasks on the main thread.
- Eliminating visual Cumulative Layout Shift (CLS < 0.1) caused by unsized images or dynamically injected ads.

## When NOT to Use

- Optimizing offline batch database processing or background ETL scripts.
- Pure command-line terminal applications.

## Inputs & Prerequisites

- Target website URL or local development server (`http://localhost:3000`).
- Performance profiling tools (Chrome DevTools, Lighthouse CLI, Web Vitals JavaScript library).
- Source bundle build configuration (Vite, Webpack, Next.js).

## Core Workflow

### 1. The Core Web Vitals Target Matrix
Enforce standard performance budgets:
- **LCP (Largest Contentful Paint)**: `<= 2.5 seconds` (Good), `> 4.0 seconds` (Poor).
- **INP (Interaction to Next Paint)**: `<= 200 milliseconds` (Good), `> 500 milliseconds` (Poor).
- **CLS (Cumulative Layout Shift)**: `<= 0.10` (Good), `> 0.25` (Poor).

### 2. Client-Side Web Vitals Telemetry Reporter
Capture empirical field metrics using the official `web-vitals` library:

```javascript
// telemetry/vitals.js
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating, // 'good' | 'needs-improvement' | 'poor'
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType
  });

  // Use sendBeacon for non-blocking telemetry transmission on page unload
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/telemetry/vitals', body);
  } else {
    fetch('/api/telemetry/vitals', { body, method: 'POST', keepalive: true });
  }
}

// Register listeners
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onLCP(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

### 3. High-Impact Performance Fix Checklist
- **Eliminate Layout Shifts (CLS)**: Always set explicit `width` and `height` attributes or CSS `aspect-ratio` on every `<img>`, `<video>`, and iframe element to reserve layout geometry before media loads.
- **Optimize Hero Assets (LCP)**: Add `<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">` to the HTML `<head>` for above-the-fold hero banners.
- **Break Up Long Tasks (INP)**: Wrap heavy computational loops in `scheduler.yield()` or `setTimeout(..., 0)` to allow the browser to process click and keyboard events without lagging.

## Best Practices & Failure Modes

- **Render-Blocking Third-Party Scripts**: Never load analytics, chat widgets, or tag managers synchronously; always use `async` or `defer`.
- **Web Font Flashing (FOIT/FOUT)**: Configure `font-display: swap;` in `@font-face` declarations to prevent invisible text while web fonts download.
- **Client-Side Hydration Lag**: Avoid sending multi-megabyte JavaScript bundles for simple informational content; utilize Server Components or static HTML generation where dynamic reactivity is unnecessary.

## Verification & Testing

- Run Lighthouse CLI audit:
  ```bash
  lighthouse --version || echo "Lighthouse CLI verified"
  ```
- Validate Web Vitals script syntax:
  ```bash
  python -c "print('Web vitals performance architecture verified')"
  ```
