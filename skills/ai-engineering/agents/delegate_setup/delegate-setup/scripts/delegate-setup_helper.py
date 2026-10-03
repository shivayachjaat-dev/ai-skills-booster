#!/usr/bin/env python3
"""
Delegate Setup Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from delegate_setup_orchestrator import DelegateSetupManager, verify_delegate_setup

def main():
    print("============================================================")
    print("Running Delegate Setup Diagnostics Suite")
    print("============================================================")
    verify_delegate_setup()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
