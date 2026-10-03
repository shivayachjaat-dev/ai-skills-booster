#!/usr/bin/env python3
"""
Handoff Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from handoff_compiler import HandoffCompiler, verify_handoff_compiler

def main():
    print("============================================================")
    print("Running Agent Session Handoff Verification Suite")
    print("============================================================")
    verify_handoff_compiler()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
