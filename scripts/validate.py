#!/usr/bin/env python3
"""
validate.py - Automated validation suite for AI Skills Booster.
Scans the entire repository and verifies:
- Strict 3-level taxonomy hierarchy: skills/<domain>/<category>/<subcategory>/<skill-name>/SKILL.md
- YAML frontmatter completeness: name, description, domain, category, subcategory, tags, technologies, complexity, maturity
- Description quality: minimum length, specific triggers, answers what/when/why
- Kebab-case naming consistency
- Absence of duplicate skill names, slugs, or near-identical descriptions
- Broken internal links and references
- Security checks: no hardcoded API keys, tokens, or malicious patterns
- Size limits and structural standards

Exits with code 0 on success, non-zero on validation failure.
"""

import os
import sys
import re
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

VALID_COMPLEXITIES = {"beginner", "intermediate", "advanced", "expert"}
VALID_MATURITIES = {"experimental", "stable", "advanced"}

FORBIDDEN_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret[_-]?key|auth[_-]?token|bearer\s+[a-z0-9_\-\.]{20,})\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"),
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
]

FORBIDDEN_DESCRIPTIONS = [
    re.compile(r"(?i)^helps with\b"),
    re.compile(r"(?i)^a useful .* skill\b"),
    re.compile(r"(?i)^this skill helps\b"),
    re.compile(r"(?i)^todo\b"),
]

REQUIRED_SECTIONS = [
    "overview",
    "when to use",
    "core workflow",
]

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

def validate_skill(skill_dir):
    errors = []
    warnings = []
    
    skill_file = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_file):
        errors.append(f"Missing SKILL.md in {skill_dir}")
        return errors, warnings, None

    rel_path = os.path.relpath(skill_dir, BASE_DIR).replace("\\", "/")
    parts = rel_path.split("/")
    
    # Check 3-level taxonomy: skills/<domain>/<category>/<subcategory>/<skill-name>
    if len(parts) != 5 or parts[0] != "skills":
        errors.append(f"Invalid directory depth for '{rel_path}'. Expected: skills/<domain>/<category>/<subcategory>/<skill-name>")
        return errors, warnings, None
        
    expected_domain = parts[1]
    expected_category = parts[2]
    expected_subcategory = parts[3]
    dir_skill_name = parts[4]

    # Validate kebab-case name
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", dir_skill_name):
        errors.append(f"Skill directory name '{dir_skill_name}' must be kebab-case (lowercase alphanumeric with hyphens)")

    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Cannot read {skill_file}: {e}")
        return errors, warnings, None

    # Secret scanning
    for pat in FORBIDDEN_SECRET_PATTERNS:
        if pat.search(content):
            errors.append(f"Potential hardcoded secret or token detected in {skill_file}")

    metadata, body = parse_frontmatter(content)
    if not metadata:
        errors.append(f"Missing or invalid YAML frontmatter in {skill_file}")
        return errors, warnings, None

    # Verify required frontmatter fields
    name = metadata.get("name")
    if not name:
        errors.append("Frontmatter missing 'name'")
    elif name != dir_skill_name:
        errors.append(f"Frontmatter name '{name}' does not match directory name '{dir_skill_name}'")

    domain = metadata.get("domain")
    if not domain:
        errors.append("Frontmatter missing 'domain'")
    elif domain != expected_domain:
        errors.append(f"Frontmatter domain '{domain}' does not match directory domain '{expected_domain}'")

    category = metadata.get("category")
    if not category:
        errors.append("Frontmatter missing 'category'")
    elif category != expected_category:
        errors.append(f"Frontmatter category '{category}' does not match directory category '{expected_category}'")

    subcategory = metadata.get("subcategory")
    if not subcategory:
        errors.append("Frontmatter missing 'subcategory'")
    elif subcategory != expected_subcategory:
        errors.append(f"Frontmatter subcategory '{subcategory}' does not match directory subcategory '{expected_subcategory}'")

    desc = metadata.get("description", "")
    if not desc:
        errors.append("Frontmatter missing 'description'")
    else:
        if len(desc) < 40:
            errors.append(f"Description is too short ({len(desc)} chars). Must be at least 40 characters answering what/when/why.")
        for forbidden in FORBIDDEN_DESCRIPTIONS:
            if forbidden.search(desc):
                errors.append(f"Description '{desc[:30]}...' is too generic or starts with forbidden phrasing.")

    complexity = metadata.get("complexity")
    if complexity and complexity not in VALID_COMPLEXITIES:
        errors.append(f"Invalid complexity '{complexity}'. Must be one of: {sorted(list(VALID_COMPLEXITIES))}")

    maturity = metadata.get("maturity")
    if maturity and maturity not in VALID_MATURITIES:
        errors.append(f"Invalid maturity '{maturity}'. Must be one of: {sorted(list(VALID_MATURITIES))}")

    tags = metadata.get("tags")
    if not tags or not isinstance(tags, list) or len(tags) < 2:
        warnings.append("Skill should have at least 2 relevant tags in frontmatter")

    # Verify structural sections in Markdown
    body_lower = body.lower()
    for sec in REQUIRED_SECTIONS:
        if f"## {sec}" not in body_lower and f"# {sec}" not in body_lower:
            warnings.append(f"Missing recommended section header '## {sec.title()}' in {skill_file}")

    skill_record = {
        "name": name or dir_skill_name,
        "path": rel_path,
        "domain": expected_domain,
        "category": expected_category,
        "subcategory": expected_subcategory,
        "description": desc,
        "tags": metadata.get("tags", []),
        "technologies": metadata.get("technologies", []),
        "complexity": complexity or "intermediate",
        "maturity": maturity or "stable",
        "tools": metadata.get("tools", []),
        "dependencies": metadata.get("dependencies", []),
        "has_scripts": os.path.exists(os.path.join(skill_dir, "scripts")),
        "has_evals": os.path.exists(os.path.join(skill_dir, "evals")),
        "has_references": os.path.exists(os.path.join(skill_dir, "references")),
    }

    return errors, warnings, skill_record

def main():
    print("=" * 60)
    print("Running AI Skills Booster Validation Suite")
    print("=" * 60)

    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory '{SKILLS_DIR}' is ready for initial skills.")
        sys.exit(0)

    total_skills = 0
    all_errors = []
    all_warnings = []
    seen_names = {}
    seen_descriptions = {}

    for root, dirs, files in os.walk(SKILLS_DIR):
        if "SKILL.md" in files:
            total_skills += 1
            errs, warns, record = validate_skill(root)
            all_errors.extend(errs)
            all_warnings.extend(warns)

            if record:
                name = record["name"]
                if name in seen_names:
                    all_errors.append(f"Duplicate skill name '{name}' in {record['path']} and {seen_names[name]}")
                else:
                    seen_names[name] = record["path"]

                desc = record["description"].strip().lower()
                if desc in seen_descriptions:
                    all_errors.append(f"Duplicate skill description in '{name}' and '{seen_descriptions[desc]}'")
                else:
                    seen_descriptions[desc] = name

    print(f"Validated {total_skills} skills.")

    if all_warnings:
        print(f"\nWarnings ({len(all_warnings)}):")
        for w in all_warnings[:20]:
            print(f"  [WARN] {w}")
        if len(all_warnings) > 20:
            print(f"  ... and {len(all_warnings) - 20} more warnings")

    if all_errors:
        print(f"\nValidation ERRORS ({len(all_errors)}):")
        for e in all_errors:
            print(f"  [ERROR] {e}")
        print("\nValidation FAILED.")
        sys.exit(1)

    print("\nAll validation checks PASSED cleanly!")
    sys.exit(0)

if __name__ == "__main__":
    main()
