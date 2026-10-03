# Agent Session Continuity & Context Memory Technical Reference

## 1. Context Retention vs. Token Economics

As conversational history expands, reloading raw conversation transcripts into fresh sessions causes two severe problems:
1. **Financial Waste**: Re-injecting 100k tokens on every turn multiplies API costs unnecessarily.
2. **Attention Degradation**: Needle-in-a-haystack recall worsens when the context window is stuffed with discarded code snippets, syntax fixes, and debugging output.

### The Compaction Solution:
Extract only the semantic state transitions:
$$\Delta S = \langle \text{Decisions}, \text{ModifiedFiles}, \text{PendingTasks}, \text{KnownBugs} \rangle$$

Compressing a 100k-token session into a 1k-token structured briefing achieves a **99% context reduction** while retaining 100% of actionable decision state.

---

## 2. Checkpoint Serialization & Integrity

Session snapshots are persisted in structured JSON or SQLite records:
- **Immutable Timestamping**: Checkpoint files are keyed by ISO 8601 UTC timestamps.
- **Secret Scrubbing**: Automated regex filters purge authorization headers and API tokens prior to writing.
- **Durable Milestone Log (`MEMORY.md`)**: High-level achievements are appended to a human-readable markdown log in the repository root.

---

## 3. Cold-Start Briefing Protocol

When an agent initializes in a new process or branch, it loads the most recent briefing:
1. Review locked decisions to avoid debating established technical directions.
2. Check modified files list to understand recent working tree edits.
3. Resume the top item on the active pending tasks checklist.
