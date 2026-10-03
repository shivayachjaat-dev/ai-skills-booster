# Autonomous AI Agent Frameworks & Evaluation Reference

## Multi-Agent Framework Comparison Matrix
| Framework | Primary Abstraction | State Management | Multi-Agent Protocol | Tool Calling Standard | Best Suited For |
|---|---|---|---|---|---|
| **LangGraph** | Cyclic StateGraph | Checkpointed Postgres/SQLite | Message passing via State | Pydantic / LangChain Tools | Complex enterprise workflows, human-in-the-loop |
| **CrewAI** | Role-based Crew | In-memory / Chroma vector memory | Hierarchical / Sequential delegate | LangChain / Custom Python tools | Collaborative agent teams with specific roles |
| **AutoGen** | ConversableAgent | In-memory message history | Multi-agent conversation loops | Python functions / Docker exec | Multi-agent debate, code execution sandboxing |
| **Semantic Kernel** | Kernel Plugins & Planners | Volatile / Distributed cache | Native orchestration | OpenAPI / Native functions | C# / .NET enterprise integrations |
| **LlamaIndex Workflows** | Event-driven EventStream | Step context snapshots | Async event emitters | LlamaHub tool specs | RAG-heavy document reasoning agents |

## Agent Security & Sandboxing Checklist
1. **Container Isolation**:
   - Run code execution tools inside non-root Docker containers with `--read-only` root filesystems and mounted temporary volumes.
   - Restrict outbound egress network traffic (`--network internal`) unless specific API domains are allowlisted.
2. **Human-in-the-Loop Approval Gates**:
   - Classify tools into `READ_ONLY` vs `WRITE_STATE` vs `DESTRUCTIVE`.
   - All `DESTRUCTIVE` tools (e.g. file deletion, database modification, payment authorization) require interactive terminal approval before execution.
3. **Memory Boundary Separation**:
   - Prevent cross-session data leakage by partitioning episodic checkpoints with tenant-scoped UUIDs.
