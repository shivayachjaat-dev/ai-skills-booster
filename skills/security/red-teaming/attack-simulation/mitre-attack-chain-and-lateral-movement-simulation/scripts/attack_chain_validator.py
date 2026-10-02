#!/usr/bin/env python3
import sys

VALID_TACTICS = {
    "TA0001": "Initial Access",
    "TA0002": "Execution",
    "TA0003": "Persistence",
    "TA0004": "Privilege Escalation",
    "TA0005": "Defense Evasion",
    "TA0006": "Credential Access",
    "TA0007": "Discovery",
    "TA0008": "Lateral Movement",
    "TA0009": "Collection",
    "TA0010": "Exfiltration",
    "TA0011": "Command and Control",
    "TA0040": "Impact"
}

SAMPLE_CHAIN = [
    {"step": 1, "tactic": "TA0001", "technique": "T1566.001", "desc": "Spearphishing Attachment", "has_detection": True},
    {"step": 2, "tactic": "TA0002", "technique": "T1059.001", "desc": "PowerShell Script Execution", "has_detection": True},
    {"step": 3, "tactic": "TA0006", "technique": "T1558.003", "desc": "Kerberoasting SPN Request", "has_detection": False},
    {"step": 4, "tactic": "TA0008", "technique": "T1021.006", "desc": "WinRM Lateral Execution", "has_detection": True},
    {"step": 5, "tactic": "TA0010", "technique": "T1567.002", "desc": "Exfiltration to Cloud Storage", "has_detection": False},
]

def evaluate_chain(chain):
    print("=" * 65)
    print("MITRE ATT&CK Attack Chain & Detection Coverage Audit")
    print("=" * 65)
    
    total_steps = len(chain)
    covered = 0
    
    for item in chain:
        tactic_name = VALID_TACTICS.get(item["tactic"], "Unknown Tactic")
        status = "[DETECTED]" if item["has_detection"] else "[TELEMETRY GAP]"
        if item["has_detection"]:
            covered += 1
        print(f"Step {item['step']}: {item['technique']:<10} | {tactic_name:<20} | {status:<15} | {item['desc']}")
        
    coverage_pct = (covered / total_steps) * 100
    print(f"\nOverall Detection Coverage: {covered}/{total_steps} ({coverage_pct:.1f}%)")
    if coverage_pct < 80:
        print("[WARNING]: Critical telemetry gaps identified. Adversary may achieve lateral movement undetected.")

if __name__ == "__main__":
    evaluate_chain(SAMPLE_CHAIN)
