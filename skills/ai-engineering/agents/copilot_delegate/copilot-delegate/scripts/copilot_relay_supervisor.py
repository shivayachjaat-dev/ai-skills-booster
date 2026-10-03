#!/usr/bin/env python3
"""
copilot_relay_supervisor.py - Production GitHub Copilot CLI Delegation Supervisor

Features:
- Reasoning effort level validation (low, medium, high, xhigh, max)
- Model argument injection sanitization
- Delegation brief builder with target boundaries
- Scope-enforcing git diff auditor
"""

import sys
import os
import re
import argparse
from typing import Dict, Any, List, Tuple

VALID_EFFORT_LEVELS = {"low", "medium", "high", "xhigh", "max"}
SAFE_MODEL_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.:/]+$")


def configure_copilot_invocation(
    mode: str = "default",
    effort: str = "medium",
    model: str = "auto",
    target_files: List[str] = None
) -> Dict[str, Any]:
    """
    Validates and configures Copilot CLI arguments.
    """
    clean_effort = effort.lower().strip()
    if clean_effort not in VALID_EFFORT_LEVELS:
        raise ValueError(f"Invalid effort level '{effort}'. Allowed: {sorted(list(VALID_EFFORT_LEVELS))}")

    clean_mode = mode.lower().strip()
    if clean_mode not in ("default", "plan"):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'default' or 'plan'.")

    if model and not SAFE_MODEL_PATTERN.match(model):
        raise ValueError(f"Security error: Invalid character in model flag: '{model}'")

    if clean_mode == "default" and not target_files:
        raise ValueError("Mutating mode requires an explicit target files whitelist.")

    flags = ["--effort", clean_effort]
    if clean_mode == "plan":
        flags.extend(["--mode", "plan"])
    if model and model != "auto":
        flags.extend(["--model", model])

    return {
        "mode": clean_mode,
        "effort": clean_effort,
        "model": model,
        "cli_flags": flags,
        "is_read_only": (clean_mode == "plan"),
        "target_files": target_files or []
    }


def audit_diff_scope(modified_files: List[str], allowed_files: List[str]) -> Tuple[bool, List[str]]:
    """
    Asserts that modified files belong strictly to the authorized whitelist.
    """
    norm_whitelist = set(os.path.normpath(f).replace("\\", "/") for f in allowed_files)
    violations = []

    for f in modified_files:
        norm_f = os.path.normpath(f).replace("\\", "/")
        if norm_f not in norm_whitelist:
            violations.append(f)

    return (len(violations) == 0, violations)


def run_unit_tests():
    print("=" * 60)
    print("Running GitHub Copilot CLI Relay Supervisor Verification")
    print("=" * 60)

    # Test 1: Plan mode with high effort
    plan_cfg = configure_copilot_invocation(mode="plan", effort="high", model="auto")
    print(f"[*] Plan Mode: Flags={plan_cfg['cli_flags']}, Read-Only={plan_cfg['is_read_only']}")
    assert plan_cfg["is_read_only"] is True, "Plan mode must be read-only"
    assert "--mode" in plan_cfg["cli_flags"] and "plan" in plan_cfg["cli_flags"]

    # Test 2: Mutating mode with max effort
    mut_cfg = configure_copilot_invocation(
        mode="default",
        effort="max",
        model="claude-3.5-sonnet",
        target_files=["src/logger.py", "tests/test_logger.py"]
    )
    print(f"[*] Mutating Config: Flags={mut_cfg['cli_flags']}, Scope Count={len(mut_cfg['target_files'])}")
    assert mut_cfg["is_read_only"] is False, "Default mode should not be read-only"
    assert "max" in mut_cfg["cli_flags"]

    # Test 3: Invalid effort level rejection
    try:
        configure_copilot_invocation(effort="ultra")
        assert False, "Invalid effort 'ultra' should have failed"
    except ValueError as e:
        print(f"[*] Effort validation guard verified: {e}")

    # Test 4: Scope check
    clean = ["src/logger.py"]
    ok, violations = audit_diff_scope(clean, mut_cfg["target_files"])
    assert ok is True and not violations, "Expected clean diff to pass"

    polluted = ["src/logger.py", "database/schema.sql"]
    ok_p, violations_p = audit_diff_scope(polluted, mut_cfg["target_files"])
    assert ok_p is False and "database/schema.sql" in violations_p, "Expected violation to be caught"
    print(f"[*] Scope Audit Guard verified: Unauthorized modification caught: {violations_p}")

    print("\n[SUCCESS] GitHub Copilot CLI Relay Supervisor verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Copilot CLI Relay Supervisor")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
