---
name: ai-engineer
description: "Use this skill to design, build, and operate production-grade LLM applications, advanced Retrieval-Augmented Generation (RAG) pipelines, and intelligent agent architectures. It covers hybrid search (dense embeddings + sparse BM25), cross-encoder reranking, LLM gateway routing, semantic caching, token economics, and hallucination evaluation guardrails."
domain: ai-engineering
category: models
subcategory: ai_engineer
tags:
  - ai-engineering
  - llm-applications
  - advanced-rag
  - hybrid-search
  - semantic-caching
  - model-routing
  - guardrails
technologies:
  - Python
  - RAG
  - PyTorch
  - LangChain
  - LlamaIndex
  - Vector Databases
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
  - numpy@>=1.24.0
version: 1.0.0
author: Antigravity Team
---

# Production AI Engineering & Enterprise LLM Systems Architecture

## Overview

A comprehensive engineering standard for architecting, deploying, and operating production-grade Large Language Model (LLM) applications and Advanced Retrieval-Augmented Generation (RAG) systems. Moving from proof-of-concept prototypes to enterprise-grade AI requires solving hard engineering challenges: mitigating non-deterministic hallucinations, optimizing token expenditure and latency, implementing multi-stage hybrid retrieval (dense semantic vectors combined with sparse lexical BM25), enforcing strict output schema contracts (Pydantic/instructor), and securing against prompt injection attacks. This skill provides production patterns for AI systems engineers and autonomous coding agents.

```
+--------------------------------------------------------------------------------+
|                       Production Enterprise LLM Gateway                        |
|                                                                                |
|  [ User Prompt ] ---> [ Security Guardrail: Prompt Injection Filter ]          |
|                                     |                                          |
|                                     v                                          |
|                          [ Semantic Cache Check ]                              |
|                          (Cosine Similarity > 0.96)                            |
|                           /                    \                               |
|                     [Cache Hit]            [Cache Miss]                        |
|                     Return Cache                |                              |
|                                                 v                              |
|                                     [ Hybrid Search Engine ]                   |
|                                     (Dense HNSW + Sparse BM25)                 |
|                                                 |                              |
|                                                 v                              |
|                                     [ Cross-Encoder Re-Ranker ]                |
|                                     (Top 30 chunks -> Top 5)                   |
|                                                 |                              |
|                                                 v                              |
|                                     [ Intelligent Model Router ]               |
|                                     (Tier 1: Claude/GPT-4o, Tier 2: Flash)     |
|                                                 |                              |
|                                                 v                              |
|                               [ Faithfulness & Hallucination Guardrail ]       |
+--------------------------------------------------------------------------------+
```

## When to Use

- Architecting enterprise RAG applications over large unstructured document repositories (PDFs, Confluence, Slack, databases).
- Implementing resilient LLM gateways with automated fallback, semantic caching, rate limiting, and cost controls.
- Optimizing context windows via document chunking strategies (semantic chunking, parent-document retrieval, recursive text splitting).
- Building evaluation pipelines (RAGAS / TruLens) to measure context precision, context recall, and faithfulness.

## When NOT to Use

- Simple deterministic algorithmic workflows or standard relational CRUD applications where LLM inference introduces unnecessary cost and latency.
- Training foundation models from scratch (use distributed pre-training frameworks like Megatron-LM).

## Inputs & Prerequisites

- Python 3.10+ runtime with `numpy`, `requests`, and embedding/vector client libraries.
- API credentials for primary and fallback LLM providers (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`).
- Target vector database (Qdrant, Pinecone, Milvus, Weaviate, or pgvector).

## Core Workflow

### Step 1: Hybrid Retrieval with Reciprocal Rank Fusion (RRF)
Combine dense vector embeddings (capturing semantic intent) and sparse lexical BM25 (capturing exact keywords, SKUs, and error codes):

```python
def reciprocal_rank_fusion(dense_results: list[dict], sparse_results: list[dict], k: int = 60) -> list[dict]:
    """Combines dense and sparse ranked lists using Reciprocal Rank Fusion."""
    scores = {}
    doc_map = {}

    for rank, doc in enumerate(dense_results):
        doc_id = doc["id"]
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)

    for rank, doc in enumerate(sparse_results):
        doc_id = doc["id"]
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank + 1)

    # Sort descending by fused RRF score
    sorted_ids = sorted(scores.keys(), key=lambda did: scores[did], reverse=True)
    return [dict(doc_map[did], rrf_score=round(scores[did], 5)) for did in sorted_ids]
```

### Step 2: Semantic Caching Implementation
Prevent redundant LLM API spend by intercepting identical or semantically equivalent questions:

```python
import numpy as np

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot = np.dot(v1, v2)
    norm = np.linalg.norm(v1) * np.linalg.norm(v2)
    return float(dot / norm) if norm > 0 else 0.0

def query_semantic_cache(new_embedding: np.ndarray, cache: list[dict], threshold: float = 0.95) -> dict | None:
    """Returns cached LLM response if query similarity exceeds threshold."""
    best_match = None
    best_sim = 0.0

    for item in cache:
        sim = cosine_similarity(new_embedding, item["embedding"])
        if sim > best_sim:
            best_sim = sim
            best_match = item

    if best_sim >= threshold:
        print(f"[CACHE HIT] Found equivalent cached response (Similarity={best_sim:.3f})")
        return best_match["response"]
    return None
```

### Step 3: Cross-Encoder Re-Ranking
Pass the top candidates from hybrid retrieval through a cross-encoder model to score joint query-document relevance:

```python
def rerank_documents(query: str, retrieved_docs: list[dict], top_n: int = 5) -> list[dict]:
    """Simulates cross-encoder relevance scoring and prunes context window."""
    # In production: cross_encoder.predict([(query, d['text']) for d in retrieved_docs])
    # Prune context to prevent 'Lost in the Middle' LLM attention degradation
    return retrieved_docs[:top_n]
```

### Step 4: Cost-Aware Intelligent Model Routing
Route queries to lightweight models for straightforward tasks, reserving frontier models for complex multi-step reasoning:

```python
def route_model(prompt: str, token_estimate: int) -> str:
    """Selects optimal model tier based on task complexity and budget."""
    complex_triggers = ["proof", "architect", "multi-agent", "formal verification", "complex refactor"]
    is_complex = any(t in prompt.lower() for t in complex_triggers)
    
    if is_complex or token_estimate > 4000:
        return "tier-1-frontier" # e.g. Claude 3.5 Sonnet / GPT-4o
    else:
        return "tier-2-fast"     # e.g. Gemini 1.5 Flash / GPT-4o-mini
```

## Best Practices & Failure Modes

- **Lost in the Middle**: LLMs attend disproportionately to the beginning and end of long prompts. Always place the most critical retrieved evidence at the top or bottom of the system prompt.
- **Chunk Size Tuning**: For general prose, use chunk sizes of 400-600 tokens with 10-15% overlap. For codebases, chunk strictly along syntax boundaries (AST functions and classes).
- **Prompt Injection Defense**: Never concatenate raw user input directly into system instructions without structural delimiters (e.g. `<user_input>...</user_input>`).

## Verification & Testing

1. Validate RRF hybrid fusion: Run `python scripts/llm_gateway_profiler.py --test-rrf` to verify rank fusion math.
2. Estimate token budgets: Run `python scripts/llm_gateway_profiler.py --estimate-cost --prompt-tokens 2500 --completion-tokens 500 --model gpt-4o`.
3. Check prompt injection filtering: Run `python scripts/llm_gateway_profiler.py --test-injection-guard` to verify detection of common jailbreak patterns.
