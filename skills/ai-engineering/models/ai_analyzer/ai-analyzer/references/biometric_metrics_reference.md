# Biometric Reference Ranges & Physiological Metrics

## Standard Adult Physiological Reference Ranges
| Metric | Normal Range | Alert Threshold (Low) | Alert Threshold (High) | Measurement Context |
|---|---|---|---|---|
| **Resting Heart Rate (RHR)** | 60 - 80 bpm | $< 48$ bpm (Bradycardia) | $> 100$ bpm (Tachycardia) | Measured during deep sleep / waking |
| **HRV (rMSSD)** | 25 - 65 ms | $< 18$ ms (Systemic stress) | Individual baseline | Root mean square of successive RR intervals |
| **Blood Oxygen ($SpO_2$)** | 95% - 100% | $< 92$ % (Hypoxia risk) | N/A | Pulse oximetry at rest |
| **Systolic Blood Pressure** | $< 120$ mmHg | $< 90$ mmHg (Hypotension) | $\ge 140$ mmHg (Stage 2 HTN) | Clinical seated measurement |

## CUSUM Parameter Tuning Guidelines
The Cumulative Sum (CUSUM) detector tracks deviations in units of standard deviation ($\sigma$):
- **Allowance / Slack ($k$)**: Typically set to $0.5\sigma$. Represents half the minimum shift magnitude intended to detect quickly.
- **Decision Interval / Threshold ($h$)**: Typically set between $3.0\sigma$ and $5.0\sigma$. Higher values reduce false alarm rates while slightly delaying detection latency.

## Medical AI Regulatory Boundaries
- In accordance with FDA and CE-MDR Software as a Medical Device (SaMD) classifications, algorithmic risk estimators must not output prescriptive diagnostic claims without clinician sign-off.
- Outputs must be framed as supportive physiological screening data indicating statistical divergence from personal baselines.
