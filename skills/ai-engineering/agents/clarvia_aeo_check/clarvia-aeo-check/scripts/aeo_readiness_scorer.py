#!/usr/bin/env python3
"""
aeo_readiness_scorer.py - Production Agent Experience Optimization (AEO) Scorer

Features:
- Audits MCP Tool and API definitions for Agent-Readiness
- 4 Scoring Dimensions:
  1. Schema Clarity (types, parameter docs, required fields)
  2. Data Structuring (strict JSON contracts, error codes)
  3. Token Efficiency (payload conciseness, context economy)
  4. Trust & Safety (idempotency, side-effect annotations)
- Generates 0-100 AEO Score and letter grade
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List, Tuple


def score_schema_clarity(tool_def: Dict[str, Any]) -> Tuple[int, List[str]]:
    score = 25
    issues = []
    
    desc = tool_def.get("description", "")
    if len(desc) < 25:
        score -= 10
        issues.append("Tool description is too brief (<25 characters).")
        
    params = tool_def.get("parameters", {}).get("properties", {})
    if not params:
        score -= 5
        issues.append("Parameters object is empty or missing.")
    else:
        for p_name, p_val in params.items():
            if not p_val.get("description"):
                score -= 3
                issues.append(f"Parameter '{p_name}' lacks a clear description.")
            if not p_val.get("type"):
                score -= 4
                issues.append(f"Parameter '{p_name}' lacks explicit data type.")
                
    return max(0, score), issues


def score_data_structuring(returns_structured_json: bool, provides_error_codes: bool) -> Tuple[int, List[str]]:
    score = 25
    issues = []
    
    if not returns_structured_json:
        score -= 15
        issues.append("Tool returns unstructured prose or raw HTML instead of structured JSON.")
    if not provides_error_codes:
        score -= 10
        issues.append("Errors lack machine-parseable code identifiers.")
        
    return max(0, score), issues


def score_token_efficiency(avg_response_chars: int) -> Tuple[int, List[str]]:
    score = 25
    issues = []
    
    # 1 token ~= 4 chars
    approx_tokens = avg_response_chars / 4.0
    if approx_tokens > 2500:
        score -= 15
        issues.append(f"Response is excessively verbose (~{int(approx_tokens)} tokens). Exceeds 2500 token target.")
    elif approx_tokens > 1000:
        score -= 5
        issues.append(f"Response is moderately large (~{int(approx_tokens)} tokens). Consider summarizing.")
        
    return max(0, score), issues


def score_trust_and_safety(declares_idempotency: bool, is_non_interactive: bool) -> Tuple[int, List[str]]:
    score = 25
    issues = []
    
    if not is_non_interactive:
        score -= 20
        issues.append("CRITICAL: Tool requires interactive stdin input which blocks agent execution.")
    if not declares_idempotency:
        score -= 5
        issues.append("Tool does not declare read/write side-effects or idempotency guarantees.")
        
    return max(0, score), issues


def compute_aeo_score(
    tool_def: Dict[str, Any],
    returns_structured_json: bool = True,
    provides_error_codes: bool = True,
    avg_response_chars: int = 1200,
    declares_idempotency: bool = True,
    is_non_interactive: bool = True
) -> Dict[str, Any]:
    """
    Computes aggregate 0-100 AEO Readiness Score.
    """
    s1, iss1 = score_schema_clarity(tool_def)
    s2, iss2 = score_data_structuring(returns_structured_json, provides_error_codes)
    s3, iss3 = score_token_efficiency(avg_response_chars)
    s4, iss4 = score_trust_and_safety(declares_idempotency, is_non_interactive)
    
    total = s1 + s2 + s3 + s4
    
    grade = (
        "A (Agent-Ready Production)" if total >= 90
        else "B (Usable with Minor Gaps)" if total >= 75
        else "C (High Agent Failure Risk)" if total >= 60
        else "F (Unsuitable for Autonomous Agents)"
    )
    
    all_issues = iss1 + iss2 + iss3 + iss4
    
    return {
        "aeo_score": total,
        "grade": grade,
        "breakdown": {
            "schema_clarity": s1,
            "data_structuring": s2,
            "token_efficiency": s3,
            "trust_and_safety": s4
        },
        "identified_issues": all_issues
    }


def run_unit_tests():
    print("=" * 60)
    print("Running AEO (Agent Experience Optimization) Scorer Tests")
    print("=" * 60)

    # Test 1: Ideal well-architected MCP tool
    ideal_tool = {
        "name": "query_database",
        "description": "Executes a parameterized read-only SQL query against the analytics database.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "A valid SELECT SQL query."
                },
                "max_rows": {
                    "type": "integer",
                    "description": "Maximum number of rows to return."
                }
            },
            "required": ["sql_query"]
        }
    }
    res_ideal = compute_aeo_score(ideal_tool, avg_response_chars=800)
    print(f"[*] Ideal Tool AEO Score: {res_ideal['aeo_score']}/100 -> Grade: {res_ideal['grade']}")
    assert res_ideal["aeo_score"] >= 95, "Ideal tool should achieve Grade A score >= 95"

    # Test 2: Defective tool with blocking stdin and undocumented parameters
    bad_tool = {
        "name": "do_stuff",
        "description": "Runs script",
        "parameters": {
            "type": "object",
            "properties": {
                "opt": {}
            }
        }
    }
    res_bad = compute_aeo_score(bad_tool, is_non_interactive=False, returns_structured_json=False)
    print(f"[*] Defective Tool AEO Score: {res_bad['aeo_score']}/100 -> Grade: {res_bad['grade']}")
    assert res_bad["aeo_score"] < 60, "Defective tool must score low"
    assert any("interactive stdin" in iss for iss in res_bad["identified_issues"])

    print("\n[SUCCESS] AEO Readiness Scorer verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="AEO Tool Readiness Scorer")
    parser.add_argument("--test-all", action="store_true", help="Run self-tests")
    args = parser.parse_args()

    run_unit_tests()


if __name__ == "__main__":
    main()
