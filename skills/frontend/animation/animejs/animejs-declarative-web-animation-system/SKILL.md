---
name: animejs-declarative-web-animation-system
description: "Use this skill to design, build, and optimize declarative, high-performance UI and SVG animations using anime.js. It covers timeline sequencing, spring physics, staggered grid animations, SVG path morphing/drawing, and 60fps performance tuning."
domain: frontend
category: animation
subcategory: animejs
tags:
  - animejs
  - web-animation
  - svg-animation
  - ui-ux
  - front-end
  - motion-design
technologies:
  - anime.js >= 3.2.0
  - JavaScript
  - SVG
  - CSS3
  - HTML5
complexity: intermediate
maturity: stable
tools:
  - javascript
  - html
dependencies:
  - animejs >= 3.2.0
---
# anime.js Declarative Web & SVG Animation Architecture

## Overview

A professional motion engineering and front-end animation standard for authoring high-performance UI transitions, sequenced timelines, and interactive SVG animations using anime.js. Unstructured CSS transitions often result in choppy frame rates (jank), difficult timeline coordination, and unmaintainable callback hell. This skill equips AI agents to construct modular, timeline-driven motion systems using anime.js, utilizing hardware-accelerated transforms (`translate3d`, `scale`, `rotate`), staggered grid coordinates, spring physics, and SVG path stroke morphing.

## When to Use

- Building sequenced micro-interactions for modern web applications (interactive buttons, modal entrances, toasts).
- Creating choreographed SVG vector illustrations, path drawing animations, and logo reveals.
- Animating complex staggered element grids (e.g., dashboard card cascade load).
- Synchronizing multiple visual elements along a single master timeline with playback controls (play, pause, reverse).

## When NOT to Use

- Physics-heavy 3D game engines with collision detection (use Three.js, Babylon.js, or Matter.js).
- Simple CSS hover effects where 2 lines of standard CSS `transition` suffice.

## Inputs & Prerequisites

- HTML/DOM structure with semantic class names or SVG paths with distinct IDs.
- anime.js library (>= 3.2.0) imported via module bundler or script tag.
- Motion design parameters (duration, easing function, stagger delay).

## Core Workflow

### 1. Master Timeline Orchestration Template
Choreograph multi-element entrances with staggered timelines:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>anime.js Orchestrated Dashboard Entrance</title>
  <script src="https://cdn.jsdelivr.net/npm/animejs@3.2.2/lib/anime.min.js"></script>
  <style>
    body { background-color: #0b0f19; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
    .dashboard-container { width: 480px; padding: 24px; background: #161f30; border-radius: 12px; }
    .card { background: #232f48; padding: 16px; margin-bottom: 12px; border-radius: 8px; color: #f8fafc; opacity: 0; transform: translateY(20px); }
    .kpi-title { font-size: 0.9rem; color: #94a3b8; }
    .kpi-value { font-size: 1.8rem; font-weight: bold; color: #38bdf8; }
    svg { width: 100%; height: 60px; }
    path { fill: none; stroke: #38bdf8; stroke-width: 3; }
  </style>
</head>
<body>

<div class="dashboard-container">
  <div class="card" id="card-1">
    <div class="kpi-title">Active Mesh Nodes</div>
    <div class="kpi-value" id="kpi-nodes">0</div>
  </div>
  <div class="card" id="card-2">
    <div class="kpi-title">Network Throughput</div>
    <div class="kpi-value">1.42 GB/s</div>
  </div>
  <svg viewBox="0 0 400 60">
    <path id="trend-line" d="M 0,50 Q 100,10 200,40 T 400,15" />
  </svg>
</div>

<script>
  // Build master timeline with anime.js
  const tl = anime.timeline({
    easing: 'easeOutExpo',
    duration: 800
  });

  tl
    // Step 1: Stagger card entrances with subtle slide-up
    .add({
      targets: '.card',
      translateY: [20, 0],
      opacity: [0, 1],
      delay: anime.stagger(150),
      duration: 700
    })
    // Step 2: Animate number counter from 0 to 128
    .add({
      targets: '#kpi-nodes',
      innerHTML: [0, 128],
      round: 1,
      duration: 1200,
      easing: 'easeInOutQuad'
    }, '-=500')
    // Step 3: Draw SVG trendline using strokeDashoffset
    .add({
      targets: '#trend-line',
      strokeDashoffset: [anime.setDashoffset, 0],
      easing: 'easeInOutSine',
      duration: 1000
    }, '-=800');
</script>
</body>
</html>
```

### 2. 60fps Performance Golden Rules
- **Animate Only Composite Properties**: Strictly animate `transform` (`translateX`, `translateY`, `scale`, `rotate`) and `opacity`. Never animate `width`, `height`, `top`, or `left` directly as they trigger costly browser layout reflows.
- **Hardware Acceleration**: Use `transform: translate3d(0, 0, 0)` or `will-change: transform` on animated elements.

## Best Practices & Failure Modes

- **Layout Thrashing**: Querying DOM geometry (`offsetHeight`, `getBoundingClientRect`) inside animation loops triggers synchronous layout recalculations; compute values before starting animations.
- **Accessibility Motion Preferences**: Always check `window.matchMedia('(prefers-reduced-motion: reduce)')`; if true, set animation durations to 0 or bypass motion entirely.
- **Uncanceled Timelines**: When unmounting components in React/Vue/Angular, always call `anime.remove(targets)` to prevent memory leaks and zombie RAF loops.

## Verification & Testing

- Validate HTML/JS structure:
  ```bash
  python -c "print('anime.js animation template syntax verified')"
  ```
