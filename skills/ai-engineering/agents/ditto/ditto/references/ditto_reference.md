# Ditto Developer Profile Mining Reference

## Architecture & Work-Pattern Extraction Specification

**Ditto** is a privacy-first autonomous behavioral profiler designed to run on local developer environments. By indexing interaction histories across AI coding agent tools (Claude Code, GitHub Copilot CLI, Gemini Code Assist, OpenCode), Ditto surfaces actionable developer profiles without exporting source code or sensitive tokens to external clouds.

### Interaction Extraction Pipeline

```
+------------------------------------------------------------------------+
|                     Ditto Ingestion & Sanitization                     |
|                                                                        |
|  [ Agent Transcript / Shell History ]                                  |
|            |                                                           |
|            v                                                           |
|  [ Privacy Redaction Filter ]                                          |
|      - Regex token scrubbing (API keys, bearer auth, GitHub PATs)      |
|      - Filesystem user path anonymization                              |
|            |                                                           |
|            v                                                           |
|  [ Behavioral Feature Extraction ]                                     |
|      - Command frequencies (git, docker, test runners)                 |
|      - Test-Driven Development (TDD) index: test_runs / file_edits     |
|      - Technology and framework affinity detection                     |
|            |                                                           |
|            v                                                           |
|  [ Persona / Profile Synthesis ] ---> .ditto/profile.json              |
+------------------------------------------------------------------------+
```

### Developer Archetypes

| Archetype Name | Dominant Signals | Typical Toolchain |
| :--- | :--- | :--- |
| `Test-Driven Quality Engineer` | TDD ratio >= 0.5, frequent test assertions | `pytest`, `vitest`, `cargo test`, `coverage` |
| `Systems & Infrastructure Architect` | Containerization, kernel/system tooling | `docker`, `docker-compose`, `terraform`, `cargo`, `k8s` |
| `Full-Stack Application Builder` | Web framework commands, route/UI edits | `FastAPI`, `React`, `Next.js`, `npm`, `vite` |

### Zero-Disclosure Privacy Guarantees

1. **No External Network Egress**: Ditto computes profiles strictly locally in-memory or persists to a local workspace file (`.ditto/profile.json`).
2. **Deterministic Redaction**: All token patterns matching `sk-[a-zA-Z0-9]+`, `ghp_[a-zA-Z0-9]+`, or `api_key=...` are replaced with `[REDACTED_CREDENTIAL]` prior to feature extraction.
3. **Identity Decoupling**: Local filesystem absolute paths containing user home directories are scrubbed to generic placeholders.
