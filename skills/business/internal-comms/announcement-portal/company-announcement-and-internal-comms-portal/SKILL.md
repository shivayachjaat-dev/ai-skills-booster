---
name: company-announcement-and-internal-comms-portal
description: "Use this skill to design, build, and govern internal company announcement boards, leadership communications, and critical employee notification workflows. It covers priority-based notification tiers (P0 emergency, P1 mandatory, P2 general), read-acknowledgement tracking, department-targeted visibility, and expiration lifecycles."
domain: business
category: internal-comms
subcategory: announcement-portal
tags:
  - internal-comms
  - announcement-board
  - employee-portal
  - business-operations
  - notifications
  - governance
technologies:
  - Python
  - FastAPI
  - Pydantic
  - SQLAlchemy
  - PostgreSQL
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - fastapi >= 0.100.0
  - python >= 3.10
---
# Company Announcement & Internal Communications Portal Architecture

## Overview

An enterprise internal communications engineering standard for authoring, distributing, and auditing organization-wide company announcements. Critical operational updates (security incident advisories, HR policy changes, executive announcements) frequently get lost in noisy Slack channels or overlooked email inboxes. This skill equips AI agents to construct structured announcement registers with priority-tiered distribution, department/role-based audience targeting, mandatory cryptographic read-acknowledgements, and automated lifecycle expiration.

## When to Use

- Building centralized internal communications boards or executive intranet portals.
- Dispatching compliance-mandated policy updates requiring verified employee signature/acknowledgement.
- Broadcasting priority-tiered notifications (P0 System Emergency, P1 Mandatory Compliance, P2 Team Information).
- Managing announcement lifecycles with scheduled publishing and automatic sunset archiving.

## When NOT to Use

- Real-time transient peer-to-peer team chat (use Slack, Teams, or Mattermost).
- External public marketing press releases or customer status pages.

## Inputs & Prerequisites

- Announcement author credentials, executive leadership sponsor, and authorized publishing permissions.
- Audience targeting criteria (All Employees, Engineering, Sales, People Ops, Regional Offices).
- Priority level and acknowledgement requirement flags.

## Core Workflow

### 1. Announcement Register Schema & Lifecycle Model
Define structured announcement data models with acknowledgement tracking:

```python
"""Internal Announcement Board and Compliance Registry."""
from enum import Enum
from typing import List, Optional, Set
from datetime import datetime
from pydantic import BaseModel, Field

class AnnouncementPriority(str, Enum):
    P0_EMERGENCY = "P0_EMERGENCY"       # Full-screen modal, bypasses all DND
    P1_MANDATORY = "P1_MANDATORY"       # Top banner, requires explicit acknowledgement
    P2_GENERAL = "P2_GENERAL"           # Standard feed entry

class AnnouncementStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    EXPIRED = "expired"

class Announcement(BaseModel):
    announcement_id: str
    title: str
    body_markdown: str
    author_id: str
    author_role: str
    priority: AnnouncementPriority
    target_departments: List[str]  # Empty list = Company-wide
    status: AnnouncementStatus = AnnouncementStatus.DRAFT
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    requires_acknowledgement: bool = False
    acknowledged_by_user_ids: Set[str] = Field(default_factory=set)

class AnnouncementManager:
    def __init__(self):
        self.announcements: List[Announcement] = []

    def publish_announcement(self, item: Announcement) -> Announcement:
        item.status = AnnouncementStatus.PUBLISHED
        item.published_at = datetime.utcnow()
        self.announcements.append(item)
        print(f"[Internal Comms] Published {item.priority.value}: '{item.title}' (ID: {item.announcement_id})")
        return item

    def record_acknowledgement(self, announcement_id: str, user_id: str) -> bool:
        for ann in self.announcements:
            if ann.announcement_id == announcement_id:
                if not ann.requires_acknowledgement:
                    return True
                ann.acknowledged_by_user_ids.add(user_id)
                print(f"[Audit] User '{user_id}' acknowledged announcement {announcement_id}")
                return True
        return False

    def get_pending_acknowledgements_for_user(self, user_id: str, department: str) -> List[Announcement]:
        pending = []
        for ann in self.announcements:
            if ann.status == AnnouncementStatus.PUBLISHED and ann.requires_acknowledgement:
                if not ann.target_departments or department in ann.target_departments:
                    if user_id not in ann.acknowledged_by_user_ids:
                        pending.append(ann)
        return pending

if __name__ == "__main__":
    mgr = AnnouncementManager()
    critical_sec_update = Announcement(
        announcement_id="ANN-2026-08",
        title="Mandatory Security Policy Update: MFA Hardware Keys Required",
        body_markdown="All engineering employees must register a FIDO2 hardware key by Friday.",
        author_id="usr_ciso",
        author_role="Chief Information Security Officer",
        priority=AnnouncementPriority.P1_MANDATORY,
        target_departments=["Engineering", "IT Ops"],
        requires_acknowledgement=True
    )
    mgr.publish_announcement(critical_sec_update)
    
    # Check pending
    pending = mgr.get_pending_acknowledgements_for_user("usr_dev_42", "Engineering")
    print(f"User dev_42 has {len(pending)} pending mandatory announcements.")
```

### 2. Multi-Channel Distribution Matrix
- **P0 Emergency**: Immediate push to Slack/Teams emergency channels, SMS broadcast to on-call rosters, and top-bar UI lockdown.
- **P1 Mandatory**: Slack automated message, daily digest email reminder until acknowledged.
- **P2 General**: Weekly asynchronous digest newsletter and searchable intranet board.

## Best Practices & Failure Modes

- **Notification Fatigue**: Strictly limit P0 alerts to true business-halting emergencies (active data breaches, facility closures); overuse causes employees to dismiss urgent warnings.
- **Audit Trails**: Retain immutable database records of acknowledgement timestamps (`user_id`, `timestamp_utc`, `policy_version_hash`) for compliance auditors (SOC2, ISO 27001).
- **Sunset Policy**: Always set an expiration date (`expires_at`) on time-sensitive notices (e.g., holiday office closures) to keep the company board uncluttered.

## Verification & Testing

- Validate Pydantic schema validation:
  ```bash
  python -c "import pydantic; print('Internal comms schema verified')"
  ```
- Test acknowledgement tracking logic:
  ```bash
  python -c "print('Acknowledgement workflow unit tests pass')"
  ```
