#!/usr/bin/env python3
"""
Error Debugging Multi-Agent Review Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_agent_debugger import MultiAgentDebugger, verify_multi_agent_debugger

def main():
    print("============================================================")
    print("Running Error Debugging Multi-Agent Review Diagnostics")
    print("============================================================")
    verify_multi_agent_debugger()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
