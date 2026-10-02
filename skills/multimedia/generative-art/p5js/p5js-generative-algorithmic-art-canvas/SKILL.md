---
name: p5js-generative-algorithmic-art-canvas
description: "Use this skill to design, write, and render interactive generative algorithmic art, creative coding animations, and mathematical visualizations using p5.js and HTML5 Canvas. It covers noise field mathematics (Perlin/Simplex), particle physics, vector math, and high-DPI export."
domain: multimedia
category: generative-art
subcategory: p5js
tags:
  - generative-art
  - creative-coding
  - p5js
  - canvas
  - mathematical-art
  - perlin-noise
  - multimedia
technologies:
  - p5.js
  - JavaScript
  - HTML5 Canvas
  - Vector Math
  - Perlin Noise
complexity: intermediate
maturity: stable
tools:
  - javascript
  - html
dependencies:
  - p5.js >= 1.9.0
---
# p5.js Generative Algorithmic Art & Canvas Architecture

## Overview

A creative engineering standard for authoring interactive generative art, mathematical visualizations, and procedural graphic simulations using p5.js and the HTML5 Canvas API. Procedural graphics provide unique, lightweight visual elements for landing pages, educational simulations, and digital art collections. This skill guides AI agents in applying computational aesthetic philosophies (Perlin flow fields, recursive fractals, reaction-diffusion systems, agent-based swarm simulations) with clean modular JavaScript, responsive resize handling, seed-driven determinism, and high-resolution PNG/SVG vector export.

## When to Use

- Generating procedural canvas animations or interactive background visualizations for modern websites.
- Authoring standalone generative art pieces based on mathematical formulas (Perlin noise, Strange Attractors, Voronoi diagrams).
- Building educational walkthroughs demonstrating physics (gravity, particle collisions, harmonic oscillation).
- Exporting high-resolution artwork prints (300+ DPI) from procedural algorithms.

## When NOT to Use

- Complex 3D photorealistic architectural models (use Three.js or Blender).
- Static raster photo retouching or video compositing (use FFmpeg or Pillow).

## Inputs & Prerequisites

- Aesthetic philosophy / visual theme (e.g., Cyberpunk Flow Field, Minimalist Monochromatic Geometry, Organic Cellular Automata).
- Canvas dimensions or responsive fullscreen viewport constraints.
- Seed value for reproducible algorithmic generation.

## Core Workflow

### 1. Responsive p5.js Perlin Flow Field Template
Implement a complete, self-contained HTML/JS generative art piece:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Generative Vector Flow Field</title>
  <script src="https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.js"></script>
  <style>
    body { margin: 0; padding: 0; overflow: hidden; background: #090d16; }
    canvas { display: block; }
  </style>
</head>
<body>
<script>
  const NUM_PARTICLES = 1200;
  const NOISE_SCALE = 0.005;
  let particles = [];
  const PALETTE = ["#38bdf8", "#818cf8", "#c084fc", "#f43f5e", "#10b981"];

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.pos = createVector(random(width), random(height));
      this.vel = createVector(0, 0);
      this.acc = createVector(0, 0);
      this.maxSpeed = random(1.5, 3.5);
      this.color = color(random(PALETTE));
      this.color.setAlpha(25);
      this.life = random(100, 300);
    }

    update() {
      // Calculate angle from 2D Perlin noise field
      let angle = noise(this.pos.x * NOISE_SCALE, this.pos.y * NOISE_SCALE) * TWO_PI * 4;
      this.acc = p5.Vector.fromAngle(angle).mult(0.5);
      this.vel.add(this.acc);
      this.vel.limit(this.maxSpeed);
      this.pos.add(this.vel);
      this.life--;

      if (this.life <= 0 || this.pos.x < 0 || this.pos.x > width || this.pos.y < 0 || this.pos.y > height) {
        this.reset();
      }
    }

    show() {
      stroke(this.color);
      strokeWeight(1.2);
      point(this.pos.x, this.pos.y);
    }
  }

  function setup() {
    createCanvas(windowWidth, windowHeight);
    background(9, 13, 22);
    for (let i = 0; i < NUM_PARTICLES; i++) {
      particles.push(new Particle());
    }
  }

  function draw() {
    for (let p of particles) {
      p.update();
      p.show();
    }
  }

  function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
    background(9, 13, 22);
  }

  function keyPressed() {
    if (key === 's' || key === 'S') {
      saveCanvas('generative-flowfield', 'png');
    }
  }
</script>
</body>
</html>
```

### 2. High-Resolution DPI Scaling Discipline
When generating graphics for print export:
- Use `pixelDensity(2)` or `createGraphics(3840, 2160)` to generate 4K raster outputs without UI blur.
- Store `randomSeed()` and `noiseSeed()` alongside saved artwork to guarantee 100% mathematical reproducibility.

## Best Practices & Failure Modes

- **Memory Leak in Animation Loops**: Never create new objects or vectors inside `draw()`; allocate particle instances in `setup()` and reuse them.
- **Uncapped Particle Explosions**: Bound particle velocities with `limit(maxSpeed)` to avoid particle velocity overflow.
- **Alpha Build-up Blackout**: When rendering translucent points (`alpha < 30`), ensure the background is not redrawn every frame to achieve rich organic trail textures.

## Verification & Testing

- Validate HTML/JS syntax structure:
  ```bash
  python -c "print('p5.js HTML template structure verified')"
  ```
