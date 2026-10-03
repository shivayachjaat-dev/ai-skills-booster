#!/usr/bin/env python3
"""
ECL Harness Engineer Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ecl_harness import ECLHarness, verify_ecl_harness

def main():
    print("============================================================")
    print("Running ECL Harness Engineer Verification Suite")
    print("============================================================")
    verify_ecl_harness()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
