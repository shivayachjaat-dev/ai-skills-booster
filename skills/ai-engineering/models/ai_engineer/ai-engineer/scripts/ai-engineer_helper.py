#!/usr/bin/env python3
"""
ai-engineer_helper.py - Operational verification entry point for ai-engineer skill
"""
import sys
import subprocess
import os

def run_helper():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    profiler_path = os.path.join(script_dir, "llm_gateway_profiler.py")
    
    print("=" * 60)
    print("AI Engineer Verification: Executing LLM Gateway Profiler Suite")
    print("=" * 60)
    
    res = subprocess.run([sys.executable, profiler_path, "--test-all"], capture_output=True, text=True)
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
