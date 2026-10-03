#!/usr/bin/env python3
"""
ai_loop_orchestrator.py - Production State-Machine Engine for Autonomous Spec-Build-Review Loops

Implements:
- Finite State Machine: SPEC -> BUILD -> REVIEW -> TERMINATE
- Iteration budgeting and early termination guards
- Scope confinement (whitelist verification)
- Human approval escalation hooks
- Failure telemetry and diagnostics
"""

import sys
import os
import fnmatch
import argparse
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple


class LoopState(Enum):
    INIT = "INIT"
    SPEC = "SPEC"
    BUILD = "BUILD"
    REVIEW = "REVIEW"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    COMPLETED = "COMPLETED"
    EXHAUSTED = "EXHAUSTED"
    ABORTED = "ABORTED"


@dataclass
class SpecContract:
    objective: str
    requirements: List[str]
    allowed_patterns: List[str]
    max_iterations: int = 3
    require_human_gate: bool = False


@dataclass
class IterationRecord:
    iteration_index: int
    modified_files: List[str]
    verification_passed: bool
    diagnostics: str


class AILoopEngine:
    def __init__(self, spec: SpecContract):
        self.spec = spec
        self.state = LoopState.INIT
        self.current_iteration = 0
        self.history: List[IterationRecord] = []

    def validate_file_scope(self, files: List[str]) -> Tuple[bool, Optional[str]]:
        """Validates that modified files strictly obey the whitelist patterns."""
        for f in files:
            norm = f.replace("\\", "/")
            matched = any(fnmatch.fnmatch(norm, pattern) for pattern in self.spec.allowed_patterns)
            if not matched:
                return False, f"File '{f}' violates scope boundaries. Permitted: {self.spec.allowed_patterns}"
        return True, None

    def start(self) -> LoopState:
        """Transitions from INIT to SPEC to BUILD/APPROVAL."""
        if not self.spec.objective or not self.spec.requirements:
            self.state = LoopState.ABORTED
            return self.state

        self.state = LoopState.SPEC

        if self.spec.require_human_gate:
            self.state = LoopState.APPROVAL_REQUIRED
            return self.state

        self.state = LoopState.BUILD
        return self.state

    def submit_build_iteration(
        self,
        modified_files: List[str],
        simulated_test_pass: bool,
        test_output: str
    ) -> LoopState:
        """
        Processes a build iteration, validates file scope, and evaluates test outcomes.
        """
        self.current_iteration += 1

        # Check scope
        in_scope, err = self.validate_file_scope(modified_files)
        if not in_scope:
            self.state = LoopState.ABORTED
            self.history.append(IterationRecord(
                iteration_index=self.current_iteration,
                modified_files=modified_files,
                verification_passed=False,
                diagnostics=f"CRITICAL: Scope boundary violation: {err}"
            ))
            return self.state

        # Record test review
        record = IterationRecord(
            iteration_index=self.current_iteration,
            modified_files=modified_files,
            verification_passed=simulated_test_pass,
            diagnostics=test_output
        )
        self.history.append(record)

        if simulated_test_pass:
            self.state = LoopState.COMPLETED
            return self.state

        if self.current_iteration >= self.spec.max_iterations:
            self.state = LoopState.EXHAUSTED
            return self.state

        # Loop continues back to BUILD
        self.state = LoopState.BUILD
        return self.state


def run_unit_tests():
    print("=" * 60)
    print("Running AI Loop State Machine & Scope Confinement Verification")
    print("=" * 60)

    # Test 1: Successful converged loop
    spec_happy = SpecContract(
        objective="Implement string sanitization utility",
        requirements=["Strip control chars", "Escape HTML entities"],
        allowed_patterns=["src/utils/*.py", "tests/*.py"],
        max_iterations=3
    )
    engine = AILoopEngine(spec_happy)
    state = engine.start()
    assert state == LoopState.BUILD, f"Expected BUILD state, got {state}"

    # Iteration 1: fails tests
    state = engine.submit_build_iteration(
        modified_files=["src/utils/sanitizer.py"],
        simulated_test_pass=False,
        test_output="AssertionError: HTML entity '&' not escaped"
    )
    assert state == LoopState.BUILD, f"Expected loop back to BUILD, got {state}"
    print(f"[*] Iteration 1: Failed as expected, returned to state={state.value}")

    # Iteration 2: passes tests
    state = engine.submit_build_iteration(
        modified_files=["src/utils/sanitizer.py", "tests/test_sanitizer.py"],
        simulated_test_pass=True,
        test_output="2 passed in 0.05s"
    )
    assert state == LoopState.COMPLETED, f"Expected COMPLETED, got {state}"
    print(f"[*] Iteration 2: Verification passed, reached state={state.value}")

    # Test 2: Out of scope file modification rejection
    spec_boundary = SpecContract(
        objective="Fix database query index",
        requirements=["Add index on user_id"],
        allowed_patterns=["migrations/*.sql"],
        max_iterations=2
    )
    engine_b = AILoopEngine(spec_boundary)
    engine_b.start()
    state = engine_b.submit_build_iteration(
        modified_files=["config/database.yml", "migrations/001_idx.sql"],
        simulated_test_pass=True,
        test_output="Migration ran"
    )
    assert state == LoopState.ABORTED, f"Expected ABORTED due to scope violation, got {state}"
    print(f"[*] Scope Confinement Guard verified: Unauthorized file properly blocked -> {state.value}")

    # Test 3: Budget exhaustion
    spec_exhaust = SpecContract(
        objective="Difficult algorithmic puzzle",
        requirements=["Pass all 100 benchmark fixtures"],
        allowed_patterns=["src/*.py"],
        max_iterations=2
    )
    engine_e = AILoopEngine(spec_exhaust)
    engine_e.start()
    engine_e.submit_build_iteration(["src/algo.py"], False, "Failing on fixture 89")
    state_e = engine_e.submit_build_iteration(["src/algo.py"], False, "Failing on fixture 94")
    assert state_e == LoopState.EXHAUSTED, f"Expected EXHAUSTED after 2 iterations, got {state_e}"
    print(f"[*] Iteration Budget Guard verified: Halts cleanly on EXHAUSTED -> {state_e.value}")

    print("\n[SUCCESS] AI Loop Engine state-machine and boundaries verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="AI Loop Orchestration Engine")
    parser.add_argument("--test-all", action="store_true", help="Run full state machine verification tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
