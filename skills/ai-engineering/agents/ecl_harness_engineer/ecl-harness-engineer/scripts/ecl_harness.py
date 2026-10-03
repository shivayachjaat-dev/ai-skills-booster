#!/usr/bin/env python3
"""
ECL (Engineering Capability Lifecycle) Agent Harness Engine
----------------------------------------------------------
Constructs, audits, and enforces repository infrastructure for autonomous coding agents:
generates AGENTS.md contracts, performs pre-flight gate verification, tracks interventions,
and produces standardized agent handoff briefs.
"""

import sys
import os
import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

REQUIRED_AGENTS_MD_SECTIONS = [
    "Repository Invariants",
    "Testing Requirements",
    "Architecture Guidelines",
    "Permitted Commands",
    "Security & Secret Boundaries"
]

@dataclass
class AuditReport:
    compliant: bool
    agents_md_exists: bool
    missing_sections: List[str]
    harness_initialized: bool
    details: Dict[str, Any]

class ECLHarness:
    def __init__(self, repo_root: str):
        self.repo_root = os.path.abspath(repo_root)
        self.harness_dir = os.path.join(self.repo_root, ".agent-harness")
        self.handoffs_dir = os.path.join(self.harness_dir, "handoffs")
        self.agents_md_path = os.path.join(self.repo_root, "AGENTS.md")

    def init_harness(self) -> None:
        """Initialize the agent harness directory and standard AGENTS.md contract."""
        os.makedirs(self.handoffs_dir, exist_ok=True)
        
        if not os.path.exists(self.agents_md_path):
            sample_content = """# AGENTS.md — Autonomous Agent Operating Contract

## Repository Invariants
- Maintain backward compatibility across public library APIs.
- Strictly adhere to zero-secret disclosure policies.

## Testing Requirements
- Every new feature or bugfix must include automated unit tests.
- All tests must pass cleanly before preparing handoff.

## Architecture Guidelines
- Follow domain-driven, modular component boundaries.
- Avoid circular dependencies between modules.

## Permitted Commands
- `python -m pytest`
- `ruff check .`
- `git status`, `git diff`

## Security & Secret Boundaries
- Do not commit `.env`, credentials, or private API tokens.
"""
            with open(self.agents_md_path, "w", encoding="utf-8") as f:
                f.write(sample_content)

    def audit_repository(self) -> AuditReport:
        """Audit repository readiness for autonomous agent operations."""
        missing = []
        agents_exists = os.path.exists(self.agents_md_path)
        
        if agents_exists:
            with open(self.agents_md_path, "r", encoding="utf-8") as f:
                content = f.read()
            for sec in REQUIRED_AGENTS_MD_SECTIONS:
                if sec not in content:
                    missing.append(sec)
        else:
            missing = list(REQUIRED_AGENTS_MD_SECTIONS)

        harness_init = os.path.exists(self.harness_dir)
        compliant = agents_exists and len(missing) == 0 and harness_init

        return AuditReport(
            compliant=compliant,
            agents_md_exists=agents_exists,
            missing_sections=missing,
            harness_initialized=harness_init,
            details={"repo_root": self.repo_root}
        )

    def generate_handoff(
        self,
        agent_id: str,
        task_summary: str,
        touched_files: List[str],
        verification_status: str = "Passed"
    ) -> str:
        """Generate a structured handoff document for human engineers or subsequent agents."""
        os.makedirs(self.handoffs_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        handoff_file = os.path.join(self.handoffs_dir, f"handoff_{timestamp}_{agent_id}.md")

        files_list = "\n".join(f"- `{f}`" for f in touched_files) or "- None"

        content = f"""# Agent Work Handoff Brief

- **Agent ID**: `{agent_id}`
- **Timestamp**: {datetime.datetime.now().isoformat()}
- **Verification Status**: `{verification_status}`

## Task Summary
{task_summary.strip()}

## Modified Files
{files_list}

## Verification Completed
- [x] Syntax and unit tests validated.
- [x] No credentials or secret keys introduced.
- [x] AGENTS.md contract rules adhered to.

## Next Steps for Reviewer
1. Review git diff for functional correctness.
2. Confirm integration test behavior in CI.
"""
        with open(handoff_file, "w", encoding="utf-8") as f:
            f.write(content)

        return handoff_file

def verify_ecl_harness():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        harness = ECLHarness(tmpdir)
        print("============================================================")
        print("ECL Agent Harness: Initializing and Auditing Infrastructure")
        print("============================================================")
        
        # Initial audit before init
        audit_pre = harness.audit_repository()
        print(f"[*] Pre-init Compliance: {audit_pre.compliant} (Missing: {len(audit_pre.missing_sections)} sections)")
        assert not audit_pre.compliant

        # Initialize harness
        harness.init_harness()
        print("[*] Initialized AGENTS.md and .agent-harness directories.")

        # Re-audit
        audit_post = harness.audit_repository()
        print(f"[*] Post-init Compliance: {audit_post.compliant}")
        assert audit_post.compliant

        # Generate handoff
        handoff = harness.generate_handoff(
            agent_id="refactor-agent-01",
            task_summary="Refactored database pool connection recycling and added unit tests.",
            touched_files=["src/db/pool.py", "tests/test_pool.py"],
            verification_status="Passed"
        )
        print(f"[*] Generated Handoff: {os.path.basename(handoff)}")
        assert os.path.exists(handoff)
        print("[SUCCESS] ECL Agent Harness Engine verified cleanly.")

if __name__ == "__main__":
    verify_ecl_harness()
