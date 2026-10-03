#!/usr/bin/env python3
"""
Folder-Specific Claude and Agents MD Helper & Diagnostic Test Runner
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from folder_guidance_generator import FolderGuidanceGenerator, verify_folder_guidance

def main():
    print("============================================================")
    print("Running Folder-Specific Guidance Verification Suite")
    print("============================================================")
    verify_folder_guidance()
    print("\nSTATUS: Operational and ready.")

if __name__ == "__main__":
    main()
