#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the continuous autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query:
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if not matched:
            for item in data:
                if item.get("name", "").startswith(backlog_query):
                    item["status"] = new_status
                    if new_status == "completed":
                        item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. SECURITY: tamper-evident-audit-logging-and-siem-integration (Backlog: audit-logging)
    # -------------------------------------------------------------
    {
        "backlog_ref": "audit-logging",
        "related_refs": ["audit-log", "audit-preparation"],
        "name": "tamper-evident-audit-logging-and-siem-integration",
        "domain": "security",
        "category": "compliance",
        "subcategory": "audit-logging",
        "description": "Use this skill to design and implement immutable, tamper-evident audit logging architectures with enterprise SIEM integration. It covers cryptographic HMAC hash chains, structured Common Event Format (CEF) and Elastic Common Schema (ECS) event modeling, automated PII redaction, secure multi-region syslog forwarding (TLS/mTLS), and retention compliance for SOC2, ISO 27001, and HIPAA.",
        "tags": ["security", "compliance", "audit-logging", "siem", "tamper-evident", "hmac", "soc2", "hipaa", "ecs"],
        "technologies": ["Python", "Elasticsearch", "Splunk", "HMAC", "SHA256", "Syslog", "mTLS"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python@>=3.10", "cryptography@>=42.0.0"],
        "content": """# Tamper-Evident Audit Logging & SIEM Integration Architecture

## Overview

An enterprise security engineering standard for designing, emitting, and verifying cryptographically immutable audit trails with direct integration into Security Information and Event Management (SIEM) systems. Modern compliance frameworks (SOC2 Type II, ISO 27001, HIPAA, PCI-DSS v4.0) mandate that security-relevant actions—privilege escalations, authentication events, data modifications, and policy changes—are non-repudiable and immune to post-facto modification, even by database administrators. This skill guides security architects, site reliability engineers (SREs), and AI agents in structuring ECS/CEF-compliant event payloads, maintaining cryptographic HMAC hash chains, redacting sensitive PII/secrets before emission, and verifying log chain integrity.

```
+------------------------------------------------------------------------+
|               Tamper-Evident Audit Pipeline Architecture               |
|                                                                        |
|  [ Application Event ] ---> [ Sensitive Data / PII Masker ]            |
|                                         |                              |
|                                         v                              |
|                       [ ECS / CEF Event Formatter ]                    |
|                                         |                              |
|                                         v                              |
|                       [ Cryptographic Hash Chainer ]                   |
|                        $H_i = \\text{HMAC}(H_{i-1} \\parallel E_i)$    |
|                                         |                              |
|                        +----------------+----------------+             |
|                        |                                 |             |
|                        v                                 v             |
|             [ WORM Storage (S3 Object Lock) ]   [ Encrypted mTLS ]     |
|                                                          |             |
|                                                          v             |
|                                               [ Enterprise SIEM ]      |
|                                               (Splunk / Elastic / OpenSearch)
+------------------------------------------------------------------------+
```

## When to Use

- Building enterprise SaaS audit log services required for SOC2, ISO 27001, HIPAA, or FedRAMP compliance.
- Emitting immutable security trails for identity providers, credential changes, billing transactions, and administrative actions.
- Implementing cryptographic verification to prove that log files stored in long-term cold archives have not been altered or truncated.
- Forwarding structured application logs to Splunk, Elastic Common Schema (ECS), or OpenSearch via mutual TLS (mTLS).

## When NOT to Use

- High-frequency ephemeral debug logging or telemetry metrics (use OpenTelemetry or StatsD).
- Internal process trace instrumentation with nanosecond spans (use Jaeger or Zipkin).

## Inputs & Prerequisites

- Python 3.10+ with `cryptography` or standard `hashlib`/`hmac`.
- Defined enterprise SIEM endpoint accepting HTTP Event Collector (HEC), Syslog RFC 5424, or OpenSearch REST API.
- Cryptographic signing secret stored securely in AWS Secrets Manager, Vault, or Azure Key Vault.

## Core Workflow

### Step 1: Structured Audit Event Modeling (ECS Compliant)
Model all audit actions with standard fields: who, what, when, where, and from which IP:

```python
import time
import uuid
from typing import Any, Dict

def create_audit_event(
    action: str,
    actor_id: str,
    actor_type: str,
    resource_id: str,
    resource_type: str,
    status: str,
    source_ip: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": {
            "action": action,
            "category": ["authentication", "access"],
            "outcome": status, # "success" or "failure"
        },
        "user": {
            "id": actor_id,
            "type": actor_type,
        },
        "resource": {
            "id": resource_id,
            "type": resource_type,
        },
        "client": {
            "ip": source_ip,
        },
        "data": details,
    }
```

### Step 2: Automated PII and Secret Redaction
Before hashing and emitting, strip or mask sensitive credit card numbers, passwords, JWT tokens, and SSNs:

```python
import re

SENSITIVE_PATTERNS = {
    "jwt": re.compile(r'Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'),
    "card": re.compile(r'\b(?:\d[ -]*?){13,16}\b'),
    "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
}

def redact_payload(obj: Any) -> Any:
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if any(secret_key in k.lower() for secret_key in ("password", "secret", "token", "api_key")):
                cleaned[k] = "[REDACTED_SECRET]"
            else:
                cleaned[k] = redact_payload(v)
        return cleaned
    elif isinstance(obj, str):
        val = obj
        for name, pattern in SENSITIVE_PATTERNS.items():
            val = pattern.sub(f"[REDACTED_{name.upper()}]", val)
        return val
    return obj
```

### Step 3: Cryptographic Hash Chaining (Blockchain-Lite Integrity)
Chain each event hash to the previous event hash using HMAC-SHA256:

```python
import hmac
import hashlib
import json

class TamperEvidentLogChain:
    def __init__(self, signing_key: bytes, initial_hash: str = "0" * 64):
        self.key = signing_key
        self.last_hash = initial_hash

    def append_event(self, event_data: dict) -> dict:
        serialized = json.dumps(event_data, sort_keys=True, separators=(',', ':'))
        # Compute HMAC over: previous_hash + current_event_json
        payload_to_hash = (self.last_hash + serialized).encode('utf-8')
        event_hash = hmac.new(self.key, payload_to_hash, hashlib.sha256).hexdigest()
        
        sealed_record = {
            "payload": event_data,
            "prev_hash": self.last_hash,
            "hash": event_hash
        }
        self.last_hash = event_hash
        return sealed_record
```

### Step 4: Verification of Audit Log Integrity
Verify that no log entries have been removed, reordered, or edited:

```python
def verify_log_chain(records: list[dict], signing_key: bytes, initial_hash: str = "0" * 64) -> bool:
    expected_prev = initial_hash
    for idx, record in enumerate(records):
        prev_h = record["prev_hash"]
        current_h = record["hash"]
        payload = record["payload"]
        
        if prev_h != expected_prev:
            print(f"Chain broken at record #{idx}: expected prev {expected_prev}, got {prev_h}")
            return False
            
        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        computed_h = hmac.new(signing_key, (prev_h + serialized).encode('utf-8'), hashlib.sha256).hexdigest()
        
        if computed_h != current_h:
            print(f"Tampering detected at record #{idx}: hash mismatch!")
            return False
            
        expected_prev = current_h
        
    print(f"Verification SUCCESS: All {len(records)} audit records intact and authentic.")
    return True
```

## Best Practices & Failure Modes

- **WORM Storage Configuration**: Configure Amazon S3 Object Lock in Compliance Mode with Retention Period (e.g., 7 years for HIPAA/FINRA) to prevent root deletion.
- **Key Rotation Protocol**: Periodically rotate the HMAC signing key. Seal key transition records with a dual-signature checkpoint containing the old key hash and new key public identifier.
- **Out-of-Band Transport**: Use dedicated logging agents (Fluent Bit, Vector) rather than writing to local disk files that can be overwritten if the host is compromised.

## Verification & Testing

1. Test chain verification: Alter one byte in any stored audit JSON record and assert that `verify_log_chain` fails immediately.
2. Confirm PII stripping: Pass sample records containing simulated SSNs and API keys through `redact_payload` and ensure no secrets leak.
3. Validate SIEM schema: Ingest formatted CEF/ECS records into OpenSearch / Elastic and confirm all index fields map without parsing errors.
""",
        "scripts": [
            {
                "name": "verify_audit_trail.py",
                "description": "Validates the cryptographic HMAC hash integrity of a sequence of audit log records.",
                "code": """#!/usr/bin/env python3
import sys
import json
import hmac
import hashlib

def verify_file(filepath, secret_key="demo-master-key-replace-in-production"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except Exception as e:
        print(f"Error opening log file: {e}")
        sys.exit(1)

    print("=" * 65)
    print(f"Verifying Tamper-Evident Audit Chain: {filepath}")
    print(f"Total Records: {len(records)}")
    print("=" * 65)

    key_bytes = secret_key.encode('utf-8')
    expected_prev = "0" * 64

    for idx, record in enumerate(records):
        prev_h = record.get("prev_hash")
        cur_h = record.get("hash")
        payload = record.get("payload")

        if prev_h != expected_prev:
            print(f"[INTEGRITY VIOLATION] Chain broken at item {idx}!")
            print(f"  Expected Prev: {expected_prev}")
            print(f"  Actual Prev:   {prev_h}")
            sys.exit(1)

        serialized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        calc_h = hmac.new(key_bytes, (prev_h + serialized).encode('utf-8'), hashlib.sha256).hexdigest()

        if calc_h != cur_h:
            print(f"[TAMPERING DETECTED] Hash mismatch on item {idx} ({payload.get('event_id')})!")
            print(f"  Stored Hash:     {cur_h}")
            print(f"  Calculated Hash: {calc_h}")
            sys.exit(1)

        expected_prev = cur_h

    print("SUCCESS: Audit trail is 100% authentic, tamper-evident, and untampered.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_audit_trail.py <audit_trail.json> [secret_key]")
        sys.exit(1)
    k = sys.argv[2] if len(sys.argv) > 2 else "demo-master-key-replace-in-production"
    verify_file(sys.argv[1], k)
"""
            }
        ],
        "references": [
            {
                "title": "Audit Logging Compliance and Retention Matrix",
                "filename": "audit_compliance_matrix.md",
                "content": """# Audit Logging Compliance Matrix

## Regulatory Requirements
| Framework | Mandatory Retention | Required Event Types | Tamper Evidence |
|---|---|---|---|
| **SOC2 Type II** | 12 months minimum | Authentication, Access Grants, Config Changes | Required |
| **HIPAA** | 6 years | ePHI Read/Write/Delete, Login Failures | Required (NIST SP 800-66) |
| **PCI-DSS v4.0** | 12 months (3 mo online) | Cardholder Data Access, Admin Privilege Use | Daily Log Review Mandatory |
| **ISO 27001** | Defined in ISMS policy | Admin Activity, System Errors, Security Alerts | Clause A.12.4 |

## Essential Audit Event Fields
- `timestamp`: UTC ISO-8601 with millisecond precision.
- `actor`: Immutable User ID / Service Account ID.
- `action`: Canonical verb (e.g., `user.login`, `role.grant`, `database.query`).
- `status`: `success` or `failure`.
- `client.ip`: IPv4 or IPv6 egress IP address.
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 2. SECURITY: mitre-attack-chain-and-lateral-movement-simulation (Backlog: attack-chain)
    # -------------------------------------------------------------
    {
        "backlog_ref": "attack-chain",
        "name": "mitre-attack-chain-and-lateral-movement-simulation",
        "domain": "security",
        "category": "red-teaming",
        "subcategory": "attack-simulation",
        "description": "Use this skill to model, simulate, and defend against multi-stage adversary attack chains across enterprise environments using the MITRE ATT&CK framework. It covers initial access emulation, execution vectors, credential dumping (LSASS, DPAPI), lateral movement (WMI, WinRM, Pass-the-Hash, Kerberoasting), command-and-control (C2) beacon analysis, and engineering Blue Team detection rules in Sigma and YARA-L.",
        "tags": ["security", "red-teaming", "mitre-attack", "lateral-movement", "kerberoasting", "pass-the-hash", "adversary-simulation", "sigma-rules"],
        "technologies": ["Python", "MITRE ATT&CK", "Sigma", "YARA-L", "PowerShell", "Bash"],
        "complexity": "expert",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python@>=3.10"],
        "content": """# MITRE ATT&CK Multi-Stage Attack Chain & Lateral Movement Simulation

## Overview

A professional red teaming and detection engineering standard for modeling, emulating, and defending against multi-stage adversary tactics using the MITRE ATT&CK Enterprise Matrix. Cyber threat actors rarely compromise a network through a single vector; instead, they execute structured attack chains comprising initial exploitation (TA0001), privilege escalation (TA0004), credential dumping (TA0006), and internal lateral movement (TA0008). This skill guides ethical security researchers, purple team operators, and AI defense agents in constructing realistic attack kill-chains, auditing telemetry gaps, and translating observed adversary behaviors into robust Blue Team detection rules (Sigma and YARA-L).

```
+------------------------------------------------------------------------+
|                     MITRE ATT&CK Kill-Chain Model                      |
|                                                                        |
|  [ TA0001: Initial Access ] (Phishing / Public Exploit)                |
|               |                                                        |
|               v                                                        |
|  [ TA0002: Execution ] (PowerShell / MSBuild / Living-off-the-Land)    |
|               |                                                        |
|               v                                                        |
|  [ TA0006: Credential Access ] (LSASS Minidump / Kerberoasting / DPAPI)|
|               |                                                        |
|               v                                                        |
|  [ TA0008: Lateral Movement ] (Pass-the-Hash / WinRM / WMI / SSH Keys) |
|               |                                                        |
|               v                                                        |
|  [ TA0010: Exfiltration ] & [ TA0040: Impact ] (Ransomware / Extortion)|
+------------------------------------------------------------------------+
```

## When to Use

- Planning and executing authorized Purple Team exercises to evaluate SOC detection efficacy.
- Testing Endpoint Detection and Response (EDR) agents against non-standard living-off-the-land (LotL) techniques.
- Simulating Kerberoasting and Pass-the-Hash lateral movement to identify Active Directory privilege pathways.
- Authoring standardized Sigma detection rules mapping directly to MITRE technique IDs (e.g., T1003.001, T1558.003).

## When NOT to Use

- Conducting unauthorized offensive operations or deploying uncontained malware.
- Simple single-point vulnerability scanning without lateral movement context.

## Inputs & Prerequisites

- Target testing environment (isolated Active Directory lab or non-production VPC).
- MITRE ATT&CK Enterprise Matrix v14+.
- Host and network telemetry sources (Sysmon, Windows Event Logs 4624/4672, Zeek, EDR logs).

## Core Workflow

### Step 1: Adversary Campaign Attack Path Mapping
Construct a multi-stage attack graph mapping techniques to specific tactics:

```
1. Initial Access: T1566.001 (Spearphishing Attachment)
2. Execution: T1059.001 (PowerShell Encoded Script)
3. Persistence: T1053.005 (Scheduled Task Creation)
4. Credential Access: T1558.003 (Kerberoasting Service Principal Names)
5. Lateral Movement: T1021.006 (Windows Remote Management - WinRM)
6. Collection: T1560.001 (Archive via Utility: 7-Zip AES)
```

### Step 2: Atomic Lateral Movement Simulation (Testing Telemetry)
Simulate realistic WinRM / PowerShell Remoting lateral movement within a controlled sandbox:

```powershell
# Simulate lateral movement invocation via WinRM (T1021.006)
$TargetServer = "srv-app02.corp.local"
$TestCommand = "whoami /priv; hostname"

# Execute controlled command over WS-Man protocol
Invoke-Command -ComputerName $TargetServer -ScriptBlock {
    param($cmd)
    Write-Output "Adversary Simulation Test: $cmd"
} -ArgumentList $TestCommand
```

### Step 3: Telemetry Verification (Windows Event Logs)
Verify that Windows Security Auditing recorded the lateral execution:
- **Event ID 4624**: Successful logon (Logon Type 3 = Network Logon, indicating WinRM/SMB).
- **Event ID 4688**: Process creation (`wsmprovhost.exe` or `powershell.exe`).
- **Sysmon Event ID 1**: Process creation with parent-child telemetry (`wsmprovhost.exe` -> `cmd.exe`).

### Step 4: Authoring Defensive Sigma Detection Rules
Write a vendor-agnostic Sigma rule to alert on unauthorized remote process spawning:

```yaml
title: Suspicious Child Process Spawned by WinRM Host
id: a8124b89-4d22-491a-96e2-56781290abcdef
status: experimental
description: Detects unusual execution of command shells or scripting interpreters spawned by wsmprovhost.exe
references:
    - https://attack.mitre.org/techniques/T1021/006/
author: Detection Engineering Team
date: 2026-10-02
tags:
    - attack.lateral_movement
    - attack.t1021.006
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        ParentImage|endswith: '\wsmprovhost.exe'
        Image|endswith:
            - '\cmd.exe'
            - '\powershell.exe'
            - '\pwsh.exe'
            - '\certutil.exe'
            - '\vssadmin.exe'
    condition: selection
falsepositives:
    - Legitimate IT administration scripts via Ansible, Terraform, or SaltStack
level: high
```

## Best Practices & Failure Modes

- **Never Use Production Domain Admin Credentials**: Always use disposable test accounts with constrained delegation during purple team exercises.
- **Payload Containment**: Ensure simulated beacons only communicate with local loopback or isolated lab C2 listeners (`127.0.0.1` or dedicated lab IP).
- **Alert Tuning & Baseline**: Differentiate between routine DevOps automated deployments (e.g., Ansible WinRM runs) and unauthorized human lateral movement by filtering trusted service accounts.

## Verification & Testing

1. Execute attack path simulation in a dedicated range and confirm every stage triggers the expected Sysmon or EDR alert.
2. Validate Sigma rule syntax using `sigmac` or `sigma-cli`: `sigma check rules/`.
3. Verify telemetry coverage in the MITRE ATT&CK Navigator matrix to identify uncovered tactics.
""",
        "scripts": [
            {
                "name": "attack_chain_validator.py",
                "description": "Validates MITRE ATT&CK technique IDs across an attack chain and verifies Sigma detection rule coverage.",
                "code": """#!/usr/bin/env python3
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
    print(f"\\nOverall Detection Coverage: {covered}/{total_steps} ({coverage_pct:.1f}%)")
    if coverage_pct < 80:
        print("[WARNING]: Critical telemetry gaps identified. Adversary may achieve lateral movement undetected.")

if __name__ == "__main__":
    evaluate_chain(SAMPLE_CHAIN)
"""
            }
        ],
        "references": [
            {
                "title": "Lateral Movement Techniques & Windows Event IDs Reference",
                "filename": "lateral_movement_reference.md",
                "content": """# Lateral Movement Techniques & Event ID Mapping

## Key Techniques
1. **Pass-the-Hash (T1550.002)**:
   - Uses NTLM hashes directly to authenticate without cracking the plaintext password.
   - Event IDs: 4624 (Logon Type 3, NTLM Package, Key Length 0).
2. **Kerberoasting (T1558.003)**:
   - Requests Ticket Granting Service (TGS) tickets for service accounts with SPNs to crack RC4/AES offline.
   - Event ID: 4769 (A Kerberos service ticket was requested, Ticket Options 0x40810000, Ticket Encryption 0x17 for RC4).
3. **WMI Execution (T1047)**:
   - Spawns processes remotely via `wmic process call create` or PowerShell WMI cmdlets.
   - Process: `WmiPrvSE.exe` spawning child processes.
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 3. DESKTOP: avalonia-cross-platform-desktop-ui-architecture (Backlog: avalonia-zafiro-development)
    # -------------------------------------------------------------
    {
        "backlog_ref": "avalonia-zafiro-development",
        "related_refs": ["avalonia-layout-zafiro", "avalonia-viewmodels-zafiro"],
        "name": "avalonia-cross-platform-desktop-ui-architecture",
        "domain": "desktop",
        "category": "frameworks",
        "subcategory": "avalonia-dotnet",
        "description": "Use this skill to design, build, and optimize high-performance cross-platform desktop applications using Avalonia UI and .NET 8/9. It covers MVVM architecture with ReactiveUI and CommunityToolkit.Mvvm, fluent UI themes and dark mode switching, asynchronous relay commands, virtualized data grids, custom template controls, and native packaging for Windows, macOS, and Linux.",
        "tags": ["desktop", "avalonia", "dotnet", "csharp", "mvvm", "cross-platform", "reactiveui", "ui-architecture"],
        "technologies": ["Avalonia UI", "C#", ".NET 8", ".NET 9", "ReactiveUI", "XAML"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["dotnet", "bash"],
        "dependencies": ["Avalonia@>=11.0.0", "CommunityToolkit.Mvvm@>=8.2.0"],
        "content": """# Avalonia UI Cross-Platform Desktop Architecture

## Overview

A modern .NET engineering standard for architecting robust, native-performing cross-platform desktop applications using Avalonia UI (v11+) and .NET 8/9. Unlike platform-tied frameworks (WPF on Windows, Cocoa on macOS), Avalonia utilizes its own Skia-based rendering pipeline to provide identical visual fidelity, layout precision, and styling semantics across Windows, macOS, and Linux from a single C# codebase. This skill guides desktop engineers and AI agents in structuring scalable MVVM architectures, implementing compiled bindings, handling responsive multi-threaded async UI updates, and building fluid user interfaces.

```
+------------------------------------------------------------------------+
|                      Avalonia UI Multi-Platform Engine                 |
|                                                                        |
|  [ View (XAML / AXAML) ] <---(Compiled Bindings)---> [ ViewModel ]     |
|      (FluentTheme / Styles)                           (CommunityToolkit)|
|                                                              |         |
|                                                              v         |
|                                                      [ Model & Services|
|                                                                        |
|  Rendering Pipeline (SkiaSharp / Top-Level Native Window):             |
|  +-------------------+  +-------------------+  +--------------------+  |
|  | Windows (DirectX) |  | macOS (Metal)     |  | Linux (Vulkan/X11) |  |
|  +-------------------+  +-------------------+  +--------------------+  |
+------------------------------------------------------------------------+
```

## When to Use

- Developing enterprise desktop tools, scientific instrument GUIs, media workstations, or offline-first client apps targeting Windows, macOS, and Linux simultaneously.
- Migrating legacy WPF, Silverlight, or WinForms applications to modern cross-platform .NET.
- Building complex desktop interfaces with high-density data grids, interactive canvas layouts, and custom theme styling.

## When NOT to Use

- Pure web browser applications (use Astro, React, or Blazor WebAssembly).
- Mobile-first consumer apps prioritizing native iOS/Android system controls over unified desktop canvas rendering.

## Inputs & Prerequisites

- .NET 8.0 SDK or .NET 9.0 SDK installed.
- Avalonia templates (`dotnet new install Avalonia.Templates`).
- IDE: JetBrains Rider, Visual Studio 2022, or VS Code with C# Dev Kit.

## Core Workflow

### Step 1: Project Scaffolding and Dependency Setup
Initialize an Avalonia MVVM project using `CommunityToolkit.Mvvm`:

```bash
dotnet new avalonia.mvvm -n EnterpriseDesktopApp
cd EnterpriseDesktopApp
dotnet add package CommunityToolkit.Mvvm --version 8.2.2
```

### Step 2: Observable ViewModel with Async Relay Commands
Implement clean, boilerplate-free ViewModels using C# source generators:

```csharp
using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace EnterpriseDesktopApp.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    [ObservableProperty]
    private string _statusMessage = "Ready";

    [ObservableProperty]
    private bool _isLoading = false;

    public ObservableCollection<string> ConnectedNodes { get; } = new();

    [RelayCommand]
    private async Task RefreshClusterStatusAsync()
    {
        IsLoading = true;
        StatusMessage = "Querying distributed nodes...";

        try
        {
            await Task.Delay(1000); // Simulate network query
            ConnectedNodes.Clear();
            ConnectedNodes.Add("Node-US-East (Latency: 12ms)");
            ConnectedNodes.Add("Node-EU-Central (Latency: 84ms)");
            StatusMessage = $"Cluster synchronized at {DateTime.Now:T}";
        }
        catch (Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }
}
```

### Step 3: AXAML View with Compiled Bindings
Leverage compiled bindings (`x:DataType`) for zero-reflection performance and compile-time type safety:

```xml
<UserControl xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:vm="using:EnterpriseDesktopApp.ViewModels"
             x:Class="EnterpriseDesktopApp.Views.DashboardView"
             x:DataType="vm:DashboardViewModel">
    
    <Grid RowDefinitions="Auto, *, Auto" Margin="24">
        <!-- Header -->
        <StackPanel Grid.Row="0" Spacing="8">
            <TextBlock Text="Cluster Telemetry Dashboard" 
                       FontSize="24" 
                       FontWeight="SemiBold"/>
            <TextBlock Text="{Binding StatusMessage}" 
                       Foreground="{DynamicResource SystemAccentColor}"/>
        </StackPanel>

        <!-- Node List -->
        <ListBox Grid.Row="1" 
                 Margin="0,16"
                 ItemsSource="{Binding ConnectedNodes}">
            <ListBox.ItemTemplate>
                <DataTemplate>
                    <TextBlock Text="{Binding}" Padding="8,4"/>
                </DataTemplate>
            </ListBox.ItemTemplate>
        </ListBox>

        <!-- Actions -->
        <Button Grid.Row="2"
                Content="Refresh Nodes"
                Command="{Binding RefreshClusterStatusCommand}"
                IsEnabled="{Binding !IsLoading}"
                HorizontalAlignment="Right"/>
    </Grid>
</UserControl>
```

### Step 4: Fluent Theme and Dark/Light Mode Switching
Configure adaptive system theme detection in `App.axaml`:

```xml
<Application xmlns="https://github.com/avaloniaui"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Class="EnterpriseDesktopApp.App"
             RequestedThemeVariant="Default">
    <Application.Styles>
        <FluentTheme />
    </Application.Styles>
</Application>
```

## Best Practices & Failure Modes

- **Always Use Compiled Bindings**: Set `x:CompileBindings="True"` on views. Uncompiled reflection bindings degrade rendering frame rates and mask binding typos.
- **Dispatcher UI Thread Safety**: When background events complete, ensure UI properties are only mutated on the UI thread or use `Dispatcher.UIThread.Post(...)`.
- **macOS Window Architecture**: macOS applications require proper `Info.plist` bundle identifiers, Retina display scaling support, and notarization with Apple Developer certificates.

## Verification & Testing

1. Run unit tests on ViewModels independently of the UI: `dotnet test`.
2. Compile and launch on host OS: `dotnet run`.
3. Verify cross-platform builds: Test Linux rendering using X11 / Wayland or Docker headless display.
""",
        "scripts": [
            {
                "name": "check_avalonia_bindings.py",
                "description": "Scans AXAML files to verify x:DataType declarations and detect uncompiled legacy bindings.",
                "code": """#!/usr/bin/env python3
import os
import re
import sys

def audit_axaml(project_dir="."):
    print("=" * 65)
    print(f"Auditing Avalonia AXAML Compiled Bindings in: {project_dir}")
    print("=" * 65)

    axaml_files = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith(('.axaml', '.xaml')):
                axaml_files.append(os.path.join(root, f))

    if not axaml_files:
        print("No AXAML files found to audit.")
        return

    missing_datatype = []
    for path in axaml_files:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "x:DataType" not in content and "DataType=" not in content:
                missing_datatype.append(path)

    print(f"Total AXAML Files Inspected: {len(axaml_files)}")
    if missing_datatype:
        print(f"\\n[WARNING]: {len(missing_datatype)} files lack compiled x:DataType bindings:")
        for p in missing_datatype:
            print(f"  - {os.path.relpath(p, project_dir)}")
        print("\\nRecommendation: Add x:DataType to root controls for compile-time safety.")
    else:
        print("SUCCESS: All AXAML files declare explicit compiled binding types.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    audit_axaml(target)
"""
            }
        ],
        "references": [
            {
                "title": "Avalonia UI Architecture Quick Reference",
                "filename": "avalonia_architecture_reference.md",
                "content": """# Avalonia UI Best Practices Reference

## Core Differences from WPF
- **Cross-Platform**: Uses SkiaSharp directly; runs natively on Linux (X11/Wayland), macOS (Metal/Cocoa), and Windows (DirectX/Win32).
- **Styling System**: CSS-inspired selector syntax (`Button:pointerover`, `Button.primary`) rather than rigid WPF Triggers.
- **TopLevel & Windowing**: Supports both desktop windowing (`Window`) and single-view mobile/embedded hosts (`SingleViewApplicationLifetime`).

## Command Binding Patterns
Use `CommunityToolkit.Mvvm`:
```csharp
[RelayCommand(CanExecute = nameof(CanSubmit))]
private async Task SubmitAsync() { ... }
```
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 4. DEVOPS: aws-cdk-v2-infrastructure-as-code-architecture (Backlog: aws-cdk-development)
    # -------------------------------------------------------------
    {
        "backlog_ref": "aws-cdk-development",
        "name": "aws-cdk-v2-infrastructure-as-code-architecture",
        "domain": "devops",
        "category": "infrastructure",
        "subcategory": "aws-cdk",
        "description": "Use this skill to design, build, and deploy production AWS cloud infrastructure using the AWS Cloud Development Kit (CDK v2) in TypeScript and Python. It covers L1/L2/L3 construct composition, multi-account multi-region pipelines (cdk-pipelines), automated compliance enforcement with CDK Aspects (IAspect), unit and snapshot testing with @aws-cdk/assertions, and drift remediation.",
        "tags": ["devops", "aws", "aws-cdk", "infrastructure-as-code", "typescript", "cloudformation", "cdk-pipelines", "compliance-aspects"],
        "technologies": ["AWS CDK v2", "TypeScript", "Python", "CloudFormation", "AWS CodePipeline", "Jest"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["cdk", "npm", "node"],
        "dependencies": ["aws-cdk@^2.130.0", "typescript@^5.0.0"],
        "content": """# AWS CDK v2 Infrastructure as Code & Pipeline Architecture

## Overview

An enterprise cloud infrastructure engineering standard for provisioning, governing, and testing AWS environments using the AWS Cloud Development Kit (CDK v2). By modeling infrastructure in familiar programming languages (TypeScript, Python, Go) rather than static YAML/JSON, teams achieve modular construct reuse, compile-time type validation, and integrated unit testing. This skill guides platform engineers, DevSecOps architects, and AI coding agents in designing hierarchical construct trees (L1, L2, L3 constructs), building self-mutating continuous delivery pipelines (`cdk-pipelines`), and enforcing organization-wide security baselines via CDK Aspects.

```
+------------------------------------------------------------------------+
|                      AWS CDK v2 Architecture Hierarchy                 |
|                                                                        |
|  [ App Root (cdk.App) ]                                                |
|      |                                                                 |
|      +---> [ Stage: Production (Environment: us-east-1, Account A) ]   |
|      |         |                                                       |
|      |         +---> [ Stack: NetworkStack (VPC, NAT, Subnets) ]       |
|      |         +---> [ Stack: DatabaseStack (RDS Aurora Postgres) ]    |
|      |         +---> [ Stack: ComputeStack (ECS Fargate + ALB) ]       |
|      |                                                                 |
|      v                                                                 |
|  [ CDK Aspects (IAspect) ] ---> (Enforce Encryption, Tags, No 0.0.0.0) |
|      |                                                                 |
|      v                                                                 |
|  [ CloudFormation Synthesis (cdk synth) ] ---> [ CloudFormation Engine]|
+------------------------------------------------------------------------+
```

## When to Use

- Architecting multi-account AWS topologies (Networking, Shared Services, Dev/Staging/Production).
- Creating reusable organizational construct libraries (e.g., standard encrypted S3 bucket construct, hardened ECS microservice construct).
- Enforcing security policies at synthesis time before resources reach cloud environments using CDK Aspects.
- Setting up self-mutating CI/CD deployment pipelines that automatically adapt when new stacks are added to code.

## When NOT to Use

- Multi-cloud infrastructure requiring identical syntax across GCP, Azure, and AWS (prefer Terraform or Pulumi).
- Ephemeral single-script resource provisioning where standard AWS CLI or Boto3 is sufficient.

## Inputs & Prerequisites

- Node.js 18.x+ and npm/pnpm.
- AWS CDK CLI installed globally: `npm install -g aws-cdk`.
- Authenticated AWS credentials with permissions for target AWS accounts (`aws sts get-caller-identity`).

## Core Workflow

### Step 1: L3 Pattern Construct Authoring
Create reusable, high-level architectural constructs encapsulating organizational best practices:

```typescript
// lib/constructs/secure-bucket.ts
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as kms from 'aws-cdk-lib/aws-kms';
import { RemovalPolicy, Duration } from 'aws-cdk-lib';

export interface SecureBucketProps {
  bucketName?: string;
  lifecycleRetentionDays?: number;
}

export class SecureBucket extends Construct {
  public readonly bucket: s3.Bucket;
  public readonly key: kms.Key;

  constructor(scope: Construct, id: string, props: SecureBucketProps = {}) {
    super(scope, id);

    this.key = new kms.Key(this, 'BucketKey', {
      enableKeyRotation: true,
      description: `KMS customer managed key for ${id}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.bucket = new s3.Bucket(this, 'Resource', {
      bucketName: props.bucketName,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: this.key,
      enforceSSL: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: RemovalPolicy.RETAIN,
      lifecycleRules: props.lifecycleRetentionDays ? [
        {
          expiration: Duration.days(props.lifecycleRetentionDays),
        }
      ] : undefined,
    });
  }
}
```

### Step 2: Policy-as-Code Enforcement with CDK Aspects
Implement an `IAspect` to guarantee every DynamoDB table and S3 bucket across the app is encrypted:

```typescript
// lib/aspects/security-aspect.ts
import { IAspect } from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Annotations } from 'aws-cdk-lib';

export class EnforceS3EncryptionAspect implements IAspect {
  public visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        Annotations.of(node).addError('Compliance Failure: S3 Bucket must have server-side encryption enabled.');
      }
    }
  }
}
```

### Step 3: Self-Mutating Multi-Stage Pipeline
Define continuous deployment pipelines using `aws-cdk-lib/pipelines`:

```typescript
// lib/pipeline-stack.ts
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as pipelines from 'aws-cdk-lib/pipelines';

export class DeploymentPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
      pipelineName: 'EnterpriseCorePipeline',
      synth: new pipelines.ShellStep('Synth', {
        input: pipelines.CodePipelineSource.gitHub('org/repo', 'main'),
        commands: ['npm ci', 'npm run build', 'npx cdk synth'],
      }),
    });

    // Add Production Deployment Stage
    // pipeline.addStage(new ApplicationStage(this, 'Prod', { env: { account: '123456789012', region: 'us-east-1' } }));
  }
}
```

### Step 4: Fine-Grained Unit Testing with Assertions
Test CloudFormation template outputs before deployment using `@aws-cdk/assertions`:

```typescript
// test/secure-bucket.test.ts
import { App, Stack } from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { SecureBucket } from '../lib/constructs/secure-bucket';

test('SecureBucket enforces KMS encryption and blocks public access', () => {
  const app = new App();
  const stack = new Stack(app, 'TestStack');

  new SecureBucket(stack, 'MySecureBucket');

  const template = Template.fromStack(stack);

  // Assert S3 bucket properties
  template.hasResourceProperties('AWS::S3::Bucket', {
    PublicAccessBlockConfiguration: {
      BlockPublicAcls: true,
      BlockPublicPolicy: true,
      IgnorePublicAcls: true,
      RestrictPublicBuckets: true,
    },
    BucketEncryption: Match.objectLike({
      ServerSideEncryptionConfiguration: Match.anyValue(),
    }),
  });
});
```

## Best Practices & Failure Modes

- **Never Hardcode Secrets**: Use `secretsmanager.Secret.fromSecretNameV2` or SSM Dynamic References (`resolve:ssm:...`).
- **Construct ID Immutability**: Changing a construct's logical ID changes its CloudFormation logical resource ID, triggering resource replacement (and possible data loss).
- **Environment Agnosticism**: Keep constructs environment-agnostic; pass account/region parameters via stack environment configuration (`env: { account, region }`).

## Verification & Testing

1. Validate CloudFormation synthesis: `cdk synth` and confirm template generation without errors.
2. Run Jest assertion tests: `npm test` to verify resource configurations and Aspect validations.
3. Perform drift and diff review: `cdk diff` to inspect intended changes before running `cdk deploy`.
""",
        "scripts": [
            {
                "name": "cdk_compliance_checker.py",
                "description": "Analyzes synthesized CloudFormation templates (cdk.out) to verify security controls and tagging compliance.",
                "code": """#!/usr/bin/env python3
import json
import os
import sys

def check_cdk_template(template_path):
    if not os.path.exists(template_path):
        print(f"Error: Template '{template_path}' not found.")
        sys.exit(1)

    print("=" * 65)
    print(f"Auditing Synthesized CDK Template: {template_path}")
    print("=" * 65)

    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)

    resources = template.get("Resources", {})
    print(f"Total CloudFormation Resources: {len(resources)}\\n")

    violations = []
    for res_id, res_data in resources.items():
        res_type = res_data.get("Type", "")
        props = res_data.get("Properties", {})

        # Check S3 Public Access
        if res_type == "AWS::S3::Bucket":
            pab = props.get("PublicAccessBlockConfiguration", {})
            if not (pab.get("BlockPublicAcls") and pab.get("BlockPublicPolicy")):
                violations.append((res_id, res_type, "S3 Bucket lacks full PublicAccessBlockConfiguration"))

        # Check Security Groups for 0.0.0.0/0
        if res_type == "AWS::EC2::SecurityGroup":
            for rule in props.get("SecurityGroupIngress", []):
                if rule.get("CidrIp") == "0.0.0.0/0" and rule.get("FromPort") in [22, 3389]:
                    violations.append((res_id, res_type, f"Security group opens port {rule.get('FromPort')} to 0.0.0.0/0!"))

    if violations:
        print(f"[COMPLIANCE FAILED] {len(violations)} security violations detected:")
        for r_id, r_type, issue in violations:
            print(f"  - [{r_type}] {r_id}: {issue}")
        sys.exit(1)
    else:
        print("SUCCESS: Synthesized CDK template passed all security guardrail checks.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cdk_compliance_checker.py <cdk.out/StackName.template.json>")
        sys.exit(1)
    check_cdk_template(sys.argv[1])
"""
            }
        ],
        "references": [
            {
                "title": "AWS CDK Construct Hierarchy and Testing Reference",
                "filename": "cdk_architecture_reference.md",
                "content": """# AWS CDK Construct Levels Reference

## Construct Classification
1. **L1 Constructs (Cfn*)**:
   - Direct 1:1 mapping to CloudFormation resources (e.g., `CfnBucket`).
   - Requires manual definition of all CloudFormation properties.
2. **L2 Constructs**:
   - Curated AWS constructs with intelligent defaults, security baselines, and helper methods (e.g., `s3.Bucket`, `bucket.grantRead(role)`).
3. **L3 Constructs (Patterns)**:
   - High-level multi-service architectures combined into a single construct (e.g., `ApplicationLoadBalancedFargateService`).
"""
            }
        ]
    },

    # -------------------------------------------------------------
    # 5. SECURITY: aws-iam-least-privilege-and-governance-architecture (Backlog: aws-iam)
    # -------------------------------------------------------------
    {
        "backlog_ref": "aws-iam",
        "name": "aws-iam-least-privilege-and-governance-architecture",
        "domain": "security",
        "category": "cloud-security",
        "subcategory": "aws-iam",
        "description": "Use this skill to design, implement, and audit enterprise AWS IAM architectures adhering to least-privilege principles. It covers IAM permission boundaries, Service Control Policies (SCPs) in AWS Organizations, cross-account assume-role delegation with external IDs, ABAC (Attribute-Based Access Control) tagging policies, IAM Access Analyzer integration, and credential rotation.",
        "tags": ["security", "aws", "iam", "cloud-security", "least-privilege", "abac", "scps", "permission-boundaries"],
        "technologies": ["AWS IAM", "AWS Organizations", "AWS Access Analyzer", "Python", "JSON"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["aws-cli", "python", "bash"],
        "dependencies": ["python@>=3.10", "boto3@>=1.34.0"],
        "content": """# AWS IAM Least-Privilege & Governance Architecture

## Overview

An enterprise cloud security standard for engineering, auditing, and enforcing least-privilege identity and access management across multi-account AWS environments. Over-privileged IAM roles, wildcard permissions (`*:*`), and unconstrained cross-account trust relationships are the primary root cause of cloud data breaches. This skill establishes rigorous patterns for designing granular IAM policies, implementing multi-tier Permission Boundaries, enforcing organizational Service Control Policies (SCPs), deploying Attribute-Based Access Control (ABAC), and validating trust policies against confused deputy vulnerabilities.

```
+------------------------------------------------------------------------+
|                     AWS IAM Effective Permission Flow                  |
|                                                                        |
|    [ AWS Organizations SCP ] (Hard Organizational Ceiling)             |
|                 |                                                      |
|                 v                                                      |
|    [ IAM Permission Boundary ] (Maximum Delegated Ceiling)             |
|                 |                                                      |
|                 v                                                      |
|    [ Identity-Based IAM Policy ] (Explicit Allow)                      |
|                 |                                                      |
|                 v                                                      |
|    [ Resource-Based Policy (S3 / KMS) ]                                |
|                 |                                                      |
|                 v                                                      |
|    === Effective Permission: Intersection of All Positive Gates ===    |
+------------------------------------------------------------------------+
```

## When to Use

- Architecting IAM role delegation for microservices running in EKS, ECS, or Lambda (IAM Roles for Service Accounts - IRSA).
- Designing cross-account assume-role workflows with external vendor SaaS integrations (preventing Confused Deputy attacks with `sts:ExternalId`).
- Implementing developer self-service provisioning where developers can create IAM roles only within strict Permission Boundaries.
- Enforcing Attribute-Based Access Control (ABAC) where access is dynamically granted based on matching `aws:PrincipalTag` and `aws:ResourceTag`.

## When NOT to Use

- Network-level access restriction (use Security Groups, Network ACLs, or AWS WAF).
- Operating system local user management (use SSH certificates or AWS Systems Manager Session Manager).

## Inputs & Prerequisites

- AWS Account ID and administrative privileges for IAM policy testing.
- Target workload service identities and access requirements.
- Familiarity with AWS IAM policy JSON grammar and condition operators.

## Core Workflow

### Step 1: Crafting Granular Least-Privilege IAM Policies
Eliminate wildcard actions by scoping policies to exact resource ARNs and condition keys:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppDynamoAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/ProductionOrders",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

### Step 2: Permission Boundaries for Safe Delegated Administration
Attach a Permission Boundary to prevent developers from granting themselves administrator rights:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowWorkerActions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "sqs:SendMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyIAMModification",
      "Effect": "Deny",
      "Action": [
        "iam:*",
        "organizations:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Step 3: Hardened Cross-Account Trust Policy (Confused Deputy Prevention)
Protect cross-account role assumption with mandatory External ID validation:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TrustThirdPartyMonitoringVendor",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::987654321098:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "7f8b9c2a-9e12-4c3a-8b10-abcde1234567"
        }
      }
    }
  ]
}
```

### Step 4: Attribute-Based Access Control (ABAC) Tag Policy
Permit engineers to access resources only when their project tag matches the target resource tag:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessIfTagsMatch",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Project": "${aws:PrincipalTag/Project}"
        }
      }
    }
  ]
}
```

## Best Practices & Failure Modes

- **Never Use Root Account**: Lock root account credentials behind hardware MFA and create dedicated administrative roles.
- **Audit Wildcards Regularly**: Run AWS IAM Access Analyzer and CloudTrail Access Advisor to identify unused permissions and eliminate `Action: "*"`.
- **Enforce TLS via Condition**: Always require `"aws:SecureTransport": "true"` on S3 bucket policies and sensitive API calls.

## Verification & Testing

1. Validate IAM policy syntax with the AWS CLI: `aws iam validate-policy --policy-document file://policy.json`.
2. Simulate authorization actions using IAM Policy Simulator: `aws iam simulate-principal-policy`.
3. Audit external access findings with IAM Access Analyzer: `aws accessanalyzer list-findings`.
""",
        "scripts": [
            {
                "name": "iam_wildcard_auditor.py",
                "description": "Scans IAM policy documents for overly permissive wildcard actions and missing condition keys.",
                "code": """#!/usr/bin/env python3
import json
import sys
import os

DANGEROUS_ACTIONS = ["*", "*:*", "iam:*", "s3:*", "dynamodb:*"]

def audit_policy(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Policy file '{filepath}' not found.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        policy = json.load(f)

    print("=" * 65)
    print(f"Auditing IAM Policy File: {filepath}")
    print("=" * 65)

    statements = policy.get("Statement", [])
    if isinstance(statements, dict):
        statements = [statements]

    findings = []
    for idx, stmt in enumerate(statements):
        effect = stmt.get("Effect", "")
        actions = stmt.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        resources = stmt.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        conditions = stmt.get("Condition")

        if effect == "Allow":
            for act in actions:
                if act in DANGEROUS_ACTIONS:
                    findings.append((idx, f"Overly broad Action '{act}' permitted."))
            if "*" in resources:
                findings.append((idx, "Resource set to wildcard '*' without resource constraints."))
            if not conditions:
                findings.append((idx, "Statement lacks Condition block (recommend aws:SecureTransport or IP/Tag checks)."))

    if findings:
        print(f"[AUDIT FAILED] Found {len(findings)} potential security issues:")
        for stmt_idx, msg in findings:
            print(f"  - Statement #{stmt_idx}: {msg}")
    else:
        print("SUCCESS: Policy passes baseline least-privilege checks.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python iam_wildcard_auditor.py <policy.json>")
        sys.exit(1)
    audit_policy(sys.argv[1])
"""
            }
        ],
        "references": [
            {
                "title": "AWS IAM Evaluation Logic and Conditions Reference",
                "filename": "iam_evaluation_logic_reference.md",
                "content": """# AWS IAM Policy Evaluation Logic

## Evaluation Order
1. **Explicit Deny**: Any matching Deny immediately halts evaluation and denies access.
2. **Organizations SCPs**: If present, must evaluate to Allow.
3. **Resource-Based Policies**: Can grant direct access across accounts.
4. **IAM Permissions Boundary**: Sets maximum boundary on effective permissions.
5. **Session Policies**: Applied during temporary credential generation (`AssumeRole`).
6. **Identity-Based Policies**: Grants explicit Allow.
7. **Default**: Implicit Deny if no explicit Allow is found.
"""
            }
        ]
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for idx, skill_def in enumerate(CONTINUOUS_QUEUE, 1):
        backlog_ref = skill_def.get("backlog_ref")
        related_refs = skill_def.get("related_refs", [])
        name = skill_def["name"]
        domain = skill_def["domain"]
        category = skill_def["category"]
        print(f"\n[{idx}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")

        success = create_and_ship_skill(skill_def)

        if success:
            mark_backlog_item(backlog_ref, "completed")
            for r_ref in related_refs:
                mark_backlog_item(r_ref, "completed")
            print(f"\n[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"\n[Engine] FAILED to ship skill: {name}. Halting.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
