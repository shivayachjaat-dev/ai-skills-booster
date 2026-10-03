# Agent Evaluation Framework Reference

## Evaluation Methodologies for Autonomous AI Agents

Unlike traditional unit tests that evaluate deterministic pure functions, autonomous AI agents operate nondeterministically across broad action spaces. Systematically evaluating agents requires combining deterministic assertions with behavioral rubrics.

### Evaluation Dimensions

```
                    [ Agent Input / Prompt ]
                                |
                                v
                       [ Autonomous Agent ]
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
     [ Tool Selection ]  [ Output Content ]  [ SLA & Safety ]
     - Exact match       - Schema adherence  - Latency SLA
     - Argument typing   - Grounding check   - Forbidden tokens
             |                  |                  |
             +------------------+------------------+
                                |
                                v
                    [ Pass / Fail & Scoring ]
```

### Deterministic vs Model-Based Evals

1. **Deterministic Assertions**:
   - Tool calling fidelity: verifying that the expected tool was invoked with schema-compliant arguments.
   - Negative constraints: checking that forbidden tokens (e.g. `eval()`, credentials, hallucinated endpoints) are absent.
   - Substring & schema presence: checking required JSON keys or markdown sections.
   - Latency thresholds: verifying response within allowable time budget.

2. **Model-Based Rubrics (LLM-as-a-Judge)**:
   - Factual grounding: does the response hallucinate citations or dependencies?
   - Tone & persona adherence: does the output match prompt engineering constraints?
   - Instruction following: multi-step task completion verification.

### Continuous Evaluation in CI/CD

- **Baseline Freezing**: Maintain a golden dataset of evaluated runs (`golden_eval_dataset.json`).
- **Regression Gates**: Fail pull requests if Pass@1 falls below configured threshold (e.g. 85%) or if token consumption increases by > 20% without performance gains.
