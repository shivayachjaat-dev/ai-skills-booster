#!/usr/bin/env python3
"""
search_skills.py - Fast CLI search engine for AI Skills Booster.
Supports queries across name, description, tags, domain, category, technology, task, and complexity.

Usage:
    python scripts/search_skills.py postgres
    python scripts/search_skills.py "slow api"
    python scripts/search_skills.py --category code-review
    python scripts/search_skills.py --domain security
    python scripts/search_skills.py --tag mcp
    python scripts/search_skills.py --tech react
    python scripts/search_skills.py --complexity expert
"""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "skills-index.json")

def load_index():
    if not os.path.exists(INDEX_PATH):
        # Fallback to scanning
        alt = os.path.join(BASE_DIR, "docs", "skills-index.json")
        if os.path.exists(alt):
            with open(alt, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def match_skill(skill, query_tokens, args):
    if args.domain and skill.get("domain", "").lower() != args.domain.lower():
        return False
    if args.category and skill.get("category", "").lower() != args.category.lower():
        return False
    if args.subcategory and skill.get("subcategory", "").lower() != args.subcategory.lower():
        return False
    if args.complexity and skill.get("complexity", "").lower() != args.complexity.lower():
        return False
    if args.maturity and skill.get("maturity", "").lower() != args.maturity.lower():
        return False

    if args.tag:
        skill_tags = [t.lower() for t in skill.get("tags", [])]
        if args.tag.lower() not in skill_tags:
            return False

    if args.tech:
        skill_techs = [t.lower() for t in skill.get("technologies", [])]
        if args.tech.lower() not in skill_techs:
            return False

    if not query_tokens:
        return True

    text = f"{skill['name']} {skill['description']} {' '.join(skill.get('tags', []))} {' '.join(skill.get('technologies', []))}".lower()
    return all(token in text for token in query_tokens)

def main():
    parser = argparse.ArgumentParser(description="Search AI Skills Booster library")
    parser.add_argument("query", nargs="*", help="Search terms or keywords")
    parser.add_argument("--domain", help="Filter by domain")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--subcategory", help="Filter by subcategory")
    parser.add_argument("--tag", help="Filter by exact tag")
    parser.add_argument("--tech", help="Filter by technology")
    parser.add_argument("--complexity", choices=["beginner", "intermediate", "advanced", "expert"], help="Filter by complexity")
    parser.add_argument("--maturity", choices=["experimental", "stable", "advanced"], help="Filter by maturity")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()
    skills = load_index()

    query_tokens = [q.lower() for q in args.query]
    matched = [s for s in skills if match_skill(s, query_tokens, args)]

    if args.json:
        print(json.dumps(matched, indent=2))
        return

    print("=" * 70)
    print(f"AI Skills Booster Search | Found {len(matched)} matching skills")
    print("=" * 70)

    if not matched:
        print("\nNo skills matched your search criteria.")
        print("Try broader keywords or browse docs/CATEGORIES.md")
        return

    for s in matched:
        print(f"\n* {s['name']}  [{s['domain']} > {s['category']} > {s['subcategory']}]")
        print(f"  Path:        {s['path']}/SKILL.md")
        print(f"  Complexity:  {s.get('complexity', 'intermediate')} | Maturity: {s.get('maturity', 'stable')}")
        if s.get("tags"):
            print(f"  Tags:        {', '.join(s['tags'])}")
        if s.get("technologies"):
            print(f"  Tech:        {', '.join(s['technologies'])}")
        print(f"  Description: {s['description']}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
