#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the continuous autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query:
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if not matched:
            for item in data:
                if item.get("name", "").startswith(backlog_query):
                    item["status"] = new_status
                    if new_status == "completed":
                        item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. FRONTEND: astro-content-and-islands-web-architecture (Backlog: astro)
    # -------------------------------------------------------------
    {
        "backlog_ref": "astro",
        "name": "astro-content-and-islands-web-architecture",
        "domain": "frontend",
        "category": "frameworks",
        "subcategory": "astro-islands",
        "description": "Use this skill to design, build, and optimize content-driven websites and web applications using Astro 4/5 Islands Architecture. It covers zero-JS by default rendering, selective client hydration (client:load, client:idle, client:visible), type-safe Content Collections with Zod schemas, View Transitions API, hybrid SSR adapter configuration, and SEO optimization.",
        "tags": ["frontend", "astro", "islands-architecture", "ssg", "ssr", "typescript", "content-collections", "web-performance"],
        "technologies": ["Astro", "TypeScript", "Zod", "Vite", "Node.js", "Tailwind CSS"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["astro", "npm", "node"],
        "dependencies": ["astro@^4.0.0", "typescript@^5.0.0", "zod@^3.22.0"],
        "content": """# Astro Content Collections & Islands Architecture

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
""",
        "scripts": [
            {
                "name": "audit_astro_islands.py",
                "description": "Scans an Astro project repository to audit client:* directive hydration usage and detect unnecessary JS bundle bloat.",
                "code": """#!/usr/bin/env python3
import os
import re
import sys

DIRECTIVE_PATTERN = re.compile(r'client:(load|idle|visible|media|only)')

def audit_islands(src_dir="src"):
    if not os.path.exists(src_dir):
        print(f"Error: Directory '{src_dir}' not found.")
        sys.exit(1)

    print("=" * 65)
    print(f"Auditing Astro Islands Hydration in: {src_dir}")
    print("=" * 65)

    findings = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.astro', '.mdx', '.jsx', '.tsx')):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        matches = DIRECTIVE_PATTERN.findall(line)
                        for match in matches:
                            findings.append((filepath, line_no, match, line.strip()))

    if not findings:
        print("Pure Static Architecture: No client hydration directives found (0kb JS).")
        return

    counts = {}
    for _, _, directive, _ in findings:
        counts[directive] = counts.get(directive, 0) + 1

    print(f"Total Interactive Islands Found: {len(findings)}\\n")
    print("Hydration Breakdown:")
    for directive, count in sorted(counts.items()):
        print(f"  - client:{directive:<10}: {count} occurrences")

    print("\\nDirectives Audit List:")
    for path, line_no, directive, snippet in findings[:15]:
        rel_path = os.path.relpath(path, src_dir)
        print(f"  [{directive:<7}] {rel_path}:{line_no} -> {snippet[:60]}")

    if counts.get('load', 0) > 5:
        print("\\n[WARNING]: High client:load count detected (>5). Consider client:idle or client:visible for non-critical UI.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "src"
    audit_islands(target)
"""
            }
        ],
        "references": [
            {
                "title": "Astro Islands Architecture & Content Collections Reference",
                "filename": "astro_architecture_reference.md",
                "content": """# Astro Architecture & Performance Guidelines

## Islands Architecture Philosophy
Astro pioneered the Islands Architecture paradigm for web development. In this paradigm:
- The base HTML document is 100% static, pre-rendered during build or on the server edge.
- Interactive components are isolated widgets embedded in the document slot.
- JavaScript runtime is strictly downloaded and executed when the specified trigger condition is satisfied.

## Performance Checklist
1. **Fonts & Assets**: Always use `@astrojs/image` or native Astro `<Image />` component with automated WebP conversion and `srcset` attributes.
2. **SSR Adapters**: When switching from SSG to SSR, select the appropriate official adapter:
   - `@astrojs/node` for standalone Node.js container environments.
   - `@astrojs/cloudflare` for zero-cold-start edge workers.
   - `@astrojs/vercel` for serverless Lambdas.
3. **Cross-Island Communication**:
   Use Nano Stores for lightweight (<1kb), framework-agnostic shared state:
   ```typescript
   import { atom } from 'nanostores';
   export const isCartOpen = atom(false);
   ```
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 2. DATA-ANALYTICS: astropy-computational-astronomy-and-coordinate-systems (Backlog: astropy)
    # -------------------------------------------------------------
    {
        "backlog_ref": "astropy",
        "name": "astropy-computational-astronomy-and-coordinate-systems",
        "domain": "data-analytics",
        "category": "scientific-computing",
        "subcategory": "astronomy-physics",
        "description": "Use this skill to perform computational astronomy, astrophysical data analysis, and celestial mechanics using Astropy. It covers celestial coordinate transformations (ICRS, Galactic, FK5, AltAz), FITS image and table I/O with WCS header mapping, physical units and dimensional quantities, time standards (UTC, TDB, Julian Dates), and cosmological parameter modeling.",
        "tags": ["data-analytics", "scientific-computing", "astronomy", "astrophysics", "astropy", "fits", "coordinate-frames", "celestial-mechanics"],
        "technologies": ["Astropy", "NumPy", "SciPy", "Matplotlib", "Python"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["astropy@^6.0.0", "numpy@^1.26.0", "scipy@^1.12.0"],
        "content": """# Astropy Computational Astronomy & Coordinate Systems

## Overview

A scientific computing engineering standard for processing astronomical datasets, calculating orbital trajectories, and transforming celestial coordinate frames using Python and the Astropy core library. Astronomical data processing demands strict precision regarding relativistic time scales (UTC vs. TAI vs. TDB), spherical trigonometry frame conversions (ICRS, Galactic, AltAz topocentric), FITS (Flexible Image Transport System) file parsing with World Coordinate Systems (WCS), and physical unit dimension checking. This skill provides production patterns for astrophysicists, data engineers, and AI research agents.

```
+------------------------------------------------------------------------+
|                      Astropy Core Architecture                         |
|                                                                        |
|  [ Physical Units & Quantities ] <---> [ Time & Epoch Management ]     |
|      (astropy.units, u.Quantity)           (astropy.time.Time, JD/MJD) |
|                      |                                |                |
|                      v                                v                |
|  [ Celestial Coordinate Frames ]     [ FITS Data I/O & WCS Mapping ]   |
|   (SkyCoord, ICRS, Galactic, AltAz)     (astropy.io.fits, astropy.wcs) |
|                      |                                |                |
|                      +----------------+---------------+                |
|                                       v                                |
|                        [ Cosmological Distance Models ]                |
|                           (astropy.cosmology.FlatLambdaCDM)            |
+------------------------------------------------------------------------+
```

## When to Use

- Parsing, validating, and modifying scientific FITS images, multi-extension headers, and binary tables.
- Converting astronomical observation targets between equatorial coordinates (RA/Dec in ICRS or FK5) and local observatory horizons (Altitude/Azimuth with atmospheric refraction).
- Performing dimensionally safe physics calculations (velocities, luminosity, parsecs, light-years) with automated unit cancellation.
- Computing cosmological distances (angular diameter distance, luminosity distance, lookback time) using standard $\\Lambda\\text{CDM}$ parameterizations.

## When NOT to Use

- General tabular data manipulation with no astronomical spatial/coordinate context (use pure pandas/Polars).
- Simple cartesian 2D/3D geometry without celestial sphere projection or epoch precession.

## Inputs & Prerequisites

- Python 3.10+ with `astropy`, `numpy`, and `scipy` installed.
- Target astronomical dataset (FITS files, Gaia/SDSS/Kepler catalog tables, or coordinate catalogs).
- Observatory site specifications (latitude, longitude, elevation, and timestamp) for topocentric calculations.

## Core Workflow

### Step 1: Dimensioned Quantities and Physical Unit Safety
Prevent unit calculation errors by wrapping values in `astropy.units`:

```python
import astropy.units as u
from astropy.constants import G, M_earth, R_earth

# Calculate Earth escape velocity with automatic unit simplification
v_escape = ((2 * G * M_earth) / R_earth)**0.5
v_escape_km_s = v_escape.to(u.km / u.s)

print(f"Earth Escape Velocity: {v_escape_km_s:.2f}")
# Output: 11.18 km / s
```

### Step 2: Celestial Coordinate Transformations
Transform celestial targets from ICRS (equatorial) to local horizon (AltAz) for a specific ground-based telescope:

```python
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u

# Target: Crab Nebula (M1)
crab = SkyCoord.from_name("M1")

# Observation site: Keck Observatory, Mauna Kea, Hawaii
keck = EarthLocation.of_site("Keck Observatory")

# Observation epoch: 2026-10-15 08:30:00 UTC
obs_time = Time("2026-10-15 08:30:00", scale="utc")

# Transform to local horizon frame
altaz_frame = AltAz(obstime=obs_time, location=keck)
crab_altaz = crab.transform_to(altaz_frame)

print(f"Crab Nebula Altitude: {crab_altaz.alt:.2f}, Azimuth: {crab_altaz.az:.2f}")
if crab_altaz.alt > 30 * u.deg:
    print("Target is observable above airmass limit (>30 deg).")
```

### Step 3: FITS File I/O and WCS Projection
Load high-energy telescope FITS data, inspect headers, and map pixel coordinates to real sky coordinates:

```python
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np

def inspect_fits_file(filepath: str):
    with fits.open(filepath) as hdul:
        hdul.info()
        primary_hdu = hdul[0]
        header = primary_hdu.header
        image_data = primary_hdu.data
        
        # Initialize World Coordinate System
        wcs = WCS(header)
        
        # Convert central pixel to RA/Dec
        ny, nx = image_data.shape
        center_sky = wcs.pixel_to_world(nx / 2, ny / 2)
        print(f"Center Coordinate (ICRS): {center_sky.to_string('hmsdms')}")
        
        return header, image_data, wcs
```

### Step 4: Cosmological Redshift Calculations
Compute luminosity distance and lookback time for high-redshift galaxies:

```python
from astropy.cosmology import FlatLambdaCDM
import astropy.units as u

# Standard Planck 2018 cosmology: H0 = 67.4 km/s/Mpc, Om0 = 0.315
cosmo = FlatLambdaCDM(H0=67.4 * u.km / (u.s * u.Mpc), Om0=0.315)

z = 2.45 # Distant quasar redshift
d_L = cosmo.luminosity_distance(z)
t_lookback = cosmo.lookback_time(z)

print(f"Redshift z={z}: Luminosity Distance = {d_L.to(u.Gpc):.2f}, Lookback Time = {t_lookback.to(u.Gyr):.2f}")
```

## Best Practices & Failure Modes

- **Never Assume UTC for Orbital Mechanics**: High-precision ephemerides require Terrestrial Time (TT) or Barycentric Dynamical Time (TDB) rather than UTC to account for leap seconds.
- **WCS Axis Order**: Remember that NumPy indexing is `[row, col]` (y, x), whereas FITS WCS indexing is `(x, y)` (NAXIS1, NAXIS2). Inverting coordinates leads to flipped astronomical projections.
- **Large FITS Memory Management**: For gigabyte-scale survey images, use `memmap=True` in `fits.open(..., memmap=True)` to avoid reading the entire dataset into RAM.

## Verification & Testing

1. Validate coordinate conversion accuracy against the SIMBAD or VizieR astronomical databases.
2. Verify dimensional consistency: Ensure formulas evaluate without `UnitConversionError`.
3. Check FITS header compliance: Validate with `fits.verify('fix')` to detect non-standard FITS keywords.
""",
        "scripts": [
            {
                "name": "fits_header_analyzer.py",
                "description": "Analyzes a FITS astronomical file, extracting metadata, WCS projections, and photometric zero-points.",
                "code": """#!/usr/bin/env python3
import sys
import os

def analyze_fits(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    try:
        from astropy.io import fits
        from astropy.wcs import WCS
    except ImportError:
        print("Error: Astropy is required. Run 'pip install astropy'.")
        sys.exit(1)

    print("=" * 65)
    print(f"Analyzing Astronomical FITS File: {os.path.basename(filepath)}")
    print("=" * 65)

    with fits.open(filepath) as hdul:
        print(f"HDU Extensions: {len(hdul)}")
        for idx, hdu in enumerate(hdul):
            shape_str = str(hdu.data.shape) if hdu.data is not None else "No Data"
            print(f"  HDU #{idx}: Name={hdu.name}, Type={type(hdu).__name__}, Shape={shape_str}")

        primary = hdul[0]
        hdr = primary.header
        
        keys_of_interest = ['TELESCOP', 'INSTRUME', 'OBJECT', 'EXPTIME', 'DATE-OBS', 'FILTER']
        print("\\nKey Observation Metadata:")
        for k in keys_of_interest:
            if k in hdr:
                print(f"  {k:<12}: {hdr[k]}")

        try:
            wcs = WCS(hdr)
            if wcs.has_celestial:
                print("\\nWorld Coordinate System (WCS) Found:")
                print(f"  Projection Type: {wcs.wcs.ctype[0]} / {wcs.wcs.ctype[1]}")
                print(f"  Reference Pixel: {wcs.wcs.crpix}")
                print(f"  Ref Coordinates: {wcs.wcs.crval} deg")
        except Exception as e:
            print(f"\\nNo valid celestial WCS: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fits_header_analyzer.py <path-to-fits-file>")
        sys.exit(1)
    analyze_fits(sys.argv[1])
"""
            }
        ],
        "references": [
            {
                "title": "Astronomical Coordinate Systems & Epoch Quick Reference",
                "filename": "coordinate_frames_reference.md",
                "content": """# Celestial Coordinate Systems Reference

## Reference Frames
1. **ICRS (International Celestial Reference System)**:
   - Origin: Barycenter of the Solar System.
   - Axes: Aligned with FK5 at J2000.0, fixed against distant extragalactic radio sources (quasars). Standard for modern deep-sky catalogs.
2. **Galactic Frame**:
   - Origin: Galactic Center ($\text{Sgr A}^*$).
   - Coordinates: Galactic Longitude ($l$) and Latitude ($b$), useful for interstellar dust and Milky Way structure studies.
3. **AltAz (Horizontal / Topocentric)**:
   - Origin: Observer's location on Earth's surface.
   - Dependent on geographic coordinates, elevation, pressure, temperature, and exact epoch.

## Time Scales
- **UTC**: Universal Time Coordinated, ticks with atomic seconds but includes irregular leap seconds.
- **TAI**: International Atomic Time, continuous without leap seconds.
- **TDB**: Barycentric Dynamical Time, standard for Solar System dynamics and relativistic orbital modeling.
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 3. BACKEND: asyncio-concurrency-and-event-loop-architecture (Backlog: async-python-patterns)
    # -------------------------------------------------------------
    {
        "backlog_ref": "async-python-patterns",
        "name": "asyncio-concurrency-and-event-loop-architecture",
        "domain": "backend",
        "category": "python",
        "subcategory": "async-concurrency",
        "description": "Use this skill to design, implement, and debug high-performance asynchronous Python systems using standard asyncio. It covers structured concurrency with asyncio.TaskGroup (Python 3.11+), resilient cancellation semantics, worker queues with backpressure, thread/process pool offloading with run_in_executor, event loop latency profiling, and avoiding blocking I/O pitfalls.",
        "tags": ["backend", "python", "asyncio", "concurrency", "event-loop", "taskgroup", "multithreading", "performance"],
        "technologies": ["Python", "asyncio", "uvloop", "concurrent.futures"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python@>=3.11", "uvloop@>=0.19.0"],
        "content": """# Python AsyncIO Concurrency & Event Loop Architecture

## Overview

A systems-level engineering standard for building robust, high-throughput asynchronous services and event-driven architectures in modern Python (3.11+). While Python's `asyncio` delivers massive I/O concurrency without thread overhead, production systems frequently suffer from unhandled task cancellations, silent task failures, blocking CPU operations that freeze the event loop, and queue memory leaks. This skill establishes clean patterns for structured concurrency (`asyncio.TaskGroup`), bounded worker pools, graceful process shutdown, and low-latency profiling.

```
+------------------------------------------------------------------------+
|                          AsyncIO Single-Thread Event Loop              |
|                                                                        |
|  +--------------------+     +--------------------+                     |
|  | Coroutine Task A   |     | Coroutine Task B   |  (Non-blocking I/O) |
|  | (Network Socket)   |     | (Database Client)  |                     |
|  +--------------------+     +--------------------+                     |
|            |                          |                                |
|            v                          v                                |
|  [ Structured Concurrency: asyncio.TaskGroup / ExceptionGroup ]        |
|                               |                                        |
|  [ Bounded Worker Queues ]    |   [ ThreadPoolExecutor Offloading ]    |
|   (asyncio.Queue maxsize=100) |    (CPU-bound / Legacy Blocking SDKs)  |
|                               |                                        |
+-------------------------------+----------------------------------------+
```

## When to Use

- Building high-concurrency microservices, network proxies, stream processors, or web scraping pipelines handling thousands of open sockets.
- Implementing worker pools where work generation must pause when downstream processing is saturated (backpressure).
- Refactoring legacy code with `asyncio.gather()` to modern structured concurrency (`asyncio.TaskGroup`) for bulletproof exception propagation.
- Offloading synchronous or CPU-intensive operations (cryptography, image manipulation, file I/O) to thread/process executors without stalling the event loop.

## When NOT to Use

- Pure CPU-bound parallel number crunching (use `multiprocessing`, Ray, or PySpark instead).
- Simple scripts with strictly linear, sequential tasks where synchronous execution is clearer and faster to maintain.

## Inputs & Prerequisites

- Python 3.11 or higher (leveraging `asyncio.TaskGroup` and `ExceptionGroup`).
- Async-compatible network and database drivers (`httpx`, `aiohttp`, `asyncpg`, `aiosqlite`).

## Core Workflow

### Step 1: Structured Concurrency with TaskGroup
Eliminate orphan tasks and race conditions by replacing `asyncio.gather()` with `asyncio.TaskGroup`. If any subtask raises an exception, remaining tasks are automatically cancelled:

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

async def fetch_telemetry(device_id: str) -> dict:
    await asyncio.sleep(0.1) # Simulate network fetch
    if device_id == "sensor-invalid":
        raise ValueError(f"Telemetry corruption on {device_id}")
    return {"device_id": device_id, "status": "online"}

async def ingest_device_fleet(device_ids: list[str]) -> list[dict]:
    results = []
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_telemetry(did)) for did in device_ids]
            
        # All tasks completed successfully if we reach here
        results = [t.result() for t in tasks]
    except* ValueError as eg:
        for exc in eg.exceptions:
            logger.error("Fleet ingestion validation error: %s", exc)
        raise
    return results
```

### Step 2: Bounded Worker Pool with Backpressure
Prevent memory exhaustion under traffic surges by using `asyncio.Queue` with a strict `maxsize`:

```python
import asyncio
import random

async def worker(worker_id: int, queue: asyncio.Queue):
    while True:
        job = await queue.get()
        try:
            # Process job
            await asyncio.sleep(random.uniform(0.05, 0.2))
            print(f"Worker {worker_id} processed job {job['id']}")
        except asyncio.CancelledError:
            # Clean up before exit
            raise
        except Exception as e:
            print(f"Worker {worker_id} encountered job error: {e}")
        finally:
            queue.task_done()

async def producer(queue: asyncio.Queue, total_jobs: int):
    for i in range(total_jobs):
        # When queue reaches maxsize, producer will asynchronously pause here
        await queue.put({"id": i, "payload": f"data_{i}"})
    print("Producer finished enqueuing all jobs.")

async def run_pipeline():
    queue = asyncio.Queue(maxsize=50) # Strict backpressure buffer
    
    # Spawn 5 worker coroutines
    workers = [asyncio.create_task(worker(i, queue)) for i in range(5)]
    
    await producer(queue, total_jobs=200)
    await queue.join() # Wait until all items are processed
    
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
```

### Step 3: Offloading Blocking Synchronous Calls
Never execute blocking I/O (e.g., standard `requests.get()`, `time.sleep()`, disk writes) directly in the event loop:

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=8)

def blocking_legacy_computation(data: bytes) -> bytes:
    # CPU or blocking disk operation
    time.sleep(0.5)
    return data.upper()

async def safe_async_wrapper(data: bytes) -> bytes:
    loop = asyncio.get_running_loop()
    # Runs in worker thread, leaving event loop unblocked
    result = await loop.run_in_executor(executor, blocking_legacy_computation, data)
    return result
```

### Step 4: Graceful Signal Handling and Teardown
Handle `SIGINT` / `SIGTERM` cleanly to allow ongoing requests to finish within a timeout:

```python
import signal

def setup_graceful_shutdown(loop, stop_event: asyncio.Event):
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(handle_exit(s, stop_event)))
        except NotImplementedError:
            # Windows fallback
            pass

async def handle_exit(sig, stop_event: asyncio.Event):
    print(f"\\nReceived signal {sig.name}. Initiating graceful shutdown...")
    stop_event.set()
```

## Best Practices & Failure Modes

- **Event Loop Starvation**: Avoid any operation taking > 10ms without an `await`. Use Python's `-X dev` or `PYTHONASYNCIODEBUG=1` to detect slow callbacks automatically.
- **CancelledError Swallowing**: Never catch `except Exception:` without re-raising `asyncio.CancelledError`, or tasks will become un-cancellable zombies.
- **ContextVars Thread-Safety**: When using `asyncio.create_task()`, context variables (`contextvars`) are copied shallowly to child tasks.
- **uvloop in Production**: On Linux/macOS production servers, install `uvloop` and call `uvloop.install()` before running the event loop for a 2-4x speedup.

## Verification & Testing

1. Test cancellation semantics using `pytest-asyncio` with explicit task timeout wrappers.
2. Run loop debug mode: `python -X dev server.py` and ensure zero `Executing <Task ...> took 0.XXX seconds` warnings appear.
3. Verify leak prevention: Run memory profiling during sustained load to confirm `asyncio.all_tasks()` count remains bounded.
""",
        "scripts": [
            {
                "name": "event_loop_profiler.py",
                "description": "Profiles event loop latency and detects blocking operations by measuring scheduling jitter.",
                "code": """#!/usr/bin/env python3
import asyncio
import time
import sys

async def jitter_monitor(interval=0.05, threshold=0.03):
    print(f"Monitoring event loop jitter (interval={interval}s, warning threshold={threshold}s)...")
    lag_samples = []
    
    try:
        while True:
            target = time.perf_counter() + interval
            await asyncio.sleep(interval)
            now = time.perf_counter()
            drift = now - target
            
            if drift > threshold:
                print(f"[EVENT LOOP STALL DETECTED]: Delay={drift*1000:.2f}ms above baseline!")
            
            lag_samples.append(drift)
            if len(lag_samples) >= 50:
                avg_lag = sum(lag_samples) / len(lag_samples) * 1000
                max_lag = max(lag_samples) * 1000
                print(f"Metrics (last 50 ticks): Avg Jitter={avg_lag:.2f}ms | Max Stall={max_lag:.2f}ms")
                lag_samples.clear()
    except asyncio.CancelledError:
        print("Jitter monitor stopped cleanly.")

async def simulate_workload():
    await asyncio.sleep(1.0)
    print("Simulating brief blocking operation to verify detector...")
    time.sleep(0.08) # Deliberate 80ms block
    await asyncio.sleep(2.0)

async def main():
    monitor_task = asyncio.create_task(jitter_monitor())
    workload_task = asyncio.create_task(simulate_workload())
    
    await workload_task
    monitor_task.cancel()
    await asyncio.gather(monitor_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
"""
            }
        ],
        "references": [
            {
                "title": "AsyncIO Antipatterns and Performance Checklist",
                "filename": "asyncio_architecture_reference.md",
                "content": """# AsyncIO Engineering Patterns & Antipatterns

## Critical Antipatterns
1. **Unbounded `asyncio.gather(*tasks)` with thousands of elements**:
   - Spawns thousands of concurrent sockets immediately, exhausting file descriptors (`ulimit -n`).
   - Fix: Use `asyncio.Semaphore(max_concurrent)` or an `asyncio.Queue` worker pool.

2. **Synchronous File I/O in Async Handlers**:
   - `open('large.json', 'r').read()` blocks the main thread completely.
   - Fix: Use `anyio.to_thread.run_sync` or `aiofiles`.

3. **Silent Exception Loss**:
   - Spawning fire-and-forget tasks with `asyncio.create_task(coro())` without retaining references. If the task fails, the exception is only printed when garbage collected.
   - Fix: Retain task references or use `TaskGroup`.
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 4. SECURITY: threat-modeling-and-attack-tree-construction (Backlog: attack-tree-construction)
    # -------------------------------------------------------------
    {
        "backlog_ref": "attack-tree-construction",
        "name": "threat-modeling-and-attack-tree-construction",
        "domain": "security",
        "category": "threat-modeling",
        "subcategory": "attack-trees",
        "description": "Use this skill to systematically model adversary capabilities and visualize attack vectors using hierarchical AND/OR attack trees. It covers root goal definition, node decomposition, probability and cost quantification, STRIDE mapping, residual risk scoring (DREAD/CVSS), and mapping defensive countermeasures directly to leaf-node vectors.",
        "tags": ["security", "threat-modeling", "attack-trees", "risk-assessment", "stride", "dread", "appsec", "adversary-modeling"],
        "technologies": ["Threat Modeling", "Mermaid.js", "Python", "Graphviz", "STRIDE", "CVSS"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python@>=3.10"],
        "content": """# Threat Modeling & Hierarchical Attack Tree Construction

## Overview

A structured security engineering framework for modeling adversary tactics, calculating compromise probabilities, and designing defensive mitigations using hierarchical Attack Trees (Schneier methodology). While high-level threat frameworks like STRIDE enumerate abstract categories of risk, Attack Trees mathematically decompose a root compromise goal (e.g., "Exfiltrate Customer Database") into logical AND/OR conditions across concrete attack surfaces. This skill guides security architects, penetration testers, and AI agents in constructing valid attack trees, quantifying adversary cost vs. payoff, and prioritizing security controls.

```
                     [ Root Goal: Compromise Production DB ]
                                        |
                 +----------------------+----------------------+ (OR)
                 |                                             |
    [ Target: Exfiltrate via SQLi ]              [ Target: Stolen IAM Credentials ]
                 |                                             |
        +--------+--------+ (AND)                     +--------+--------+ (AND)
        |                 |                           |                 |
 [ Find Unsanitized ] [ Bypass WAF ]           [ Phish Admin Key ] [ Bypass MFA ]
```

## When to Use

- Performing architecture threat assessments during design phases for cloud, fintech, or healthcare infrastructure.
- Evaluating the security posture of an existing software system prior to third-party penetration testing.
- Quantifying the ROI of security mitigations (e.g., measuring whether implementing WebAuthn MFA breaks the lowest-cost attack path).
- Formalizing attack chains for incident response table-top exercises.

## When NOT to Use

- Automated low-level vulnerability scanning (e.g., running Semgrep, Trivy, or OWASP ZAP).
- Writing exploitation payloads or exploit automation code.

## Inputs & Prerequisites

- System architecture diagrams, data flow diagrams (DFD), trust boundaries, and asset inventory.
- Target threat actor profiles (opportunistic script kiddie, cybercriminal group, malicious insider, nation-state).
- Graphing utilities (Mermaid.js or Graphviz) for tree rendering.

## Core Workflow

### Step 1: Root Goal Identification and Scope
Select an attacker-centric root objective focused on critical asset compromise rather than an abstract vulnerability:
- *Bad*: "SQL Injection in User Profile" (Vulnerability, not goal).
- *Good*: "Exfiltrate Unencrypted PII from Customer Database" (Root objective).

### Step 2: Hierarchical Node Decomposition (AND/OR Logic)
Decompose nodes top-down into logical prerequisites:
- **OR Nodes**: The attacker succeeds if *any* single child node succeeds (multiple alternate paths).
- **AND Nodes**: The attacker succeeds *only if all* child nodes succeed (chained prerequisites).

```mermaid
graph TD
    Root["Goal: Unauthorized Admin Access to Cloud Console"]
    Root --> OR1{"OR"}
    
    OR1 --> PathA["Compromise IAM Long-Lived Key"]
    OR1 --> PathB["Session Hijacking / Token Theft"]
    OR1 --> PathC["Exploit SSO Identity Provider"]
    
    PathA --> AND1{"AND"}
    AND1 --> A1["Scan Public GitHub for Leaked Access Key"]
    AND1 --> A2["Key lacks IP Restriction Policy"]
    
    PathB --> AND2{"AND"}
    AND2 --> B1["Deploy Infostealer Malware to Admin Laptop"]
    AND2 --> B2["Extract Active AWS SSO Cookie"]
    AND2 --> B3["Bypass Conditional Access Session Token"]
```

### Step 3: Adversary Cost and Feasibility Quantification
Assign standard quantitative attributes to each leaf node:
- **Cost**: Financial expenditure required (Low: <$100, Medium: <$10k, High: >$10k).
- **Skill Required**: Novice, Intermediate, Advanced, Elite/Nation-State.
- **Likelihood**: Probability of success within 12 months (0.0 to 1.0).
- **Detection Probability**: Chance of triggering an alert during execution.

### Step 4: Defense Mapping & Cut-Set Identification
Identify the "Minimal Cut Set"—the smallest combination of defensive mitigations that completely severs all valid attack paths leading to the root goal:

| Leaf Node Attack Vector | Defensive Countermeasure | Impact on Attack Tree |
|---|---|---|
| Leaked Access Keys in Git | Git pre-commit secret scanning + short-lived AWS IAM Identity Center tokens | Completely eliminates Path A |
| Cookie Theft via Infostealer | FIDO2 / WebAuthn Hardware Security Keys (Device-bound credentials) | Cuts Path B session reuse |
| SSO Credential Stuffing | Phishing-resistant MFA + Risk-based conditional access policies | Cuts Path C |

## Best Practices & Failure Modes

- **Avoid Infinite Leaf Explosion**: Stop decomposing when reaching standard primitives (e.g., "Exploit known CVE in unpatched nginx") rather than modeling compiler internals.
- **Strict AND/OR Semantics**: Ensure intermediate nodes explicitly declare whether children are independent options (OR) or mandatory steps in a sequential chain (AND).
- **Keep Trees Dynamic**: Update trees when defensive controls change or when new public exploit techniques are disclosed.

## Verification & Testing

1. Verify that every path from root to leaves contains valid logical transitions without circular loops.
2. Confirm that proposed defensive controls break at least one node in every branch of an OR set.
3. Validate tree syntax with Mermaid linting or Graphviz compile tests.
""",
        "scripts": [
            {
                "name": "attack_tree_evaluator.py",
                "description": "Parses a JSON/YAML attack tree model and computes the lowest-cost attack path and minimal cut set.",
                "code": """#!/usr/bin/env python3
import json
import sys

SAMPLE_TREE = {
    "goal": "Exfiltrate Customer DB",
    "type": "OR",
    "children": [
        {
            "name": "SQL Injection in Search API",
            "type": "AND",
            "children": [
                {"name": "Discover parameter SQLi", "cost": 2, "skill": "medium"},
                {"name": "Bypass ModSecurity WAF", "cost": 4, "skill": "high"}
            ]
        },
        {
            "name": "Compromise Database Backup Bucket",
            "type": "AND",
            "children": [
                {"name": "Obtain S3 read credentials", "cost": 3, "skill": "medium"},
                {"name": "Overcome S3 bucket KMS encryption", "cost": 6, "skill": "high"}
            ]
        },
        {
            "name": "Insider Credential Abuse",
            "cost": 10,
            "skill": "low"
        }
    ]
}

def calculate_min_cost(node):
    if "cost" in node and "children" not in node:
        return node["cost"], [node["name"]]
    
    node_type = node.get("type", "OR")
    if node_type == "AND":
        total_cost = 0
        all_steps = []
        for child in node["children"]:
            c, steps = calculate_min_cost(child)
            total_cost += c
            all_steps.extend(steps)
        return total_cost, all_steps
    else: # OR node
        best_cost = float("inf")
        best_path = []
        for child in node["children"]:
            c, steps = calculate_min_cost(child)
            if c < best_cost:
                best_cost = c
                best_path = steps
        return best_cost, best_path

def evaluate_tree(tree_data):
    print("=" * 65)
    print(f"Attack Tree Evaluation: Root Goal = '{tree_data['goal']}'")
    print("=" * 65)
    min_cost, path = calculate_min_cost(tree_data)
    print(f"Lowest Adversary Cost to Compromise: {min_cost} points")
    print("\\nMost Probable / Lowest-Resistance Attack Path:")
    for idx, step in enumerate(path, 1):
        print(f"  {idx}. {step}")

if __name__ == "__main__":
    evaluate_tree(SAMPLE_TREE)
"""
            }
        ],
        "references": [
            {
                "title": "Attack Tree Modeling Methodology & STRIDE Mapping Guide",
                "filename": "attack_tree_methodology.md",
                "content": """# Attack Tree Methodology Guide

## Bruce Schneier Attack Tree Notation
Attack trees were popularized by Bruce Schneier in 1999 as a formal method to evaluate cyber-physical and information security systems:
- Nodes represent sub-goals.
- Leaves represent individual attack vectors.
- Operators (AND / OR) quantify whether attackers need parallel conditions or choices.

## Node Scoring Matrix
| Metric | Low (1 pt) | Medium (3 pts) | High (5 pts) | Extreme (10 pts) |
|---|---|---|---|---|
| Attacker Cost | < $100 | $100 - $5,000 | $5,000 - $50,000 | > $50,000 |
| Skill Needed | Script Kiddie | Experienced Dev | Penetration Tester | Nation-State APT |
| Equipment | Standard Laptop | Commercial Tools | Specialized Hardware | Zero-Day Research Lab |
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 5. AI-ENGINEERING: whisper-speech-to-text-and-diarization-pipeline (Backlog: audio-transcriber)
    # -------------------------------------------------------------
    {
        "backlog_ref": "audio-transcriber",
        "name": "whisper-speech-to-text-and-diarization-pipeline",
        "domain": "ai-engineering",
        "category": "audio-processing",
        "subcategory": "speech-recognition",
        "description": "Use this skill to build end-to-end automated speech recognition (ASR) and speaker diarization pipelines using OpenAI Whisper and PyAnnote. It covers CTranslate2 (faster-whisper) acceleration, Silero Voice Activity Detection (VAD) audio chunking, multi-speaker clustering, precise timestamp word alignment, and structured Markdown, SRT, and JSON transcript generation.",
        "tags": ["ai-engineering", "audio-processing", "speech-to-text", "whisper", "faster-whisper", "speaker-diarization", "pyannote", "vad"],
        "technologies": ["Whisper", "faster-whisper", "PyAnnote", "Silero VAD", "FFmpeg", "Python"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "ffmpeg", "bash"],
        "dependencies": ["faster-whisper@>=1.0.0", "pyannote.audio@>=3.1.0", "torch@>=2.1.0"],
        "content": """# Whisper Speech-to-Text & Multi-Speaker Diarization Pipeline

## Overview

A production engineering standard for building high-accuracy, cost-effective automated speech recognition (ASR) pipelines with multi-speaker diarization. While vanilla Whisper models transcribe audio with remarkable linguistic precision, enterprise use cases (boardroom meetings, clinical consultations, podcast production, customer support triage) require knowing *who* spoke *when*, filtering non-speech background noise, and executing inference with high throughput. This skill guides AI engineers in integrating `faster-whisper` (CTranslate2 INT8/FP16 quantization), Silero Voice Activity Detection (VAD), and `pyannote.audio` speaker clustering to generate timestamped, speaker-labeled Markdown and subtitle outputs.

```
+------------------------------------------------------------------------+
|                 Speech Processing & Diarization Pipeline               |
|                                                                        |
|  [ Raw Audio / Video ] ---> [ FFmpeg Audio Normalization (16kHz Mono) ]|
|                                              |                         |
|                      +-----------------------+                         |
|                      |                                                 |
|                      v                                                 |
|          [ Silero VAD Pre-Filter ] (Remove dead silence & background)  |
|                      |                                                 |
|         +------------+------------+                                    |
|         v                         v                                    |
|  [ faster-whisper ]      [ pyannote.audio ]                            |
|  (CTranslate2 ASR)       (Speaker Embedding & Clustering)              |
|         |                         |                                    |
|         +------------+------------+                                    |
|                      v                                                 |
|      [ Timestamp Alignment & Speaker Fusion ]                          |
|                      |                                                 |
|                      v                                                 |
|  [ Formatted Output: Markdown Notes / SRT / JSON Transcript ]          |
+------------------------------------------------------------------------+
```

## When to Use

- Transcribing executive meetings, interviews, podcasts, or customer calls where distinguishing speaker identities is mandatory.
- Deploying private, on-premise, or cloud ASR pipelines that eliminate recurring third-party API costs.
- Generating synchronized subtitle files (`.srt`, `.vtt`) with precise word-level timing.
- Batch processing gigabytes of legacy audio recordings with GPU-accelerated INT8 quantization.

## When NOT to Use

- Real-time, ultra-low latency voice-to-voice streaming conversational agents (<200ms budget; use streaming WebRTC ASR like Whisper-live or Deepgram Nova-2).
- Non-speech audio classification (e.g., gunshot detection, musical pitch estimation).

## Inputs & Prerequisites

- Audio/video files in standard formats (`.wav`, `.mp3`, `.m4a`, `.mp4`, `.flac`).
- FFmpeg installed in the system PATH.
- Python 3.10+ with PyTorch (CUDA optional but recommended for speed).
- Hugging Face user access token for downloading PyAnnote diarization weights.

## Core Workflow

### Step 1: Audio Pre-Processing with FFmpeg
Convert incoming audio streams to 16kHz 16-bit mono PCM, the standard sample rate for Whisper and PyAnnote:

```bash
ffmpeg -i input_media.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le normalized_audio.wav
```

### Step 2: Accelerated Transcription with faster-whisper
Use `faster-whisper` (CTranslate2) for 4x faster execution and 50% lower VRAM consumption:

```python
from faster_whisper import WhisperModel

# Use "large-v3" for maximum accuracy, or "distil-large-v3" for high speed
# Compute type: "float16" on GPU, "int8" on CPU
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    "normalized_audio.wav",
    beam_size=5,
    vad_filter=True, # Built-in Silero VAD chunking
    vad_parameters=dict(min_silence_duration_ms=500),
    language="en",
    word_timestamps=True
)

transcription_segments = []
for segment in segments:
    transcription_segments.append({
        "start": segment.start,
        "end": segment.end,
        "text": segment.text.strip(),
        "words": [{"word": w.word, "start": w.start, "end": w.end, "prob": w.probability} for w in segment.words]
    })
```

### Step 3: Speaker Diarization with pyannote.audio
Extract speaker segmentation turns from the normalized audio:

```python
from pyannote.audio import Pipeline
import torch

def run_diarization(audio_path: str, hf_token: str):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        
    diarization = pipeline(audio_path)
    
    speaker_turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_turns.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return speaker_turns
```

### Step 4: Speaker-to-Text Temporal Fusion
Assign speaker labels to transcription segments by calculating maximum temporal intersection:

```python
def merge_speaker_and_text(transcripts, speaker_turns):
    merged = []
    
    for seg in transcripts:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_mid = (seg_start + seg_end) / 2.0
        
        # Find overlapping speaker
        matched_speaker = "Unknown"
        for turn in speaker_turns:
            if turn["start"] <= seg_mid <= turn["end"]:
                matched_speaker = turn["speaker"]
                break
                
        merged.append({
            "speaker": matched_speaker,
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"]
        })
        
    return merged
```

### Step 5: Structured Markdown Output Formatting
Group consecutive utterances by the same speaker into readable conversation blocks:

```python
def format_to_markdown(merged_entries) -> str:
    md_lines = ["# Meeting & Audio Transcription\\n"]
    current_speaker = None
    
    for entry in merged_entries:
        speaker = entry["speaker"]
        timestamp = f"[{int(entry['start'] // 60):02d}:{int(entry['start'] % 60):02d}]"
        
        if speaker != current_speaker:
            current_speaker = speaker
            md_lines.append(f"\\n### {speaker} {timestamp}\\n")
            
        md_lines.append(f"{entry['text']} ")
        
    return "\\n".join(md_lines)
```

## Best Practices & Failure Modes

- **Audio Clipping & Low SNR**: Poor microphone gain leads to hallucinated repetitive sentences in Whisper. Normalize audio gain using `-af loudnorm` in FFmpeg.
- **Cross-Talk & Overlapping Speakers**: When two speakers talk simultaneously, PyAnnote flags overlapping segments. Whisper might capture only the louder speaker. Handle overlapping intervals gracefully.
- **VAD Truncation**: Ensure `min_silence_duration_ms` is set to at least 400-500ms; overly aggressive silence pruning cuts off word endings and natural pauses.

## Verification & Testing

1. Test transcription accuracy against a standardized ground truth audio snippet (measure Word Error Rate / WER).
2. Verify speaker change transitions: Ensure no single speaker monologue artificially crosses distinct conversational turns.
3. Validate output formats: Generate valid SRT files and verify with subtitle players like VLC.
""",
        "scripts": [
            {
                "name": "audio_transcription_cli.py",
                "description": "CLI utility to transcribe audio files with faster-whisper, generating timestamped Markdown transcripts.",
                "code": """#!/usr/bin/env python3
import sys
import os

def transcribe_file(audio_path, output_md=None):
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found.")
        sys.exit(1)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper is not installed. Run 'pip install faster-whisper'.")
        sys.exit(1)

    print("=" * 65)
    print(f"Transcribing Audio: {os.path.basename(audio_path)}")
    print("=" * 65)

    # Use CPU int8 by default for universal portability
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=3, vad_filter=True)

    print(f"Detected Language: '{info.language}' (Probability: {info.language_probability:.2f})\\n")

    lines = [f"# Transcript: {os.path.basename(audio_path)}\\n"]
    for seg in segments:
        ts = f"[{int(seg.start // 60):02d}:{int(seg.start % 60):02d} -> {int(seg.end // 60):02d}:{int(seg.end % 60):02d}]"
        print(f"{ts} {seg.text.strip()}")
        lines.append(f"**{ts}** {seg.text.strip()}\\n")

    if output_md:
        with open(output_md, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\\nSaved transcript to {output_md}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audio_transcription_cli.py <path-to-audio-file> [output.md]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    transcribe_file(sys.argv[1], out)
"""
            }
        ],
        "references": [
            {
                "title": "Speech Recognition & Diarization Performance Reference",
                "filename": "speech_pipeline_reference.md",
                "content": """# Whisper & Diarization Optimization Reference

## Whisper Model Comparison
| Model Size | Parameters | VRAM (FP16) | Relative Speed | Typical WER (English) |
|---|---|---|---|---|
| tiny | 39 M | ~1 GB | 32x | ~8-10% |
| base | 74 M | ~1 GB | 16x | ~6-8% |
| small | 244 M | ~2 GB | 6x | ~4-5% |
| medium | 769 M | ~5 GB | 2x | ~3-4% |
| large-v3 | 1550 M | ~10 GB | 1x | ~2-3% |
| distil-large-v3 | 756 M | ~4 GB | 6x | ~2.5-3.5% |

## FFmpeg Commands for Audio Normalization
```bash
# Normalize loudness to EBU R128 standard
ffmpeg -i raw_input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 16000 -ac 1 clean_mono.wav
```
"""
            }
        ]
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for idx, skill_def in enumerate(CONTINUOUS_QUEUE, 1):
        backlog_ref = skill_def.get("backlog_ref")
        name = skill_def["name"]
        domain = skill_def["domain"]
        category = skill_def["category"]
        subcategory = skill_def.get("subcategory", "")
        print(f"\n[{idx}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")

        success = create_and_ship_skill(skill_def)

        if success:
            mark_backlog_item(backlog_ref, "completed")
            print(f"\n[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"\n[Engine] FAILED to ship skill: {name}. Halting.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
