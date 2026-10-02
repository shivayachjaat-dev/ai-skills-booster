#!/usr/bin/env python3
"""
generate_catalog.py - Automated catalog and index generator for AI Skills Booster.
Scans all skills and generates:
- SKILLS.md & docs/SKILLS.md
- skills-index.json (searchable JSON database)
- docs/skill-inventory.json (master source of truth database)
- docs/CATEGORIES.md
- docs/TAXONOMY.md
- docs/STATISTICS.md
- docs/BY-TASK.md
- docs/BY-TECHNOLOGY.md
- docs/BY-ROLE.md
- docs/categories/*.md (per-category detailed markdown files)
- README.md dynamic badge update
"""

import os
import sys
import re
import json
from collections import defaultdict, Counter
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CAT_DIR = os.path.join(DOCS_DIR, "categories")

ROLE_MAPPINGS = {
    "AI Engineer": ["rag", "agent", "llm", "embedding", "model", "mcp", "prompt", "inference", "vector"],
    "Security Engineer": ["security", "audit", "secret", "auth", "vulnerability", "hardening", "owasp", "injection"],
    "DevOps Engineer": ["docker", "kubernetes", "ci-cd", "pipeline", "terraform", "cloud", "aws", "gcp", "azure", "deploy", "monitoring"],
    "Backend Engineer": ["api", "database", "postgres", "redis", "fastapi", "django", "express", "sql", "migration", "cache", "grpc"],
    "Frontend Engineer": ["react", "nextjs", "vue", "tailwind", "css", "component", "ui", "accessibility", "frontend", "state"],
    "QA / Test Engineer": ["test", "playwright", "cypress", "e2e", "unit", "mock", "integration", "coverage"],
    "Data Engineer": ["etl", "pipeline", "pandas", "polars", "duckdb", "clickhouse", "analytics", "sql", "data"]
}

TASK_MAPPINGS = {
    "Build & Create": ["build", "scaffold", "create", "implement", "design", "develop", "setup"],
    "Debug & Troubleshoot": ["debug", "troubleshoot", "fix", "error", "crash", "diagnose", "investigate"],
    "Review & Audit": ["review", "audit", "inspect", "assess", "check", "verify"],
    "Optimize & Performance": ["optimize", "performance", "speed", "latency", "scale", "memory", "profil"],
    "Test & Verify": ["test", "e2e", "unit", "integration", "mock", "assert", "evaluat"],
    "Secure & Harden": ["secure", "harden", "auth", "secret", "protect", "defense", "safeguard"],
    "Deploy & Automate": ["deploy", "ci-cd", "pipeline", "release", "ship", "automat", "workflow"]
}

def parse_frontmatter(content):
    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            current_key = None
            for line in fm_text.splitlines():
                line = line.rstrip()
                if not line or line.startswith("#"):
                    continue
                m = re.match(r"^([a-zA-Z0-9_\-]+):\s*(.*)$", line)
                if m:
                    current_key = m.group(1)
                    val = m.group(2).strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    if val == "" or val == "[]":
                        metadata[current_key] = []
                    else:
                        metadata[current_key] = val
                elif current_key and (line.startswith("  - ") or line.startswith("- ")):
                    item = line.lstrip("- ").strip()
                    if item.startswith('"') and item.endswith('"'):
                        item = item[1:-1]
                    elif item.startswith("'") and item.endswith("'"):
                        item = item[1:-1]
                    if not isinstance(metadata.get(current_key), list):
                        metadata[current_key] = []
                    metadata[current_key].append(item)
    return metadata, body

def scan_all_skills():
    skills = []
    if not os.path.exists(SKILLS_DIR):
        return skills

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            skill_file = os.path.join(root, "SKILL.md")
            rel_path = os.path.relpath(root, BASE_DIR).replace("\\", "/")
            parts = rel_path.split("/")
            
            domain = parts[1] if len(parts) > 1 else "general"
            category = parts[2] if len(parts) > 2 else "general"
            subcategory = parts[3] if len(parts) > 3 else "general"
            skill_name = parts[4] if len(parts) > 4 else os.path.basename(root)

            try:
                with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            meta, body = parse_frontmatter(content)
            
            skills.append({
                "name": meta.get("name") or skill_name,
                "slug": skill_name,
                "path": rel_path,
                "domain": meta.get("domain") or domain,
                "category": meta.get("category") or category,
                "subcategory": meta.get("subcategory") or subcategory,
                "description": meta.get("description", "").strip(),
                "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
                "technologies": meta.get("technologies") if isinstance(meta.get("technologies"), list) else [],
                "complexity": meta.get("complexity", "intermediate"),
                "maturity": meta.get("maturity", "stable"),
                "tools": meta.get("tools") if isinstance(meta.get("tools"), list) else [],
                "dependencies": meta.get("dependencies") if isinstance(meta.get("dependencies"), list) else [],
                "has_scripts": os.path.exists(os.path.join(root, "scripts")),
                "has_evals": os.path.exists(os.path.join(root, "evals")),
                "has_references": os.path.exists(os.path.join(root, "references")),
                "source": "AI_Skills_Booster",
                "license": "MIT",
                "updated_at": datetime.now(timezone.utc).isoformat()
            })

    skills.sort(key=lambda s: (s["domain"], s["category"], s["subcategory"], s["name"]))
    return skills

def generate_markdown_catalog(skills):
    lines = [
        "# AI Skills Booster — Master Catalog",
        "",
        f"> **Total Skills**: {len(skills):,} | **Organized by 3-Level Taxonomy**",
        "",
        "| Skill | Domain | Category | Subcategory | Complexity | Maturity | Description |",
        "|---|---|---|---|---|---|---|"
    ]
    for s in skills:
        link = f"[{s['name']}]({s['path']}/SKILL.md)"
        desc = s['description'].replace("|", "\\|")
        lines.append(f"| {link} | `{s['domain']}` | `{s['category']}` | `{s['subcategory']}` | `{s['complexity']}` | `{s['maturity']}` | {desc} |")
    lines.append("")
    return "\n".join(lines)

def generate_categories_md(skills):
    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for s in skills:
        tree[s["domain"]][s["category"]][s["subcategory"]].append(s)

    lines = [
        "# Skill Categories & Directory Map",
        "",
        f"Master navigation for **{len(skills):,}** skills across structured domains, categories, and subcategories.",
        ""
    ]

    for domain in sorted(tree.keys()):
        domain_count = sum(len(skills_list) for cat in tree[domain].values() for skills_list in cat.values())
        lines.append(f"## {domain.replace('-', ' ').title()} ({domain_count} skills)")
        lines.append("")
        for cat in sorted(tree[domain].keys()):
            cat_count = sum(len(skills_list) for skills_list in tree[domain][cat].values())
            lines.append(f"### {cat.replace('-', ' ').title()} ({cat_count} skills)")
            lines.append(f"Category index: [`docs/categories/{cat}.md`](categories/{cat}.md)")
            lines.append("")
            for subcat in sorted(tree[domain][cat].keys()):
                sub_skills = tree[domain][cat][subcat]
                lines.append(f"- **{subcat.replace('-', ' ').title()}** ({len(sub_skills)}):")
                for s in sub_skills:
                    lines.append(f"  - [{s['name']}](../{s['path']}/SKILL.md) — {s['description']}")
            lines.append("")

    return "\n".join(lines)

def generate_taxonomy_md(skills):
    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for s in skills:
        tree[s["domain"]][s["category"]][s["subcategory"]].append(s)

    lines = [
        "# Visual Taxonomy Map",
        "",
        "```text",
        "AI_Skills_Booster/"
    ]
    for domain in sorted(tree.keys()):
        lines.append(f"├── {domain}/")
        cats = sorted(tree[domain].keys())
        for c_idx, cat in enumerate(cats):
            c_prefix = "│   ├── " if c_idx < len(cats) - 1 else "│   └── "
            lines.append(f"{c_prefix}{cat}/")
            subcats = sorted(tree[domain][cat].keys())
            for s_idx, sub in enumerate(subcats):
                s_prefix = "│   │   ├── " if s_idx < len(subcats) - 1 else "│   │   └── "
                count = len(tree[domain][cat][sub])
                lines.append(f"{s_prefix}{sub}/ ({count} skills)")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)

def generate_statistics_md(skills):
    domains = Counter(s["domain"] for s in skills)
    categories = Counter(s["category"] for s in skills)
    complexities = Counter(s["complexity"] for s in skills)
    maturities = Counter(s["maturity"] for s in skills)
    with_scripts = sum(1 for s in skills if s["has_scripts"])
    with_evals = sum(1 for s in skills if s["has_evals"])
    with_refs = sum(1 for s in skills if s["has_references"])

    lines = [
        "# Repository Statistics",
        "",
        f"- **Total Active Skills**: {len(skills):,}",
        f"- **Total Domains**: {len(domains)}",
        f"- **Total Categories**: {len(categories)}",
        f"- **Skills with Automation Scripts**: {with_scripts:,}",
        f"- **Skills with Formal Evaluations**: {with_evals:,}",
        f"- **Skills with Reference Docs**: {with_refs:,}",
        "",
        "## Distribution by Domain",
        "",
        "| Domain | Skill Count | Percentage |",
        "|---|---|---|"
    ]
    for d, c in domains.most_common():
        pct = (c / max(1, len(skills))) * 100
        lines.append(f"| `{d}` | {c} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Distribution by Complexity",
        "",
        "| Complexity | Count | Percentage |",
        "|---|---|---|"
    ])
    for cx, c in complexities.most_common():
        pct = (c / max(1, len(skills))) * 100
        lines.append(f"| `{cx}` | {c} | {pct:.1f}% |")

    lines.extend([
        "",
        "## Distribution by Maturity",
        "",
        "| Maturity | Count | Percentage |",
        "|---|---|---|"
    ])
    for m, c in maturities.most_common():
        pct = (c / max(1, len(skills))) * 100
        lines.append(f"| `{m}` | {c} | {pct:.1f}% |")

    lines.append("")
    return "\n".join(lines)

def generate_by_task_md(skills):
    task_groups = defaultdict(list)
    for s in skills:
        text = (s["name"] + " " + s["description"]).lower()
        matched = False
        for task, keywords in TASK_MAPPINGS.items():
            if any(k in text for k in keywords):
                task_groups[task].append(s)
                matched = True
        if not matched:
            task_groups["General Workflows"].append(s)

    lines = [
        "# Skills by Task Intent",
        "",
        "Find the exact agent skill according to what task you need completed.",
        ""
    ]
    for task in sorted(task_groups.keys()):
        lines.append(f"## {task} ({len(task_groups[task])} skills)")
        lines.append("")
        for s in task_groups[task]:
            lines.append(f"- [{s['name']}](../{s['path']}/SKILL.md) — `{s['domain']}/{s['category']}`: {s['description']}")
        lines.append("")
    return "\n".join(lines)

def generate_by_technology_md(skills):
    tech_groups = defaultdict(list)
    for s in skills:
        techs = s["technologies"]
        if not techs:
            techs = ["General / Agnostic"]
        for t in techs:
            tech_groups[t].append(s)

    lines = [
        "# Skills by Technology",
        "",
        "Discover skills tailored to specific frameworks, platforms, and languages.",
        ""
    ]
    for t in sorted(tech_groups.keys()):
        lines.append(f"## {t} ({len(tech_groups[t])} skills)")
        lines.append("")
        for s in tech_groups[t]:
            lines.append(f"- [{s['name']}](../{s['path']}/SKILL.md) — {s['description']}")
        lines.append("")
    return "\n".join(lines)

def generate_by_role_md(skills):
    role_groups = defaultdict(list)
    for s in skills:
        text = (s["name"] + " " + s["description"] + " " + s["domain"] + " " + s["category"]).lower()
        matched = False
        for role, keywords in ROLE_MAPPINGS.items():
            if any(k in text for k in keywords):
                role_groups[role].append(s)
                matched = True
        if not matched:
            role_groups["Software Engineer"].append(s)

    lines = [
        "# Skills by Developer Role",
        "",
        "Curated workflows organized by professional role and specialization.",
        ""
    ]
    for role in sorted(role_groups.keys()):
        lines.append(f"## {role} ({len(role_groups[role])} skills)")
        lines.append("")
        for s in role_groups[role]:
            lines.append(f"- [{s['name']}](../{s['path']}/SKILL.md) — `{s['domain']}`: {s['description']}")
        lines.append("")
    return "\n".join(lines)

def generate_category_indexes(skills):
    os.makedirs(CAT_DIR, exist_ok=True)
    cat_map = defaultdict(list)
    for s in skills:
        cat_map[s["category"]].append(s)

    for cat, cskills in cat_map.items():
        file_path = os.path.join(CAT_DIR, f"{cat}.md")
        lines = [
            f"# Category Index: {cat.replace('-', ' ').title()}",
            "",
            f"> **{len(cskills)} skills** available in this category.",
            "",
            "| Skill | Subcategory | Complexity | Maturity | Description |",
            "|---|---|---|---|---|"
        ]
        for s in cskills:
            link = f"[{s['name']}](../../{s['path']}/SKILL.md)"
            desc = s['description'].replace("|", "\\|")
            lines.append(f"| {link} | `{s['subcategory']}` | `{s['complexity']}` | `{s['maturity']}` | {desc} |")
        lines.append("")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

def update_readme_stats(skills_count):
    readme_path = os.path.join(BASE_DIR, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Replace badge or count
        updated = re.sub(r"skills-(\d+[\+]?)-blue", f"skills-{skills_count}+-blue", content)
        updated = re.sub(r"\*\*Total Active Skills\*\*:\s*`\d+`", f"**Total Active Skills**: `{skills_count}`", updated)
        if updated != content:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(updated)

def main():
    os.makedirs(DOCS_DIR, exist_ok=True)
    skills = scan_all_skills()
    print(f"Generating catalogs and indexes for {len(skills)} skills...")

    # Write SKILLS.md and docs/SKILLS.md
    cat_md = generate_markdown_catalog(skills)
    with open(os.path.join(BASE_DIR, "SKILLS.md"), "w", encoding="utf-8") as f:
        f.write(cat_md)
    with open(os.path.join(DOCS_DIR, "SKILLS.md"), "w", encoding="utf-8") as f:
        f.write(cat_md)

    # Write master machine-readable inventory
    with open(os.path.join(DOCS_DIR, "skill-inventory.json"), "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2)

    # Write search index
    search_index = [
        {
            "name": s["name"],
            "path": s["path"],
            "domain": s["domain"],
            "category": s["category"],
            "subcategory": s["subcategory"],
            "description": s["description"],
            "tags": s["tags"],
            "technologies": s["technologies"],
            "complexity": s["complexity"],
            "maturity": s["maturity"]
        }
        for s in skills
    ]
    with open(os.path.join(BASE_DIR, "skills-index.json"), "w", encoding="utf-8") as f:
        json.dump(search_index, f, indent=2)
    with open(os.path.join(DOCS_DIR, "skills-index.json"), "w", encoding="utf-8") as f:
        json.dump(search_index, f, indent=2)

    # Write specialized indexes
    with open(os.path.join(DOCS_DIR, "CATEGORIES.md"), "w", encoding="utf-8") as f:
        f.write(generate_categories_md(skills))

    with open(os.path.join(DOCS_DIR, "TAXONOMY.md"), "w", encoding="utf-8") as f:
        f.write(generate_taxonomy_md(skills))

    with open(os.path.join(DOCS_DIR, "STATISTICS.md"), "w", encoding="utf-8") as f:
        f.write(generate_statistics_md(skills))

    with open(os.path.join(DOCS_DIR, "BY-TASK.md"), "w", encoding="utf-8") as f:
        f.write(generate_by_task_md(skills))

    with open(os.path.join(DOCS_DIR, "BY-TECHNOLOGY.md"), "w", encoding="utf-8") as f:
        f.write(generate_by_technology_md(skills))

    with open(os.path.join(DOCS_DIR, "BY-ROLE.md"), "w", encoding="utf-8") as f:
        f.write(generate_by_role_md(skills))

    # Generate individual category files
    generate_category_indexes(skills)

    # Update README
    update_readme_stats(len(skills))

    print("All catalogs, indexes, and documentation updated successfully.")

if __name__ == "__main__":
    main()
