# Dispatching Parallel Agents Technical Reference

## Architecture & Fan-Out / Fan-In Standards

When decomposing large software engineering workflows across autonomous AI agents, parallel execution dramatically lowers end-to-end latency compared to sequential iteration. However, uncoordinated parallel agent dispatch introduces race conditions, state clobbering, context pollution, and LLM rate-limit saturation.

### Parallel Execution Topology

```
                  [ Orchestrator / Dispatcher ]
                                |
             +------------------+------------------+
             |                  |                  |
             v                  v                  v
     [ Subagent A ]      [ Subagent B ]     [ Subagent C ]
     (Static Audit)      (Unit Testing)     (Documentation)
             |                  |                  |
             +------------------+------------------+
                                |
                                v
               [ Reconciler / Synthesizer Layer ]
                                |
                                v
                   [ Consolidated Deliverable ]
```

### Eligibility Criteria for Parallel Dispatch

A group of tasks is eligible for concurrent parallel dispatch if and only if all of the following conditions hold:
1. **State Independence**: No task mutates files, databases, or variables that another concurrent task reads or writes.
2. **Context Disjointness**: Subagent prompts require specialized, partitioned contexts rather than the full monolithic session history.
3. **Deterministic Idempotency**: Each subagent run can be retried independently upon failure without side-effects.

### Concurrency & Rate Limit Management

- **Worker Pool Sizing**: Recommended concurrency cap is `4-8` concurrent subagents to avoid LLM tokens-per-minute (TPM) throttling.
- **Circuit Breakers**: If consecutive subagent calls encounter `429 Too Many Requests`, pause the pool and apply exponential backoff (`t_backoff = 2^k * base_delay`).
- **Timeout Quotas**: Explicit execution timeouts (typically `30s` to `120s`) prevent orphaned subagent processes from blocking reconciliation.
