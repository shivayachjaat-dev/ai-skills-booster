#!/usr/bin/env python3
"""
Elon Musk Engineering Persona & First-Principles Helper Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principles_engine import FirstPrinciplesReviewer, verify_first_principles_reviewer

def main():
    print("============================================================")
    print("Running Elon Musk First-Principles Diagnostics Suite")
    print("============================================================")
    verify_first_principles_reviewer()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
