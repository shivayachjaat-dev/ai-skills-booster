# Dialectical Idea Evaluation Reference

## Adversarial Multi-Agent Debate Framework

Single-agent evaluation of business ideas, architectural proposals, or startup concepts frequently falls prey to uncritical optimism (sycophancy) or blanket cynicism. The **Dialectical Multi-Agent Evaluation** framework deploys structured role-playing agents to force synthesis through structured opposition.

### Debate & Adjudication Pipeline

```
                     [ Proposal / Concept Input ]
                                  |
                                  v
              +-------------------+-------------------+
              |                                       |
              v                                       v
    [ Proponent Agent ]                       [ Skeptic Agent ]
    - Value proposition                       - Incumbent response
    - Defensibility & moat                    - Unit economics & CAC
    - Market tailwinds                        - Operational fragility
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                    [ Cross-Examination Rebuttals ]
                                  |
                                  v
                      [ Neutral Judge / Oracle ]
                      - Opportunity Score (0-50)
                      - Risk Discount (0-50)
                      - Net Viability Score (0-100)
                      - Calibrated Verdict & Action Plan
```

### Viability Scoring Rubric

$$\text{NetViability} = \max(0, \min(100, (\text{Opportunity} - 0.5 \times \text{RiskDiscount}) \times 2))$$

| Score Tier | Verdict | Meaning |
| :--- | :--- | :--- |
| **80 - 100** | `PURSUE_AGGRESSIVELY` | Strong product-market fit signal with manageable downside risk. |
| **60 - 79** | `PURSUE_WITH_PIVOT` | Core idea has merit, but requires structural refactoring of business/tech model. |
| **40 - 59** | `DE_PRIORITIZE` | High opportunity cost relative to returns; monitor market signals. |
| **0 - 39** | `ABANDON` | Fatal structural flaws, lack of defensible moat, or severe regulatory barriers. |
