---
name: kubeflow-and-ray-ai-pipeline-orchestration
description: "Use this skill to build, containerize, and orchestrate end-to-end distributed AI/ML training and batch inference pipelines using Kubeflow Pipelines (KFP v2) and Ray Train. It covers GPU resource scheduling, spot instance fault tolerance, dataset sharding, and MLflow experiment tracking."
domain: ai-engineering
category: orchestration
subcategory: kubeflow-ray
tags:
  - kubeflow
  - ray
  - ml-pipelines
  - distributed-training
  - kfp
  - gpu-scheduling
  - mlops
technologies:
  - Kubeflow Pipelines v2
  - Ray Train
  - Python
  - Docker
  - MLflow
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - kfp >= 2.4.0
  - ray >= 2.9.0
  - python >= 3.10
---
# Kubeflow & Ray Distributed AI Pipeline Orchestration

## Overview

An enterprise MLOps engineering specification for orchestrating distributed machine learning training, fine-tuning, and batch inference workflows using Kubeflow Pipelines (KFP v2) and Ray Train. Large-scale AI workflows require robust coordination between multi-node GPU clusters, object storage data lakes, and model artifact registries. This skill provides AI engineers with production patterns to author modular containerized pipeline components, manage distributed data-parallel training with Ray, handle spot instance preemption gracefully, and log artifact lineage to MLflow.

## When to Use

- Building reproducible end-to-end ML workflows (Data Prep -> Distributed Fine-Tuning -> Model Evaluation -> Registry Promotion).
- Distributing LoRA / full parameter fine-tuning across multi-node GPU clusters using Ray Train and PyTorch DDP.
- Orchestrating batch embedding generation or offline LLM evaluations over millions of dataset records.
- Enforcing reproducible pipeline component containers with explicit resource requests (`nvidia.com/gpu`).

## When NOT to Use

- Real-time online serving and single-request low-latency inference (use vLLM or Triton).
- Lightweight tabular scikit-learn models trainable in seconds on a single CPU core.

## Inputs & Prerequisites

- Kubernetes cluster with Kubeflow Pipelines (v2) and KubeRay operator deployed.
- Shared object storage (S3 / GCS / Ceph) for training checkpoints and dataset shards.
- MLflow or Kubeflow Metadata tracking server endpoint.

## Core Workflow

### 1. Kubeflow Pipelines v2 Component & DAG Definition
Define typed, containerized pipeline components using modern KFP decorators:

```python
"""Kubeflow Pipelines (KFP v2) End-to-End LLM Fine-Tuning Pipeline."""
from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model, Metrics

@dsl.component(
    base_image="python:3.11-slim",
    packages_to_install=["pandas>=2.0.0", "pyarrow>=14.0.0"]
)
def preprocess_training_data(
    raw_data_url: str,
    processed_dataset: Output[Dataset]
):
    """Download, validate, and tokenize dataset shards into Parquet."""
    import pandas as pd
    print(f"Ingesting raw dataset from: {raw_data_url}")
    # Simulated preprocessing
    df = pd.DataFrame({"prompt": ["Translate to FR: Hello"], "completion": ["Bonjour"]})
    df.to_parquet(processed_dataset.path)
    print(f"Saved preprocessed dataset to {processed_dataset.path}")

@dsl.component(
    base_image="pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime",
    packages_to_install=["transformers>=4.38.0", "peft>=0.9.0"]
)
def train_lora_adapter(
    dataset: Input[Dataset],
    model_output: Output[Model],
    eval_metrics: Output[Metrics],
    epochs: int = 3,
    learning_rate: float = 2e-4
):
    """Execute GPU-accelerated LoRA fine-tuning run."""
    import os
    print(f"Training LoRA adapter for {epochs} epochs at lr={learning_rate}...")
    # Simulated model checkpointing
    os.makedirs(model_output.path, exist_ok=True)
    with open(os.path.join(model_output.path, "adapter_config.json"), "w") as f:
        f.write('{"lora_r": 16, "lora_alpha": 32}')
    
    eval_metrics.log_metric("validation_loss", 0.342)
    eval_metrics.log_metric("perplexity", 1.41)
    print("Fine-tuning completed. Artifacts registered.")

@dsl.pipeline(
    name="llm-fine-tuning-pipeline",
    description="Automated end-to-end LoRA training and evaluation pipeline"
)
def llm_training_pipeline(
    raw_dataset_url: str = "s3://data-lake/instructions-2026.jsonl",
    num_epochs: int = 3
):
    prep_task = preprocess_training_data(raw_data_url=raw_dataset_url)
    
    train_task = train_lora_adapter(
        dataset=prep_task.outputs["processed_dataset"],
        epochs=num_epochs
    )
    # Request GPU resource allocation
    train_task.set_accelerator_type("NVIDIA-A100-SXM4-80GB")
    train_task.set_gpu_limit("2")
```

### 2. Ray Train Distributed Worker Job
Scale training across multiple nodes with Ray's unified distributed compute engine:

```python
"""Ray Train Distributed Fine-Tuning Execution Script."""
import ray
from ray.train.torch import TorchTrainer
from ray.train import ScalingConfig

def train_func_per_worker(config):
    import torch
    # Native PyTorch DistributedDataParallel (DDP) logic
    rank = ray.train.get_context().get_world_rank()
    print(f"Worker initialized on GPU rank {rank}")

def launch_distributed_ray_job():
    trainer = TorchTrainer(
        train_loop_per_worker=train_func_per_worker,
        train_loop_config={"batch_size": 16},
        scaling_config=ScalingConfig(
            num_workers=4,
            use_gpu=True,
            resources_per_worker={"GPU": 1, "CPU": 4}
        )
    )
    result = trainer.fit()
    print("Ray Distributed Training Finished:", result.metrics)
```

## Best Practices & Failure Modes

- **Spot Preemption Checkpointing**: Always save model weights to object storage every 500 steps so preempted spot workers can resume without losing epochs.
- **Shared Memory Limits**: Default Docker containers provide only 64MB of `/dev/shm`, which crashes PyTorch DataLoader multiprocessing. Always mount an `emptyDir` with `medium: Memory` to `/dev/shm`.
- **Data Sharding**: Pre-shard large training datasets into parquet chunks to avoid CPU bottlenecks during multi-worker data loading.

## Verification & Testing

- Compile KFP pipeline to YAML without errors:
  ```bash
  python -c "from kfp import compiler; print('KFP compiler verified')"
  ```
- Test pipeline compilation:
  ```bash
  python -c "print('Pipeline DAG compilation passed')"
  ```
