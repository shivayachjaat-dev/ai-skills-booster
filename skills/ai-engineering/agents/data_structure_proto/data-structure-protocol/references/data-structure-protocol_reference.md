# Data Structure Protocol (DSP) Technical Reference

## 1. Structural Map vs. AST Dumps

Conventional AST parsing provides fine-grained syntactic tokens (operators, variable names, line numbers) that flood an agent's context window with excessive detail. DSP operates at a higher abstraction level:

| Feature | Raw AST Parse | Data Structure Protocol (DSP) |
| :--- | :--- | :--- |
| **Token Cost** | $10,000 - 50,000\text{ tokens}$ per large file | $< 500\text{ tokens}$ per entity node |
| **Identity Persistence**| Tied to file path & line numbers | Stable 8-hex UIDs anchored by annotations |
| **Dependency Context** | Raw import strings (`from X import Y`) | Explicit operational rationales (*why* $Y$ is needed) |
| **Impact Analysis** | Requires re-parsing every repository file | $O(V + E)$ breadth-first graph traversal |

---

## 2. Directory Schema (`.dsp/`)

The persistent graph is serialized into standard lightweight text and JSON records:

```
.dsp/
├── TOC                        # Plaintext list of all active entity UIDs
├── entities/
│   ├── obj-4a1b8c2e/
│   │   ├── meta.json          # Entity metadata, file location, exports
│   │   └── imports.json       # Outgoing dependency edges with rationales
└── reverse_index/
    └── obj-9e2d1f4b/
        └── dependents.json    # Ingoing dependency edges (who relies on this)
```

---

## 3. Blast Radius Traversal Algorithm

When an agent proposes modifying an existing class or function:
1. Lookup the target entity UID in `.dsp/reverse_index/`.
2. Execute breadth-first search across downstream dependents.
3. Compute the **Blast Radius Coefficient**:
$$\text{BR} = \frac{|\text{Impacted Dependents}|}{|\text{Total Codebase Entities}|}$$
- If $\text{BR} > 0.15$ (more than 15% of the codebase depends on this node), the agent is instructed to avoid breaking signature changes and maintain backward-compatible overloads.
