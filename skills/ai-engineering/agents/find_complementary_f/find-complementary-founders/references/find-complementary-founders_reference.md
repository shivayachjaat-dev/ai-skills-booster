# Complementary Founder Matching Reference

## Multi-Dimensional Founder Fit Specification

Startup cofounder failure is one of the leading causes of venture mortality. In many cases, technical founders mistakenly recruit clones of themselves (e.g. two backend engineers who both avoid customer calls and sales). Effective founder matching requires maximizing **skill complementarity** (covering orthogonal domains) while ensuring **value & commitment alignment**.

### Domain Decomposition

```
+------------------------------------------------------------------------+
|                     Founder Capability Vectors                         |
|                                                                        |
|      [ Technical Engineering ] <=========> [ GTM & Sales ]             |
|                 ^                                    ^                 |
|                 |         [ Core Problem Space ]     |                 |
|                 v                                    v                 |
|      [ Product & UX Design ]   <=========> [ Operations & Finance ]    |
+------------------------------------------------------------------------+
```

### Scoring Formula

1. **Gap Coverage**: Quantifies how effectively the candidate covers the owner's lowest-scoring functional domains:
   $$\text{GapScore} = \sum_{\text{weaknesses}} \max(0, \text{CandScore} - \text{OwnerScore})$$
2. **Commitment Alignment**: Penalizes discrepancies between full-time dedicated founders and part-time hobbyists.
3. **Domain Resonance**: Checks intersection between shared industry passions (e.g. Developer Tools, HealthTech, AI Infrastructure).

### Privacy & Consent Guardrails

- **Zero Unilateral Disclosure**: The agent evaluates and ranks only publicly published candidate profiles or profiles with explicit opt-in matching consent.
- **Scrubbed Sensitive Financials**: Personal net worth, cap table specifics, and past confidential compensation records must never be stored or evaluated.
