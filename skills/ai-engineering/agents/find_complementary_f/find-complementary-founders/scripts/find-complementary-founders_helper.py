#!/usr/bin/env python3
"""
Find Complementary Founders Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from founder_matching_engine import ComplementaryFounderMatcher, verify_founder_matcher

def main():
    print("============================================================")
    print("Running Find Complementary Founders Verification Suite")
    print("============================================================")
    verify_founder_matcher()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
