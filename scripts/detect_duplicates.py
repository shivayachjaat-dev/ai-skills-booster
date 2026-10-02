#!/usr/bin/env python3
"""
detect_duplicates.py - Advanced duplicate and collision detection engine.
Identifies:
- Exact name and directory duplicates
- Slug clashes (e.g. 'postgres-query' vs 'postgres_query')
- Semantic and text similarity in descriptions using Jaccard word token sets
- Redundant and overlapping skill scopes
"""

import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def tokenize(text):
    text = text.lower()
    tokens = set(re.findall(r"[a-z0-9]{3,}", text))
    stopwords = {"this", "that", "with", "from", "when", "using", "guides", "used", "into", "their", "there", "about", "which"}
    return tokens - stopwords

def jaccard_similarity(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def extract_meta(skill_file):
    name = None
    desc = ""
    try:
        with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return None, ""
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                m_name = re.match(r"^name:\s*['\"]?([a-zA-Z0-9_\-]+)['\"]?", line)
                if m_name:
                    name = m_name.group(1).strip()
                m_desc = re.match(r"^description:\s*['\"]?(.*?)['\"]?$", line)
                if m_desc:
                    desc = m_desc.group(1).strip()
    return name, desc

def main():
    print("=" * 60)
    print("Running AI Skills Booster Duplicate Detector")
    print("=" * 60)

    if not os.path.exists(SKILLS_DIR):
        print("No skills directory yet. Zero duplicates.")
        sys.exit(0)

    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            skill_file = os.path.join(root, "SKILL.md")
            name, desc = extract_meta(skill_file)
            if not name:
                name = os.path.basename(root)
            rel = os.path.relpath(root, BASE_DIR).replace("\\", "/")
            skills.append({
                "name": name,
                "path": rel,
                "desc": desc,
                "desc_tokens": tokenize(desc),
                "name_tokens": tokenize(name.replace("-", " "))
            })

    print(f"Auditing {len(skills)} skills for duplicates and collisions...")

    collisions = []
    high_sim = []

    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            s1 = skills[i]
            s2 = skills[j]

            # Exact name match
            if s1["name"] == s2["name"]:
                collisions.append(f"Exact name match: '{s1['name']}' in {s1['path']} and {s2['path']}")

            # Slug collision (different separators)
            slug1 = s1["name"].replace("-", "").replace("_", "")
            slug2 = s2["name"].replace("-", "").replace("_", "")
            if slug1 == slug2 and s1["name"] != s2["name"]:
                collisions.append(f"Slug collision: '{s1['name']}' vs '{s2['name']}'")

            # High description similarity (threshold > 0.82)
            sim = jaccard_similarity(s1["desc_tokens"], s2["desc_tokens"])
            if sim > 0.82:
                high_sim.append(f"High description similarity ({sim:.2f}) between:\n    - {s1['name']} ({s1['path']})\n    - {s2['name']} ({s2['path']})")

    if collisions:
        print(f"\nCRITICAL DUPLICATES FOUND ({len(collisions)}):")
        for c in collisions:
            print(f"  [COLLISION] {c}")
        sys.exit(1)

    if high_sim:
        print(f"\nPOTENTIAL HIGH OVERLAP DETECTED ({len(high_sim)}):")
        for h in high_sim:
            print(f"  [WARN] {h}")

    print("\nZero critical duplicate collisions detected. Check passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
