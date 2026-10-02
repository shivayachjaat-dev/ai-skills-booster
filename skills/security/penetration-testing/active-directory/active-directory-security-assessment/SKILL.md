---
name: active-directory-security-assessment
description: "Use this skill when auditing, assessing, and hardening Microsoft Active Directory (AD) and hybrid Azure AD/Entra ID environments against common identity attack vectors. It guides the agent through identifying Kerberoasting vulnerabilities, AS-REP roasting, BloodHound attack path mapping, DCSync credential dumping risks, and Active Directory Certificate Services (ADCS) misconfigurations."
domain: security
category: penetration-testing
subcategory: active-directory
tags:
  - active-directory
  - pentesting
  - security
  - kerberos
  - bloodhound
  - adcs
  - red-team
technologies:
  - Active Directory
  - Kerberos
  - BloodHound
  - PowerView
  - Impacket
  - Python
complexity: advanced
maturity: stable
tools:
  - python
  - powershell
dependencies:
  - impacket >= 0.11.0
---
# Active Directory Security Assessment & Hardening Architecture

## Overview

A definitive production security reference for auditing, assessing, and hardening Microsoft Active Directory (AD) enterprise environments against credential attacks and privilege escalation paths. Over 90% of Fortune 500 enterprises rely on Active Directory for identity and access management, making it the primary target during internal network compromises. This skill instructs AI agents on analyzing Kerberos delegation vulnerabilities, identifying Kerberoasting and AS-REP roasting vectors, mapping attack paths using BloodHound, and establishing defenses against DCSync attacks.

## When to Use

- Conducting internal network penetration testing and red-team/blue-team identity audits.
- Identifying over-privileged Domain Admin accounts and unconstrained Kerberos delegation.
- Auditing Service Principal Names (SPNs) configured with weak or crackable service account passwords.
- Defending Active Directory Certificate Services (ADCS) against ESC1-ESC8 template escalation attacks.

## When NOT to Use

- Cloud-native identity providers without Active Directory integration (pure Google Workspace or Okta).
- Web application vulnerability scanning (use OWASP ZAP or Burp Suite).

## Inputs & Prerequisites

- Read-only domain user credentials or access to domain controller audit logs.
- Python 3.10+ with `impacket` installed.
- Understanding of Kerberos ticket granting mechanisms (TGT, TGS).

## Core Workflow

### 1. Kerberoasting Attack Vector Audit
Identify service accounts with registered Service Principal Names (SPNs) vulnerable to offline hash cracking:

```python
from impacket.krb5.kerberosv5 import getKerberosTGT, getKerberosTGS
from impacket.krb5 import constants
import datetime

def audit_service_principal_names(spn_accounts: list[dict]):
    """
    Checks service accounts for weak encryption types (RC4 vs AES)
    and non-expiring passwords that allow offline hash cracking.
    """
    vulnerable_accounts = []
    for account in spn_accounts:
        spn = account.get("servicePrincipalName")
        encryption_types = account.get("msDS-SupportedEncryptionTypes", 0)
        password_last_set = account.get("pwdLastSet")
        
        # Flag accounts that still support weak RC4-HMAC (type 4)
        supports_rc4 = (encryption_types & 0x4) != 0 or encryption_types == 0
        
        # Check password age
        if supports_rc4:
            vulnerable_accounts.append({
                "account_name": account.get("sAMAccountName"),
                "spn": spn,
                "risk": "HIGH: Vulnerable to Kerberoasting (RC4-HMAC supported)",
                "remediation": "Configure AES-256 encryption and enforce 25+ character passwords or Group Managed Service Accounts (gMSA)."
            })
            
    return vulnerable_accounts
```

### 2. BloodHound Graph Analysis: Identifying Shortest Attack Paths
Model AD objects as a directed graph to discover hidden transitive paths to Domain Admin:

```cypher
// BloodHound Cypher Query: Find shortest path from any Domain User to Domain Admins
MATCH (u:Group {name: "DOMAIN USERS@CORP.LOCAL"}), (da:Group {name: "DOMAIN ADMINS@CORP.LOCAL"})
MATCH p = shortestPath((u)-[*1..6]->(da))
RETURN p;
```

### 3. DCSync Replication Rights Audit
Verify which non-Domain Controller principals possess `DS-Replication-Get-Changes-All` rights:

```powershell
# PowerShell ActiveDirectory Module
Get-Acl "AD:\DC=corp,DC=local" | Select-Object -ExpandProperty Access | Where-Object {
    $_.ObjectType -eq "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2" -or # DS-Replication-Get-Changes
    $_.ObjectType -eq "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"     # DS-Replication-Get-Changes-All
} | Select-Object IdentityReference, ActiveDirectoryRights, AccessControlType
```

## Best Practices & Failure Modes

1. **Static Plaintext Service Account Passwords**: Traditional service accounts frequently have passwords set once that never expire. Always migrate service accounts to Group Managed Service Accounts (gMSA), where Windows rotates 128-character passwords automatically every 30 days.
2. **Unconstrained Kerberos Delegation**: Servers configured with unconstrained delegation store client TGTs in LSASS memory. If an attacker compromises an unconstrained server, they can impersonate any domain admin who connects to that server. Use Constrained Delegation or Resource-Based Constrained Delegation (RBCD).
3. **Allowing NTLM in Modern Networks**: NTLM lacks mutual authentication and is vulnerable to relay attacks. Enforce Kerberos-only authentication and disable NTLM via Group Policy.

## Verification & Testing

- Audit domain controller event logs for Event ID 4769 (Kerberos Ticket Request) with failure code `0x1f` or RC4 encryption (`0x17`):
  ```powershell
  Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4769} -MaxEvents 50 | 
      Where-Object { $_.Properties[4].Value -eq '0x17' }
  ```
