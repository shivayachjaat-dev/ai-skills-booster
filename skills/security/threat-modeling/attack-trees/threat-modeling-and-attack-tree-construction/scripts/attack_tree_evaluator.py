#!/usr/bin/env python3
import json
import sys

SAMPLE_TREE = {
    "goal": "Exfiltrate Customer DB",
    "type": "OR",
    "children": [
        {
            "name": "SQL Injection in Search API",
            "type": "AND",
            "children": [
                {"name": "Discover parameter SQLi", "cost": 2, "skill": "medium"},
                {"name": "Bypass ModSecurity WAF", "cost": 4, "skill": "high"}
            ]
        },
        {
            "name": "Compromise Database Backup Bucket",
            "type": "AND",
            "children": [
                {"name": "Obtain S3 read credentials", "cost": 3, "skill": "medium"},
                {"name": "Overcome S3 bucket KMS encryption", "cost": 6, "skill": "high"}
            ]
        },
        {
            "name": "Insider Credential Abuse",
            "cost": 10,
            "skill": "low"
        }
    ]
}

def calculate_min_cost(node):
    if "cost" in node and "children" not in node:
        return node["cost"], [node["name"]]
    
    node_type = node.get("type", "OR")
    if node_type == "AND":
        total_cost = 0
        all_steps = []
        for child in node["children"]:
            c, steps = calculate_min_cost(child)
            total_cost += c
            all_steps.extend(steps)
        return total_cost, all_steps
    else: # OR node
        best_cost = float("inf")
        best_path = []
        for child in node["children"]:
            c, steps = calculate_min_cost(child)
            if c < best_cost:
                best_cost = c
                best_path = steps
        return best_cost, best_path

def evaluate_tree(tree_data):
    print("=" * 65)
    print(f"Attack Tree Evaluation: Root Goal = '{tree_data['goal']}'")
    print("=" * 65)
    min_cost, path = calculate_min_cost(tree_data)
    print(f"Lowest Adversary Cost to Compromise: {min_cost} points")
    print("\nMost Probable / Lowest-Resistance Attack Path:")
    for idx, step in enumerate(path, 1):
        print(f"  {idx}. {step}")

if __name__ == "__main__":
    evaluate_tree(SAMPLE_TREE)
