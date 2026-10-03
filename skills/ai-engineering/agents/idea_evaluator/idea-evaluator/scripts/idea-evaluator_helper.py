#!/usr/bin/env python3
"""
Idea Evaluator Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dialectical_idea_evaluator import DialecticalIdeaEvaluator, verify_idea_evaluator

def main():
    print("============================================================")
    print("Running Dialectical Idea Evaluator Verification Suite")
    print("============================================================")
    verify_idea_evaluator()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
