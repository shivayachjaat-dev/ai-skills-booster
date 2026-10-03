# Agent Experience Optimization (AEO) Technical Reference

## 1. Principles of Agent Experience Optimization

AEO is the practice of designing, structuring, and optimizing software interfaces (APIs, Model Context Protocol servers, CLI commands) specifically for consumption by autonomous LLM agents:

$$\text{Agent Friction Index} = \frac{\text{Prompt Complexity} \times \text{Token Footprint}}{\text{Schema Determinism} \times \text{Error Actionability}}$$

### Key Friction Vectors:
1. **Ambiguous Documentation**: LLMs hallucinate parameter values when descriptions do not explicitly enumerate valid options, units, or constraints.
2. **Context Window Pollution**: An API that returns 500 lines of unparsed HTML or nested metadata depletes the agent's attention budget and increases hallucination probability on subsequent turns.
3. **Interactive Blocking**: Command-line tools that block on interactive terminal input without non-interactive flags freeze the agent process indefinitely.

---

## 2. Model Context Protocol (MCP) Design Rubric

To achieve Grade A (Score $\ge 90$) AEO readiness:
- **Parameter Schemas**: Every parameter must declare an explicit JSON Schema `type`, a clear `description`, and explicit `enum` arrays where values are discrete.
- **Idempotency Annotations**: Read-only tools must be clearly annotated (`"is_read_only": true`) so the agent knows invocations cannot cause destructive side-effects.
- **Payload Truncation & Paging**: Tools returning lists or search hits must implement sensible default page limits (e.g. 5-10 records) with cursor-based pagination tokens.

---

## 3. Machine-Parseable Error Taxonomy

When an agent invokes a tool with incorrect arguments, the error response must provide actionable remediation:

```json
{
  "status": "error",
  "error_code": "INVALID_ENUM_PARAMETER",
  "field": "environment",
  "received_value": "prod-east",
  "allowed_values": ["development", "staging", "production"],
  "remediation": "Select one of the allowed_values."
}
```

This deterministic structure enables the LLM to self-correct in a single turn rather than drifting into repeated speculative failures.
