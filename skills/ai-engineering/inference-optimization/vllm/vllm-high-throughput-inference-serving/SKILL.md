---
name: vllm-high-throughput-inference-serving
description: "Use this skill when architecting, configuring, and deploying high-throughput LLM serving infrastructure using vLLM. It guides the agent through PagedAttention memory management, continuous dynamic batching, tensor parallelism for multi-GPU distribution, prefix caching for long prompts, and hosting OpenAI-compatible API servers."
domain: ai-engineering
category: inference-optimization
subcategory: vllm
tags:
  - vllm
  - llm-serving
  - inference
  - paged-attention
  - gpu
  - ai-infrastructure
technologies:
  - vLLM
  - PyTorch
  - CUDA
  - TensorRT
  - FastAPI
  - Ray
complexity: advanced
maturity: stable
tools:
  - vllm
  - curl
  - nvidia-smi
dependencies:
  - vllm >= 0.4.0
  - torch >= 2.1.0
---
# vLLM High-Throughput Inference Serving Architecture

## Overview

A definitive production engineering reference for hosting open-source foundation models with maximum tokens-per-second throughput using vLLM. Powered by PagedAttention (managing KV-cache memory like virtual memory pages in operating systems), this skill instructs AI agents on optimizing continuous dynamic batching, distributing models across multi-GPU nodes with tensor parallelism, activating prefix caching, and operating production OpenAI-compatible endpoints.

## When to Use

- Serving open-source LLMs (Llama 3, Mistral, Qwen, DeepSeek) for production API traffic with low latency.
- Maximizing GPU hardware utilization (achieving 2x-4x higher throughput than HuggingFace TGI or Ollama).
- Distributing large models (70B+) across multiple GPUs using Tensor Parallelism.
- Serving high-context workloads (RAG systems, document summarization) where Prefix Caching drastically reduces redundant compute.

## When NOT to Use

- Lightweight CPU-only embedded inference on edge devices (use llama.cpp or ONNX Runtime).
- Training or fine-tuning models (use `llm-lora-fine-tuning-pipeline`).

## Inputs & Prerequisites

- NVIDIA GPUs (Ampere A10/A100, Ada Lovelace L40/RTX 4090, or Hopper H100) with CUDA 12+.
- Python 3.10+ with `vllm >= 0.4.0` installed.
- HuggingFace access token for gated models (Meta-Llama-3).

## Core Workflow

### 1. Launching OpenAI-Compatible Server with Multi-GPU Tensor Parallelism
Launch vLLM server distributed across 2 GPUs with prefix caching enabled:

```bash
python3 -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Meta-Llama-3-8B-Instruct \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192 \
    --enable-prefix-caching \
    --port 8000 \
    --host 0.0.0.0
```

### 2. High-Performance Programmatic Inference in Python
Execute high-throughput batch inference directly using the `LLM` engine:

```python
from vllm import LLM, SamplingParams

# Configure sampling parameters
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=256,
    stop=["<|eot_id|>"]
)

# Initialize engine with PagedAttention and FP16/BF16
llm = LLM(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.85,
    max_model_len=4096,
    trust_remote_code=True
)

prompts = [
    "Explain quantum computing in three sentences.",
    "Write a Python function to compute Fibonacci numbers efficiently.",
    "What are the primary differences between TCP and UDP?"
]

# Generates completions using continuous dynamic batching
outputs = llm.generate(prompts, sampling_params)

for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(f"PROMPT: {prompt}\nREPLY: {generated_text}\n" + "-"*50)
```

### 3. Asynchronous Streaming Client (OpenAI SDK Compatible)
Stream completions from the vLLM server with sub-second Time to First Token (TTFT):

```python
from openai import AsyncOpenAI
import asyncio

client = AsyncOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

async def stream_completion():
    stream = await client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        messages=[{"role": "user", "content": "Explain raft consensus in 100 words."}],
        stream=True,
        temperature=0.2
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)

asyncio.run(stream_completion())
```

## Best Practices & Failure Modes

1. **GPU Out of Memory on KV-Cache Allocation**: Setting `--gpu-memory-utilization` too high (e.g. 0.98) leaves insufficient memory for temporary PyTorch workspace buffers during CUDA graph capture, causing crashes at startup. Set between 0.85 and 0.92.
2. **Context Length Mismatch**: If `--max-model-len` is set higher than the model's native rotary position embedding (RoPE) window without configuring yarn/rope scaling, model output degrades into gibberish.
3. **Prefix Caching Invalidation**: Prefix caching relies on exact token prefixes. Ensure system prompts are identical across requests (including whitespace and formatting) to benefit from cache hits.

## Verification & Testing

- Check server health endpoint:
  ```bash
  curl -i http://localhost:8000/health
  ```
- Benchmark tokens-per-second performance using vLLM benchmark tool:
  ```bash
  python3 -m vllm.entrypoints.benchmark_throughput \
      --model meta-llama/Meta-Llama-3-8B-Instruct \
      --dataset ShareGPT_V3_unfiltered_cleaned_split.json \
      --num-prompts 500
  ```
