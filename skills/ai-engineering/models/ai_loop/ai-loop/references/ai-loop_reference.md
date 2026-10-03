# Bounded Autonomous Development Loops Technical Reference

## 1. Mathematical Formalization of Bounded Coding Loops

Autonomous code synthesis can be modeled as a directed state machine:

$$S = \langle Q, \Sigma, \delta, q_0, F \rangle$$

Where:
- $Q = \{ \text{INIT}, \text{SPEC}, \text{BUILD}, \text{REVIEW}, \text{APPROVAL\_REQUIRED}, \text{COMPLETED}, \text{EXHAUSTED}, \text{ABORTED} \}$
- $\Sigma$ represents the set of input actions: user specifications, diff applications, test outputs, human approvals.
- $\delta: Q \times \Sigma \to Q$ is the state transition function.
- $q_0 = \text{INIT}$
- $F = \{ \text{COMPLETED}, \text{EXHAUSTED}, \text{ABORTED} \}$

### Termination Proof Guarantee
An unconstrained agentic loop can loop infinitely if bug fixes repeatedly generate new orthogonal bugs. To guarantee termination:
1. **Strictly Monotonic Iteration Budget**: Every transition through `BUILD -> REVIEW` increments an iteration counter $i \in \mathbb{N}$.
2. **Hard Termination Bound**: When $i = I_{\max}$ (default: 3 to 5), the system is forced into terminal state `EXHAUSTED`.
3. Therefore, the state machine is guaranteed to terminate in at most $I_{\max}$ review steps.

---

## 2. Scope Confinement & Ast-Based Diff Auditing

To prevent speculative refactoring and context drift:

1. **Path Whitelisting**: Glob expressions defining permissible write targets:
   - Example: `["src/components/Avatar.tsx", "tests/unit/Avatar.test.tsx"]`
   - Any write or delete action outside these paths triggers immediate `ABORTED` state.
2. **Syntactic Boundary Enforcement**: Ensure the agent does not rewrite entire source files when modifying small functions. Utilize AST diff tools to restrict mutations to intended target functions.
3. **Entropy & Volume Limits**: Reject single-iteration diffs exceeding 500 LOC unless explicitly annotated as a greenfield feature.

---

## 3. Human-In-The-Loop Escalation Matrix

| Risk Category | Trigger Condition | Escalation Action |
| :--- | :--- | :--- |
| **Data Integrity** | DDL migration scripts, `DROP TABLE`, destructive disk I/O | Transition to `APPROVAL_REQUIRED`; block execution until confirmation. |
| **External Side-Effects** | Network calls to external APIs with write verbs (`POST`, `PUT`, `DELETE`) | Require human authorization or mock interceptor configuration. |
| **Architectural Pivot** | Introducing new dependencies in `package.json` or `pyproject.toml` | Prompt human reviewer with rationale and dependency security review. |
| **Budget Exhaustion** | Reached $I_{\max}$ iterations without full test suite passing | Surface structured diagnostic log with failure points and ask for direction. |
