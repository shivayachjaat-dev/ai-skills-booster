#!/usr/bin/env python3
import sys
import re
import os

SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS Access Key"),
    (re.compile(r"ghp_[0-9a-zA-Z]{36}"), "GitHub Personal Access Token"),
    (re.compile(r"-----BEGIN (RSA|EC|OPENSSH)? PRIVATE KEY-----"), "Private Key"),
    (re.compile(r"(?i)(password|secret|token|api_key)\s*[:=]\s*['"][^'"]{10,}['"]"), "Hardcoded Credential")
]

def scan_diff_file(filepath):
    if not os.path.exists(filepath):
        print(f"Diff file {filepath} not found.")
        return 1
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    findings = 0
    for idx, line in enumerate(lines, 1):
        if line.startswith("+") and not line.startswith("+++"):
            for pat, desc in SECRET_PATTERNS:
                if pat.search(line):
                    print(f"[ALERT] Line {idx}: {desc} detected: {line.strip()[:60]}...")
                    findings += 1
    print(f"Scan complete. {findings} potential secrets flagged.")
    return 0 if findings == 0 else 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_pr_diff.py <diff_file>")
        sys.exit(1)
    sys.exit(scan_diff_file(sys.argv[1]))
