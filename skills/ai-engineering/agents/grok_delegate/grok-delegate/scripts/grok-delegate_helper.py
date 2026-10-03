#!/usr/bin/env python3
"""
Grok Delegate Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grok_delegator import GrokDelegator, verify_grok_delegator

def main():
    print("============================================================")
    print("Running Grok Delegate Verification Suite")
    print("============================================================")
    verify_grok_delegator()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
