#!/usr/bin/env python3
"""
talking-avatar-video_helper.py - Integrity and Pre-Flight Cost Calculator.
Verifies package archive SHA-256 checksums, checks credential permissions,
and calculates cost estimates before dispatching avatar video generation tasks.
"""

import sys
import os
import hashlib
import json
import argparse

EXPECTED_DIGEST = "cb62d8e3fa65b48f3c3f1803e2008e1b9c25ff057c0a35184e8fcc7d9771eb80"

# Standard cost model: credits per second of output video
MODEL_RATES = {
    "avatar-v2-standard": 1.5,
    "avatar-v2-hd": 3.0,
    "avatar-v2-expressive": 4.5,
}

def verify_archive_hash(archive_path: str, expected_hash: str = EXPECTED_DIGEST) -> bool:
    if not os.path.exists(archive_path):
        print(f"Error: Archive '{archive_path}' not found.")
        return False

    sha256 = hashlib.sha256()
    with open(archive_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    
    actual_hash = sha256.hexdigest()
    print("=" * 60)
    print("Package SHA-256 Integrity Verification")
    print("=" * 60)
    print(f"File:           {os.path.basename(archive_path)}")
    print(f"Actual Hash:    {actual_hash}")
    print(f"Expected Hash:  {expected_hash}")
    
    if actual_hash.lower() == expected_hash.lower():
        print("RESULT: [PASSED] Cryptographic digest verified.")
        return True
    else:
        print("RESULT: [FAILED] Checksum mismatch! Possible tampering.")
        return False

def check_credentials_security(creds_path: str = None) -> bool:
    if not creds_path:
        home = os.path.expanduser("~")
        creds_path = os.path.join(home, ".beatra", "credentials.json")

    print("\n" + "=" * 60)
    print("Audit Credential Storage Security")
    print("=" * 60)
    print(f"Target Path: {creds_path}")

    if not os.path.exists(creds_path):
        print("Status: No credentials file found. (Clean state)")
        return True

    # On POSIX systems, check for 0600 permissions
    if hasattr(os, "stat"):
        st = os.stat(creds_path)
        mode = oct(st.st_mode)[-3:]
        print(f"File Permissions: {mode}")
        if os.name != 'nt' and mode not in ["600", "400"]:
            print(f"[WARNING]: Insecure file permissions ({mode}). Must be 0600 (chmod 600 {creds_path}).")
            return False
        else:
            print("Permissions check: [SECURE]")

    return True

def generate_cost_card(audio_duration_sec: float, model: str = "avatar-v2-standard", balance: float = 100.0):
    rate = MODEL_RATES.get(model, 2.0)
    estimated_credits = round(audio_duration_sec * rate, 2)
    has_sufficient_balance = balance >= estimated_credits

    print("\n" + "=" * 60)
    print("PRE-FLIGHT COST APPROVAL CARD")
    print("=" * 60)
    print(f"Target Model:         {model}")
    print(f"Base Rate:            {rate} credits / second")
    print(f"Audio Duration:       {audio_duration_sec:.2f} seconds")
    print(f"Estimated Total:      {estimated_credits} credits")
    print(f"Current Balance:      {balance:.2f} credits")
    print(f"Balance Sufficient:   {'YES' if has_sufficient_balance else 'NO (Top-up required)'}")
    print("=" * 60)
    print("CRITICAL: Do not dispatch task without explicit user approval of this cost card.")
    return {
        "model": model,
        "duration": audio_duration_sec,
        "estimated_credits": estimated_credits,
        "balance": balance,
        "approved_to_run": has_sufficient_balance
    }

def main():
    parser = argparse.ArgumentParser(description="Talking Avatar Video Pre-Flight & Verification Utility")
    parser.add_argument("--verify-archive", type=str, help="Path to package tar.gz archive to verify SHA-256")
    parser.add_argument("--check-creds", action="store_true", help="Audit local credentials permissions")
    parser.add_argument("--estimate-cost", type=float, help="Calculate cost card for given audio duration in seconds")
    parser.add_argument("--model", type=str, default="avatar-v2-standard", choices=list(MODEL_RATES.keys()))
    parser.add_argument("--balance", type=float, default=100.0, help="Current prepaid credit balance")

    args = parser.parse_args()

    if args.verify_archive:
        ok = verify_archive_hash(args.verify_archive)
        sys.exit(0 if ok else 1)

    if args.check_creds:
        ok = check_credentials_security()
        sys.exit(0 if ok else 1)

    if args.estimate_cost:
        generate_cost_card(args.estimate_cost, args.model, args.balance)
        return

    # Default action: run self-diagnostics
    print("=" * 60)
    print("Talking Avatar Video Helper: Ready")
    print("Supported Models:")
    for m, r in MODEL_RATES.items():
        print(f"  - {m:<22}: {r} credits/sec")
    print("\nRun with --help to see available verification and estimation tools.")

if __name__ == "__main__":
    main()
