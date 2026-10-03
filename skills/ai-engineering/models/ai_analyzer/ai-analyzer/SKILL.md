---
name: ai-analyzer
description: "Use this skill to perform AI-driven health analytics, biometric time-series anomaly detection, and physiological risk modeling. It implements statistical drift detection (CUSUM, rolling Z-scores), cardiovascular risk scoring (ASCVD), sleep quality indices (PSQI), and clinical telemetry reporting with strict medical AI safety guardrails."
domain: ai-engineering
category: models
subcategory: ai_analyzer
tags:
  - ai-engineering
  - health-analytics
  - biometric-telemetry
  - anomaly-detection
  - time-series
  - cusum
  - physiological-modeling
technologies:
  - Python
  - NumPy
  - SciPy
  - CUSUM Algorithm
  - ASCVD Risk Calculator
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
  - numpy@>=1.24.0
  - scipy@>=1.10.0
version: 1.0.0
author: Antigravity Team
---

# Biometric Anomaly Detection & AI Health Analytics Architecture

## Overview

A clinical data science standard for analyzing physiological time-series datasets, detecting subtle health anomalies, and calculating multi-factor health risk scores using statistical and machine learning models. Wearable devices and clinical monitors stream continuous physiological signals (resting heart rate, heart rate variability [HRV], blood oxygen saturation [SpO2], continuous glucose monitors [CGM], and sleep architecture). This skill establishes rigorous patterns for noise filtering, rolling Z-score outlier detection, Cumulative Sum (CUSUM) baseline drift identification, and multi-system risk stratification while enforcing strict medical safety guardrails.

```
+--------------------------------------------------------------------------------+
|                    Biometric Telemetry Analysis Pipeline                       |
|                                                                                |
|  [ Multi-Sensor Biometric Stream (RHR, HRV, SpO2, Sleep) ]                    |
|                               |                                                |
|                               v                                                |
|  [ Signal Cleaning: Moving Median Window & Artifact Rejection ]                |
|                               |                                                |
|                               v                                                |
|  [ Statistical Anomaly Detection: Rolling Z-Score ($Z > 2.5$) ]                |
|                               |                                                |
|                               v                                                |
|  [ Baseline Drift Analysis: Two-Sided CUSUM Change-Point Detector ]           |
|                               |                                                |
|                               v                                                |
|  [ Multi-Factor Risk Assessment (ASCVD / Metabolic Variability / PSQI) ]       |
|                               |                                                |
|                               v                                                |
|  [ Structured Telemetry Summary Report with Clinical Disclaimers ]             |
+--------------------------------------------------------------------------------+
```

## When to Use

- Ingesting and analyzing wearable sensor telemetry (Apple HealthKit, Garmin, Oura, Whoop, Fitbit) to identify acute physiological stress or baseline shifts.
- Detecting sudden autonomic nervous system anomalies using resting heart rate (RHR) and heart rate variability (HRV rMSSD).
- Computing standardized health risk models (ASCVD 10-year cardiovascular risk, Pittsburgh Sleep Quality Index [PSQI]).
- Generating clinical review summaries for remote patient monitoring (RPM) platforms.

## When NOT to Use

- Real-time acute emergency diagnosis (e.g., automated diagnosis of myocardial infarction or stroke; immediately direct users to emergency medical services).
- Direct therapeutic intervention or automated medication dose adjustments without licensed physician oversight.

## Inputs & Prerequisites

- Python 3.10+ with `numpy` and `scipy` installed.
- Timestamped physiological time-series data (CSV, JSON, or Parquet format) with standard column headers: `timestamp`, `rhr_bpm`, `hrv_rmssd_ms`, `spo2_pct`.
- User demographic context (age, biological sex, systolic blood pressure, cholesterol levels) if calculating multi-factor risk scores.

## Core Workflow

### Step 1: Biometric Data Ingestion & Artifact Filtering
Raw optical wearable sensors frequently introduce motion artifacts. Apply a 5-point rolling median filter to suppress spurious spikes:

```python
import numpy as np

def clean_biometric_series(raw_values: list[float], min_valid: float, max_valid: float) -> np.ndarray:
    """Clips out-of-range hardware artifacts and interpolates missing entries."""
    arr = np.array(raw_values, dtype=float)
    # Filter biologically impossible outliers
    arr[(arr < min_valid) | (arr > max_valid)] = np.nan
    # Linear interpolation over NaN gaps
    nans = np.isnan(arr)
    x = lambda z: z.nonzero()[0]
    if np.any(nans) and not np.all(nans):
        arr[nans] = np.interp(x(nans), x(~nans), arr[~nans])
    return arr
```

### Step 2: Rolling Z-Score Anomaly Detection
Compute localized deviations against a dynamic 14-day rolling baseline:

```python
def detect_zscore_anomalies(data: np.ndarray, window_size: int = 14, threshold: float = 2.5) -> list[int]:
    """Identifies indices where the signal deviates beyond threshold standard deviations."""
    anomalies = []
    for i in range(window_size, len(data)):
        window = data[i - window_size : i]
        mean = np.mean(window)
        std = np.std(window)
        if std > 0:
            z = abs((data[i] - mean) / std)
            if z > threshold:
                anomalies.append(i)
    return anomalies
```

### Step 3: Cumulative Sum (CUSUM) Baseline Shift Detection
Detect progressive, systemic drift (such as onset of infection, overtraining syndrome, or chronic recovery deficit):

```python
def cusum_detector(series: np.ndarray, slack: float = 0.5, threshold: float = 4.0) -> list[int]:
    """Two-sided CUSUM algorithm for detecting mean shift change-points."""
    mean = np.mean(series)
    std = np.std(series)
    if std == 0:
        return []
    
    normalized = (series - mean) / std
    s_pos = 0.0
    s_neg = 0.0
    change_points = []

    for i, x in enumerate(normalized):
        s_pos = max(0.0, s_pos + x - slack)
        s_neg = min(0.0, s_neg + x + slack)
        if s_pos > threshold or s_neg < -threshold:
            change_points.append(i)
            s_pos = 0.0
            s_neg = 0.0

    return change_points
```

### Step 4: Multi-Factor Cardiovascular Risk Estimation (ASCVD)
Calculate 10-year risk of atherosclerotic cardiovascular disease using pooled cohort equations:

```python
def calculate_ascvd_risk(age: int, sex: str, systolic_bp: float, total_chol: float, hdl_chol: float, smoker: bool) -> float:
    """Computes simplified ACC/AHA 10-year ASCVD risk percentage."""
    if age < 40 or age > 79:
        raise ValueError("ASCVD pooled cohort equations are validated only for ages 40-79.")
    
    # Baseline logarithmic risk factors for non-diabetic non-treated cohort
    ln_age = np.log(age)
    ln_tot_chol = np.log(total_chol)
    ln_hdl = np.log(hdl_chol)
    ln_sbp = np.log(systolic_bp)

    if sex.lower() == "male":
        coeff_sum = (12.344 * ln_age) + (11.853 * ln_tot_chol) - (2.664 * ln_age * ln_tot_chol) - (7.990 * ln_hdl) + (1.769 * ln_age * ln_hdl) + (1.764 * ln_sbp) + (7.837 if smoker else 0.0)
        baseline_survival = 0.9144
        mean_coeff = 61.18
    else:
        coeff_sum = (-29.799 * ln_age) + (4.884 * (ln_age**2)) + (13.540 * ln_tot_chol) - (3.114 * ln_age * ln_tot_chol) - (13.578 * ln_hdl) + (3.149 * ln_age * ln_hdl) + (1.957 * ln_sbp) + (7.574 if smoker else 0.0)
        baseline_survival = 0.9665
        mean_coeff = -29.18

    individual_risk = 1.0 - (baseline_survival ** np.exp(coeff_sum - mean_coeff))
    return round(float(individual_risk * 100), 2)
```

## Best Practices & Failure Modes

- **Never Diagnose**: Every output report must include the explicit notice: *"Informational screening only; consult a licensed medical provider for clinical evaluation."*
- **Circadian Rhythm Standardization**: Compare resting metrics (heart rate, temperature, HRV) strictly against matched sleep epochs rather than active daylight hours.
- **Handling Incomplete Data**: Do not attempt risk modeling on streams with $> 30\%$ missing values over the evaluation window.

## Verification & Testing

1. Validate statistical math: Run `python scripts/biometric_analyzer.py --test-synthetic` to verify that injected synthetic heart-rate anomalies are accurately detected by Z-score and CUSUM filters.
2. Verify ASCVD calculator: Validate risk outputs against published ACC/AHA clinical calculator test cases.
3. Test artifact rejection: Confirm that extreme noise spikes (e.g., $220\text{ bpm}$ sensor disconnect) are rejected during pre-processing.
