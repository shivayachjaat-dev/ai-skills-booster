#!/usr/bin/env python3
"""
ax-extract-workflow_helper.py - Operational verification entry point for ax-extract-workflow skill
"""
import sys
import subprocess
import os

def run_helper():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    engine_path = os.path.join(script_dir, "workflow_reconstruction_engine.py")
    
    print("=" * 60)
    print("Workflow Forensics Verification: Executing Reconstruction Suite")
    print("=" * 60)
    
    res = subprocess.run([sys.executable, engine_path, "--test-all"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
        
    if res.returncode == 0:
        print("STATUS: Operational and ready.")
    else:
        print(f"STATUS: Failed with exit code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    run_helper()
