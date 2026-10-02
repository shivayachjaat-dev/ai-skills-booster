---
name: rag-retrieval-evaluation
description: "Use this skill when evaluating, benchmarking, and optimizing the retrieval quality of a Retrieval-Augmented Generation (RAG) system. It guides the agent through calculating Recall@K, Precision@K, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (NDCG), and context relevance to eliminate hallucinations caused by poor context retrieval."
domain: ai-engineering
category: rag
subcategory: evaluation
tags:
  - rag
  - evaluation
  - vector-search
  - embeddings
  - information-retrieval
  - llm-benchmarking
technologies:
  - Python
  - Vector Databases
  - Embeddings
  - Ragas
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.9
  - numpy
---
# RAG Retrieval Evaluation

## Overview

A systematic evaluation and tuning workflow for Retrieval-Augmented Generation (RAG) systems. This skill enables agents to quantify retrieval accuracy, detect retrieval failures, diagnose embedding misalignment, and optimize chunking strategies to eliminate hallucinations caused by omitted or irrelevant context.

## When to Use

- Benchmarking retrieval performance of vector search, hybrid search, or dense retrieval pipelines.
- Investigating RAG hallucinations or evasive "I don't know" answers when documentation exists.
- Evaluating changes to chunk size, chunk overlap, embedding models, or re-ranking algorithms.
- Establishing automated CI/CD quality gates for enterprise search and RAG knowledge bases.

## When NOT to Use

- Pure generative style or tone evaluation (use `llm-output-quality-evaluation`).
- Vector database infrastructure scaling or cluster sharding (use `vector-database-performance-tuning`).

## Inputs & Prerequisites

- Ground-truth evaluation dataset containing: `query`, `ground_truth_context_ids`, and optional `ideal_answer`.
- Access to the retrieval function or vector search API endpoint.
- Python environment with NumPy or evaluation libraries (e.g. Ragas / TruLens).

## Core Workflow

### 1. Metric Selection & Target Thresholds
Establish core retrieval metrics:
- **Recall@K**: Proportion of relevant documents retrieved in top $K$ results (target: $\ge 0.85$ at $K=5$).
- **Precision@K**: Proportion of top $K$ retrieved documents that are actually relevant.
- **MRR (Mean Reciprocal Rank)**: Evaluates whether the primary correct document ranks at position 1.
- **NDCG@K**: Evaluates ranked order with graded relevance.
- **Context Relevance**: Measures the percentage of retrieved sentences that directly answer the query.

### 2. Retrieval Evaluation Execution
Run the evaluation test harness over the benchmark dataset:
```python
def evaluate_retrieval(query, retrieved_ids, ground_truth_ids, k=5):
    top_k = retrieved_ids[:k]
    relevant_retrieved = set(top_k).intersection(set(ground_truth_ids))
    recall = len(relevant_retrieved) / max(1, len(ground_truth_ids))
    precision = len(relevant_retrieved) / k
    reciprocal_rank = 0.0
    for idx, doc_id in enumerate(top_k):
        if doc_id in ground_truth_ids:
            reciprocal_rank = 1.0 / (idx + 1)
            break
    return {"recall@k": recall, "precision@k": precision, "mrr": reciprocal_rank}
```

### 3. Failure Mode Diagnosis
Categorize retrieval errors:
1. **Vocabulary Mismatch**: Query uses domain synonyms not captured in dense embeddings (Solution: Add BM25 hybrid search).
2. **Chunk Boundary Truncation**: Answer spans multiple chunks split by rigid character limits (Solution: Implement sentence-aware or semantic chunking with 20% overlap).
3. **Embedding Compression Loss**: Embedding fails to capture fine-grained numeric or entity details (Solution: Add metadata filtering or reciprocal rank fusion).
4. **Distractor Interference**: High similarity chunks containing outdated or conflicting policies rank above current data (Solution: Temporal decay weighting or reranking with cross-encoders).

### 4. Remediation & Tuning Plan
Execute step-by-step optimization:
- If Recall@5 < 0.70: Implement hybrid search (Dense vector + BM25 keyword).
- If Precision@5 < 0.50: Introduce a cross-encoder re-ranker (e.g. BGE-Reranker or Cohere Rerank) to filter noise.
- Re-run benchmark to verify metric improvement.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Synthetic test data generation needed | Use an LLM to generate diverse user queries (paraphrased, noisy, entity-specific) from raw source documents with labeled ground-truth chunks. |
| High retrieval latency | Limit cross-encoder reranking to top-20 retrieved candidates, returning top-5 to context window. |
| Mixed language queries | Evaluate cross-lingual embedding models (e.g. multilingual-e5) and inspect language identification steps. |

## Validation & Acceptance Criteria

- [ ] Benchmark test suite executed over at least 50 representative domain queries.
- [ ] Recall@K, Precision@K, and MRR quantified and logged.
- [ ] Failure analysis identifies root cause for every query scoring Recall < 0.50.
- [ ] Post-tuning benchmark proves measurable improvement over baseline.

## Failure Handling & Recovery

- If vector database connection drops during batch evaluation, checkpoint results after every 10 queries and resume automatically.

## Expected Output & Artifacts

- Evaluation scorecard report (`docs/rag-retrieval-benchmark.md`).
- Metric summary JSON (`metrics/retrieval-eval-results.json`).

## Related Skills

- `context-window-engineering`
- `llm-cost-and-latency-optimization`
- `model-evaluation-and-benchmarking`
