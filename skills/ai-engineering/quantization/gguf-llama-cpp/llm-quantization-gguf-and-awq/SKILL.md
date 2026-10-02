---
name: llm-quantization-gguf-and-awq
description: "Use this skill when quantizing, optimizing, and compressing Large Language Models for efficient CPU and GPU inference using GGUF (llama.cpp) and AWQ (Activation-aware Weight Quantization). It guides the agent through GGUF k-quant selection (Q4_K_M vs Q5_K_M vs Q8_0), AWQ 4-bit tensor calibration, perplexity evaluation against WikiText-2, and benchmark testing."
domain: ai-engineering
category: quantization
subcategory: gguf-llama-cpp
tags:
  - quantization
  - gguf
  - llama-cpp
  - awq
  - llm-compression
  - ai-engineering
technologies:
  - llama.cpp
  - AutoAWQ
  - GGUF
  - PyTorch
  - HuggingFace
complexity: advanced
maturity: stable
tools:
  - llama.cpp
  - python
dependencies:
  - autoawq >= 0.2.0
  - torch >= 2.1.0
---
# LLM Quantization: GGUF & AWQ Production Compression

## Overview

A definitive deep-learning engineering guide for compressing Large Language Models from 16-bit floating point down to 4-bit integers while preserving model reasoning quality. This skill instructs AI agents on two complementary industry standards: GGUF format quantization via `llama.cpp` for CPU/edge and hybrid GPU execution, and AWQ (Activation-aware Weight Quantization) for high-throughput GPU serving in vLLM. It covers k-quant selection, activation calibration, and perplexity degradation benchmarking.

## When to Use

- Compressing 8B, 14B, or 70B parameter models to fit inside constrained GPU VRAM (e.g. running 70B on 48GB VRAM).
- Packaging models into single GGUF binaries for local deployment on laptops, embedded devices, or CPU servers via llama.cpp / Ollama.
- Achieving 3x higher inference speed with less than 1% perplexity degradation.
- Calibrating 4-bit weights specifically protecting salient outlier weights using AWQ.

## When NOT to Use

- High-precision medical or numerical reasoning tasks where any loss in numerical precision is intolerable (use FP16 or BF16).
- Model training or active fine-tuning (use QLoRA during training; quantize weights after merging).

## Inputs & Prerequisites

- Python 3.10+ with `torch` and `autoawq` installed.
- `llama.cpp` compiled from source (`make` or `cmake -B build`).
- Unquantized 16-bit base model checkpoint (HuggingFace format).

## Core Workflow

### 1. GGUF Quantization Pipeline (llama.cpp)
Convert HuggingFace weights into GGUF format and apply optimal k-quants:

```bash
# Step 1: Convert HuggingFace checkpoint to full-precision GGUF (FP16)
python3 llama.cpp/convert_hf_to_gguf.py ./models/Meta-Llama-3-8B-Instruct \
    --outfile ./models/llama-3-8b-fp16.gguf \
    --outtype f16

# Step 2: Apply Q4_K_M (Medium 4-bit K-quant: uses Q6_K for attention layers, Q4_K for MLP)
# Offers the best balance between compression and reasoning preservation
./llama.cpp/llama-quantize \
    ./models/llama-3-8b-fp16.gguf \
    ./models/llama-3-8b-Q4_K_M.gguf \
    Q4_K_M

# Step 3: (Optional) Apply Q5_K_M for near-zero perplexity loss (< 0.05 increase)
./llama.cpp/llama-quantize \
    ./models/llama-3-8b-fp16.gguf \
    ./models/llama-3-8b-Q5_K_M.gguf \
    Q5_K_M
```

### 2. AWQ 4-bit GPU Quantization Pipeline (`AutoAWQ`)
Perform activation-aware weight quantization using calibration data:

```python
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_path = "./models/Meta-Llama-3-8B-Instruct"
quant_path = "./models/Meta-Llama-3-8B-Instruct-AWQ"

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM" # Optimized for NVIDIA Tensor Cores
}

# 1. Load Model & Tokenizer
model = AutoAWQForCausalLM.from_pretrained(model_path, **{"low_cpu_mem_usage": True})
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# 2. Quantize with calibration dataset
model.quantize(tokenizer, quant_config=quant_config)

# 3. Save quantized weights ready for vLLM inference
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
print(f"AWQ quantization complete. Model saved to {quant_path}")
```

### 3. Measuring Perplexity Degradation on WikiText-2
Validate that quantization did not degrade model language modeling capabilities:

```bash
# Compute perplexity using llama.cpp perplexity benchmark tool
./llama.cpp/llama-perplexity \
    -m ./models/llama-3-8b-Q4_K_M.gguf \
    -f ./data/wikitext-2-raw/wiki.test.raw \
    --chunks 50
# Target: Perplexity delta between FP16 and Q4_K_M should be < 0.15
```

## Best Practices & Failure Modes

1. **Using Legacy Q4_0 Instead of K-Quants**: Plain `Q4_0` quantizes all layers uniformly, destroying reasoning quality. Always use `Q4_K_M` or `Q5_K_M`, which selectively keep critical attention weight tensors at higher precision (6-bit).
2. **Calibration Dataset Bias in AWQ**: Running AWQ calibration on synthetic gibberish or mismatched languages damages activation distributions. Use representative, clean conversational data (e.g. ShareGPT or WikiText) for calibration.
3. **RAM Exhaustion during Conversion**: Converting 70B models requires significant system RAM. Use `--outtype f16` and ensure swap space or high-memory instances (> 128GB RAM) are used during the initial GGUF conversion stage.

## Verification & Testing

- Test local interactive execution via llama-cli:
  ```bash
  ./llama.cpp/llama-cli -m ./models/llama-3-8b-Q4_K_M.gguf -p "Explain gravity in one sentence:" -n 64
  ```
- Verify AWQ model serving in vLLM:
  ```bash
  python3 -m vllm.entrypoints.openai.api_server \
      --model ./models/Meta-Llama-3-8B-Instruct-AWQ \
      --quantization awq
  ```
