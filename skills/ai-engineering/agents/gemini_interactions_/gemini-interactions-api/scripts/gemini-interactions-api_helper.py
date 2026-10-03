#!/usr/bin/env python3
"""
Gemini Interactions API Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_interactions_client import GeminiInteractionsClient, verify_gemini_interactions

def main():
    print("============================================================")
    print("Running Gemini Interactions API Verification Suite")
    print("============================================================")
    verify_gemini_interactions()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
