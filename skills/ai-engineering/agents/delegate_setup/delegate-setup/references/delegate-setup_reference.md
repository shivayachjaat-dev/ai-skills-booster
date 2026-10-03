# Delegate Setup Technical Reference

## Architecture & Delegation Lanes Specification

The **Delegate Setup** system serves as the governance and configuration layer for multi-agent autonomous engineering environments. When orchestrating heterogeneous implementer CLIs (such as Gemini, Claude, Copilot, Cline, or Aider), system stability and security require explicit delegation contracts, capability detection, and fallback resolution.

### Security Permission Tiers

| Tier Name | Filesystem Access | Network Access | Version Control Mutability | Intended Workload |
| :--- | :--- | :--- | :--- | :--- |
| `strict_read_only` | Read only | Allowed | Prohibited | Codebase audits, security triage, architectural analysis |
| `workspace_write_isolated` | Workspace only | Prohibited | Prohibited | Unit test generation, single-file refactoring, sandbox changes |
| `supervised_commit` | Workspace only | Allowed | Staged changes only | Multi-file bugfixes, PR preparation, continuous integration tasks |
| `full_delegation` | Full repository | Allowed | Commit and Push | Autonomous pipeline execution, migration scripts |

### CLI Discovery & Verification Flow

```
+------------------------------------------------------------------------+
|                      Delegate Setup Engine                             |
|                                                                        |
|  [ Environment Probe ] -> Scans PATH for agent binaries               |
|            |                                                           |
|            v                                                           |
|  [ Capability Matrix ] -> Assesses stdin pipe, json streaming, context |
|            |                                                           |
|            v                                                           |
|  [ Lane Assignment ]   -> Binds agent ID to Permission Tier            |
|            |                                                           |
|            v                                                           |
|  [ Fallback Routing ]  -> Constructs ordered resilience ladder         |
+------------------------------------------------------------------------+
```

### Delegation Policy Schema (`.delegate-lanes.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "version": "1.0.0",
  "routing": {
    "primary": "gemini",
    "fallbacks": ["claude", "aider"]
  },
  "security_lanes": {
    "gemini": {
      "installed": true,
      "tier": "full_delegation",
      "capabilities": ["stdin_prompt", "json_output", "context_window_1m"]
    },
    "claude": {
      "installed": true,
      "tier": "supervised_commit",
      "capabilities": ["stdin_prompt", "json_output", "context_window_200k"]
    }
  }
}
```

### Failover & Resilience Protocol

1. **Health Check Probing**: Before dispatching tasks, verify that the selected delegate binary responds within timeout limits (`<= 2000ms`).
2. **Deterministic Fallback**: If the primary agent CLI experiences quota exhaustion, binary crash, or rate limiting, cascade immediately to the secondary agent specified in `fallbacks`.
3. **Audit Trail**: Every delegation request, argument bundle, and exit status must be captured in the execution journal.
