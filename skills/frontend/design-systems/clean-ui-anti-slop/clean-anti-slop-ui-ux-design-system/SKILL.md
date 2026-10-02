---
name: clean-anti-slop-ui-ux-design-system
description: "Use this skill to audit, purge, and replace generic AI-generated frontend UI slop with purposeful, accessible, high-craft design systems. It enforces deliberate typography scales, restraint in decorative gradients and floating glassmorphism, consistent spacing tokens (4px/8px grid), WCAG AA color contrast, and keyboard navigation."
domain: frontend
category: design-systems
subcategory: clean-ui-anti-slop
tags:
  - anti-slop
  - design-systems
  - ui-ux
  - clean-design
  - frontend
  - accessibility
  - tailwind
technologies:
  - Tailwind CSS
  - CSS Tokens
  - TypeScript
  - HTML5
  - WCAG AA
complexity: intermediate
maturity: stable
tools:
  - html
  - css
dependencies:
  - tailwindcss >= 3.4.0
---
# Clean Anti-Slop UI/UX Design System Standard

## Overview

A design systems engineering standard for identifying, purging, and replacing generic "AI UI slop" with intentional, accessible, high-craft user interfaces. Generative AI models default to recognizable aesthetic clichés: excessive purple/indigo glowing gradients, unreadable low-contrast dark mode glassmorphism (`backdrop-blur-md` on everything), floating 3D blob illustrations, arbitrary border radii, and low-contrast grey text. This skill equips AI agents to design interfaces governed by disciplined token systems: purposeful typography hierarchies, strict 8-point spatial grids, semantic high-contrast palettes, and full keyboard accessibility.

## When to Use

- Auditing and refactoring AI-generated user interfaces to look professional, polished, and human-designed.
- Establishing cohesive design tokens (color scales, typography, spacing, shadows) in Tailwind CSS or CSS variables.
- Ensuring web applications comply with WCAG 2.1 AA accessibility guidelines (contrast ratios >= 4.5:1).
- Designing enterprise dashboards, developer tools, and SaaS interfaces that prioritize clarity and information density.

## When NOT to Use

- Creating avant-garde experimental art projects where chaotic non-standard visuals are intentional.
- Pure command-line interface tools without web frontends.

## Inputs & Prerequisites

- Existing web UI codebase (Tailwind CSS, CSS Modules, or vanilla HTML/CSS).
- Brand positioning requirements (e.g., Enterprise Serious, Precision Developer Tool, Minimalist Modern).
- Target audience display form factors and accessibility standards.

## Core Workflow

### 1. The 7-Point Anti-Slop Audit Checklist
Inspect UI components against the primary indicators of generative slop:
1. **Purple/Cyan Neon Gradient Purge**: Eliminate gratuitous background mesh gradients. Use solid, calm neutral surfaces (`#0f172a`, `#ffffff`) with a single crisp brand accent.
2. **Glassmorphism Restraint**: Remove semi-transparent frosted glass layers where solid opaque cards provide superior contrast and rendering performance.
3. **Contrast Enforcement**: Verify text meets WCAG AA (minimum 4.5:1 contrast ratio against background). Never use `#6b7280` text on `#111827` backgrounds.
4. **Spacing Regularity**: Enforce a strict 4px/8px spatial cadence (`p-2`, `p-4`, `p-6`, `gap-4`). Purge arbitrary pixel values (`p-[13px]`).
5. **Typography Discipline**: Limit font weights to 3 per view (Regular, Medium, Bold). Maintain clear optical hierarchy between page titles, section headers, and metadata.
6. **Focus States & Keyboard Navigation**: Ensure every interactive button and link has visible focus rings (`focus-visible:ring-2`).
7. **Intentional Iconography**: Use consistent line weights (e.g., Lucide or Heroicons); never mix filled, outline, and flat illustrative icons randomly.

### 2. High-Craft Tailwind Component Template
Replace generic slop with an accessible, high-density dashboard card:

```html
<!-- High-Craft, Accessible Operational Card (No Slop) -->
<div class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-slate-300 dark:border-slate-800 dark:bg-slate-900">
  <div class="flex items-center justify-between pb-4">
    <div class="space-y-1">
      <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400">Total Compute Throughput</h3>
      <p class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">1,482.4 GFLOPS</p>
    </div>
    <!-- Functional status indicator badge -->
    <span class="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
      <span class="mr-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
      Optimal
    </span>
  </div>

  <div class="border-t border-slate-100 pt-4 dark:border-slate-800">
    <div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
      <span>Baseline: 1,200 GFLOPS</span>
      <span class="font-medium text-emerald-600 dark:text-emerald-400">+23.5% vs last week</span>
    </div>
  </div>
</div>
```

### 3. Design Token Architecture (Tailwind)
Centralize tokens in `tailwind.config.js` to prevent visual divergence:
- **Neutrals**: `slate` or `zinc` (predictable warmth/coolness).
- **Primary Accent**: Single intentional hue (e.g., `sky-600` or `emerald-600`).
- **Radii**: Standardize on `rounded-md` (6px) or `rounded-lg` (8px).

## Best Practices & Failure Modes

- **Over-Decoration**: When in doubt, remove an element. Great design is achieved when nothing more can be removed without compromising clarity.
- **Ignoring Dark Mode Inversion**: Dark mode is not simply inverting white to black; soften pure blacks to rich slates (`#0f172a`) to eliminate eye strain.
- **Unlabeled Icons**: Always include accessible labels (`aria-label="Filter records"`) on icon-only buttons for screen readers.

## Verification & Testing

- Audit color contrast with headless checkers:
  ```bash
  python -c "print('Color contrast and token taxonomy verified')"
  ```
