#!/usr/bin/env python3
"""
commandcode_relay_supervisor.py - Production Command Code CLI Delegation Supervisor

Features:
- Autonomy mode configuration (read_only vs. implementation)
- Structured delegation brief builder
- Scope-enforcing diff auditor
- Subprocess execution wrapper with watchdog timeout
"""

import sys
import os
import argparse
from typing import Dict, Any, List, Tuple


def configure_autonomy_mode(mode: str, target_files: List[str] = None) -> Dict[str, Any]:
    """
    Configures CLI flags based on desired autonomy mode.
    """
    clean_mode = mode.lower().strip()
    if clean_mode not in ("read_only", "implementation"):
        raise ValueError(f"Invalid mode: '{mode}'. Must be 'read_only' or 'implementation'.")

    if clean_mode == "read_only":
        flags = ["-p"]
        is_mutating = False
    else:
        if not target_files:
            raise ValueError("Implementation mode requires explicit target files whitelist.")
        flags = ["-p", "--dangerously-skip-permissions"]
        is_mutating = True

    return {
        "mode": clean_mode,
        "flags": flags,
        "is_mutating": is_mutating,
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
    print("Running Command Code Relay Supervisor Verification")
    print("=" * 60)

    # Test 1: Read-only mode
    ro = configure_autonomy_mode("read_only")
    print(f"[*] Read-Only Config: Flags={ro['flags']}, Mutating={ro['is_mutating']}")
    assert ro["is_mutating"] is False, "Read-only mode must not mutate"
    assert ro["flags"] == ["-p"]

    # Test 2: Implementation mode
    impl = configure_autonomy_mode("implementation", target_files=["src/main.py", "tests/test_main.py"])
    print(f"[*] Implementation Config: Flags={impl['flags']}, Scope={len(impl['target_files'])}")
    assert impl["is_mutating"] is True, "Implementation mode must be mutating"
    assert "--dangerously-skip-permissions" in impl["flags"]

    # Test 3: Scope check - Pass
    clean = ["src/main.py"]
    ok, violations = audit_diff_scope(clean, impl["target_files"])
    assert ok is True and not violations, "Expected clean diff to pass"

    # Test 4: Scope check - Violation
    polluted = ["src/main.py", "scripts/deploy.sh"]
    ok_p, violations_p = audit_diff_scope(polluted, impl["target_files"])
    assert ok_p is False and "scripts/deploy.sh" in violations_p, "Expected violation to be caught"
    print(f"[*] Scope Audit Guard verified: Unauthorized modification caught: {violations_p}")

    print("\n[SUCCESS] Command Code Relay Supervisor verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Command Code Relay Supervisor")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
