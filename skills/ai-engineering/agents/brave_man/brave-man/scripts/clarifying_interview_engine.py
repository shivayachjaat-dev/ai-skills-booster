#!/usr/bin/env python3
"""
clarifying_interview_engine.py - Production Pre-Build Interview & Specification Engine

Features:
- Project complexity triage calibration (calculates required interview depth)
- Batched question generation across 5 discovery phases
- Automated prompt.md execution spec synthesis
- Verification acceptance harness check
"""

import sys
import os
import argparse
from typing import List, Dict, Any, Optional


def calibrate_triage_depth(
    is_multi_user: bool,
    has_database_state: bool,
    has_external_auth: bool,
    estimated_views_or_endpoints: int
) -> Dict[str, Any]:
    """
    Calibrates how deep the discovery interview must be to prevent costly assumptions.
    """
    score = 1
    if is_multi_user:
        score += 1
    if has_database_state:
        score += 1
    if has_external_auth:
        score += 1
    if estimated_views_or_endpoints > 5:
        score += 1

    depth_label = (
        "DEEP_MULTI_TIER" if score >= 4
        else "STANDARD_MODULAR" if score >= 2
        else "LIGHTWEIGHT_SCRIPT"
    )

    phases_needed = ["Phase 0: Triage", "Phase 1: Purpose"]
    if score >= 2:
        phases_needed.extend(["Phase 2: User Flows", "Phase 3: Data Model"])
    if score >= 4:
        phases_needed.append("Phase 4: Non-Functional & Security")

    return {
        "complexity_score": score,
        "interview_depth": depth_label,
        "required_phases": phases_needed,
        "skip_auth_questions": not has_external_auth
    }


def synthesize_prompt_spec(
    project_name: str,
    target_users: str,
    core_purpose: str,
    mvp_features: List[str],
    out_of_scope: List[str],
    tech_stack: List[str],
    verification_commands: List[str]
) -> str:
    """
    Synthesizes a complete, production-grade prompt.md specification.
    """
    doc = [
        f"# Execution Specification: {project_name}",
        "",
        "## 1. Executive Summary & Purpose",
        f"- **Target Users**: {target_users}",
        f"- **Primary Value Proposition**: {core_purpose}",
        "",
        "## 2. In-Scope MVP Deliverables",
    ]
    for feat in mvp_features:
        doc.append(f"- [ ] {feat}")

    doc.append("\n## 3. Explicit Out-of-Scope (Do NOT Build in v1)")
    for oos in out_of_scope:
        doc.append(f"- {oos}")

    doc.append("\n## 4. Technical Constraints & Architecture")
    for t in tech_stack:
        doc.append(f"- {t}")

    doc.append("\n## 5. Verification Commands & Acceptance Criteria")
    for cmd in verification_commands:
        doc.append(f"```bash\n{cmd}\n```")

    return "\n".join(doc)


def run_unit_tests():
    print("=" * 60)
    print("Running Pre-Build Interview & Spec Engine Verification")
    print("=" * 60)

    # Test 1: Lightweight script triage
    light = calibrate_triage_depth(False, False, False, 1)
    print(f"[*] Lightweight Triage: Score={light['complexity_score']}, Depth={light['interview_depth']}")
    assert light["interview_depth"] == "LIGHTWEIGHT_SCRIPT", "Expected LIGHTWEIGHT_SCRIPT"

    # Test 2: Multi-tier complex system triage
    heavy = calibrate_triage_depth(True, True, True, 10)
    print(f"[*] Complex Triage: Score={heavy['complexity_score']}, Depth={heavy['interview_depth']}")
    assert heavy["interview_depth"] == "DEEP_MULTI_TIER", "Expected DEEP_MULTI_TIER"
    assert len(heavy["required_phases"]) == 5, "Expected all 5 phases for complex system"

    # Test 3: Spec synthesis
    spec_md = synthesize_prompt_spec(
        project_name="Autonomous Task Queue",
        target_users="Backend engineers",
        core_purpose="Reliable FIFO background processing with Redis",
        mvp_features=["Enqueue job", "Worker poll", "Dead letter queue"],
        out_of_scope=["Web dashboard", "Billing integrations"],
        tech_stack=["Python 3.11", "Redis", "Pytest"],
        verification_commands=["pytest tests/test_queue.py"]
    )
    print("[*] Spec Synthesis Test: Generated length =", len(spec_md))
    assert "## 2. In-Scope MVP Deliverables" in spec_md
    assert "pytest tests/test_queue.py" in spec_md
    assert "Dead letter queue" in spec_md

    print("\n[SUCCESS] Pre-Build Clarification Engine verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Pre-Build Clarification & Specification Engine")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
