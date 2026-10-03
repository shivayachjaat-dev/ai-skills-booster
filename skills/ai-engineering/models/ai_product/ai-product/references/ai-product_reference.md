# AI Product Architecture, Unit Economics & SLA Technical Reference

## 1. AI Product Unit Economics & COGS Modeling

Unlike conventional SaaS where compute cost per user request is negligible ($< \$0.0001$), generative AI requests carry significant direct inference costs ($0.001\text{ to }0.05\text{ USD}$ per request).

### Financial Formulae:
$$\text{Monthly Inference COGS} = \sum_{u=1}^U \left( \frac{T_{\text{in}}^{(u)}}{10^6} \cdot P_{\text{in}} + \frac{T_{\text{out}}^{(u)}}{10^6} \cdot P_{\text{out}} \right)$$

$$\text{Gross Margin \%} = \frac{\text{Monthly Subscription Revenue} - \text{Total Inference COGS}}{\text{Monthly Subscription Revenue}} \times 100$$

### Target Gross Margin Benchmarks:
- **Enterprise B2B AI SaaS**: Target $\ge 75\% - 80\%$ gross margin.
- **Consumer Pro AI Tools**: Target $\ge 65\% - 70\%$ gross margin.
- **Free Tier / Trial**: Hard token ceiling (e.g. 50k tokens/month) enforced at the reverse proxy gateway to prevent infrastructure drain.

---

## 2. Latency Budget Allocation (P95 SLAs)

| Interaction Surface | Target TTFT | Target Total Duration | Recommended Architecture |
| :--- | :--- | :--- | :--- |
| **Inline Autocomplete (Ghost text)** | $< 150\text{ ms}$ | $< 300\text{ ms}$ | Distilled edge model (1B-3B) or speculative decoding |
| **Conversational Co-Pilot** | $< 600\text{ ms}$ | $< 4.0\text{ s}$ | SSE Token streaming with semantic caching |
| **Deep Synthesis / Document Generation** | $< 1.5\text{ s}$ | $< 25\text{ s}$ | Asynchronous job queue + WebSocket progress updates |

---

## 3. Structured Output Contracts & Schema Drift Recovery

In production product flows, generative responses feed directly into downstream APIs, databases, and UI components. Unstructured markdown breaks these integrations.

### Defensive Schema Protocol:
1. **Grammar-Guided Decoding**: Restrict model sampling logits strictly to valid JSON tokens matching the target JSON Schema.
2. **Schema Validation Layer**: Validate model responses against strict Pydantic models with type assertions.
3. **Graceful Field Fallback**: If an optional or non-critical attribute fails validation, assign deterministic fallback values rather than rejecting the entire user request.
4. **Automated Escalation**: When validation fails on critical transaction fields (e.g. monetary amounts, account identifiers), flag the record for human-in-the-loop review.
