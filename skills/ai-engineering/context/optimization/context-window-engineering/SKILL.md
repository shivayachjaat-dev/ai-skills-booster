---
name: context-window-engineering
description: "Use this skill when managing, structuring, and compressing context windows for LLMs and autonomous agents. It enforces prompt caching alignment, 'lost in the middle' attention optimization, dynamic token budget allocation, semantic pruning, and multi-turn message compaction to maximize reasoning accuracy while minimizing latency and token costs."
domain: ai-engineering
category: context
subcategory: optimization
tags:
  - context-window
  - prompt-engineering
  - prompt-caching
  - token-optimization
  - ai-engineering
technologies:
  - Python
  - Anthropic Prompt Caching
  - OpenAI
  - Tiktoken
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.9
---
# Context Window Engineering

## Overview

Context Window Engineering is the discipline of structuring, budgeting, and pruning the token stream presented to large language models. It maximizes reasoning accuracy, prevents "lost in the middle" attention degradation, minimizes time-to-first-token (TTFT), and slashes operational API costs by up to 90% through prompt caching alignment.

## When to Use

- Agents operate on large codebases where reading entire directories causes context overflow or budget exhaustion.
- Multi-turn conversational sessions slow down and become expensive as conversation history grows.
- LLM exhibits "needle-in-a-haystack" failure, ignoring instructions placed in the middle of large context blocks.
- Structuring prompts to take full advantage of Anthropic/OpenAI prompt caching.

## When NOT to Use

- Trivial, single-sentence completions with < 500 total tokens.
- Permanent disk storage optimization (use database indexing).

## Inputs & Prerequisites

- Token counter library (e.g. `tiktoken` for OpenAI models, Anthropic token count utilities).
- Target LLM context limit (e.g. 128k, 200k, 1M tokens) and target token budget per turn.

## Core Workflow

### 1. Token Budget Allocation
Establish an explicit token distribution model before sending queries:
```text
Total Budget: 64,000 tokens
├── Fixed System Instructions:      2,000 tokens (Cached)
├── Repository Architecture Map:    4,000 tokens (Cached)
├── Retrieved RAG Chunks / Code:   40,000 tokens (Dynamic)
├── Multi-Turn Chat History:       10,000 tokens (Rolling window)
└── Output Generation Headroom:     8,000 tokens (Reserved)
```

### 2. Prompt Caching Alignment
Position static, invariant content at the top of the prompt stream to enable hardware KV-cache reuse:
1. **Cache Layer 1 (Static)**: System role, permanent behavioral guidelines, tool definitions.
2. **Cache Layer 2 (Semi-static)**: Core codebase structure, database schemas, API specs.
3. **Dynamic Layer (Volatile)**: Current user query, dynamic tool outputs, recent conversational turns.
> Never interleave timestamps or dynamic session IDs before cached prefix blocks, as even a 1-character difference breaks cache reuse.

### 3. Mitigating "Lost in the Middle" Degradation
LLM attention weights are highest at the very beginning and very end of the prompt:
- Place primary instructions and system constraints at the top.
- Place retrieved reference documents and data in the center.
- Place the exact user question and specific output format rules at the very end of the prompt (the recency bias zone).

### 4. Semantic Context Pruning & Compaction
When conversation history approaches 70% of available budget:
1. **Summarize Older Turns**: Compress turns 1 through $N-4$ into a concise markdown bullet summary of decisions made.
2. **Retain Immediate Turns**: Preserve the last 4 turns verbatim to maintain natural dialogue continuity.
3. **Strip Intermediate Tool Output**: Replace verbose intermediate tool results (e.g. 500 lines of raw compiler logs) with a 2-line summary of outcome.

### 5. Monitoring & Cost Accounting
Log prompt cache hit rates and token efficiency metrics:
```python
cache_read_tokens = response.usage.get("cache_read_input_tokens", 0)
cache_write_tokens = response.usage.get("cache_creation_input_tokens", 0)
print(f"Cache Efficiency: {cache_read_tokens / (cache_read_tokens + cache_write_tokens):.1%}")
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Large file (> 5,000 lines) needs analysis | Do not dump the entire file. Use AST parsing to extract class and function signatures first, reading function bodies only on demand. |
| Multiple documents retrieved via RAG | Sort retrieved chunks by relevance score in ascending order (most relevant chunk placed last, immediately before user query). |
| Dynamic tool execution history | Compact tool output strings before appending to history (truncate arrays after 10 elements with `... [X items omitted]`). |

## Validation & Acceptance Criteria

- [ ] Static prompt prefixes maintain strict byte-for-byte consistency across turns.
- [ ] Prompt cache hit rate exceeds 80% on multi-turn agent interactions.
- [ ] Total input tokens remain within allocated budget without truncation errors.
- [ ] Critical instructions placed at prompt extremities to prevent attention loss.

## Failure Handling & Recovery

- If context limit is exceeded, automatically trigger urgent compaction, dropping older file reads before terminating the conversation.

## Expected Output & Artifacts

- Token-optimized prompt templates with caching breakpoints.
- Context pruning utilities and compaction logs.

## Related Skills

- `agent-project-memory`
- `rag-retrieval-evaluation`
- `llm-cost-and-latency-optimization`
