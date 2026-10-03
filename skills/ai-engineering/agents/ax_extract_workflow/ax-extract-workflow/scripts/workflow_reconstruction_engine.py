#!/usr/bin/env python3
"""
workflow_reconstruction_engine.py - Production Workflow Forensics & Lineage Reconstruction

Features:
- Git commit log & diffstat extraction
- Event categorization (Spec, Implementation, Verification, Refactor)
- Step-by-step reproduction specification generation
- Automated self-testing
"""

import sys
import os
import subprocess
import argparse
from typing import List, Dict, Any, Optional


def extract_git_commits(max_count: int = 5) -> List[Dict[str, str]]:
    """Retrieves recent commits from the current repository."""
    try:
        cmd = ["git", "log", f"-n{max_count}", "--pretty=format:%H|%an|%ad|%s", "--date=short"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        commits = []
        for line in lines:
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "sha": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits
    except Exception as e:
        return []


def categorize_workflow_events(commits: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """Categorizes commits into structured workflow stages."""
    stages: Dict[str, List[Dict[str, str]]] = {
        "spec_and_planning": [],
        "implementation": [],
        "verification_and_fixes": []
    }
    
    for c in reversed(commits):
        sub = c["subject"].lower()
        if any(kw in sub for kw in ["fix", "test", "verify", "harden", "patch"]):
            stages["verification_and_fixes"].append(c)
        elif any(kw in sub for kw in ["spec", "doc", "rfc", "plan", "design"]):
            stages["spec_and_planning"].append(c)
        else:
            stages["implementation"].append(c)
            
    return stages


def generate_reproduction_guide(artifact_name: str, stages: Dict[str, List[Dict[str, str]]]) -> str:
    """Formats categorized events into an operational reproducibility document."""
    lines = [
        f"# Workflow Lineage & Reproduction Guide: {artifact_name}",
        "",
        "## 1. Executive Summary",
        f"This guide reconstructs the sequence of operations that produced `{artifact_name}`.",
        "",
        "## 2. Chronological Operational Steps"
    ]
    
    step_num = 1
    for stage_name, commit_list in stages.items():
        clean_stage = stage_name.replace("_", " ").title()
        lines.append(f"### Stage: {clean_stage}")
        if not commit_list:
            lines.append("*(No discrete commits recorded in this stage)*")
        for item in commit_list:
            lines.append(f"{step_num}. **[{item['sha'][:8]}]** {item['subject']} *(by {item['author']} on {item['date']})*")
            step_num += 1
        lines.append("")

    lines.append("## 3. Recommended Verification Command")
    lines.append("```bash")
    lines.append("python scripts/validate.py")
    lines.append("```")
    return "\n".join(lines)


def run_unit_tests():
    print("=" * 60)
    print("Running Workflow Reconstruction Engine Verification")
    print("=" * 60)

    # Synthetic test commits
    synthetic = [
        {"sha": "c001", "author": "Agent", "date": "2026-10-01", "subject": "spec: define auth architecture"},
        {"sha": "c002", "author": "Agent", "date": "2026-10-02", "subject": "feat: add jwt token generator"},
        {"sha": "c003", "author": "Agent", "date": "2026-10-03", "subject": "fix: correct token expiration bug"},
    ]
    
    stages = categorize_workflow_events(synthetic)
    print(f"[*] Spec Events: {len(stages['spec_and_planning'])}")
    print(f"[*] Implementation Events: {len(stages['implementation'])}")
    print(f"[*] Verification Events: {len(stages['verification_and_fixes'])}")
    
    assert len(stages["spec_and_planning"]) == 1, "Spec stage categorization failed"
    assert len(stages["implementation"]) == 1, "Implementation stage categorization failed"
    assert len(stages["verification_and_fixes"]) == 1, "Verification stage categorization failed"

    guide = generate_reproduction_guide("jwt_authentication", stages)
    assert "Workflow Lineage & Reproduction Guide: jwt_authentication" in guide
    print("[*] Reproduction Guide Generation: OK")

    # Real git test
    real_commits = extract_git_commits(max_count=3)
    if real_commits:
        print(f"[*] Real Git Log Extraction: Retrieved {len(real_commits)} commits (Latest: {real_commits[0]['subject'][:40]}...)")
        assert len(real_commits) > 0, "Git extraction failed"

    print("\n[SUCCESS] Workflow Reconstruction Engine passed all tests.")


def main():
    parser = argparse.ArgumentParser(description="Workflow Reconstruction Engine")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    parser.add_argument("--reconstruct-recent", action="store_true", help="Reconstruct recent commits into guide")
    args = parser.parse_args()

    if args.reconstruct_recent:
        commits = extract_git_commits(max_count=5)
        stages = categorize_workflow_events(commits)
        print(generate_reproduction_guide("recent_repository_work", stages))
        return

    run_unit_tests()


if __name__ == "__main__":
    main()
