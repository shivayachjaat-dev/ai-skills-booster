#!/usr/bin/env python3
"""
ai-loop_helper.py - Operational verification entry point for ai-loop skill
"""
import sys
import subprocess
import os

def run_helper():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    orchestrator_path = os.path.join(script_dir, "ai_loop_orchestrator.py")
    
    print("=" * 60)
    print("AI Loop Verification: Executing State Machine & Scope Harness")
    print("=" * 60)
    
    res = subprocess.run([sys.executable, orchestrator_path, "--test-all"], capture_output=True, text=True)
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
