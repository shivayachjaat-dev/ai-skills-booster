# ECL Agent Harness Architecture Reference

## Standard Specification for Autonomous Engineering Repositories

The **ECL (Engineering Capability Lifecycle) Agent Harness** defines the foundational repository environment required for autonomous and semi-autonomous coding agents to function reliably alongside human engineers.

### Core Harness Components

```
<repo-root>/
├── AGENTS.md                   # Operational commandments, test commands, rules
├── .agent-harness/
│   ├── config.json             # Execution gates and timeout limits
│   ├── handoffs/               # Session handoff documents for PR review
│   └── audit-log.jsonl         # Append-only journal of agent actions
```

### AGENTS.md Mandatory Sections

1. **Repository Invariants**: Immutable constraints (e.g. backward compatibility, zero secret leaks).
2. **Testing Requirements**: Minimum coverage thresholds and commands to execute prior to handoff.
3. **Architecture Guidelines**: Directory boundaries, layer separation, modular conventions.
4. **Permitted Commands**: Explicit whitelist of CLI commands an agent is authorized to execute.
5. **Security & Secret Boundaries**: Prohibition on accessing `.env`, private SSH keys, and tokens.

### Pre-Flight Gate & Handoff Standard

Before an agent commits code or prepares a pull request, the ECL Harness mandates:
- **Lint & Syntax Validation**: All modified source files compile with 0 syntax errors.
- **Contract Adherence**: No forbidden file edits outside the authorized task scope.
- **Handoff Generation**: Emission of a clear Markdown brief containing touched files, test outcomes, and unresolved ambiguities.
