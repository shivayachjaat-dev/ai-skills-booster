#!/usr/bin/env python3
"""
Evaluation Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_eval_framework import AgentEvaluationHarness, verify_eval_framework

def main():
    print("============================================================")
    print("Running Agent Evaluation Framework Verification Suite")
    print("============================================================")
    verify_eval_framework()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
