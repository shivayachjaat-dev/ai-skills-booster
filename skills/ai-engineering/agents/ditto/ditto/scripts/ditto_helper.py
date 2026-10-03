#!/usr/bin/env python3
"""
Ditto Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ditto_profiler import DittoProfiler, verify_ditto_miner

def main():
    print("============================================================")
    print("Running Ditto Profile Miner Verification Suite")
    print("============================================================")
    verify_ditto_miner()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
