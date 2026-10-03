---
name: ai-native-ui
description: "Use this skill to design, build, and optimize AI-Native User Interfaces (Generative UI). It covers streaming token rendering, dynamic component hydration from structured JSON-RPC / tool calls, progressive visual disclosure, optimistic UI state management, adaptive canvas layouts, and shimmer/glow state animations."
domain: ai-engineering
category: models
subcategory: ai_native_ui
tags:
  - generative-ui
  - conversational-interfaces
  - streaming-tokens
  - dynamic-component-hydration
  - adaptive-layout
  - ai-native-ux
  - react-server-components
technologies:
  - TypeScript
  - React
  - Next.js
  - TailwindCSS
  - CSS-Keyframes
  - WebSockets
  - Server-Sent-Events
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
version: 1.0.0
author: Antigravity Team
---

# AI-Native User Interfaces & Generative UI Architecture Standard

## Overview

The `ai-native-ui` skill provides the engineering specifications, interaction models, and frontend integration patterns for constructing AI-Native User Interfaces. In contrast to conventional static Web 2.0 interfaces, an AI-Native UI is fluid, conversational-first, and generative: layout canvases morph dynamically in response to user intent, Server-Sent Events (SSE) stream incremental tokens directly into interactive components, and generative loading states replace static spinners with shimmering layout skeletons. This skill guides frontend and full-stack engineers in delivering low-latency, accessible generative user experiences without Cumulative Layout Shift (CLS).

```
+-----------------------------------------------------------------------------------+
|                        Generative UI Streaming Pipeline                           |
|                                                                                   |
|  [ LLM Inference Engine ]                                                         |
|            |                                                                      |
|            | (Server-Sent Events: chunked tokens / partial tool call JSON)        |
|            v                                                                      |
|  [ Incremental Streaming Parser ] <--- Reconstructs partial JSON trees on-the-fly |
|            |                                                                      |
|            v                                                                      |
|  [ Dynamic Component Hydrator ] <--- Maps tool name to React / Svelte Widget      |
|            |                                                                      |
|            +-----------------------+-----------------------+                      |
|            |                       |                       |                      |
|            v                       v                       v                      |
|    [ Skeleton Shimmer ]    [ Partial Render ]      [ Interactive Ready ]          |
|    (CLS Bounding Box)      (Optimistic Updates)    (Full Hydration & Actions)     |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When building conversational agents that return interactive widgets (e.g. flight selectors, code diff viewers, financial charts, purchase cards) rather than plain markdown.
- When implementing streaming component hydration from LLM function calls / structured tool outputs.
- When designing adaptive, canvas-based workspaces where the UI adjusts its container hierarchy based on generated content density.
- When optimizing Time-To-First-Widget and eliminating Cumulative Layout Shift during streaming generation.

## When NOT to Use

- For static marketing landing pages or traditional CRUD admin dashboards with fixed, predictable relational forms.
- Offline batch processing interfaces where latency and streaming feedback are irrelevant.
- Low-bandwidth or headless embedded systems with no graphical display layer.

---

## Inputs & Prerequisites

1. **Structured Tool / Schema Definition**: JSON Schema specification representing component props (e.g., `FlightCardProps`, `ChartWidgetProps`).
2. **Streaming Protocol**: Server-Sent Events (SSE) or WebSocket channel carrying chunked deltas.
3. **Design System Tokens**: CSS/Tailwind variables defining iridescent gradients, shimmer keyframe speeds, and dark/light mode elevation palettes.

---

## Core Workflow

### Step 1: Incremental Partial JSON Parsing for Tool Calls
While the model streams a tool call, the frontend must render partial component states before the closing JSON braces arrive:

```python
import json
from typing import Dict, Any, Optional

def parse_partial_json(raw_buffer: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to parse partially completed JSON strings emitted by streaming LLMs
    by progressively closing open brackets and quotation marks.
    """
    cleaned = raw_buffer.strip()
    if not cleaned:
        return None

    # Try direct parse first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Heuristic bracket/quote repair for streaming buffers
    repaired = cleaned
    if repaired.count('"') % 2 != 0:
        repaired += '"'
    
    open_curlies = repaired.count('{') - repaired.count('}')
    if open_curlies > 0:
        repaired += '}' * open_curlies

    open_squares = repaired.count('[') - repaired.count(']')
    if open_squares > 0:
        repaired += ']' * open_squares

    try:
        return json.loads(repaired)
    except json.JSONDecodeError:
        return None
```

### Step 2: Cumulative Layout Shift (CLS) Container Bounding
Reserve fixed aspect-ratio bounding boxes to prevent jumpy layout re-flows when generative components appear:

```css
/* Generative UI Shimmer & Layout Bounding Standard */
.generative-container {
  min-height: 180px;
  position: relative;
  transition: height 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.ai-shimmer-active {
  background: linear-gradient(
    90deg,
    rgba(240, 240, 245, 0.6) 0%,
    rgba(220, 225, 240, 0.9) 50%,
    rgba(240, 240, 245, 0.6) 100%
  );
  background-size: 200% 100%;
  animation: aiPulseShimmer 1.8s infinite linear;
}

@keyframes aiPulseShimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Step 3: Progressive Component Hydration
Transition the UI widget through discrete lifecycle stages:
1. `SKELETON`: Pre-allocated bounding box with iridescent shimmer.
2. `PARTIAL`: Streaming initial scalar fields (e.g. title, summary).
3. `HYDRATED`: All payload fields available; interactive controls enabled.
4. `ERROR_FALLBACK`: Graceful degradation to markdown quote on parse failure.

---

## Best Practices & Failure Modes

- **Layout Stability (CLS = 0)**: Never let streamed text push existing interactive buttons out of the viewport while the user is attempting to click.
- **Accessibility & Screen Readers**: Use `aria-live="polite"` with an atomic container for streaming responses; avoid `aria-live="assertive"` which overwhelms screen readers on every token.
- **Optimistic Abort Handling**: When the user types a new prompt or clicks "Stop Generating", immediately freeze the stream, prune dangling unclosed elements, and retain already generated content.

---

## Verification & Testing

1. Run the streaming component hydrator and partial JSON test suite:
   ```bash
   python scripts/ai-native-ui_helper.py
   ```
2. Verify streaming buffer repair and CLS bounding calculations:
   ```bash
   python scripts/streaming_component_hydrator.py --test-all
   ```
