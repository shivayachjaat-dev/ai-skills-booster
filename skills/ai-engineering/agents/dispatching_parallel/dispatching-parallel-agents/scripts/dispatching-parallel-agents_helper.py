#!/usr/bin/env python3
"""
Dispatching Parallel Agents Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parallel_agent_dispatcher import ParallelAgentDispatcher, verify_parallel_dispatcher

def main():
    print("============================================================")
    print("Running Dispatching Parallel Agents Verification Suite")
    print("============================================================")
    verify_parallel_dispatcher()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
