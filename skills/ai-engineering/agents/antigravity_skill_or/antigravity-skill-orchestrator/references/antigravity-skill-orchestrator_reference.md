# Agent Skill Meta-Orchestrator Technical Reference

## 1. Meta-Agent Decision Theory & Complexity Gating

Executing multi-agent or multi-skill workflows introduces significant latency and token costs. A production meta-orchestrator must evaluate utility before scheduling:

$$\mathbb{E}[U(\text{Orchestrate})] = P(\text{Success}_{\text{orch}}) \cdot V(\text{Task}) - C_{\text{tokens}} - C_{\text{latency}}$$

$$\mathbb{E}[U(\text{Direct})] = P(\text{Success}_{\text{direct}}) \cdot V(\text{Task}) - C_{\text{direct}}$$

### Gating Rule
Invoke multi-skill orchestration if and only if:
$$\mathbb{E}[U(\text{Orchestrate})] > \mathbb{E}[U(\text{Direct})] + \tau_{\text{overhead}}$$

Where $\tau_{\text{overhead}}$ is an empirical margin preventing over-orchestration on tasks solvable with native shell commands and direct edits.

---

## 2. Directed Acyclic Graph (DAG) Resolution

Multi-domain software engineering problems map naturally to dependency graphs:

$$G = (V, E)$$

Where:
- Each vertex $v \in V$ represents a specialized skill execution stage (e.g. `schema-design`, `api-implementation`, `ui-component`, `security-audit`).
- Each directed edge $(u, v) \in E$ indicates that skill $v$ depends on the completed artifacts of skill $u$.

### Topological Sorting & Parallelism
1. **Topological Order**: Linear ordering of vertices such that for every directed edge $(u, v)$, vertex $u$ comes before $v$ in the ordering.
2. **Independent Stages**: Vertices with in-degree 0 at any execution wave can run concurrently across subagents.

---

## 3. Inter-Skill Artifact Contracts

To prevent cross-stage hallucination, skills communicate strictly via persistent disk artifacts:
- **Database Phase -> API Phase**: Emits SQL migration files and typed entity definitions.
- **API Phase -> Frontend Phase**: Emits standard OpenAPI / JSON Schema contracts.
- **Frontend Phase -> E2E Phase**: Emits DOM test selectors and route manifests.

If any intermediate artifact fails structural validation, the pipeline halts immediately with actionable diagnostics rather than cascading errors downstream.
