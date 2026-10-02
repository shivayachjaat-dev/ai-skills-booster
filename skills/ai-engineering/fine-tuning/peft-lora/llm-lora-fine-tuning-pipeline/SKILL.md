---
name: llm-lora-fine-tuning-pipeline
description: "Use this skill when designing, training, and evaluating parameter-efficient fine-tuning (PEFT) pipelines for Large Language Models using LoRA and QLoRA. It guides the agent through 4-bit/8-bit quantization via bitsandbytes, LoRA hyperparameter configuration (rank r, alpha, target modules), dataset preparation and token masking, SFTTrainer orchestration, and adapter weight merging."
domain: ai-engineering
category: fine-tuning
subcategory: peft-lora
tags:
  - fine-tuning
  - lora
  - qlora
  - peft
  - llm
  - huggingface
  - pytorch
technologies:
  - PyTorch
  - HuggingFace Transformers
  - PEFT
  - TRL
  - bitsandbytes
complexity: advanced
maturity: stable
tools:
  - python
  - accelerate
dependencies:
  - transformers >= 4.38.0
  - peft >= 0.9.0
  - trl >= 0.7.11
  - bitsandbytes >= 0.42.0
---
# LLM LoRA & QLoRA Parameter-Efficient Fine-Tuning

## Overview

A production deep-learning engineering guide for fine-tuning Large Language Models (LLMs) on consumer or enterprise GPUs using Low-Rank Adaptation (LoRA) and Quantized LoRA (QLoRA). This skill instructs AI agents on dataset formatting, BitsAndBytes 4-bit NF4 quantization, LoRA adapter configuration, gradient checkpointing, supervised fine-tuning (SFTTrainer), and adapter weight merging for deployment.

## When to Use

- Adapting open-source foundation models (Llama 3, Mistral, Qwen, Gemma) to specific domain vocabularies or structured output formats (JSON/SQL).
- Fine-tuning 7B to 70B parameter models within constrained GPU memory (e.g. single 24GB RTX 4090 or A10G).
- Maintaining multiple specialized adapters while sharing a single immutable base model in production.
- Training conversational or instruction-following models using Supervised Fine-Tuning (SFT).

## When NOT to Use

- Tasks solvable through in-context learning, prompt engineering, or RAG without model weight adjustments.
- Continual pre-training on massive raw corpora (> 100 billion tokens), where full parameter pre-training is required.

## Inputs & Prerequisites

- PyTorch 2.1+ with CUDA 12+ enabled.
- Python packages: `transformers`, `peft`, `trl`, `bitsandbytes`, `datasets`.
- Instruction-tuning dataset in JSON Lines format: `{"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}`.

## Core Workflow

### 1. QLoRA 4-bit Quantization Configuration
Configure 4-bit NormalFloat (NF4) quantization with double quantization to minimize base model footprint:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# 4-bit Quantization Configuration
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)

tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16
)
```

### 2. LoRA Adapter Hyperparameters (PEFT)
Configure low-rank matrices targeting all linear projection layers:

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Prepare model for k-bit training with gradient checkpointing
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,                           # LoRA Rank (8, 16, 32)
    lora_alpha=32,                  # Scaling parameter (typically 2 * r)
    target_modules=[                # Target all projection layers for best performance
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: ~41M || all params: ~8B || trainable%: ~0.51%
```

### 3. Supervised Fine-Tuning Execution (`TRL SFTTrainer`)
Launch training loop with memory optimization:

```python
from transformers import TrainingArguments
from trl import SFTTrainer
from datasets import load_dataset

dataset = load_dataset("json", data_files="instructions_train.jsonl", split="train")

training_args = TrainingArguments(
    output_dir="./lora-llama3-output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    optim="paged_adamw_8bit",       # Paged optimizer prevents OOM spikes
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    logging_steps=10,
    save_strategy="epoch",
    evaluation_strategy="steps",
    eval_steps=50,
    fp16=False,
    bf16=True,                      # Use bfloat16 on Ampere / Ada Lovelace / Hopper
    max_grad_norm=0.3,
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=lora_config,
    dataset_text_field="text",
    max_seq_length=2048,
    tokenizer=tokenizer,
    args=training_args
)

trainer.train()
trainer.save_model("./final-lora-adapter")
```

### 4. Adapter Merging for Low-Latency Serving
Merge the trained LoRA adapter weights directly into the base 16-bit model for standalone deployment:

```python
from peft import PeftModel

# Load unquantized base model in FP16/BF16
base_model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="cpu"
)

# Load LoRA adapter
peft_model = PeftModel.from_pretrained(base_model, "./final-lora-adapter")

# Merge adapter weights into base model layers
merged_model = peft_model.merge_and_unload()

# Save standalone model for vLLM or HuggingFace TGI inference
merged_model.save_pretrained("./merged-model-fp16")
tokenizer.save_pretrained("./merged-model-fp16")
```

## Best Practices & Failure Modes

1. **Loss of Catastrophic Forgetting**: Tuning on narrow domain data with high learning rates ruins general reasoning. Use low learning rates (`1e-4` to `2e-4`) and mix in 5-10% general instruction data (replay buffer).
2. **Prompt Loss Masking**: Ensure that loss is only calculated on assistant completion tokens, not on system prompts and user questions (Data Collator for Completion-Only LM).
3. **GPU Out of Memory (OOM)**: Always enable `gradient_checkpointing=True` and `optim="paged_adamw_8bit"`. If OOM still occurs, reduce `per_device_train_batch_size` to 1 or 2 and increase `gradient_accumulation_steps`.

## Verification & Testing

- Inspect trainable parameter count before launching:
  ```python
  model.print_trainable_parameters()
  ```
- Test inference with trained adapter:
  ```python
  from transformers import pipeline
  pipe = pipeline("text-generation", model=peft_model, tokenizer=tokenizer)
  output = pipe("Explain distributed locks in 3 bullet points:", max_new_tokens=150)
  print(output[0]["generated_text"])
  ```
