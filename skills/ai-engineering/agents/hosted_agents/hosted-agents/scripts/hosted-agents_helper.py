#!/usr/bin/env python3
"""
Hosted Agents Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sandbox_agent_runtime import HostedAgentSandbox, verify_hosted_sandbox

def main():
    print("============================================================")
    print("Running Hosted Agent Sandbox Verification Suite")
    print("============================================================")
    verify_hosted_sandbox()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
