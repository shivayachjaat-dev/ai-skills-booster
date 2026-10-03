#!/usr/bin/env python3
"""
meta_skill_orchestrator.py - Production Agent Skill Meta-Orchestrator Engine

Features:
- Complexity gate: Distinguishes simple direct tasks from multi-domain orchestrated tasks
- Semantic / Jaccard keyword capability matching against skill catalogs
- Topological DAG resolution for multi-skill execution workflows
- Cycle detection and validation
"""

import sys
import os
import graphlib
import argparse
from typing import List, Dict, Any, Set, Tuple


def evaluate_task_complexity(prompt: str) -> Dict[str, Any]:
    """
    Evaluates whether a user prompt requires multi-skill orchestration.
    """
    prompt_lower = prompt.lower()
    
    domain_map = {
        "database": ["database", "schema", "migration", "sql", "orm", "postgres", "sqlite"],
        "backend": ["api", "endpoint", "fastapi", "rest", "graphql", "authentication", "backend"],
        "frontend": ["ui", "component", "react", "nextjs", "css", "tailwind", "frontend"],
        "devops": ["docker", "kubernetes", "ci/cd", "terraform", "deploy", "monitoring"],
        "security": ["rbac", "jwt", "encryption", "audit", "sanitization", "vulnerability"]
    }
    
    detected = [d for d, keywords in domain_map.items() if any(kw in prompt_lower for kw in keywords)]
    words = len(prompt.split())
    
    # Over-orchestration guard: simple requests with < 2 domains are handled directly
    needs_orchestration = len(detected) >= 2 or (words > 50 and len(detected) >= 1)
    
    return {
        "needs_orchestration": needs_orchestration,
        "domains": detected,
        "word_count": words,
        "recommendation": "ORCHESTRATE_PIPELINE" if needs_orchestration else "DIRECT_TOOL_CALL"
    }


def compute_catalog_match_score(task_tokens: Set[str], skill_tags: List[str], skill_desc: str) -> float:
    """
    Computes Jaccard similarity between task tokens and skill metadata.
    """
    skill_words = set(w.lower() for w in skill_tags + skill_desc.split())
    if not task_tokens or not skill_words:
        return 0.0
    intersection = task_tokens.intersection(skill_words)
    union = task_tokens.union(skill_words)
    return round(len(intersection) / len(union), 4)


def build_and_schedule_dag(dependency_edges: List[Tuple[str, str]]) -> Tuple[bool, List[str], str]:
    """
    Constructs a dependency DAG and computes execution order using graphlib.TopologicalSorter.
    Format: (child, parent_it_depends_on) -> parent must run before child.
    Returns (success, execution_order, message).
    """
    graph: Dict[str, Set[str]] = {}
    
    for child, parent in dependency_edges:
        if child not in graph:
            graph[child] = set()
        graph[child].add(parent)
        if parent not in graph:
            graph[parent] = set()
            
    try:
        ts = graphlib.TopologicalSorter(graph)
        order = list(ts.static_order())
        return True, order, "DAG scheduled successfully"
    except graphlib.CycleError as e:
        return False, [], f"Cycle detected in skill dependency graph: {e}"


def run_unit_tests():
    print("=" * 60)
    print("Running Meta-Skill Orchestrator & DAG Scheduling Verification")
    print("=" * 60)

    # Test 1: Simple task complexity guard (anti-overuse)
    simple_prompt = "Fix the typo in the login button text from Submit to Continue"
    res_simple = evaluate_task_complexity(simple_prompt)
    print(f"[*] Simple Task Check: Recommendation={res_simple['recommendation']}")
    assert res_simple["needs_orchestration"] is False, "Simple task should NOT trigger orchestration"

    # Test 2: Complex multi-domain task complexity guard
    complex_prompt = (
        "Build a multi-tenant payment system with PostgreSQL migration scripts, "
        "a secure FastAPI backend with Stripe webhooks, and a responsive React checkout UI."
    )
    res_complex = evaluate_task_complexity(complex_prompt)
    print(f"[*] Complex Task Check: Domains={res_complex['domains']}, Recommendation={res_complex['recommendation']}")
    assert res_complex["needs_orchestration"] is True, "Multi-domain task must trigger orchestration"

    # Test 3: DAG scheduling (topological order)
    # Backend depends on Database, Frontend depends on Backend, Evals depend on Frontend
    dependencies = [
        ("api-backend", "postgres-schema"),
        ("react-frontend", "api-backend"),
        ("e2e-evals", "react-frontend"),
    ]
    ok, order, msg = build_and_schedule_dag(dependencies)
    print(f"[*] DAG Execution Order: {' -> '.join(order)}")
    assert ok is True, f"DAG scheduling failed: {msg}"
    assert order.index("postgres-schema") < order.index("api-backend"), "DB must precede backend"
    assert order.index("api-backend") < order.index("react-frontend"), "Backend must precede frontend"

    # Test 4: Cycle detection
    cyclic_deps = [
        ("skill-A", "skill-B"),
        ("skill-B", "skill-A")
    ]
    ok_cycle, _, msg_cycle = build_and_schedule_dag(cyclic_deps)
    print(f"[*] Cycle Detection Guard: Detected={not ok_cycle}")
    assert ok_cycle is False, "Cycle error should be caught"

    print("\n[SUCCESS] Meta-Skill Orchestrator verified cleanly.")


def main():
    parser = argparse.ArgumentParser(description="Agent Skill Meta-Orchestrator")
    parser.add_argument("--test-all", action="store_true", help="Run full self-test suite")
    parser.add_argument("--evaluate", type=str, help="Evaluate a natural language user prompt")
    args = parser.parse_args()

    if args.evaluate:
        res = evaluate_task_complexity(args.evaluate)
        print(f"Recommendation: {res['recommendation']}")
        print(f"Detected Domains: {res['domains']}")
        return

    run_unit_tests()


if __name__ == "__main__":
    main()
