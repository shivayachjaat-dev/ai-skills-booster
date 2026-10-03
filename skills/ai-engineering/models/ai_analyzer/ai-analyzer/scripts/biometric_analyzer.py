#!/usr/bin/env python3
"""
biometric_analyzer.py - Biometric Time-Series Anomaly & Drift Detector.
Implements rolling Z-scores and two-sided CUSUM algorithms for physiological telemetry
monitoring (Resting Heart Rate, HRV, SpO2, Sleep).
"""

import sys
import math
import random
import argparse

def detect_anomalies_zscore(values: list[float], window: int = 7, threshold: float = 2.5) -> list[dict]:
    anomalies = []
    for i in range(window, len(values)):
        sub = values[i - window : i]
        mean = sum(sub) / len(sub)
        var = sum((x - mean) ** 2 for x in sub) / len(sub)
        std = math.sqrt(var) if var > 0 else 0.0001
        
        val = values[i]
        z = abs(val - mean) / std
        if z > threshold:
            anomalies.append({
                "index": i,
                "value": val,
                "baseline_mean": round(mean, 2),
                "z_score": round(z, 2)
            })
    return anomalies

def detect_cusum_drift(values: list[float], slack: float = 0.5, threshold: float = 3.5) -> list[int]:
    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / len(values)
    std = math.sqrt(var) if var > 0 else 0.0001
    
    s_pos = 0.0
    s_neg = 0.0
    drift_points = []

    for idx, v in enumerate(values):
        norm = (v - mean) / std
        s_pos = max(0.0, s_pos + norm - slack)
        s_neg = min(0.0, s_neg + norm + slack)
        if s_pos > threshold or s_neg < -threshold:
            drift_points.append(idx)
            s_pos = 0.0
            s_neg = 0.0

    return drift_points

def run_synthetic_test():
    print("=" * 65)
    print("Running Biometric Telemetry Anomaly Detection Self-Test")
    print("=" * 65)

    # Generate 30 days of baseline resting heart rate (mean = 62 bpm, std = 2)
    random.seed(42)
    series = [62.0 + random.gauss(0, 1.8) for _ in range(30)]

    # Inject acute spike at day 14 (fever / acute stress: 82 bpm)
    series[14] = 82.5

    # Inject baseline shift from day 22 onwards (sustained drift: mean 70 bpm)
    for i in range(22, 30):
        series[i] = 70.0 + random.gauss(0, 1.5)

    print(f"Generated 30-day telemetry stream with injected anomalies.")
    print("Analyzing stream with rolling Z-score & CUSUM change-point detectors...\n")

    anomalies = detect_anomalies_zscore(series, window=7, threshold=2.5)
    drifts = detect_cusum_drift(series, slack=0.5, threshold=3.0)

    print(f"Rolling Z-Score Outliers Detected: {len(anomalies)}")
    for a in anomalies:
        print(f"  - Day {a['index']:<2}: Value={a['value']:.1f} bpm | Baseline={a['baseline_mean']:.1f} | Z={a['z_score']}")

    print(f"\nCUSUM Mean Shift Drift Points Detected: {len(drifts)}")
    for d in drifts:
        print(f"  - Shift detected starting around Day {d} (Value={series[d]:.1f} bpm)")

    spike_found = any(a["index"] == 14 for a in anomalies)
    drift_found = any(d >= 22 for d in drifts)

    print("-" * 65)
    if spike_found and drift_found:
        print("Self-Test Result: [PASSED] Both acute spike and sustained drift detected.")
        return True
    else:
        print("Self-Test Result: [FAILED] Did not isolate expected anomaly indices.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Biometric Time-Series Anomaly Detector")
    parser.add_argument("--test-synthetic", action="store_true", help="Run synthetic data self-test")

    args = parser.parse_args()

    if args.test_synthetic:
        ok = run_synthetic_test()
        sys.exit(0 if ok else 1)

    print("=" * 65)
    print("Biometric Anomaly Detector Utility Ready")
    print("Run with --test-synthetic to verify statistical filters.")

if __name__ == "__main__":
    main()
