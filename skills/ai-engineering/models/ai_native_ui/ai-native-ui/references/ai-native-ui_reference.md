# AI-Native User Interfaces & Generative UX Technical Reference

## 1. Interaction Models: Direct Manipulation vs. Conversational Co-Pilot

Traditional GUI design relies on static visual affordances (menus, buttons, tabs). AI-Native UI introduces dynamic, intent-driven interface synthesis:

```
[ Natural Language Intent / Voice Prompt ]
                   |
                   v
       [ LLM Tool Calling Engine ]
                   |
                   v
       [ Generative Widget Stream ]
      /             |              \
     v              v               v
[ Data Filter ]  [ Inline Chart ]  [ Action Card ]
```

### Core Principles
1. **Conversational Primacy**: Text and voice prompts represent first-class navigation and action invocation channels.
2. **Generative Loading Skeletons**: Static spinners are replaced by content-aware shimmering wireframes that mimic the expected final layout.
3. **Adaptive Form Factor**: Widgets dynamically resize and refactor their layout density (compact mobile list vs. multi-column analytics grid) based on generated payload schema.

---

## 2. Server-Sent Events (SSE) Chunking & Protocol Contract

Streaming generative components requires structured framing over standard HTTP/2 Server-Sent Events.

```
event: component_chunk
data: {"widget_id": "card_01", "type": "FlightCard", "delta": {"origin": "SFO"}}

event: component_chunk
data: {"widget_id": "card_01", "type": "FlightCard", "delta": {"destination": "HND"}}

event: component_ready
data: {"widget_id": "card_01", "status": "interactive"}
```

---

## 3. Cumulative Layout Shift (CLS) Mitigation

Google Core Web Vitals targets a **CLS score $< 0.10$**. In AI-Native UI, incremental token streaming poses high layout shift risk.

### Defensive Engineering Patterns:
- **Aspect-Ratio Placeholders**: Pre-allocate fixed aspect ratio boxes (`aspect-video`, `aspect-[4/3]`) or CSS `min-height` before token streaming commences.
- **Content Anchoring**: Keep viewport scroll positions locked to the bottom or active reading cursor using `overflow-anchor: auto`.
- **Skeleton Shimmer**: Animate background gradients using hardware-accelerated GPU transforms (`transform: translate3d`) rather than CSS `left` or `width` mutations.

---

## 4. Accessibility (a11y) & Screen-Reader Standards

- Streaming tokens must not bombard screen readers with discrete auditory alerts on every word.
- Enforce `aria-live="polite"` on container elements and defer full accessibility announcements until the `component_ready` event completes.
- Ensure all generative form controls provide fallback standard keyboard navigation (`Tab`, `Space`, `Enter`).
