#!/usr/bin/env python3
"""
Git PR Workflows Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_pr_orchestrator import GitPROrchestrator, verify_git_pr_orchestrator

def main():
    print("============================================================")
    print("Running Git PR Workflows Verification Suite")
    print("============================================================")
    verify_git_pr_orchestrator()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
