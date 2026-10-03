#!/usr/bin/env python3
"""
Fable Safe Prompt Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_safety_reframer import PromptSafetyReframer, verify_prompt_reframer

def main():
    print("============================================================")
    print("Running Fable Safe Prompt Verification Suite")
    print("============================================================")
    verify_prompt_reframer()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
