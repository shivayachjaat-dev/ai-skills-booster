---
name: ai-ml
description: "Use this skill to architect, orchestrate, and operationalize enterprise AI and Machine Learning systems across the full lifecycle—from data pipeline ingestion, feature stores, and model training/fine-tuning to LLM serving, RAG orchestration, evaluation benchmarks, and MLOps observability."
domain: ai-engineering
category: models
subcategory: ai_ml
tags:
  - ai-engineering
  - machine-learning
  - mlops
  - model-serving
  - feature-store
  - model-evaluation
  - model-drift
technologies:
  - Python
  - PyTorch
  - Scikit-Learn
  - MLflow
  - ONNX
  - Pandas
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

# Production AI & Machine Learning Lifecycle Architecture (MLOps Standard)

## Overview

The `ai-ml` skill defines the architectural standards, verification gates, and deployment patterns for enterprise machine learning and artificial intelligence systems. Bridging the gap between empirical experimentation and mission-critical production requires continuous data drift auditing, rigorous offline/online evaluation metrics, reproducible artifact registries, low-latency inference runtimes, and automated rollback triggers. This skill equips autonomous agents and systems engineers to develop, validate, and manage robust ML/AI pipelines.

```
+-----------------------------------------------------------------------------------+
|                     Enterprise AI / ML Operational Pipeline                       |
|                                                                                   |
|  [ Ingestion & Feature Store ]                                                    |
|            |                                                                      |
|            v                                                                      |
|  [ Training & Fine-Tuning Pipeline ]                                              |
|            |                                                                      |
|            v                                                                      |
|  [ Model Evaluation & Safety Gate ] <--- Precision/Recall, Latency p95, Bias      |
|            |                                                                      |
|            v                                                                      |
|  [ Model Registry & Artifact Packaging ] (ONNX, PyTorch JIT, SafeTensors)         |
|            |                                                                      |
|            v                                                                      |
|  [ High-Performance Serving ] (Triton / vLLM / TensorRT-LLM)                      |
|            |                                                                      |
|            v                                                                      |
|  [ Production Telemetry & Drift Detection ]                                       |
|      - Population Stability Index (PSI > 0.20 -> Trigger Retraining)              |
|      - Latency p99 SLA Watchdog                                                   |
+-----------------------------------------------------------------------------------+
```

---

## When to Use

- When architecting or refactoring end-to-end Machine Learning pipelines or Foundation Model inference services.
- When establishing automated model evaluation gates (calculating F1, AUC, Latency p95/p99) prior to staging deployment.
- When implementing data distribution drift monitors (e.g. Population Stability Index or Kolmogorov-Smirnov tests) to detect covariate shift.
- When structuring model metadata, lineage tracking, and artifact serialization.

## When NOT to Use

- For simple deterministic heuristic rules that do not involve probabilistic modeling, embeddings, or neural inference.
- Unstructured exploratory data analysis that lacks repeatable pipeline artifacts or productionization goals.
- Manual one-off spreadsheet calculations.

---

## Inputs & Prerequisites

1. **Training / Reference Dataset Distribution**: Baseline statistical feature distributions and target labels.
2. **Production Inference Sample Stream**: Monitored runtime inputs and predicted outputs.
3. **Model Artifact**: Serialized model graph (ONNX, PyTorch `.pt`, Hugging Face SafeTensors).
4. **Performance & Drift SLAs**: Maximum allowable latency (p95), minimum acceptable Macro F1, and drift thresholds (PSI $\le 0.10$).

---

## Core Workflow

### Step 1: Automated Model Evaluation Metrics
Compute classification performance and latency percentiles to determine if a candidate model satisfies release gates:

```python
import numpy as np
from typing import Dict, List, Any

def evaluate_classification_performance(
    y_true: List[int],
    y_pred: List[int]
) -> Dict[str, float]:
    """Calculates accuracy, precision, recall, and macro F1 score."""
    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    
    accuracy = float(np.mean(y_true_arr == y_pred_arr))
    classes = np.unique(np.concatenate([y_true_arr, y_pred_arr]))
    
    f1_scores = []
    for c in classes:
        tp = np.sum((y_pred_arr == c) & (y_true_arr == c))
        fp = np.sum((y_pred_arr == c) & (y_true_arr != c))
        fn = np.sum((y_pred_arr != c) & (y_true_arr == c))
        
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f1_scores.append(f1)
        
    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(float(np.mean(f1_scores)), 4)
    }
```

### Step 2: Population Stability Index (PSI) Drift Calculation
Detect distribution shift between baseline reference features and real-time production features:

```python
def calculate_psi(
    baseline: List[float],
    current: List[float],
    num_buckets: int = 10
) -> float:
    """Computes Population Stability Index (PSI) between baseline and current distributions."""
    b_arr = np.array(baseline)
    c_arr = np.array(current)
    
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bucket_edges = np.percentile(b_arr, percentiles)
    bucket_edges[0] = -np.inf
    bucket_edges[-1] = np.inf
    
    b_counts, _ = np.histogram(b_arr, bins=bucket_edges)
    c_counts, _ = np.histogram(c_arr, bins=bucket_edges)
    
    b_pct = np.where(b_counts == 0, 1e-4, b_counts) / len(b_arr)
    c_pct = np.where(c_counts == 0, 1e-4, c_counts) / len(c_arr)
    
    psi_value = np.sum((c_pct - b_pct) * np.log(c_pct / b_pct))
    return float(psi_value)
```

### Step 3: Drift Gating & Alert Rules
Interpret PSI drift levels:
- $\text{PSI} < 0.10$: Negligible shift; normal production operation.
- $0.10 \le \text{PSI} < 0.20$: Moderate shift; issue warning telemetry.
- $\text{PSI} \ge 0.20$: Significant distribution drift; trigger automated retraining and route traffic to safe fallback model.

---

## Best Practices & Failure Modes

- **Silent Feature Corruption**: Schema drift (e.g. an integer user ID serialized as a float, or localized date format changes) breaks model inference silently without throwing exceptions. Always enforce strict Pydantic input schemas at the ingress API.
- **Data Leakage in Feature Stores**: Ensure features are joined strictly with point-in-time correctness to prevent future leakage into historical training sets.
- **Cold Start Latency**: Large language models and deep neural nets suffer high first-request latency. Pre-warm container replicas with dummy payloads during readiness health checks before adding to load balancer pools.

---

## Verification & Testing

1. Run the complete AI/ML pipeline evaluation and drift detection test suite:
   ```bash
   python scripts/ai-ml_helper.py
   ```
2. Verify drift calculation and performance benchmarking via CLI:
   ```bash
   python scripts/ai_ml_pipeline_evaluator.py --test-all
   ```
