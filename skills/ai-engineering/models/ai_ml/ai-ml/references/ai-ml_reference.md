# Enterprise AI & Machine Learning Operations (MLOps) Technical Reference

## 1. Feature Distribution & Drift Monitoring

Statistical distribution shift is the primary cause of silent degradation in production AI/ML systems.

### Population Stability Index (PSI)
PSI measures changes in the distribution of an input feature or predicted probability over time:

$$\text{PSI} = \sum_{k=1}^K \left( P_k - B_k \right) \times \ln\left(\frac{P_k}{B_k}\right)$$

Where:
- $B_k$ is the proportion of observations in bucket $k$ during the baseline reference window.
- $P_k$ is the proportion of observations in bucket $k$ during the production monitoring window.
- $K$ is the number of quantile buckets (typically 10).

### Drift Severity Thresholds
- **$\text{PSI} < 0.10$**: Insignificant shift. No intervention required.
- **$0.10 \le \text{PSI} < 0.20$**: Moderate shift. Issue warning telemetry and increase sampling rate.
- **$\text{PSI} \ge 0.20$**: Severe covariate shift. Trigger automated retraining or invoke fallback heuristic rules.

---

## 2. Model Evaluation Gating Metrics

Prior to promoting candidate models from staging to production, automated CI/CD gates evaluate the following criteria:

| Metric Category | Gating Threshold | Failure Action |
| :--- | :--- | :--- |
| **Macro F1 Score** | $\ge 0.88$ (or within 1.5% of baseline) | Reject build; log misclassified error confusion matrix. |
| **p95 Latency SLA** | $\le 45\text{ ms}$ for CPU / $\le 20\text{ ms}$ for GPU | Flag performance regression; profile graph operators. |
| **p99 Latency SLA** | $\le 100\text{ ms}$ | Reject deployment if tail latency threatens downstream services. |
| **Memory Footprint** | $\le 2.0\text{ GB}$ RSS per worker | Prevent OOM container restarts in Kubernetes pods. |

---

## 3. High-Performance Model Serving Architectures

1. **Graph Compilation & Quantization**:
   - Convert PyTorch weights to ONNX graph format.
   - Apply FP16 or INT8 (AWQ/GPTQ) quantization to double inference throughput with minimal perplexity degradation.
2. **Dynamic Batching**:
   - Group concurrent incoming requests within a small time window ($2\text{--}5\text{ ms}$) to maximize GPU tensor core utilization.
3. **Continuous Token Streaming**:
   - For LLMs, implement server-sent events (SSE) with KV-cache paging (PagedAttention) to maintain consistent Time-To-First-Token (TTFT).
