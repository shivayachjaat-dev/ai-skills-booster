---
name: identity-access-review-and-certification
description: "Use this skill when designing, automating, and conducting periodic Identity Access Reviews, user entitlement certifications, and least-privilege compliance audits. It covers generating access certification campaigns, flagging dormant accounts, detecting toxic permission combinations (Segregation of Duties - SoD), and producing audit evidence for SOC2/ISO27001."
domain: security
category: identity-governance
subcategory: access-review
tags:
  - identity-governance
  - access-review
  - compliance
  - soc2
  - iam
  - least-privilege
technologies:
  - Python
  - SQLAlchemy
  - PostgreSQL
  - JSON
  - Audit Logging
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Identity Access Review & User Entitlement Certification Architecture

## Overview

A comprehensive engineering guide for establishing automated periodic Access Reviews and User Entitlement Certifications. Regulatory compliance standards (SOC 2 Type II, ISO 27001, HIPAA, SOX) mandate quarterly or bi-annual reviews of all user and service account access to production systems. This skill instructs AI agents on automating review campaigns, identifying dormant accounts, detecting Segregation of Duties (SoD) conflicts, executing approval/revocation workflows, and preserving tamper-evident audit evidence.

## When to Use

- Conducting quarterly access certification campaigns for employee and contractor permissions.
- Identifying and revoking orphaned accounts belonging to offboarded personnel.
- Detecting Segregation of Duties violations (e.g. a single user having both Code Author and Production Deployer privileges).
- Generating auditor-ready access certification evidence reports for SOC2/SOX compliance.

## When NOT to Use

- Real-time per-request API authorization checks (use `rbac-access-matrix-policy-design`).
- Single-factor password credential resets.

## Inputs & Prerequisites

- Identity catalog of active employees, contractors, and service accounts.
- System entitlement mapping (which users have which roles in which applications).
- Account activity and login telemetry (last active timestamps).

## Core Workflow

### 1. Segregation of Duties (SoD) Conflict Detection
Define toxic combinations of permissions that represent fraud or compliance risks:

```python
from dataclasses import dataclass
from typing import List, Set

@dataclass
class ToxicCombination:
    name: str
    conflicting_permissions: Set[str]
    description: str

SOD_POLICIES = [
    ToxicCombination(
        name="Invoice Creation & Payment Approval",
        conflicting_permissions={"invoices:create", "payments:approve"},
        description="A single user cannot both create an invoice and approve payment for it."
    ),
    ToxicCombination(
        name="Code Commit & Production Release",
        conflicting_permissions={"code:commit", "production:deploy"},
        description="Developers committing code cannot unilaterally approve production deployments without peer review."
    )
]

def detect_sod_violations(user_id: str, user_permissions: Set[str]) -> List[str]:
    violations = []
    for policy in SOD_POLICIES:
        if policy.conflicting_permissions.issubset(user_permissions):
            violations.append(f"SoD Conflict: {policy.name} ({policy.description})")
    return violations
```

### 2. Automated Dormant Account Detection
Identify accounts that have had zero activity for 90+ days:

```python
import datetime

def find_dormant_accounts(account_records: list[dict], threshold_days: int = 90) -> list[dict]:
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=threshold_days)
    dormant = []

    for acc in account_records:
        last_active = acc.get("last_login_at")
        if last_active is None or last_active < cutoff_date:
            dormant.append({
                "account_id": acc["id"],
                "email": acc["email"],
                "last_active": last_active,
                "days_inactive": (datetime.datetime.utcnow() - last_active).days if last_active else "Never"
            })
    return dormant
```

### 3. Access Certification Campaign Lifecycle
Generate review items for managers and record cryptographic audit logs:

```python
import hashlib
import json

class AccessReviewCampaign:
    def __init__(self, campaign_id: str, quarter: str):
        self.campaign_id = campaign_id
        self.quarter = quarter
        self.certifications = []

    def record_decision(self, reviewer_id: str, subject_user_id: str, role_id: str, decision: str, reason: str):
        assert decision in ("APPROVE", "REVOKE")
        record = {
            "campaign_id": self.campaign_id,
            "quarter": self.quarter,
            "reviewer_id": reviewer_id,
            "subject_user_id": subject_user_id,
            "role_id": role_id,
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        # Compute SHA256 integrity hash
        record_hash = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        record["integrity_hash"] = record_hash
        self.certifications.append(record)
        return record
```

## Best Practices & Failure Modes

1. **Rubber-Stamping Approvals**: Managers frequently click "Approve All" without reviewing permissions. Combat this by highlighting high-risk roles (Production Admin, Financial Signer) in distinct review tiers requiring explicit justification.
2. **Missing Automated Deprovisioning**: If a reviewer selects "REVOKE" during an access review, but revocation is not tied to automated IAM APIs (Okta, AWS IAM, GitHub), revoked access remains active. Ensure the review campaign emits deprovisioning webhooks.
3. **Omitting Service Accounts**: Access reviews often focus exclusively on human employees, completely ignoring machine service accounts with permanent root tokens. Service accounts must be included in quarterly certification campaigns.

## Verification & Testing

- Test SoD conflict detector on conflicting permission set:
  ```python
  bad_permissions = {"invoices:create", "payments:approve", "reports:read"}
  violations = detect_sod_violations("user_123", bad_permissions)
  assert len(violations) == 1
  assert "Invoice Creation & Payment Approval" in violations[0]
  ```
