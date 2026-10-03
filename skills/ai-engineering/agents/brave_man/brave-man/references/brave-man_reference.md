# Pre-Build Clarification & Specification Technical Reference

## 1. The Economics of Premature Implementation

In autonomous agent workflows, the cost of correcting a misconception scales exponentially across development phases:

$$\text{Cost to Fix}(\text{Phase}) = C_0 \cdot e^{k \cdot \text{Depth}}$$

| Phase of Discovery | Relative Cost to Correct | Primary Waste Vectors |
| :--- | :--- | :--- |
| **Discovery / Interview** | $1\times$ | Negligible; update text specification. |
| **Architecture / Scaffolding**| $5\times$ | Renaming directories, revising database migrations. |
| **Core Implementation** | $25\times$ | Rewriting component props, mutating API contracts. |
| **Post-Ship Refactor** | $100\times$ | Data migration, breaking client compatibility. |

By conducting a batched 5-minute structured interview before executing a single line of code, the agent avoids 80% of downstream rework.

---

## 2. Phased Question Hierarchy & Calibration

To avoid overwhelming the user while capturing necessary depth:
- **Calibrated Depth**: If triage indicates a standalone single-file utility, suppress questions regarding OAuth2, Redis clustering, and internationalization.
- **Negative Scope Contract**: Actively solicit what is *excluded*. Ambiguity in v1 scope invites agents to build speculative boilerplate.
- **Batched Dialogue**: Group questions thematically to minimize chat round-trips and preserve conversational momentum.

---

## 3. Specification Output Standards (`prompt.md`)

The final synthesized specification must meet strict deterministic criteria:
1. **Self-Contained**: Can be passed to a fresh, un-primed agent session without requiring access to prior chat context.
2. **Definite Verification Harness**: Contains the exact shell commands (`pytest`, `npm test`, `curl`) required to prove completion.
3. **Checklist Definition of Done**: Every feature expressed as an atomic, verifiable checklist item.
