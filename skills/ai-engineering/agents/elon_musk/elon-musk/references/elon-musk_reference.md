# First-Principles & Complexity Reduction Engineering Reference

## Foundations of First-Principles Reasoning in Software Systems

First-principles thinking involves boiling a problem down to its fundamental truths and reasoning upward from there, rather than reasoning by analogy. In software engineering, analogy often manifests as copying complex enterprise patterns (e.g., "Company X uses 40 microservices, so we should too").

### The 5-Step Engineering Algorithm

1. **Question Every Requirement**: Every requirement must be owned by an identifiable person, not an abstract team or department. Every constraint must be challenged.
2. **Delete the Part or Process**: If parts or stages are not being added back at least 10% of the time, the deletion bias is insufficient.
3. **Simplify or Optimize**: Crucially, never optimize a process or microservice that should not exist in the first place.
4. **Accelerate Cycle Time**: Once unnecessary steps are eliminated, streamline feedback loops, deployment cycles, and testing suites.
5. **Automate**: Automate only as the final step. Automating an inefficient process merely produces faster waste.

### Architecture Complexity Heuristics

| Smell / Anti-Pattern | First-Principles Critique | Remediation |
| :--- | :--- | :--- |
| **Wrapper Services** | Adds serial network hops, JSON serialization, and failure domains. | Direct in-process calls or standard reverse proxies. |
| **Premature Event Buses** | High operational overhead for low-throughput CRUD applications. | Direct database transactions until scale warrants queues. |
| **Multi-layer DTO Mapping** | Repeated translation between identical data schemas. | Unified typed domain models with validation at the boundary. |
