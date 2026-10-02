---
name: mitre-attack-chain-and-lateral-movement-simulation
description: "Use this skill to model, simulate, and defend against multi-stage adversary attack chains across enterprise environments using the MITRE ATT&CK framework. It covers initial access emulation, execution vectors, credential dumping (LSASS, DPAPI), lateral movement (WMI, WinRM, Pass-the-Hash, Kerberoasting), command-and-control (C2) beacon analysis, and engineering Blue Team detection rules in Sigma and YARA-L."
domain: security
category: red-teaming
subcategory: attack-simulation
tags:
  - security
  - red-teaming
  - mitre-attack
  - lateral-movement
  - kerberoasting
  - pass-the-hash
  - adversary-simulation
  - sigma-rules
technologies:
  - Python
  - MITRE ATT&CK
  - Sigma
  - YARA-L
  - PowerShell
  - Bash
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---
# MITRE ATT&CK Multi-Stage Attack Chain & Lateral Movement Simulation

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
            - 'ssadmin.exe'
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
