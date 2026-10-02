---
name: ragas-rag-triad-evaluation
description: "Use this skill when evaluating, benchmarking, and auditing Retrieval-Augmented Generation (RAG) pipelines using RAGAS and the RAG Triad framework. It guides the agent through calculating Faithfulness (hallucination detection), Answer Relevance, Context Precision, and Context Recall, building synthetic evaluation datasets, and CI automated regression gating."
domain: ai-engineering
category: evaluation
subcategory: ragas-rag-evaluation
tags:
  - rag
  - evaluation
  - ragas
  - llm-evaluation
  - faithfulness
  - benchmarking
technologies:
  - Ragas
  - LangChain
  - OpenAI
  - LlamaIndex
  - HuggingFace
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - ragas >= 0.1.0
  - datasets >= 2.14.0
---
# RAGAS & RAG Triad Automated Evaluation Framework

## Overview

A production engineering standard for objectively scoring and regression-testing Retrieval-Augmented Generation (RAG) pipelines. This skill instructs AI agents on implementing the RAG Triad evaluation methodology using RAGAS: quantifying Faithfulness (measuring hallucinations against retrieved context), Answer Relevance (checking query-answer alignment), Context Precision (assessing retrieval ranking), and Context Recall (measuring coverage against ground truth).

## When to Use

- Quantifying whether an updated embedding model, chunking size, or prompt template improved RAG answer quality.
- Detecting LLM hallucinations where the generated answer makes claims not substantiated by retrieved context.
- Running automated CI/CD regression gates before deploying new knowledge base indices.
- Benchmarking competing vector databases or retrieval algorithms (Dense vs Hybrid vs Re-ranking).

## When NOT to Use

- Non-RAG LLM evaluation tasks like code synthesis correctness (use unit test execution) or classification accuracy (use standard F1/Precision/Recall).
- Real-time latency evaluation of streaming APIs.

## Inputs & Prerequisites

- Python 3.10+ environment.
- Evaluation dataset containing: `question`, `contexts` (list of retrieved chunks), `answer` (generated response), and optional `ground_truth`.
- Evaluator LLM API access (e.g., GPT-4o or Claude 3.5 Sonnet for judge scoring).

## Core Workflow

### 1. The RAG Triad Metrics
Evaluate the three core relationships:
1. **Context Relevance / Precision**: Is retrieved context relevant to the question?
2. **Groundedness / Faithfulness**: Is the answer derived strictly from the context?
3. **Answer Relevance**: Does the answer directly answer the user's question?

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)

def run_rag_triad_evaluation(test_samples: list) -> dict:
    """
    test_samples format:
    [
        {
            "question": "What is the return policy for damaged electronics?",
            "contexts": [
                "Damaged electronics must be reported within 14 days of delivery for a full refund."
            ],
            "answer": "You must report damaged electronics within 14 days to receive a full refund.",
            "ground_truth": "Customers have 14 days from delivery to report damaged electronics for a full refund."
        }
    ]
    """
    
    # Format into HuggingFace Dataset
    dataset = Dataset.from_list(test_samples)

    # Execute RAGAS evaluation
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall
        ]
    )

    return results
```

### 2. CI/CD Quality Gate Script
Fail pipeline builds if faithfulness drops below threshold:

```python
import sys
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from datasets import Dataset

MIN_FAITHFULNESS_THRESHOLD = 0.85
MIN_RELEVANCY_THRESHOLD = 0.80

def enforce_quality_gate(eval_dataset: Dataset):
    scores = evaluate(eval_dataset, metrics=[faithfulness, answer_relevancy])
    df = scores.to_pandas()
    
    avg_faithfulness = df["faithfulness"].mean()
    avg_relevancy = df["answer_relevancy"].mean()

    print(f"Evaluation Results:")
    print(f"  Faithfulness: {avg_faithfulness:.4f} (Threshold: {MIN_FAITHFULNESS_THRESHOLD})")
    print(f"  Answer Relevancy: {avg_relevancy:.4f} (Threshold: {MIN_RELEVANCY_THRESHOLD})")

    failed = False
    if avg_faithfulness < MIN_FAITHFULNESS_THRESHOLD:
        print("[FAIL] Faithfulness is below acceptable safety threshold!")
        failed = True
    if avg_relevancy < MIN_RELEVANCY_THRESHOLD:
        print("[FAIL] Answer Relevancy is below threshold!")
        failed = True

    if failed:
        sys.exit(1)
    print("[PASS] RAG Quality Gate passed successfully.")
```

### 3. Diagnosing Failure Modes from Metric Scores
- **Low Faithfulness (< 0.70)**: The generator is hallucinating facts not in context. *Remedy*: Tighten system prompt ("Answer ONLY using provided context"), lower temperature to 0.0.
- **Low Context Precision (< 0.60)**: Irrelevant chunks are ranked higher than relevant chunks. *Remedy*: Integrate a cross-encoder re-ranker (Cohere Re-rank, BGE-Reranker) before prompt assembly.
- **Low Context Recall (< 0.60)**: Retrieval failed to find all facts necessary to answer ground truth. *Remedy*: Increase top-k chunks, implement hybrid dense + sparse retrieval, or reduce chunk size.

## Best Practices & Failure Modes

1. **Judge Model Bias**: Using weak judge models (e.g. 7B parameter models) produces inconsistent, noisy evaluation scores. Always use strong frontier models (GPT-4o, Claude 3.5 Sonnet) as the judge evaluator.
2. **Leakage in Ground Truth Generation**: Generating synthetic questions directly from chunk text without adversarial filtering yields unrealistically high recall scores. Include negative samples (questions where answers are not in the context).
3. **Missing Token Truncation Checks**: If retrieved chunks exceed judge model context length, chunks get silently truncated, leading to artificially low faithfulness scores.

## Verification & Testing

- Execute quick benchmark run with test data:
  ```python
  test_data = [{
      "question": "What is the capital of France?",
      "contexts": ["Paris is the capital and most populous city of France."],
      "answer": "The capital of France is Paris.",
      "ground_truth": "Paris is France's capital."
  }]
  result = run_rag_triad_evaluation(test_data)
  assert result["faithfulness"] > 0.9
  assert result["answer_relevancy"] > 0.9
  ```
