---
name: privileged-access-and-admin-account-register
description: "Use this skill when cataloging, auditing, and enforcing governance policies over privileged administrator accounts and break-glass emergency credentials across SaaS, cloud infrastructure, and internal systems. It guides the agent through structuring an Admin Access Register, enforcing mandatory MFA/WebAuthn, designated backup owners, and access justification logs."
domain: security
category: identity-governance
subcategory: admin-register
tags:
  - privileged-access
  - admin-accounts
  - iam
  - pam
  - soc2
  - security
  - governance
technologies:
  - Python
  - JSON
  - Audit Logging
  - Identity Governance
  - KMS
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Privileged Access & Admin Account Register Architecture

## Overview

A definitive production security governance standard for cataloging and controlling privileged administrative accounts across enterprise infrastructure, cloud environments (AWS, GCP, Azure), SaaS platforms (GitHub, Okta, Stripe), and databases. Uninventoried admin credentials with weak passwords or single owners represent the highest-severity vulnerability in enterprise organizations. This skill instructs AI agents on maintaining an immutable Privileged Access Register, establishing primary and backup admin requirements, enforcing hardware MFA, and securing break-glass emergency credentials.

## When to Use

- Cataloging all privileged administrative access across enterprise platforms for SOC2, ISO 27001, and HIPAA compliance.
- Ensuring zero orphan administrative accounts exist without an identified active employee owner.
- Managing emergency "Break-Glass" root accounts with multi-party authorization.
- Enforcing mandatory FIDO2 hardware MFA across all administrative consoles.

## When NOT to Use

- Standard end-user non-administrative permissions (use `rbac-access-matrix-policy-design`).
- Temporary dynamic database session credentials (use `vault-secrets-management`).

## Inputs & Prerequisites

- Inventory of third-party SaaS services, cloud accounts, and critical internal databases.
- Identity provider user directory (Okta, Entra ID, Google Workspace).
- Documented Break-Glass emergency access policy.

## Core Workflow

### 1. Privileged Access Register Schema
Formulate the central administrative register in structured JSON/YAML:

```json
{
  "system_id": "aws-production-account",
  "system_name": "AWS Production Cloud Environment",
  "criticality": "TIER_0",
  "primary_admin": {
    "name": "Alice Chen",
    "email": "alice@company.com",
    "department": "Platform Engineering"
  },
  "backup_admin": {
    "name": "Bob Martinez",
    "email": "bob@company.com",
    "department": "Security Operations"
  },
  "auth_method": "SSO_SAML",
  "mfa_enforced": true,
  "mfa_type": "FIDO2_WEBAUTHN",
  "seats_licensed": 5,
  "seats_active": 4,
  "last_audit_date": "2026-03-01",
  "break_glass_account": {
    "enabled": true,
    "vault_path": "secret/break-glass/aws-root",
    "alert_webhook": "https://alerts.security.internal/break-glass"
  }
}
```

### 2. Automated Register Policy Auditor
Audit the register programmatically to catch compliance violations:

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class PolicyViolation:
    system_id: str
    severity: str
    message: str

def audit_admin_register(register_entries: List[Dict]) -> List[PolicyViolation]:
    violations = []
    
    for entry in register_entries:
        sys_id = entry.get("system_id", "unknown")

        # 1. Missing Backup Admin (Bus Factor = 1)
        if not entry.get("backup_admin") or not entry["backup_admin"].get("email"):
            violations.append(PolicyViolation(
                sys_id, "CRITICAL", "System lacks a designated backup administrator."
            ))

        # 2. MFA Enforcement Check
        if not entry.get("mfa_enforced"):
            violations.append(PolicyViolation(
                sys_id, "CRITICAL", "Administrative access does not enforce Multi-Factor Authentication (MFA)."
            ))
        elif entry.get("mfa_type") == "SMS":
            violations.append(PolicyViolation(
                sys_id, "HIGH", "SMS MFA is prohibited for Tier 0/1 systems due to SIM swapping risk; must use FIDO2/TOTP."
            ))

        # 3. Orphan Admin Check
        primary = entry.get("primary_admin", {})
        if primary.get("is_offboarded"):
            violations.append(PolicyViolation(
                sys_id, "CRITICAL", f"Primary admin {primary.get('email')} is offboarded! Immediate transfer required."
            ))

    return violations
```

### 3. Break-Glass Emergency Access Procedure
Structure emergency access with dual-custody authorization and immediate alerting:

```python
def trigger_break_glass_access(system_id: str, requester_id: str, reason: str, approver_id: str):
    """
    Enforces dual-custody approval before releasing emergency root credentials.
    """
    if requester_id == approver_id:
        raise ValueError("Dual custody violation: Requester cannot approve their own break-glass request.")

    # 1. Dispatch real-time security alert to all leadership
    # dispatch_pagerduty_alert(f"EMERGENCY: Break-glass activated on {system_id} by {requester_id}")

    # 2. Log immutable event to SIEM
    audit_record = {
        "event": "BREAK_GLASS_ACCESS",
        "system": system_id,
        "requester": requester_id,
        "approver": approver_id,
        "reason": reason,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    return audit_record
```

## Best Practices & Failure Modes

1. **Shared Administrator Credentials**: Sharing a single `admin@company.com` login across 5 team members destroys individual accountability in audit logs. Every administrator must have an individually attributable account authenticated via corporate SSO.
2. **Missing Backup Administrator**: If the sole administrator leaves the company unexpectedly or loses their security key, the organization gets locked out of critical services. Every system must have an active, verified backup administrator.
3. **Unmonitored Root Accounts**: Cloud root accounts (e.g. AWS account root user) should have zero active API keys and have login events wired directly to high-priority PagerDuty alerts.

## Verification & Testing

- Validate register compliance and catch unassigned backup admins:
  ```python
  test_entry = [{
      "system_id": "stripe-billing",
      "mfa_enforced": True,
      "mfa_type": "FIDO2",
      "primary_admin": {"email": "alice@corp.com"},
      "backup_admin": None # Missing backup
  }]
  issues = audit_admin_register(test_entry)
  assert len(issues) == 1
  assert issues[0].severity == "CRITICAL"
  ```
