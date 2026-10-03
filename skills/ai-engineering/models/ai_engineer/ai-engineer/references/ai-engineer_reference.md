# Enterprise AI Engineering & Production LLM Architecture Reference

## 1. Multi-Stage Hybrid Retrieval & Reranking Architecture

In production RAG systems, single-modality retrieval (dense-only or sparse-only) suffers from severe failure modes:
- **Dense-Only Retrieval Vulnerabilities**: Out-of-vocabulary technical identifiers, UUIDs, SKUs, error codes, and exact variable names are frequently smeared across semantic vector space.
- **Sparse-Only (BM25) Vulnerabilities**: Susceptible to synonym mismatch, vocabulary mismatch, and inability to capture conceptual paraphrasing.

### Hybrid Reciprocal Rank Fusion (RRF) Formulation
To combine dense vector nearest-neighbor search with lexical BM25 without requiring score normalization calibration:

$$\text{RRF\_Score}(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where:
- $M$ is the set of retrieval models (Dense Vector Index + BM25 Lexical Index).
- $r_m(d)$ is the 1-based rank of document $d$ in system $m$.
- $k$ is a smoothing constant (standard empirical default: $k = 60$).

```
[ Query ]
   |
   +---> [ Dense Vector Search (HNSW / IVFFlat) ] ----> [ Ranked List A (Top 50) ] --+
   |                                                                                 |---> [ RRF Fusion ] ---> [ Top 30 ] ---> [ Cross-Encoder ] ---> [ Top 5 ]
   +---> [ Sparse Lexical Search (BM25 / Tantivy) ] --> [ Ranked List B (Top 50) ] --+
```

---

## 2. Semantic Caching Tier

Semantic caching intercepts identical or semantically duplicate queries before hitting downstream vector stores and LLM inference endpoints.

### Specifications:
- **Embedding Generation**: Compute cosine similarity between incoming query embedding $\vec{q}$ and cached vector entries $\vec{c}_i$.
- **Cache Hit Threshold**: Empirically calibrated between `0.94` and `0.97` depending on domain risk tolerance:
  - Exact technical tasks (code generation, legal interpretation): `threshold >= 0.97`
  - Conversational / FAQ search: `threshold >= 0.94`
- **TTL & Invalidation**: Time-to-Live tags and namespace invalidation based on document version mutations.

---

## 3. Token Economics & Cost Optimization Matrix

| Model Tier | Representative Models | Input / 1M Tokens | Output / 1M Tokens | Optimal Workloads |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Frontier Reasoning)** | GPT-4o, Claude 3.5 Sonnet | \$3.00 - \$5.00 | \$15.00 | Architectural design, multi-step agent planning, formal verification, complex code refactoring |
| **Tier 2 (High-Speed Workhorse)**| GPT-4o-mini, Claude 3.5 Haiku, Gemini 1.5 Flash | \$0.075 - \$0.80 | \$0.30 - \$4.00 | Query classification, entity extraction, semantic routing, summarization, guardrail scanning |
| **Self-Hosted / Open Weights** | Llama 3.3 70B, Qwen 2.5 72B (vLLM / TensorRT-LLM) | Fixed compute cost | Fixed compute cost | High-throughput privacy-sensitive enterprise VPC deployments |

---

## 4. Security Guardrails & Prompt Injection Mitigation

Production LLM endpoints must enforce defensive perimeter checks:

1. **Structural Delimiters**: Strict separation of system prompts from untrusted user content via XML-like tags (`<user_context>`, `<retrieved_data>`).
2. **Context Window Tamper Checks**: Scanning for instruction override patterns (`"ignore prior instructions"`, `"system override"`, chat template delimiter markers).
3. **Structured Output Validation**: Enforcing schema adherence using Pydantic / JSON Schema grammars (e.g. Outlines, vLLM guided decoding, OpenAI response_format).
