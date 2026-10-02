#!/usr/bin/env python3
"""
check_public_disclosure.py - Automated public-disclosure and privacy guardrail.
Scans the entire repository for:
- Local Windows drive paths (e.g. C:\\Users, C:/Users, D:\\, etc.)
- Reference repository names (e.g. agentic-awesome-skills, agent-skills)
- Internal provenance & source repository mappings (source_repo, derived_from, etc.)
- Internal audit/backlog references
- Credentials, private tokens, API keys

Exits with code 0 if 100% clean, exits with code 1 if any prohibited disclosure is detected.
"""

import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Prohibited patterns with explanations
PROHIBITED_PATTERNS = [
    # Reference repositories
    (re.compile(r"agentic-awesome-skills", re.IGNORECASE), "Reference repository name 'agentic-awesome-skills'"),
    (re.compile(r"agent-skills\b", re.IGNORECASE), "Reference repository name 'agent-skills'"),
    
    # Internal provenance and source tracking fields
    (re.compile(r"['\"]?source_repo['\"]?\s*:", re.IGNORECASE), "Internal field 'source_repo'"),
    (re.compile(r"['\"]?derived_from['\"]?\s*:", re.IGNORECASE), "Internal field 'derived_from'"),
    (re.compile(r"['\"]?upstream_source['\"]?\s*:", re.IGNORECASE), "Internal field 'upstream_source'"),
    (re.compile(r"['\"]?original_repository['\"]?\s*:", re.IGNORECASE), "Internal field 'original_repository'"),
    (re.compile(r"\bprovenance\.md\b", re.IGNORECASE), "Reference to PROVENANCE.md"),
    (re.compile(r"\baudit_report\.md\b", re.IGNORECASE), "Reference to AUDIT_REPORT.md"),
    (re.compile(r"\bskill-backlog\.json\b", re.IGNORECASE), "Reference to skill-backlog.json"),
    
    # Local Windows paths
    (re.compile(r"[a-zA-Z]:\\\\Users\\\\[a-zA-Z0-9_]+", re.IGNORECASE), "Local Windows user path (escaped)"),
    (re.compile(r"[a-zA-Z]:/Users/[a-zA-Z0-9_]+", re.IGNORECASE), "Local Windows user path (forward slash)"),
    (re.compile(r"\\\\Users\\\\[a-zA-Z0-9_]+", re.IGNORECASE), "Local user path"),
    (re.compile(r"/Users/[a-zA-Z0-9_]+", re.IGNORECASE), "Local user path"),
    (re.compile(r"\bMy_AI_Skills\b", re.IGNORECASE), "Local directory 'My_AI_Skills'"),
    
    # High-entropy secrets and keys
    (re.compile(r"ghp_[a-zA-Z0-9]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key ID"),
    (re.compile(r"-----BEGIN (RSA|EC|OPENSSH)? PRIVATE KEY-----"), "Private Key header"),
]

IGNORED_DIRECTORIES = {
    ".git",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".venv",
    "venv"
}

ALLOWED_EXTENSIONS = {
    ".md", ".json", ".yml", ".yaml", ".py", ".ts", ".js", ".sh", ".txt"
}

def scan_file(filepath):
    violations = []
    rel_path = os.path.relpath(filepath, BASE_DIR).replace("\\", "/")
    
    # Skip self
    if rel_path == "scripts/check_public_disclosure.py":
        return violations

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        violations.append((rel_path, 0, f"Cannot read file: {e}", ""))
        return violations

    for line_idx, line in enumerate(lines, 1):
        for pat, desc in PROHIBITED_PATTERNS:
            if pat.search(line):
                violations.append((rel_path, line_idx, desc, line.strip()))

    return violations

def main():
    print("=" * 70)
    print("Running Public Disclosure and Privacy Guardrail Scan")
    print("=" * 70)

    total_files = 0
    all_violations = []

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS or file in ["LICENSE", ".gitignore"]:
                total_files += 1
                filepath = os.path.join(root, file)
                v = scan_file(filepath)
                all_violations.extend(v)

    print(f"Scanned {total_files} repository files.")

    if all_violations:
        print("\n" + "!" * 70)
        print(f"CRITICAL: Found {len(all_violations)} prohibited disclosure violation(s)!")
        print("!" * 70)
        for rel_path, line_num, desc, line in all_violations:
            print(f"\n[VIOLATION] {rel_path}:{line_num}")
            print(f"  Reason:  {desc}")
            print(f"  Content: {line[:120]}")
        print("\nCommit BLOCKED. Please remove all prohibited disclosures before committing.")
        sys.exit(1)

    print("\nSUCCESS: Zero prohibited disclosures detected across all repository files.")
    print("Repository is completely self-contained and safe for public release.")
    print("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    main()
