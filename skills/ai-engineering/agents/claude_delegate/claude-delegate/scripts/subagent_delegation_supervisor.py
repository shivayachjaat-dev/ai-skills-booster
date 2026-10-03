#!/usr/bin/env python3
"""
subagent_delegation_supervisor.py - Production Subagent Delegation & Supervision Engine

Features:
- Self-contained delegation brief generator & schema validator
- Subprocess watchdog runner with timeout protection
- Git diff boundary auditor (whitelist scope enforcement)
- Landing gate verification
"""

import sys
import os
import subprocess
import argparse
from typing import List, Dict, Any, Tuple


def generate_delegation_brief(
    task_id: str,
    objective: str,
    target_files: List[str],
    verification_command: str,
    timeout_seconds: int = 120
) -> Dict[str, Any]:
    """
    Constructs a structured delegation brief for subordinate processes.
    """
    if not objective or not target_files:
        raise ValueError("Objective and target files must be specified")

    rendered = [
        f"# SUBAGENT DELEGATION TASK [{task_id}]",
        f"Goal: {objective}",
        "",
        "Authorized Scope (Files allowed to be modified):"
    ]
    for tf in target_files:
        rendered.append(f"  - {tf}")
    rendered.append("")
    rendered.append(f"Verification Command: {verification_command}")
    rendered.append("Instructions: Complete implementation and verify tests before exiting.")

    return {
        "task_id": task_id,
        "objective": objective,
        "target_files": target_files,
        "verification_command": verification_command,
        "timeout_seconds": timeout_seconds,
        "rendered_markdown": "\n".join(rendered)
    }


def audit_diff_scope(
    modified_files: List[str],
    allowed_whitelist: List[str]
) -> Tuple[bool, List[str]]:
    """
    Verifies that all modified files belong strictly to the authorized scope.
    """
    violations = []
    norm_whitelist = set(os.path.normpath(f).replace("\\", "/") for f in allowed_whitelist)

    for mf in modified_files:
        norm_mf = os.path.normpath(mf).replace("\\", "/")
        if norm_mf not in norm_whitelist:
            violations.append(mf)

    return (len(violations) == 0, violations)


def execute_subordinate_with_watchdog(
    cmd: List[str],
    input_text: str = "",
    timeout: int = 10
) -> Tuple[int, str, str]:
    """
    Executes a command with a strict timeout.
    """
    try:
        proc = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout expired after {timeout} seconds"
    except Exception as e:
        return -2, "", str(e)


def run_unit_tests():
    print("=" * 60)
    print("Running Subagent Delegation Supervisor Verification")
    print("=" * 60)

    # Test 1: Brief generation
    brief = generate_delegation_brief(
        task_id="TASK-881",
        objective="Implement rate-limiting middleware in Redis",
        target_files=["src/middleware/rate_limiter.py", "tests/test_rate_limiter.py"],
        verification_command="pytest tests/test_rate_limiter.py"
    )
    print(f"[*] Brief Generation: Task ID={brief['task_id']}, Target Files={len(brief['target_files'])}")
    assert "Authorized Scope" in brief["rendered_markdown"], "Brief formatting failed"

    # Test 2: Diff scope audit - Clean
    clean_mods = ["src/middleware/rate_limiter.py", "tests/test_rate_limiter.py"]
    ok, violations = audit_diff_scope(clean_mods, brief["target_files"])
    print(f"[*] Clean Scope Check: Violations={violations}")
    assert ok is True and not violations, "Expected clean scope check to pass"

    # Test 3: Diff scope audit - Scope creep violation
    polluted_mods = [
        "src/middleware/rate_limiter.py",
        "config/production_secrets.json",
        "package.json"
    ]
    ok_creep, violations_creep = audit_diff_scope(polluted_mods, brief["target_files"])
    print(f"[*] Scope Creep Check: Blocked={not ok_creep}, Violations={violations_creep}")
    assert ok_creep is False and len(violations_creep) == 2, "Expected scope violations to be detected"

    # Test 4: Subprocess watchdog execution (fast command)
    code, out, err = execute_subordinate_with_watchdog([sys.executable, "-c", "print('SUBAGENT_READY')"], timeout=5)
    print(f"[*] Watchdog Fast Execution: Exit Code={code}, Output={out.strip()}")
    assert code == 0 and "SUBAGENT_READY" in out, "Watchdog execution failed"

    print("\n[SUCCESS] Subagent Delegation Supervisor verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Subagent Delegation Supervisor")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
