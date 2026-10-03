# Data-Driven Feature Development & A/B Experimentation Technical Reference

## 1. Statistical Hypothesis Testing Mathematics

In online experimentation, determining whether an observed conversion rate difference $\Delta p = p_T - p_C$ reflects true causality rather than random sampling noise requires a two-proportion Z-test.

### Test Statistic Formulation:
$$Z = \frac{p_T - p_C}{\sqrt{p_{\text{pool}} (1 - p_{\text{pool}}) \left( \frac{1}{N_T} + \frac{1}{N_C} \right)}}$$

Where:
$$p_{\text{pool}} = \frac{S_T + S_C}{N_T + N_C}$$
- $S_T, S_C$: Number of conversions (successes) in Treatment and Control cohorts.
- $N_T, N_C$: Total distinct user sample sizes.

### P-Value & Decision Threshold:
$$p = 2 \cdot \left[ 1 - \Phi(|Z|) \right]$$

For standard statistical significance:
- $\alpha = 0.05$ ($95\%$ confidence level): $|Z| \ge 1.96 \implies p < 0.05$.
- If $p < 0.05$ and $\Delta p > 0$, the null hypothesis $H_0: p_T = p_C$ is rejected.

---

## 2. Sample Ratio Mismatch (SRM) Diagnosis

Before interpreting experiment outcomes, teams must verify that traffic allocation matches the design split (e.g. 50/50).
- An undetected SRM invalidates all downstream statistical conclusions.
- Compute Chi-Square goodness-of-fit:
$$\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}$$
- If $p < 0.001$, flag critical SRM: investigate bot filtering, caching anomalies, or redirection loop bugs.

---

## 3. Telemetry Event Schema Standards

All experimentation telemetry must adhere to typed, immutable schemas:

```json
{
  "event_id": "evt_998124a",
  "timestamp": "2026-10-03T13:45:00.000Z",
  "user_id": "usr_alpha_12",
  "experiment_id": "exp_checkout_reorder_2026",
  "variant": "treatment",
  "event_type": "conversion",
  "metric_name": "checkout_completed",
  "properties": {
    "order_value_usd": 84.50,
    "cart_size": 3
  }
}
```
