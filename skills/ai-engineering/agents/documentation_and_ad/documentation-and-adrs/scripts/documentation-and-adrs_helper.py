#!/usr/bin/env python3
"""
Documentation and ADRs Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adr_engine import ADREngine, verify_adr_engine

def main():
    print("============================================================")
    print("Running Documentation and ADRs Diagnostics Suite")
    print("============================================================")
    verify_adr_engine()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
