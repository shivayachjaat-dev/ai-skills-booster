#!/usr/bin/env python3
"""
ai_ml_pipeline_evaluator.py - Production AI/ML Lifecycle & MLOps Evaluation Engine

Features:
- Population Stability Index (PSI) drift calculation
- Multi-class classification evaluation metrics (Accuracy, Precision, Recall, Macro F1)
- Inference latency percentile profiling (p50, p95, p99)
- Gating checks for automated deployment
"""

import sys
import os
import math
import argparse
from typing import List, Dict, Any, Tuple


def calculate_accuracy_and_f1(y_true: List[int], y_pred: List[int]) -> Dict[str, float]:
    """Computes exact Accuracy and Macro F1 score without external heavy dependencies."""
    if len(y_true) != len(y_pred) or not y_true:
        raise ValueError("Inputs must have identical non-zero lengths")

    total = len(y_true)
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    accuracy = correct / total

    classes = sorted(list(set(y_true + y_pred)))
    f1_list = []

    for c in classes:
        tp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp == c)
        fp = sum(1 for yt, yp in zip(y_true, y_pred) if yt != c and yp == c)
        fn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == c and yp != c)

        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        f1_list.append(f1)

    macro_f1 = sum(f1_list) / len(f1_list) if f1_list else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "macro_f1": round(macro_f1, 4),
        "num_samples": total,
        "classes_evaluated": len(classes)
    }


def compute_psi(baseline: List[float], current: List[float], buckets: int = 10) -> Tuple[float, str]:
    """
    Computes Population Stability Index (PSI) between baseline and production distributions.
    Returns (psi_value, status_verdict).
    """
    if not baseline or not current:
        raise ValueError("Distributions must not be empty")

    b_sorted = sorted(baseline)
    n_base = len(b_sorted)

    # Establish quantile boundaries from baseline
    quantiles = [b_sorted[int(i * n_base / buckets)] for i in range(1, buckets)]
    boundaries = [-float('inf')] + quantiles + [float('inf')]

    def get_bin_counts(data: List[float]) -> List[int]:
        counts = [0] * (len(boundaries) - 1)
        for val in data:
            for i in range(len(counts)):
                if boundaries[i] <= val < boundaries[i + 1]:
                    counts[i] += 1
                    break
        return counts

    b_counts = get_bin_counts(baseline)
    c_counts = get_bin_counts(current)

    n_cur = len(current)
    psi = 0.0

    for bc, cc in zip(b_counts, c_counts):
        b_pct = (bc / n_base) if bc > 0 else (1e-4 / n_base)
        c_pct = (cc / n_cur) if cc > 0 else (1e-4 / n_cur)
        psi += (c_pct - b_pct) * math.log(c_pct / b_pct)

    psi_val = round(psi, 4)
    if psi_val < 0.10:
        verdict = "STABLE"
    elif psi_val < 0.20:
        verdict = "MODERATE_SHIFT"
    else:
        verdict = "SIGNIFICANT_DRIFT"

    return psi_val, verdict


def profile_latencies(latencies_ms: List[float]) -> Dict[str, float]:
    """Computes p50, p95, and p99 percentiles."""
    if not latencies_ms:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    sorted_l = sorted(latencies_ms)
    n = len(sorted_l)

    def percentile(p: float) -> float:
        idx = int(p * n)
        idx = min(idx, n - 1)
        return round(sorted_l[idx], 2)

    return {
        "p50": percentile(0.50),
        "p95": percentile(0.95),
        "p99": percentile(0.99),
        "mean": round(sum(sorted_l) / n, 2)
    }


def run_unit_tests():
    print("=" * 60)
    print("Running AI/ML Pipeline Lifecycle & MLOps Evaluator Tests")
    print("=" * 60)

    # Test 1: Classification Metrics
    y_true = [0, 0, 1, 1, 2, 2, 0, 1, 2, 0]
    y_pred = [0, 0, 1, 1, 2, 1, 0, 1, 2, 0]
    metrics = calculate_accuracy_and_f1(y_true, y_pred)
    print(f"[*] Classification Metrics: Accuracy={metrics['accuracy']}, Macro F1={metrics['macro_f1']}")
    assert metrics["accuracy"] >= 0.90, "Accuracy test failed"
    assert metrics["macro_f1"] >= 0.85, "Macro F1 test failed"

    # Test 2: PSI Drift Calculation on stable data
    base_dist = [float(x) for x in range(100)]
    curr_stable = [float(x + 0.5) for x in range(100)]
    psi_stable, verdict_stable = compute_psi(base_dist, curr_stable, buckets=5)
    print(f"[*] Stable PSI: {psi_stable} -> Verdict: {verdict_stable}")
    assert verdict_stable == "STABLE", f"Expected STABLE, got {verdict_stable}"

    # Test 3: PSI Drift Calculation on heavily drifted data
    curr_drifted = [float(x + 150) for x in range(100)]
    psi_drift, verdict_drift = compute_psi(base_dist, curr_drifted, buckets=5)
    print(f"[*] Drifted PSI: {psi_drift} -> Verdict: {verdict_drift}")
    assert verdict_drift == "SIGNIFICANT_DRIFT", f"Expected SIGNIFICANT_DRIFT, got {verdict_drift}"

    # Test 4: Latency Profiling
    lats = [12.4, 15.1, 14.8, 16.2, 13.9, 14.5, 45.0, 15.0, 14.2, 18.1]
    stats = profile_latencies(lats)
    print(f"[*] Latency Profile: p50={stats['p50']}ms, p95={stats['p95']}ms, p99={stats['p99']}ms")
    assert stats["p50"] <= 16.0, "p50 calculation failed"

    print("\n[SUCCESS] AI/ML Pipeline Evaluator passed all operational benchmarks.")


def main():
    parser = argparse.ArgumentParser(description="AI/ML Pipeline Lifecycle Evaluator")
    parser.add_argument("--test-all", action="store_true", help="Run self-test suite")
    parser.add_argument("--eval-demo", action="store_true", help="Run demonstration evaluation")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
