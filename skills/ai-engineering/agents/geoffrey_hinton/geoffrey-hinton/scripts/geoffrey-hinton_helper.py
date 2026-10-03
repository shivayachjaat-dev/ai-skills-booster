#!/usr/bin/env python3
"""
Geoffrey Hinton Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from representation_learning_advisor import HintonRepresentationAdvisor, verify_hinton_advisor

def main():
    print("============================================================")
    print("Running Geoffrey Hinton Deep Learning Diagnostics Suite")
    print("============================================================")
    verify_hinton_advisor()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
