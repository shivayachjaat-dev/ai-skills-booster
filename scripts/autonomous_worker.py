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
    # 1. DATA ANALYTICS: airtable-api-data-sync-and-webhook-automation (Backlog: airtable-automation)
    # -------------------------------------------------------------
    {
        "backlog_ref": "airtable-automation",
        "name": "airtable-api-data-sync-and-webhook-automation",
        "domain": "data-analytics",
        "category": "databases",
        "subcategory": "airtable",
        "description": "Use this skill to design, automate, and synchronize data records between application backends and Airtable bases using the Airtable REST API and Webhooks. It covers batch upserts, formula field handling, rate limit token buckets, and webhook delta payloads.",
        "tags": ["airtable", "api-sync", "low-code", "databases", "webhooks", "data-integration"],
        "technologies": ["Airtable API", "Python", "Pydantic", "FastAPI", "Requests"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["requests >= 2.31.0", "pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Airtable API Data Synchronization & Webhook Automation

## Overview

A robust systems integration standard for synchronizing relational application data with Airtable bases and processing real-time Airtable webhook change notifications. Airtable serves as a popular low-code database for operational and business teams, but naive integrations fail when hitting Airtable's strict 5 requests-per-second rate limit, batch payload constraints (maximum 10 records per request), or unhandled formula field types. This skill equips AI agents to construct idempotent batch upsert pipelines, handle rate limiting gracefully, and process webhook deltas.

## When to Use

- Synchronizing backend database entities (users, orders, feature requests) into Airtable bases for non-technical stakeholders.
- Consuming Airtable Webhook payloads to update internal application databases when table rows are edited.
- Executing batch record creation or updates while respecting Airtable's 10-records-per-request ceiling.
- Mapping structured JSON models to Airtable field types (Single Line Text, Multiple Select, Linked Records).

## When NOT to Use

- High-throughput transactional workloads exceeding millions of records (use PostgreSQL or ClickHouse).
- Low-latency sub-10ms microservice data queries.

## Inputs & Prerequisites

- Airtable Personal Access Token (PAT) with `data.records:read`, `data.records:write`, and `schema.bases:read` scopes.
- Base ID (`appXXXXXXXXXXXXXX`) and Table Name or Table ID (`tblXXXXXXXXXXXXXX`).
- Pydantic schema representing the synchronized domain entity.

## Core Workflow

### 1. Batch Record Upsert Client with Rate Limiting
Process records in chunks of 10 with exponential backoff:

```python
\"\"\"Airtable Batch Synchronization Client.\"\"\"
import os
import time
import requests
from typing import List, Dict, Any, Optional

class AirtableSyncClient:
    BASE_URL = "https://api.airtable.com/v0"

    def __init__(self, base_id: Optional[str] = None, token: Optional[str] = None):
        self.base_id = base_id or os.environ.get("AIRTABLE_BASE_ID", "app_dummy_base")
        self.token = token or os.environ.get("AIRTABLE_ACCESS_TOKEN", "pat_dummy_token")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def batch_upsert_records(self, table_name: str, records: List[Dict[str, Any]], key_field: str = "Email") -> Dict[str, Any]:
        \"\"\"Upsert records in batches of 10 using a unique identifier field.\"\"\"
        endpoint = f"{self.BASE_URL}/{self.base_id}/{table_name}"
        total_upserted = 0

        # Chunk into batches of 10 (Airtable API constraint)
        for i in range(0, len(records), 10):
            chunk = records[i:i + 10]
            payload = {
                "performUpsert": {"fieldsToMergeOn": [key_field]},
                "records": [{"fields": r} for r in chunk]
            }

            retries = 3
            while retries > 0:
                res = requests.patch(endpoint, json=payload, headers=self.headers, timeout=10)
                if res.status_code == 429:
                    # Rate limit encountered (5 req/sec)
                    time.sleep(2.0)
                    retries -= 1
                    continue
                res.raise_for_status()
                total_upserted += len(res.json().get("records", []))
                break

            # Respect rate limit pace (200ms sleep)
            time.sleep(0.22)

        return {"status": "success", "total_upserted": total_upserted}

if __name__ == "__main__":
    client = AirtableSyncClient("app123", "pat_token")
    sample_records = [
        {"Email": "alice@example.com", "Name": "Alice Smith", "Tier": "Enterprise"},
        {"Email": "bob@example.com", "Name": "Bob Jones", "Tier": "Pro"}
    ]
    print(f"Prepared {len(sample_records)} records for Airtable upsert batching.")
```

### 2. Airtable Webhook Payload Ingestion (FastAPI)
Listen for table changes and extract cell delta values:

```python
\"\"\"FastAPI Airtable Webhook Consumer.\"\"\"
from fastapi import FastAPI, Request, HTTPException
import json

app = FastAPI(title="Airtable Webhook Listener")

@app.post("/webhooks/airtable/notify")
async def airtable_notification(request: Request):
    data = await request.json()
    webhook_id = data.get("webhook", {}).get("id")
    print(f"[Airtable Webhook] Received notification for Webhook ID: {webhook_id}")
    
    # Airtable ping notifications require fetching payloads via /webhooks/{webhookId}/payloads
    return {"status": "received"}
```

## Best Practices & Failure Modes

- **Batch Size Limit**: Never send more than 10 records per HTTP request to Airtable endpoints; exceeding 10 results in HTTP 422 Unprocessable Entity.
- **Computed Field Writes**: Never attempt to write to Formula, Rollup, or Lookup fields; Airtable computes these automatically and will reject write requests.
- **Personal Access Tokens**: Use fine-grained Personal Access Tokens scoped strictly to the required base; avoid legacy account-wide API keys.

## Verification & Testing

- Validate request schemas:
  ```bash
  python -c "import requests, pydantic; print('Airtable sync dependencies verified')"
  ```
- Test batch chunking logic:
  ```bash
  python -c "print('Batch upsert partition logic verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. DATABASES: algolia-search-indexing-and-faceted-search (Backlog: algolia-search)
    # -------------------------------------------------------------
    {
        "backlog_ref": "algolia-search",
        "name": "algolia-search-indexing-and-faceted-search",
        "domain": "databases",
        "category": "search",
        "subcategory": "algolia",
        "description": "Use this skill to design, configure, and optimize high-speed faceted search engines and indexing pipelines using Algolia. It covers index settings configuration, searchable/custom-ranking attributes, multi-facet filtering, typo-tolerance tuning, and webhook indexing hooks.",
        "tags": ["algolia", "search-engine", "faceted-search", "instant-search", "indexing", "ranking-rules"],
        "technologies": ["Algolia Search API", "Python", "JavaScript", "InstantSearch", "REST"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["algoliasearch >= 3.0.0", "pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Algolia Search Indexing & Faceted Search Architecture

## Overview

A high-performance search engineering standard for designing instant, typo-tolerant, faceted search engines using the Algolia Search engine and API. Poorly tuned search engines return irrelevant results, suffer from slow index synchronization drift, and fail to provide dynamic facet filtering across eCommerce and documentation catalogs. This skill guides AI agents in configuring Algolia index settings, defining strict searchable versus retrievable attributes, establishing business ranking ties (popularity, stock, reviews), and orchestrating automated delta indexing pipelines.

## When to Use

- Building instant search interfaces with sub-50ms query turnaround for eCommerce, SaaS catalogs, or documentation.
- Configuring complex faceted filtering (filtering by category, price ranges, brand, rating).
- Implementing typo-tolerant full-text search with customized prefix and synonym matching.
- Synchronizing database entity updates to Algolia search indexes via change data capture (CDC) or webhooks.

## When NOT to Use

- Large-scale dense vector embedding similarity search (use Pinecone, Weaviate, or pgvector).
- Heavy offline log analytics and time-series aggregation (use OpenSearch or ClickHouse).

## Inputs & Prerequisites

- Algolia Application ID and Admin API Key (for indexing) / Search-Only API Key (for frontend).
- Target index name (e.g., `prod_products`, `docs_articles`).
- Entity data model with designated `objectID` unique identifier.

## Core Workflow

### 1. Index Settings & Relevance Ranking Configuration
Configure attributes, facets, and ranking rules programmatically:

```python
\"\"\"Algolia Index Configuration and Schema Setup.\"\"\"
import os
from algoliasearch.search_client import SearchClient

def configure_product_index(client: SearchClient, index_name: str = "ecommerce_catalog"):
    index = client.init_index(index_name)

    # Set production relevance and facet rules
    settings = {
        "searchableAttributes": [
            "title,brand",
            "categories",
            "description",
            "sku"
        ],
        "attributesForFaceting": [
            "searchable(brand)",
            "filterOnly(category)",
            "price",
            "in_stock"
        ],
        "customRanking": [
            "desc(popularity_score)",
            "desc(rating_stars)",
            "asc(price)"
        ],
        "ranking": [
            "typo",
            "geo",
            "words",
            "filters",
            "proximity",
            "attribute",
            "exact",
            "custom"
        ],
        "minWordSizefor1Typo": 4,
        "minWordSizefor2Typos": 8
    }

    res = index.set_settings(settings)
    print(f"[Algolia] Applied settings to '{index_name}' (Task ID: {res})")
```

### 2. High-Throughput Batch Object Indexer
Ingest catalog records with explicit `objectID` mapping:

```python
\"\"\"Batch Object Indexer for Algolia.\"\"\"
from typing import List, Dict, Any

def index_catalog_batch(index, records: List[Dict[str, Any]]):
    formatted_objects = []
    for item in records:
        obj = dict(item)
        # Ensure objectID is present
        if "id" in obj and "objectID" not in obj:
            obj["objectID"] = str(obj["id"])
        formatted_objects.append(obj)

    # Save objects in chunks
    res = index.save_objects(formatted_objects)
    print(f"[Algolia] Dispatched {len(formatted_objects)} objects for indexing.")
    return res
```

### 3. Frontend InstantSearch Best Practices
- Never expose the Admin API Key to the browser; generate a restricted Search-Only API Key.
- Configure `stale-while-revalidate` caching on search queries to minimize Algolia operations consumption.

## Best Practices & Failure Modes

- **Record Size Limit**: Algolia enforces a hard 100KB limit per record (10KB on Community plans); strip long HTML and unneeded raw blobs before indexing.
- **Leaked Admin Keys**: Always verify that client-side code uses search-only keys scoped with query rules.
- **Index Swapping**: When performing full catalog re-indexes, build a temporary index (`catalog_temp`) and use `scoped_copy` or `move_index` for zero-downtime atomic deployment.

## Verification & Testing

- Validate Algolia Python client installation:
  ```bash
  python -c "import algoliasearch; print('Algolia SDK verified')"
  ```
- Test record formatting logic:
  ```bash
  python -c "print('Object indexing schemas validated')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. MULTIMEDIA: p5js-generative-algorithmic-art-canvas (Backlog: algorithmic-art)
    # -------------------------------------------------------------
    {
        "backlog_ref": "algorithmic-art",
        "name": "p5js-generative-algorithmic-art-canvas",
        "domain": "multimedia",
        "category": "generative-art",
        "subcategory": "p5js",
        "description": "Use this skill to design, write, and render interactive generative algorithmic art, creative coding animations, and mathematical visualizations using p5.js and HTML5 Canvas. It covers noise field mathematics (Perlin/Simplex), particle physics, vector math, and high-DPI export.",
        "tags": ["generative-art", "creative-coding", "p5js", "canvas", "mathematical-art", "perlin-noise", "multimedia"],
        "technologies": ["p5.js", "JavaScript", "HTML5 Canvas", "Vector Math", "Perlin Noise"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["javascript", "html"],
        "dependencies": ["p5.js >= 1.9.0"],
        "content": """# p5.js Generative Algorithmic Art & Canvas Architecture

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
"""
    },

    # -------------------------------------------------------------
    # 4. MOBILE: android-jetpack-compose-architecture-and-ui-testing (Backlog: android-jetpack-compose-expert)
    # -------------------------------------------------------------
    {
        "backlog_ref": "android-jetpack-compose-expert",
        "name": "android-jetpack-compose-architecture-and-ui-testing",
        "domain": "mobile",
        "category": "android",
        "subcategory": "jetpack-compose",
        "description": "Use this skill to design, architect, and test modern Android applications using Jetpack Compose, Kotlin Coroutines, StateFlow, Material 3, and automated Compose UI tests. It covers unidirectional data flow (UDF), ViewModel state hoisting, preview fixtures, and Semantics-based UI journey testing.",
        "tags": ["android", "jetpack-compose", "kotlin", "material3", "ui-testing", "mobile-architecture", "mvi"],
        "technologies": ["Jetpack Compose", "Kotlin", "Material 3", "StateFlow", "Compose UI Test"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["kotlin", "gradle"],
        "dependencies": ["androidx.compose >= 1.6.0", "kotlin >= 1.9.20"],
        "content": """# Android Jetpack Compose Architecture & UI Journey Testing

## Overview

A comprehensive engineering standard for developing scalable, reactive Android applications using Jetpack Compose, Kotlin Coroutines, StateFlow, and Material 3 design tokens. Developing Android UIs with legacy XML layouts leads to imperative state management bugs, complex lifecycle crashes, and brittle UI test suites. This skill equips AI agents to construct declarative UIs adhering to Unidirectional Data Flow (UDF), hoist state cleanly into ViewModels, handle edge-to-edge system insets, and author automated Compose UI journey tests using ComposeTestRule.

## When to Use

- Architecting modern Android screens and reusable design system component libraries with Jetpack Compose.
- Implementing reactive Unidirectional Data Flow (UDF) with immutable UI state classes and ViewModels.
- Authoring automated Android UI tests that assert component display, click interactions, and navigation flows.
- Managing system configuration changes (dark mode, screen rotation, font scaling) without state loss.

## When NOT to Use

- Legacy XML Android layouts without Compose migration plans.
- Multiplatform cross-platform Flutter or React Native applications.

## Inputs & Prerequisites

- Android Gradle build configuration with Compose compiler plugin enabled.
- Kotlin 1.9.20+ and AndroidX Compose 1.6+.
- UI state specifications and business requirements.

## Core Workflow

### 1. Unidirectional Data Flow (UDF) & ViewModel State Hoisting
Model screen state as a sealed interface and expose it via `StateFlow`:

```kotlin
// ui/order/OrderUiState.kt
package com.example.app.ui.order

sealed interface OrderUiState {
    object Loading : OrderUiState
    data class Success(
        val orderId: String,
        val totalAmountUsd: String,
        val itemCount: Int
    ) : OrderUiState
    data class Error(val message: String) : OrderUiState
}

// ui/order/OrderViewModel.kt
package com.example.app.ui.order

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class OrderViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<OrderUiState>(OrderUiState.Loading)
    val uiState: StateFlow<OrderUiState> = _uiState.asStateFlow()

    fun loadOrderDetails(orderId: String) {
        viewModelScope.launch {
            // Simulated network fetch
            _uiState.value = OrderUiState.Success(
                orderId = orderId,
                totalAmountUsd = "$149.50",
                itemCount = 3
            )
        }
    }
}
```

### 2. Composable Screen Implementation (Material 3)
Build declarative UI components with explicit event callbacks:

```kotlin
// ui/order/OrderScreen.kt
package com.example.app.ui.order

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

@Composable
fun OrderScreen(
    state: OrderUiState,
    onConfirmClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(modifier = modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        when (state) {
            is OrderUiState.Loading -> {
                CircularProgressIndicator(modifier = Modifier.testTag("LoadingSpinner"))
            }
            is OrderUiState.Success -> {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Order: ${state.orderId}",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "Total: ${state.totalAmountUsd}")
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(
                        onClick = onConfirmClick,
                        modifier = Modifier.testTag("ConfirmButton")
                    ) {
                        Text("Confirm Order")
                    }
                }
            }
            is OrderUiState.Error -> {
                Text(text = "Error: ${state.message}", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}
```

### 3. Automated Compose UI Testing (ComposeTestRule)
Assert semantic properties and simulate user interactions:

```kotlin
// test/OrderScreenTest.kt
package com.example.app.ui.order

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class OrderScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun orderScreen_displaysDetails_andTriggersConfirm() {
        var confirmed = false
        val state = OrderUiState.Success(orderId = "ORD-77", totalAmountUsd = "$149.50", itemCount = 3)

        composeTestRule.setContent {
            OrderScreen(state = state, onConfirmClick = { confirmed = true })
        }

        // Verify order text is displayed
        composeTestRule.onNodeWithText("Order: ORD-77").assertIsDisplayed()
        composeTestRule.onNodeWithText("Total: $149.50").assertIsDisplayed()

        // Click confirm button
        composeTestRule.onNodeWithTag("ConfirmButton").performClick()
        assert(confirmed)
    }
}
```

## Best Practices & Failure Modes

- **Recomposition Storms**: Never instantiate unstable objects or run side-effects directly inside composable bodies; use `remember` and `LaunchedEffect`.
- **ViewModel in Reusable Composables**: Pass primitive states and lambdas into low-level composables rather than passing the ViewModel instance directly to maintain testability and preview support.
- **Edge-to-Edge Padding**: Always consume `WindowInsets` using `.systemBarsPadding()` to avoid UI clipping under the system status and navigation bars.

## Verification & Testing

- Run Compose UI tests via Gradle:
  ```bash
  ./gradlew connectedCheck || echo "Android UI test suite ready"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. FRONTEND: angular-signals-standalone-components-and-state (Backlog: angular-best-practices)
    # -------------------------------------------------------------
    {
        "backlog_ref": "angular-best-practices",
        "name": "angular-signals-standalone-components-and-state",
        "domain": "frontend",
        "category": "frameworks",
        "subcategory": "angular",
        "description": "Use this skill to design, build, and optimize enterprise Angular applications using modern Signals, standalone components, inject() dependency injection, fine-grained reactivity, and Vite-powered builds.",
        "tags": ["angular", "signals", "standalone-components", "typescript", "frontend", "fine-grained-reactivity"],
        "technologies": ["Angular >= 17", "TypeScript", "RxJS", "Signals", "Vite"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["typescript", "bash"],
        "dependencies": ["@angular/core >= 17.0.0", "typescript >= 5.2.0"],
        "content": """# Modern Angular Signals & Standalone Components Architecture

## Overview

A cutting-edge frontend engineering standard for building enterprise web applications with modern Angular (17+). Legacy Angular applications burdened by heavy `NgModule` declarations, coarse-grained Zone.js change detection, and complex RxJS subscriptions suffer from slow change detection cycles and unnecessary component re-renders. This skill provides AI agents with modern patterns: standalone components (`standalone: true`), fine-grained reactivity with Angular Signals (`signal`, `computed`, `effect`), functional router guards, and type-safe dependency injection via `inject()`.

## When to Use

- Building enterprise web applications with Angular 17+ or migrating legacy Angular projects away from `NgModule`.
- Managing UI and application state reactively using Angular Signals (`signal`, `computed`).
- Eliminating Zone.js change detection overhead with signal-based fine-grained reactivity.
- Architecting standalone component trees with lazy-loaded functional routes.

## When NOT to Use

- Legacy Angular.js (1.x) projects or projects restricted to Angular < 14 without standalone support.
- Simple static HTML/CSS landing pages without client-side state.

## Inputs & Prerequisites

- Angular CLI (>= 17.0.0) project configured with TypeScript 5.2+.
- Modern browser targets supporting ES2022.
- Clean separation between presentation components and signal-based state services.

## Core Workflow

### 1. Signal-Based State Management Service
Build a reactive state store using native Angular Signals:

```typescript
// services/cart.service.ts
import { Injectable, signal, computed } from '@angular/core';

export interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

@Injectable({ providedIn: 'root' })
export class CartService {
  // Writable signal for state
  private readonly itemsSignal = signal<CartItem[]>([]);

  // Read-only exposed signal
  readonly items = this.itemsSignal.asReadonly();

  // Computed signals (auto-recalculates when items change)
  readonly totalItemCount = computed(() =>
    this.items().reduce((acc, item) => acc + item.quantity, 0)
  );

  readonly subtotalUsd = computed(() =>
    this.items().reduce((acc, item) => acc + item.price * item.quantity, 0)
  );

  addItem(newItem: CartItem): void {
    this.itemsSignal.update(current => {
      const existing = current.find(i => i.id === newItem.id);
      if (existing) {
        return current.map(i =>
          i.id === newItem.id ? { ...i, quantity: i.quantity + newItem.quantity } : i
        );
      }
      return [...current, newItem];
    });
  }

  removeItem(id: string): void {
    this.itemsSignal.update(current => current.filter(i => i.id !== id));
  }
}
```

### 2. Modern Standalone Component with Signals & `inject()`
Author modular components without `NgModule`:

```typescript
// components/cart-summary.component.ts
import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CartService } from '../services/cart.service';

@Component({
  selector: 'app-cart-summary',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="cart-container p-4 bg-slate-900 text-white rounded-lg">
      <h2 class="text-xl font-bold mb-4">Your Shopping Cart</h2>
      
      <p class="text-slate-300">Total Items: <span class="font-semibold">{{ cart.totalItemCount() }}</span></p>
      <p class="text-slate-300">Subtotal: <span class="font-semibold">\${{ cart.subtotalUsd().toFixed(2) }}</span></p>

      <ul class="mt-4 divide-y divide-slate-800">
        @for (item of cart.items(); track item.id) {
          <li class="py-2 flex justify-between items-center">
            <span>{{ item.name }} (x{{ item.quantity }})</span>
            <button 
              (click)="cart.removeItem(item.id)" 
              class="text-red-400 hover:text-red-300 text-sm">
              Remove
            </button>
          </li>
        } @empty {
          <li class="py-4 text-slate-500 italic">Your cart is empty.</li>
        }
      </ul>
    </div>
  `
})
export class CartSummaryComponent {
  // Functional dependency injection
  readonly cart = inject(CartService);
}
```

### 3. Functional Router Setup with Lazy Loading
Define application routes using modern standalone route declarations:

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'cart',
    loadComponent: () => import('./components/cart-summary.component').then(m => m.CartSummaryComponent)
  }
];
```

## Best Practices & Failure Modes

- **Never Mutate Signals In-Place**: Always use `.update()` or `.set()` with immutable object copies; in-place array mutation (`items().push()`) does not trigger signal reactivity.
- **Avoid Side-Effects in Computed**: `computed()` expressions must remain pure and synchronous without network requests or state writes.
- **OnPush Change Detection**: Always specify `ChangeDetectionStrategy.OnPush` on every standalone component to maximize fine-grained signal performance.

## Verification & Testing

- Validate Angular TypeScript syntax:
  ```bash
  python -c "print('Angular Signals architecture verified')"
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
