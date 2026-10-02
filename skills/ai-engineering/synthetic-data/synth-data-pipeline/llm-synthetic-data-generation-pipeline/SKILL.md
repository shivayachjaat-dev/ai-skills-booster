---
name: llm-synthetic-data-generation-pipeline
description: "Use this skill when designing, orchestrating, and validating synthetic data generation pipelines for training, evaluating, and fine-tuning Large Language Models. It covers Self-Instruct seed bootstrapping, Evol-Instruct complexity expansion (in-breadth and in-depth), vector embedding semantic deduplication, and automated quality filtering using frontier LLM judges."
domain: ai-engineering
category: synthetic-data
subcategory: synth-data-pipeline
tags:
  - synthetic-data
  - self-instruct
  - evol-instruct
  - llm-training
  - fine-tuning
  - ai-data
technologies:
  - Python
  - HuggingFace Datasets
  - SentenceTransformers
  - OpenAI
  - Anthropic
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - datasets >= 2.14.0
  - sentence-transformers >= 2.2.0
---
# LLM Synthetic Data Generation & Evol-Instruct Pipeline

## Overview

A definitive production engineering reference for generating high-quality, diverse synthetic datasets to fine-tune and evaluate Large Language Models. Relying solely on scarce human annotations limits dataset scale. This skill instructs AI agents on implementing the Self-Instruct and Evol-Instruct methodologies: bootstrapping from verified seed tasks, dynamically increasing prompt complexity (in-depth reasoning, constraints, edge cases), deduplicating samples using vector embeddings, and filtering low-quality generations with LLM judges.

## When to Use

- Generating tens of thousands of instruction-tuning or multi-turn conversational samples for domain-specific fine-tuning (legal, medical, financial, coding).
- Augmenting sparse datasets with adversarial edge cases and complex constraint reasoning.
- Creating benchmark evaluation sets where real-world private user data cannot be exposed.
- Distilling reasoning capabilities from massive frontier models into efficient 7B/8B models.

## When NOT to Use

- Factual domain knowledge generation without source ground truth documents (causes hallucinated data).
- Simple data augmentation (synonym replacement, back-translation) where traditional NLP tools suffice.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Seed dataset (50 to 100 high-quality, human-curated instruction-response examples).
- Frontier LLM API access (e.g. Claude 3.5 Sonnet, GPT-4o) for generation and filtering.

## Core Workflow

### 1. Evol-Instruct Complexity Expansion Engine
Mutate seed instructions into significantly more complex tasks:

```python
import random

EVOL_PROMPTS = {
    "add_constraints": (
        "I want you to act as an Instruction Rewriter.\n"
        "Your task is to add 2-3 specific constraints, edge cases, or requirements to the given prompt, "
        "making it harder to solve without changing the core domain.\n"
        "Original Prompt: {prompt}\nRewritten Prompt:"
    ),
    "deepen_reasoning": (
        "I want you to act as an Instruction Rewriter.\n"
        "Rewrite the prompt so that answering it requires multi-step deduction, chain-of-thought analysis, "
        "or contrasting conflicting perspectives.\n"
        "Original Prompt: {prompt}\nRewritten Prompt:"
    ),
    "concretize": (
        "I want you to act as an Instruction Rewriter.\n"
        "Replace general statements in the prompt with concrete, realistic technical scenarios, including "
        "specific mock data, code snippets, or error traces.\n"
        "Original Prompt: {prompt}\nRewritten Prompt:"
    )
}

def evolve_instruction(llm_client, original_prompt: str) -> str:
    strategy = random.choice(list(EVOL_PROMPTS.keys()))
    meta_prompt = EVOL_PROMPTS[strategy].format(prompt=original_prompt)
    
    # Generate evolved instruction
    evolved = llm_client.generate(meta_prompt, temperature=0.7)
    return evolved.strip()
```

### 2. Semantic Deduplication via Vector Embeddings
Eliminate repetitive synthetic samples using cosine similarity clustering:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

def deduplicate_prompts(prompts: list[str], similarity_threshold: float = 0.85) -> list[str]:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(prompts, normalize_embeddings=True, show_progress_bar=False)

    unique_prompts = []
    unique_indices = []

    for i, emb in enumerate(embeddings):
        if not unique_indices:
            unique_indices.append(i)
            unique_prompts.append(prompts[i])
            continue

        # Compute cosine similarity against all accepted unique embeddings
        sims = np.dot(embeddings[unique_indices], emb)
        if np.max(sims) < similarity_threshold:
            unique_indices.append(i)
            unique_prompts.append(prompts[i])

    return unique_prompts
```

### 3. Automated Quality & Safety Verification Filter
Evaluate generated responses with an LLM judge before accepting into final training corpus:

```python
def verify_sample_quality(llm_judge, instruction: str, response: str) -> bool:
    judge_prompt = f"""
    You are an expert data quality auditor. Evaluate this synthetic instruction-response pair:
    [Instruction]: {instruction}
    [Response]: {response}

    Criteria:
    1. Does the response directly and comprehensively fulfill the instruction?
    2. Is the response factually sound and free of hallucinations?
    3. Is the formatting clean and devoid of AI conversational filler (e.g. "Certainly! Here is...")?

    Reply ONLY with 'PASS' if all criteria are satisfied, or 'FAIL' followed by a 1-sentence reason.
    """
    verdict = llm_judge.generate(judge_prompt, temperature=0.0).strip()
    return verdict.startswith("PASS")
```

## Best Practices & Failure Modes

1. **Model Self-Collapse & Homogenization**: Generating synthetic data without strict diversity mechanisms leads to repetitive sentence structures and monotonous vocabulary. Always use embedding deduplication and multi-strategy Evol-Instruct prompts.
2. **Hallucination Amplification**: Generating synthetic data about obscure factual entities without retrieval grounding bakes model hallucinations permanently into training weights. Always ground factual dataset generation with verified source texts.
3. **Conversational Artifact Bleed**: Synthetic assistant responses frequently include phrases like "As an AI, I cannot..." or "Sure, I'd be happy to help!". Strip system conversational preamble using regex before packaging datasets.

## Verification & Testing

- Verify dataset balance and distribution across token lengths:
  ```python
  from datasets import Dataset
  ds = Dataset.from_list([{"prompt": p, "response": r} for p, r in generated_pairs])
  print(ds)
  # Inspect token length histogram
  ```
- Test embedding deduplication efficiency:
  ```python
  samples = [
      "How do I sort a list in Python?",
      "In Python, what is the best way to sort a list?", # Semantic duplicate
      "How do I invert a binary tree in Go?"
  ]
  deduped = deduplicate_prompts(samples, similarity_threshold=0.80)
  assert len(deduped) == 2
  ```
