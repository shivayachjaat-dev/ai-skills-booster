# Grok Build CLI Delegation Technical Reference

## Execution Topology & Safety Consent Protocol

Delegating complex software engineering implementation loops to external CLI agents (such as the Grok Build CLI) requires clear authorization contracts, explicit consent guardrails, and deterministic process lifecycle management.

### Delegation Architecture

```
                  [ Agent / User Request ]
                             |
                             v
               [ Consent & Invariant Gate ]
              (Explicit User Consent Required)
                             |
             +---------------+---------------+
             |                               |
       [ Consent True ]               [ Consent False ]
             |                               |
             v                               v
    [ Grok CLI Process ]              [ Immediate Rejection ]
    - Subprocess spawning
    - Directory sandboxing
    - Exit status normalization
             |
             v
    [ Diff & Outcome Egress ]
```

### Delegation Invariants

1. **Mandatory Explicit Consent**: Autonomous agents must never route tasks or codebases to Grok without explicit instruction or opt-in consent from the user.
2. **Directory Sandboxing**: Execution is constrained strictly to the configured `workspace_root`.
3. **Deterministic Timeout**: Process execution is terminated with exit code `124` if runtime exceeds `timeout_sec`.
