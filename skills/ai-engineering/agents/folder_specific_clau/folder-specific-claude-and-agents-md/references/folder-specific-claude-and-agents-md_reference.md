# Folder-Specific Guidance Reference (CLAUDE.md & AGENTS.md)

## Scoped Instruction Architecture for Large Repositories

In modern monorepos and polyglot microservice codebases, relying solely on a monolithic root `AGENTS.md` leads to context window pollution and ambiguous instructions (e.g. telling an agent to run both `pytest` and `npm test` without directory scoping). Folder-scoped guidance resolves this by localizing rules to the subproject level.

### Hierarchical Resolution Model

```
<repo-root>/
├── AGENTS.md                   [Root Invariants: git rules, security policies]
├── packages/
│   ├── web-app/
│   │   ├── AGENTS.md           [Scoped: React, Next.js, npm test, lint]
│   │   └── src/
│   └── payment-api/
│       ├── AGENTS.md           [Scoped: FastAPI, pytest, DB migrations]
│       └── src/
```

### Hierarchy Precedence Invariants

1. **Child Extends Parent**: Folder-level `AGENTS.md` files inherit global constraints from the root `AGENTS.md` (e.g., zero secrets, branch naming conventions).
2. **Local Specificity**: When an agent executes commands inside `packages/web-app/`, the local test runner (`npm test`) overrides any generic root test instructions.
3. **Boundary Isolation**: Folder guidance explicitly defines import boundaries, preventing circular or unauthorized cross-package imports.
