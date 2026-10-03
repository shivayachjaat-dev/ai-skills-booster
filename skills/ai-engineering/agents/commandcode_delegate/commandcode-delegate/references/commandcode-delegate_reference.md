# Command Code CLI Delegation & Autonomy Model Technical Reference

## 1. Headless Autonomy Permissions Architecture

The Command Code CLI (`cmd` / `cmdc`) implements a binary permission model in headless non-interactive mode:

| Mode | Invocation Arguments | Tool Capabilities | Security Boundary |
| :--- | :--- | :--- | :--- |
| **Read-Only / Probe** | `-p` | Read, grep, glob | Zero mutation risk; writes refused by CLI permission layer |
| **Full Autonomy (Act)** | `-p --dangerously-skip-permissions` | Read, edit, create, delete, shell execution | Full filesystem access; requires strict worktree confinement |

Flags such as `--permission-mode auto-accept` do not bypass headless write blocks; only `--dangerously-skip-permissions` enables automated file mutation in headless processes.

---

## 2. Working Tree Scope Isolation

Because Command Code does not enforce internal path jails, the orchestrating agent is responsible for bounding execution:
1. **Target Whitelisting**: The brief explicitly lists authorized files.
2. **Post-Execution Forensic Audit**: The orchestrator inspects `git diff --name-only` immediately upon subagent exit.
3. **Rollback Policy**: If any out-of-scope file was altered, the orchestrator issues `git checkout -- .` and halts the pipeline.

---

## 3. Pre-Landing Verification Gate

A change produced by Command Code is merged if and only if:
- All modified files match the authorized brief scope.
- Automated tests covering the modified functions pass with exit code 0.
- No secrets, credentials, or transient logs were added to git tracking.
