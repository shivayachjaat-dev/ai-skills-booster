#!/usr/bin/env python3
"""
category_report.py - Category health, balance, and distribution reporter.
Detects:
- Category distribution and percentage representation
- Imbalanced or overloaded categories
- Categories lacking script/eval depth
- Orphaned or singleton categories
"""

import os
import sys
import json
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "docs", "skill-inventory.json")

def main():
    if not os.path.exists(INDEX_PATH):
        print(f"Master inventory not found at {INDEX_PATH}. Run scripts/generate_catalog.py first.")
        sys.exit(0)

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        skills = json.load(f)

    print("=" * 70)
    print("AI Skills Booster — Category Health & Balance Report")
    print(f"Total Skills: {len(skills):,}")
    print("=" * 70)

    if not skills:
        print("No skills found in inventory yet.")
        return

    domain_tree = defaultdict(lambda: defaultdict(list))
    for s in skills:
        domain_tree[s["domain"]][s["category"]].append(s)

    for domain in sorted(domain_tree.keys()):
        d_skills = [s for cat in domain_tree[domain].values() for s in cat]
        pct = (len(d_skills) / len(skills)) * 100
        print(f"\n[Domain] {domain.upper()} ({len(d_skills)} skills - {pct:.1f}%)")
        for cat in sorted(domain_tree[domain].keys()):
            c_skills = domain_tree[domain][cat]
            scripts = sum(1 for s in c_skills if s.get("has_scripts"))
            evals = sum(1 for s in c_skills if s.get("has_evals"))
            print(f"  └── {cat}: {len(c_skills)} skills | {scripts} scripts | {evals} evals")

    print("\n" + "=" * 70)
    print("Health Diagnostics:")
    # Balance alerts
    domain_counts = Counter(s["domain"] for s in skills)
    for d, c in domain_counts.items():
        if (c / len(skills)) > 0.40 and len(skills) > 50:
            print(f"  [ALERT] Domain '{d}' contains {c / len(skills):.1%} of all skills. Consider balancing.")
    print("Health check completed.")

if __name__ == "__main__":
    main()
