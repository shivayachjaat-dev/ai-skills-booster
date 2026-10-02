#!/usr/bin/env python3
"""
skill_factory.py - Autonomous Skill Producer and Deployment Engine.
Executes the strict one-skill-per-commit-and-push loop:
1. Verifies taxonomy and duplicates
2. Generates SKILL.md with full production anatomy
3. Writes ancillary files (evals, scripts, references) if specified
4. Validates the entire repository via scripts/validate.py
5. Validates duplicates via scripts/detect_duplicates.py
6. Updates all catalogs, indexes, statistics, and tables via scripts/generate_catalog.py
7. Executes git add, git commit -m "feat(skill): add <skill-name>"
8. Executes git push origin main
"""

import os
import sys
import subprocess
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

def run_cmd(cmd, cwd=BASE_DIR):
    res = subprocess.run(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"Command failed: {cmd}\nOutput: {res.stdout}\nError: {res.stderr}")
        return False, res.stdout + res.stderr
    return True, res.stdout

def create_and_ship_skill(skill_spec):
    name = skill_spec["name"]
    domain = skill_spec["domain"]
    category = skill_spec["category"]
    subcategory = skill_spec["subcategory"]
    description = skill_spec["description"]
    tags = skill_spec.get("tags", [])
    technologies = skill_spec.get("technologies", [])
    complexity = skill_spec.get("complexity", "intermediate")
    maturity = skill_spec.get("maturity", "stable")
    tools = skill_spec.get("tools", [])
    dependencies = skill_spec.get("dependencies", [])
    content = skill_spec["content"]
    evals = skill_spec.get("evals")
    scripts = skill_spec.get("scripts")
    references = skill_spec.get("references")

    target_dir = os.path.join(SKILLS_DIR, domain, category, subcategory, name)
    os.makedirs(target_dir, exist_ok=True)
    skill_md_path = os.path.join(target_dir, "SKILL.md")

    # Format YAML frontmatter
    fm_lines = [
        "---",
        f"name: {name}",
        f"description: \"{description}\"",
        f"domain: {domain}",
        f"category: {category}",
        f"subcategory: {subcategory}",
        "tags:"
    ]
    for t in tags:
        fm_lines.append(f"  - {t}")
    if technologies:
        fm_lines.append("technologies:")
        for tech in technologies:
            fm_lines.append(f"  - {tech}")
    fm_lines.append(f"complexity: {complexity}")
    fm_lines.append(f"maturity: {maturity}")
    if tools:
        fm_lines.append("tools:")
        for tl in tools:
            fm_lines.append(f"  - {tl}")
    if dependencies:
        fm_lines.append("dependencies:")
        for dep in dependencies:
            fm_lines.append(f"  - {dep}")
    fm_lines.append("---")
    fm_lines.append("")

    full_text = "\n".join(fm_lines) + content.strip() + "\n"
    with open(skill_md_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    # Write ancillary files if present
    if evals:
        eval_dir = os.path.join(target_dir, "evals")
        os.makedirs(eval_dir, exist_ok=True)
        if isinstance(evals, dict):
            for fname, fcontent in evals.items():
                with open(os.path.join(eval_dir, fname), "w", encoding="utf-8") as f:
                    f.write(fcontent)
        elif isinstance(evals, list):
            for item in evals:
                fname = item.get("name") or item.get("filename")
                fcontent = item.get("code") or item.get("content", "")
                if fname:
                    with open(os.path.join(eval_dir, fname), "w", encoding="utf-8") as f:
                        f.write(fcontent)

    if scripts:
        script_dir = os.path.join(target_dir, "scripts")
        os.makedirs(script_dir, exist_ok=True)
        if isinstance(scripts, dict):
            for fname, fcontent in scripts.items():
                with open(os.path.join(script_dir, fname), "w", encoding="utf-8") as f:
                    f.write(fcontent)
        elif isinstance(scripts, list):
            for item in scripts:
                fname = item.get("name") or item.get("filename")
                fcontent = item.get("code") or item.get("content", "")
                if fname:
                    with open(os.path.join(script_dir, fname), "w", encoding="utf-8") as f:
                        f.write(fcontent)

    if references:
        ref_dir = os.path.join(target_dir, "references")
        os.makedirs(ref_dir, exist_ok=True)
        if isinstance(references, dict):
            for fname, fcontent in references.items():
                with open(os.path.join(ref_dir, fname), "w", encoding="utf-8") as f:
                    f.write(fcontent)
        elif isinstance(references, list):
            for item in references:
                fname = item.get("filename") or item.get("name")
                fcontent = item.get("content") or item.get("code", "")
                if fname:
                    with open(os.path.join(ref_dir, fname), "w", encoding="utf-8") as f:
                        f.write(fcontent)

    print(f"\n[Factory] Created skill files at {target_dir}")

    # Step 1: Validate
    ok, out = run_cmd("python scripts/validate.py")
    if not ok:
        print(f"[Factory] Validation FAILED:\n{out}")
        return False

    # Step 2: Detect duplicates
    ok, out = run_cmd("python scripts/detect_duplicates.py")
    if not ok:
        print(f"[Factory] Duplicate detection FAILED:\n{out}")
        return False

    # Step 3: Generate catalog & update all docs
    ok, out = run_cmd("python scripts/generate_catalog.py")
    if not ok:
        print(f"[Factory] Catalog generation FAILED:\n{out}")
        return False

    # Step 4: Run Public Disclosure & Privacy Scan
    ok, out = run_cmd("python scripts/check_public_disclosure.py")
    if not ok:
        print(f"[Factory] Public disclosure scan FAILED:\n{out}")
        return False

    # Step 5: Git add
    ok, out = run_cmd("git add .")
    if not ok:
        return False

    # Step 5: Git commit
    commit_msg = f"feat(skill): add {name}"
    ok, out = run_cmd(f'git commit -m "{commit_msg}"')
    if not ok:
        print(f"[Factory] Git commit failed:\n{out}")
        return False

    # Step 6: Git push
    ok, out = run_cmd("git push origin main")
    if not ok:
        print(f"[Factory] Git push failed:\n{out}")
        return False

    print(f"==> Successfully committed and pushed skill: {name}\n")
    return True

if __name__ == "__main__":
    print("Skill Factory ready.")
