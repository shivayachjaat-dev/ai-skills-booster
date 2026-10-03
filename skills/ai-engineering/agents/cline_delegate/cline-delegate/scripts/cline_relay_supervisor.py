#!/usr/bin/env python3
"""
cline_relay_supervisor.py - Production Cline CLI Delegation & Supervision Engine

Features:
- Plan vs. Act mode gating
- Model & provider argument injection sanitization
- Delegation brief formatting
- Scope-enforcing diff auditor
"""

import sys
import os
import re
import argparse
from typing import Dict, Any, List, Tuple

SAFE_FLAG_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.:/]+$")


def validate_cline_invocation(
    mode: str,
    model: str = "",
    provider: str = "",
    target_files: List[str] = None
) -> Dict[str, Any]:
    """
    Sanitizes and constructs Cline CLI invocation flags.
    """
    clean_mode = mode.lower().strip()
    if clean_mode not in ("plan", "act"):
        raise ValueError(f"Invalid execution mode: '{mode}'. Must be 'plan' or 'act'.")

    for field_name, val in [("model", model), ("provider", provider)]:
        if val and not SAFE_FLAG_PATTERN.match(val):
            raise ValueError(f"Security error: Invalid character in {field_name}: '{val}'")

    if clean_mode == "act" and not target_files:
        raise ValueError("Act mode requires an explicit target files whitelist.")

    flags = [f"--{clean_mode}"]
    if model:
        flags.extend(["--model", model])
    if provider:
        flags.extend(["--provider", provider])

    return {
        "mode": clean_mode,
        "model": model,
        "provider": provider,
        "cli_flags": flags,
        "is_read_only": (clean_mode == "plan"),
        "target_files": target_files or []
    }


def audit_working_tree_scope(modified_files: List[str], allowed_files: List[str]) -> Tuple[bool, List[str]]:
    """
    Asserts all modified files belong strictly to the permitted whitelist.
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
    print("Running Cline CLI Relay Supervisor Verification")
    print("=" * 60)

    # Test 1: Plan mode (read-only)
    plan_cfg = validate_cline_invocation("plan", model="claude-3-5-sonnet", provider="anthropic")
    print(f"[*] Plan Mode: Flags={plan_cfg['cli_flags']}, Read-Only={plan_cfg['is_read_only']}")
    assert plan_cfg["is_read_only"] is True, "Plan mode must be read-only"
    assert "--plan" in plan_cfg["cli_flags"]

    # Test 2: Act mode with authorized scope
    act_cfg = validate_cline_invocation(
        "act",
        model="gpt-4o",
        provider="openai-native",
        target_files=["src/auth.py", "tests/test_auth.py"]
    )
    print(f"[*] Act Mode: Flags={act_cfg['cli_flags']}, Scope Count={len(act_cfg['target_files'])}")
    assert act_cfg["is_read_only"] is False, "Act mode should not be read-only"

    # Test 3: Injection attempt in model argument
    try:
        validate_cline_invocation("plan", model="model; rm -rf /")
        assert False, "Injection argument should have raised ValueError"
    except ValueError as e:
        print(f"[*] Command injection guard verified: {e}")

    # Test 4: Scope boundary check
    clean_mods = ["src/auth.py"]
    ok, violations = audit_working_tree_scope(clean_mods, act_cfg["target_files"])
    assert ok is True and not violations, "Clean diff should pass"

    polluted_mods = ["src/auth.py", "package.json"]
    ok_p, violations_p = audit_working_tree_scope(polluted_mods, act_cfg["target_files"])
    assert ok_p is False and "package.json" in violations_p, "Polluted diff must be caught"
    print(f"[*] Scope Audit Guard verified: Unauthorized file detected: {violations_p}")

    print("\n[SUCCESS] Cline CLI Relay Supervisor verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Cline CLI Relay Supervisor")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
