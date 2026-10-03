#!/usr/bin/env python3
"""
agentfolio_helper.py - Autonomous AI Agent Capability & Security Evaluator.
Computes an objective Agent Maturity Index (0-100) based on autonomy tiers,
tool reliability, memory checkpointing, and execution sandboxing.
"""

import sys
import json
import argparse

def evaluate_agent(
    name: str,
    autonomy_level: int,
    has_sandboxing: bool,
    has_checkpointing: bool,
    mcp_compliant: bool,
    error_recovery_score: float
) -> dict:
    """Evaluates an agent profile across 4 standardized capability dimensions."""
    # Weightings
    # 1. Autonomy Tier (25 pts): level 1-5 scaled to 25
    autonomy_pts = min(25.0, (autonomy_level / 5.0) * 25.0)

    # 2. Tool Reliability (25 pts): recovery score & protocol compliance
    tool_pts = (error_recovery_score / 100.0) * 20.0 + (5.0 if mcp_compliant else 0.0)

    # 3. State & Memory Persistence (25 pts)
    memory_pts = 25.0 if has_checkpointing else 5.0

    # 4. Security & Blast Radius (25 pts)
    security_pts = 25.0 if has_sandboxing else 8.0

    total_score = round(autonomy_pts + tool_pts + memory_pts + security_pts, 1)

    # Risk rating
    if not has_sandboxing and autonomy_level >= 3:
        risk = "HIGH (Unconstrained execution environment)"
    elif not has_checkpointing and autonomy_level >= 3:
        risk = "MEDIUM (State loss risk on crash)"
    else:
        risk = "LOW (Contained and recoverable)"

    report = {
        "agent_name": name,
        "autonomy_tier": f"L{autonomy_level}",
        "total_score": total_score,
        "risk_rating": risk,
        "dimensions": {
            "autonomy_score": round(autonomy_pts, 1),
            "tool_reliability_score": round(tool_pts, 1),
            "memory_persistence_score": round(memory_pts, 1),
            "security_sandboxing_score": round(security_pts, 1),
        },
        "flags": {
            "has_sandboxing": has_sandboxing,
            "has_checkpointing": has_checkpointing,
            "mcp_compliant": mcp_compliant
        }
    }

    print("=" * 65)
    print(f"Autonomous Agent Evaluation Report: {name}")
    print("=" * 65)
    print(f"Autonomy Classification:     L{autonomy_level}")
    print(f"Overall Maturity Score:      {total_score} / 100")
    print(f"Security Risk Assessment:    {risk}")
    print("-" * 65)
    print("Dimension Breakdown:")
    for dim, score in report["dimensions"].items():
        print(f"  - {dim:<28}: {score} / 25.0")
    print("-" * 65)
    
    if not has_sandboxing:
        print("[CRITICAL RECOMMENDATION]: Containerize tool execution (Docker sandbox) to prevent host damage.")
    if not has_checkpointing:
        print("[RECOMMENDATION]: Implement transactional state snapshots for crash recovery.")

    print("=" * 65)
    return report

def main():
    parser = argparse.ArgumentParser(description="Autonomous AI Agent Capability & Safety Evaluator")
    parser.add_argument("--audit", action="store_true", help="Run audit evaluation on specified agent parameters")
    parser.add_argument("--name", type=str, default="SampleAgent", help="Name of agent being evaluated")
    parser.add_argument("--autonomy-level", type=int, default=3, choices=[1, 2, 3, 4, 5], help="Autonomy level (1-5)")
    parser.add_argument("--has-sandboxing", action="store_true", help="Agent executes inside Docker/sandbox")
    parser.add_argument("--has-checkpointing", action="store_true", help="Agent supports state persistence/checkpointing")
    parser.add_argument("--mcp-compliant", action="store_true", help="Agent supports Model Context Protocol")
    parser.add_argument("--error-recovery-score", type=float, default=80.0, help="Error recovery score (0-100)")
    parser.add_argument("--test-rubric", action="store_true", help="Run rubric validation self-test")

    args = parser.parse_args()

    if args.test_rubric:
        print("=" * 65)
        print("Running Agent Capability Rubric Self-Test")
        print("=" * 65)
        rep = evaluate_agent("EnterpriseWorker", 4, True, True, True, 90.0)
        if rep["total_score"] >= 80.0:
            print("Rubric Self-Test: [PASSED]")
            return
        else:
            print("Rubric Self-Test: [FAILED]")
            sys.exit(1)

    if args.audit:
        evaluate_agent(
            args.name,
            args.autonomy_level,
            args.has_sandboxing,
            args.has_checkpointing,
            args.mcp_compliant,
            args.error_recovery_score
        )
        return

    print("=" * 65)
    print("Agentfolio Benchmark Utility Ready")
    print("Run with --audit or --test-rubric")

if __name__ == "__main__":
    main()
