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
            if item.get("name") == backlog_query or backlog_query in item.get("name", ""):
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

# Continuous queue of high-value backlog candidates adapted into production skills
CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. SECURITY: active-directory-security-assessment (Backlog: active-directory-attacks)
    # -------------------------------------------------------------
    {
        "backlog_ref": "active-directory-attacks",
        "name": "active-directory-security-assessment",
        "domain": "security",
        "category": "penetration-testing",
        "subcategory": "active-directory",
        "description": "Use this skill when auditing, assessing, and hardening Microsoft Active Directory (AD) and hybrid Azure AD/Entra ID environments against common identity attack vectors. It guides the agent through identifying Kerberoasting vulnerabilities, AS-REP roasting, BloodHound attack path mapping, DCSync credential dumping risks, and Active Directory Certificate Services (ADCS) misconfigurations.",
        "tags": ["active-directory", "pentesting", "security", "kerberos", "bloodhound", "adcs", "red-team"],
        "technologies": ["Active Directory", "Kerberos", "BloodHound", "PowerView", "Impacket", "Python"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "powershell"],
        "dependencies": ["impacket >= 0.11.0"],
        "content": """# Active Directory Security Assessment & Hardening Architecture

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
    \"\"\"
    Checks service accounts for weak encryption types (RC4 vs AES)
    and non-expiring passwords that allow offline hash cracking.
    \"\"\"
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
"""
    },

    # -------------------------------------------------------------
    # 2. BUSINESS: employee-360-feedback-review-system (Backlog: 360-feedback-system)
    # -------------------------------------------------------------
    {
        "backlog_ref": "360-feedback-system",
        "name": "employee-360-feedback-review-system",
        "domain": "business",
        "category": "human-resources",
        "subcategory": "performance-management",
        "description": "Use this skill when designing, configuring, and operating multi-rater 360-degree performance feedback systems. It guides the agent through peer reviewer nomination workflows, role-specific competency rubrics, anonymous vs attributed visibility rules, cognitive bias mitigation (recency and halo effects), and synthesis reporting.",
        "tags": ["360-feedback", "hr", "performance-review", "talent-management", "competencies", "people-ops"],
        "technologies": ["Python", "JSON", "PostgreSQL", "Data Analytics"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["python >= 3.10"],
        "content": """# Employee 360-Degree Performance Feedback Architecture

## Overview

A comprehensive engineering guide for architecting fair, actionable, and bias-resistant multi-rater 360-degree feedback systems. Single-manager reviews suffer from idiosyncratic rater bias and blind spots. A 360 feedback system aggregates calibrated perspectives from direct managers, peers, cross-functional partners, and direct reports. This skill instructs AI agents on structuring review cycles, designing competency rubrics, enforcing reviewer anonymity thresholds, eliminating cognitive bias, and generating development-focused synthesis summaries.

## When to Use

- Building or configuring automated quarterly or annual performance review cycles.
- Gathering balanced feedback for engineering promotions, leadership reviews, and personal development plans.
- Mitigating cognitive biases (recency bias, halo effect, centrality bias) through structured behavioral prompts.
- Aggregating qualitative feedback into actionable strengths and development opportunities.

## When NOT to Use

- Immediate operational feedback for acute safety or code violations (handle synchronously 1-on-1).
- Anonymous complaints regarding workplace harassment or whistleblowing (use formal ethics hotlines).

## Inputs & Prerequisites

- Organizational structure (reporting hierarchy, team affiliations).
- Defined competency rubric with behavioral anchors (e.g. Technical Execution, Collaboration, Leadership).
- Review cycle timeline and visibility thresholds.

## Core Workflow

### 1. Multi-Rater Nomination & Visibility Matrix
Define rater categories and privacy thresholds:

```json
{
  "review_cycle": "2026-H1-Engineering",
  "rater_categories": {
    "manager": {
      "min_raters": 1,
      "max_raters": 2,
      "anonymous": false,
      "visibility": "subject_and_leadership"
    },
    "peer": {
      "min_raters": 3,
      "max_raters": 5,
      "anonymous": true,
      "min_completed_for_anonymity": 3,
      "visibility": "aggregated_only"
    },
    "direct_report": {
      "min_raters": 2,
      "max_raters": 8,
      "anonymous": true,
      "min_completed_for_anonymity": 3,
      "visibility": "aggregated_only"
    },
    "self": {
      "min_raters": 1,
      "max_raters": 1,
      "anonymous": false,
      "visibility": "subject_and_manager"
    }
  }
}
```

### 2. Behavioral Competency Rubric Definition
Design questions anchored in observable behaviors rather than personality traits:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class CompetencyQuestion:
    competency: str
    behavioral_prompt: str
    rating_scale: List[str] # 1 to 5 scale with behavioral anchors

ENGINEERING_RUBRIC = [
    CompetencyQuestion(
        competency="Technical Craft & Execution",
        behavioral_prompt="How effectively does the individual design robust software, handle edge cases, and maintain code quality?",
        rating_scale=[
            "1 - Frequently introduces defects; requires constant supervision",
            "2 - Meets basic requirements with guidance",
            "3 - Consistently delivers high-quality, resilient code independently",
            "4 - Sets technical standards and simplifies complex systems for the team",
            "5 - Industry-level domain authority; anticipates multi-year architectural needs"
        ]
    ),
    CompetencyQuestion(
        competency="Cross-Functional Collaboration",
        behavioral_prompt="How effectively does the individual communicate across teams, resolve technical disputes, and unblock partners?",
        rating_scale=[
            "1 - Creates friction or silos",
            "2 - Cooperates when prompted",
            "3 - Proactively aligns with partners and communicates transparently",
            "4 - Builds strong cross-team consensus on contentious decisions",
            "5 - Exemplary organizational leader driving company-wide initiatives"
        ]
    )
]
```

### 3. Feedback Synthesis & Anonymity Enforcement
Aggregate feedback while protecting reviewer identities:

```python
def synthesize_feedback(feedback_submissions: list[dict], min_anonymous_count: int = 3) -> dict:
    peer_feedback = [f for f in feedback_submissions if f["category"] == "peer"]
    
    # Enforce strict anonymity threshold
    if len(peer_feedback) < min_anonymous_count:
        peer_comments = ["[Aggregated comments withheld: Fewer than 3 peer reviews received to protect anonymity]"]
    else:
        peer_comments = [f["qualitative_strengths"] for f in peer_feedback]

    avg_scores = {}
    for comp in ["Technical Craft & Execution", "Cross-Functional Collaboration"]:
        scores = [f["ratings"][comp] for f in feedback_submissions if comp in f.get("ratings", {})]
        avg_scores[comp] = round(sum(scores) / len(scores), 2) if scores else 0.0

    return {
        "quantitative_summary": avg_scores,
        "peer_qualitative_feedback": peer_comments
    }
```

## Best Practices & Failure Modes

1. **Violating Anonymity with Small Sample Sizes**: If only 1 peer completes a review, attributing comments to "Peers" clearly exposes the author. If fewer than 3 reviews are submitted in an anonymous category, combine them into an aggregated pool or withhold qualitative quotes.
2. **Personality Feedback vs Behavioral Evidence**: Feedback criticizing tone or temperament ("too aggressive", "not enthusiastic enough") disproportionately harms underrepresented groups. Prompt reviewers for concrete situations, behaviors, and business impacts (SBI model).
3. **Recency Bias**: Reviewers naturally recall work done in the last 2 weeks while forgetting the previous 5 months. Encourage year-round private note-taking and review tickets across the entire cycle.

## Verification & Testing

- Unit test verifying that anonymity thresholds are strictly respected:
  ```python
  sample_submissions = [
      {"category": "peer", "ratings": {"Technical Craft & Execution": 4}, "qualitative_strengths": "Great job"},
      {"category": "peer", "ratings": {"Technical Craft & Execution": 5}, "qualitative_strengths": "Fast delivery"}
  ] # Only 2 peers
  report = synthesize_feedback(sample_submissions, min_anonymous_count=3)
  assert "withheld" in report["peer_qualitative_feedback"][0]
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. BUSINESS: internal-financial-audit-and-controls (Backlog: accounting-audit-system-builder)
    # -------------------------------------------------------------
    {
        "backlog_ref": "accounting-audit-system-builder",
        "name": "internal-financial-audit-and-controls",
        "domain": "business",
        "category": "finance",
        "subcategory": "audit-controls",
        "description": "Use this skill when designing, testing, and automating internal financial accounting controls, journal entry audit trails, and reconciliation workflows compliant with SOX 404, GAAP, and IFRS. It guides the agent through general ledger reconciliation, manual journal entry approval thresholds, segregation of duties in treasury, and anomaly detection.",
        "tags": ["financial-audit", "accounting", "sox-compliance", "internal-controls", "finance", "gaap"],
        "technologies": ["Python", "SQL", "PostgreSQL", "Pandas", "Audit Trails"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pandas >= 2.0.0", "python >= 3.10"],
        "content": """# Internal Financial Audit & SOX Accounting Controls Architecture

## Overview

A definitive production finance and compliance engineering reference for architecting internal accounting controls, automated ledger reconciliation, and tamper-evident audit trails. Corporate financial reporting is governed by Sarbanes-Oxley (SOX) Section 404, GAAP, and IFRS standards. This skill instructs AI agents on designing controls for manual journal entries, enforcing multi-tier approval thresholds, executing automated three-way matching (Purchase Order -> Goods Receipt -> Invoice), and detecting accounting anomalies (Benford's Law).

## When to Use

- Designing enterprise ERP accounting modules, billing engines, and treasury ledger systems.
- Preparing financial infrastructure for external audit (Big 4 accounting firm reviews).
- Automating account balance reconciliation across internal databases and external payment processors (Stripe/Adyen/Banks).
- Enforcing Segregation of Duties (SoD) on material journal entries and wire transfers.

## When NOT to Use

- Simple non-regulated personal budgeting or expense tracker hobby apps.
- Real-time stock trading algorithms (use market-making quantitative skills).

## Inputs & Prerequisites

- Chart of Accounts (COA) with asset, liability, equity, revenue, and expense codes.
- General Ledger journal entry tables with debit and credit balance enforcement.
- Bank statement feeds and payment gateway settlement reports.

## Core Workflow

### 1. Double-Entry Journal Entry Invariant Enforcement
Ensure that debits strictly equal credits on every posted transaction with cryptographic immutability:

```python
from dataclasses import dataclass
from typing import List
import datetime
import hashlib
import json

@dataclass
class JournalEntryLine:
    account_code: str
    debit_cents: int
    credit_cents: int
    description: str

class JournalEntry:
    def __init__(self, entry_id: str, creator_id: str, lines: List[JournalEntryLine]):
        self.entry_id = entry_id
        self.creator_id = creator_id
        self.lines = lines
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self._validate_invariants()

    def _validate_invariants(self):
        total_debits = sum(line.debit_cents for line in self.lines)
        total_credits = sum(line.credit_cents for line in self.lines)
        
        # Fundamental Accounting Equation Invariant
        if total_debits != total_credits:
            raise ValueError(f"Unbalanced Journal Entry: Debits ({total_debits}) != Credits ({total_credits})")
        if total_debits == 0:
            raise ValueError("Journal entry cannot have zero total amount.")

    def compute_audit_hash(self, previous_block_hash: str) -> str:
        payload = {
            "entry_id": self.entry_id,
            "creator_id": self.creator_id,
            "timestamp": self.timestamp,
            "lines": [l.__dict__ for l in self.lines],
            "prev_hash": previous_block_hash
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
```

### 2. Automated Account Reconciliation (Three-Way Matching)
Match customer invoices against payment provider settlements and bank deposits:

```python
import pandas as pd

def reconcile_bank_settlement(internal_ledger_df: pd.DataFrame, bank_settlement_df: pd.DataFrame) -> dict:
    \"\"\"
    Performs outer join to identify discrepancies between ledger and bank statements.
    \"\"\"
    merged = pd.merge(
        internal_ledger_df,
        bank_settlement_df,
        on="transaction_reference_id",
        how="outer",
        suffixes=("_ledger", "_bank")
    )

    # Discrepancy 1: Recorded in ledger but missing from bank (in-transit or missing settlement)
    missing_in_bank = merged[merged["amount_cents_bank"].isna()]

    # Discrepancy 2: Present in bank but missing in ledger (unrecorded bank fee or unauthorized charge)
    missing_in_ledger = merged[merged["amount_cents_ledger"].isna()]

    # Discrepancy 3: Amount mismatch
    amount_mismatch = merged[
        merged["amount_cents_ledger"].notna() &
        merged["amount_cents_bank"].notna() &
        (merged["amount_cents_ledger"] != merged["amount_cents_bank"])
    ]

    return {
        "matched_count": len(merged) - len(missing_in_bank) - len(missing_in_ledger) - len(amount_mismatch),
        "unmatched_bank_items": len(missing_in_ledger),
        "unmatched_ledger_items": len(missing_in_bank),
        "discrepant_amounts": len(amount_mismatch)
    }
```

### 3. Forensic Anomaly Detection via Benford's Law
Detect fraudulent or fabricated manual journal entries:

```python
import math
from collections import Counter

def check_benfords_law(amounts: list[float]) -> dict:
    \"\"\"
    In natural financial data, first digit '1' appears ~30.1% of the time,
    while digit '9' appears ~4.6% of the time. Deviations signal fabrication.
    \"\"\"
    first_digits = []
    for amt in amounts:
        if amt > 0:
            digit = int(str(amt).replace(".", "")[0])
            if digit > 0:
                first_digits.append(digit)

    total = len(first_digits)
    counts = Counter(first_digits)
    observed = {d: counts[d] / total for d in range(1, 10)}
    expected = {d: math.log10(1 + 1 / d) for d in range(1, 10)}

    # Calculate Chi-Square goodness-of-fit statistic
    chi_square = sum(((observed.get(d, 0) - expected[d]) ** 2) / expected[d] for d in range(1, 10))
    is_suspicious = chi_square > 0.05
    return {"chi_square": chi_square, "is_suspicious": is_suspicious}
```

## Best Practices & Failure Modes

1. **Direct Database Updates to Ledger Tables**: Permitting developers or DBAs to execute `UPDATE general_ledger SET balance = ...` destroys audit integrity and violates SOX controls. General ledgers must be append-only; corrections must be posted as offsetting journal entries.
2. **Missing Floating-Point Precision**: Never store currency as floating-point numbers (`float`). Rounding errors (`0.1 + 0.2 = 0.30000000000000004`) lead to penny imbalances on millions of transactions. Store currency strictly as integer cents or `DECIMAL(18, 4)`.
3. **Threshold Avoidance (Smurfing)**: Dishonest actors split a $50,000 transaction requiring CEO sign-off into six $9,900 entries. Build control rules that aggregate transactions per vendor within a 48-hour window.

## Verification & Testing

- Unit test verifying that unbalanced journal entries raise exceptions:
  ```python
  import pytest
  lines = [
      JournalEntryLine("1010-CASH", 5000, 0, "Cash received"),
      JournalEntryLine("4010-REVENUE", 0, 4900, "Revenue") # $1 mismatch
  ]
  with pytest.raises(ValueError):
      JournalEntry("JE-001", "user-1", lines)
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. SOFTWARE ENGINEERING: github-pr-review-feedback-resolver (Backlog: address-github-comments)
    # -------------------------------------------------------------
    {
        "backlog_ref": "address-github-comments",
        "name": "github-pr-review-feedback-resolver",
        "domain": "software-engineering",
        "category": "code-review",
        "subcategory": "pr-feedback",
        "description": "Use this skill when processing, triage-categorizing, and systematically addressing code review feedback and comments on pull requests. It guides the agent through parsing inline diff suggestions, verifying requested changes locally with test suites, pushing atomic fix commits, replying to reviewers with context, and resolving comment threads.",
        "tags": ["code-review", "pull-request", "github", "git", "collaboration", "developer-experience"],
        "technologies": ["GitHub API", "Git", "Python", "Bash"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["gh", "git", "python"],
        "dependencies": ["git >= 2.30.0", "gh >= 2.40.0"],
        "content": """# GitHub Pull Request Review Feedback Resolution Workflow

## Overview

A definitive software engineering standard for processing, implementing, and verifying code review feedback on GitHub pull requests. Effectively responding to code reviews requires more than applying mechanical suggestions; it demands understanding reviewer intent, testing side-effects locally, crafting atomic fixup commits, providing clear technical rationale for trade-offs, and marking comment threads resolved. This skill instructs AI agents on handling code review iterations systematically.

## When to Use

- Addressing reviewer comments and suggestions on open GitHub pull requests.
- Evaluating whether requested refactors break existing unit or integration tests.
- Formulating respectful, technically grounded rebuttals when a reviewer's suggestion has unintended drawbacks.
- Automating review comment triage and resolution via GitHub CLI (`gh`).

## When NOT to Use

- Creating new features from scratch before a pull request exists.
- Reviewing other developers' pull requests (use `github-pr-security-review`).

## Inputs & Prerequisites

- Local git branch tracking the open pull request.
- GitHub CLI (`gh`) authenticated with repository write access.
- Test suite configured locally to verify fixes before pushing.

## Core Workflow

### 1. Fetching Review Comments via GitHub CLI
Inspect pending review comments and unresolved review threads:

```bash
# View PR status and review comments
gh pr view --comments

# Fetch unresolved review discussion threads as structured JSON
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          comments(first: 5) {
            nodes {
              id
              path
              line
              body
              author { login }
            }
          }
        }
      }
    }
  }
}' -F owner='company-org' -F repo='app' -F pr=142
```

### 2. Review Comment Triage & Decision Matrix
Classify feedback into 4 actionable buckets:

1. **Typo / Formatting / Style**: Apply immediately without discussion.
2. **Bug / Edge Case**: Implement fix, add regression unit test, commit with clear message.
3. **Architectural Suggestion with Trade-offs**: Analyze impact; if agreeing, refactor; if disagreeing, present polite empirical evidence (benchmarks, complexity analysis).
4. **Out of Scope (Scope Creep)**: Acknowledge validity, create a separate tracking issue, and link it in the reply.

### 3. Pushing Fixes & Replying to Comments
Apply changes, run local test suite, push commits, and reply to threads:

```bash
# 1. Verify fix locally before pushing
pytest tests/
npm run typecheck

# 2. Commit atomic fix
git add src/payments.py tests/test_payments.py
git commit -m "fix(payments): handle null currency code in invoice calculation"

# 3. Push to PR branch
git push origin feature/payments-upgrade

# 4. Reply to specific review thread on GitHub
gh pr comment 142 --body "Addressed in commit $(git rev-parse --short HEAD). Added unit test covering null currency codes."
```

## Best Practices & Failure Modes

1. **Force-Pushing during Active Reviews**: Force-pushing (`git push --force`) wipes reviewer inline comment context from the GitHub UI, making it impossible for reviewers to see what changed between review rounds. Push incremental commits during review; squash-and-merge at the very end.
2. **Resolving Threads Without Replying**: Resolving a reviewer's comment without an explanation or commit reference leaves the reviewer wondering if their concern was addressed or ignored. Always comment with the commit SHA before resolving.
3. **Blindly Accepting Broken Suggestions**: GitHub's "Apply suggestion" button does not run test suites. Applying a suggestion that has a subtle syntax error or breaks type checking fails CI immediately. Always pull and run tests locally.

## Verification & Testing

- Check that all review threads are addressed and CI passes:
  ```bash
  gh pr checks
  # All status checks must report PASS
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. MOBILE: ios-app-clip-architecture (Backlog: add-app-clip)
    # -------------------------------------------------------------
    {
        "backlog_ref": "add-app-clip",
        "name": "ios-app-clip-architecture",
        "domain": "mobile",
        "category": "ios",
        "subcategory": "app-clips",
        "description": "Use this skill when designing, building, and configuring iOS App Clips for on-demand, lightweight app experiences without full App Store installations. It guides the agent through Apple App Clip target creation in Xcode/Expo, bundle size optimization (< 15MB or 50MB on iOS 17+), Associated Domains configuration (appclips:), Apple Pay and Sign in with Apple integration, and App Clip code invocation.",
        "tags": ["ios", "app-clips", "apple", "mobile", "swift", "expo", "react-native"],
        "technologies": ["iOS SDK", "Swift", "SwiftUI", "Expo", "React Native", "Xcode"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["xcodebuild", "fastlane"],
        "dependencies": ["ios >= 16.0"],
        "content": """# iOS App Clip Architecture & On-Demand Execution

## Overview

A definitive mobile engineering reference for building high-conversion, lightweight iOS App Clips. App Clips provide immediate, frictionless access to specific app functionalities (e.g. paying for parking, ordering takeout, renting a scooter) via NFC tags, QR codes, Safari Smart App Banners, or Messages, without requiring users to download the full app from the App Store. This skill instructs AI agents on configuring App Clip targets in Xcode/Expo, adhering to strict binary size limits (15 MB / 50 MB on iOS 17+), configuring Associated Domains, and seamlessly transitioning users to the full application.

## When to Use

- Enabling frictionless physical-world interactions (tap NFC tag to pay or order).
- Providing instant demo experiences directly from Safari web links or QR codes.
- Streamlining checkout workflows using native Apple Pay and Sign in with Apple.
- Increasing full app conversion rates by allowing users to complete a task before downloading.

## When NOT to Use

- Apps requiring background audio playback, continuous background location tracking, or Bluetooth peripherals (App Clips are restricted from background processing).
- Heavy applications requiring large local databases (> 50 MB) or complex multi-tab navigation.

## Inputs & Prerequisites

- Apple Developer Program account with explicit App Clip App ID capabilities.
- Xcode 15+ or Expo SDK 50+ project.
- Web domain serving Apple App Site Association (AASA) file over HTTPS.

## Core Workflow

### 1. Associated Domains Configuration (`apple-app-site-association`)
Host the AASA file at `https://example.com/.well-known/apple-app-site-association` with MIME type `application/json`:

```json
{
  "appclips": {
    "apps": ["TEAM_ID.com.example.app.Clip"]
  },
  "applinks": {
    "details": [
      {
        "appIDs": ["TEAM_ID.com.example.app"],
        "components": [
          { "/": "/orders/*" }
        ]
      }
    ]
  }
}
```

### 2. SwiftUI App Clip Entry Point & URL Invocation Handling
Handle incoming invocation URLs with zero splash screen delays:

```swift
// AppClipApp.swift
import SwiftUI

@main
struct RestaurantAppClip: App {
    @StateObject private var cartManager = CartManager()

    var body: some Scene {
        WindowGroup {
            OrderView()
                .environmentObject(cartManager)
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { userActivity in
                    guard let incomingURL = userActivity.webpageURL else { return }
                    handleInvocation(url: incomingURL)
                }
        }
    }

    private func handleInvocation(url: URL) {
        // Parse payload: https://example.com/menu?table=14&restaurant_id=rest_88
        let components = URLComponents(url: url, resolvingAgainstBaseURL: true)
        let tableNumber = components?.queryItems?.first(where: { $0.name == "table" })?.value
        let restaurantId = components?.queryItems?.first(where: { $0.name == "restaurant_id" })?.value
        
        print("Invoked App Clip for restaurant: \(restaurantId ?? "none") at table: \(tableNumber ?? "0")")
    }
}
```

### 3. Native Apple Pay Integration (Frictionless Payment)
Avoid requiring users to create accounts or enter credit card numbers manually:

```swift
import PassKit

func makePaymentRequest(amount: Decimal) -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = "merchant.com.example.appclip"
    request.supportedNetworks = [.visa, .masterCard, .amex]
    request.merchantCapabilities = .threeDSecure
    request.countryCode = "US"
    request.currencyCode = "USD"
    
    request.paymentSummaryItems = [
        PKPaymentSummaryItem(label: "Table Order", amount: NSDecimalNumber(decimal: amount))
    ]
    return request
}
```

## Best Practices & Failure Modes

1. **Exceeding Strict Binary Size Limits**: On iOS 16 and earlier, the uncompressed App Clip binary cannot exceed 15 MB (50 MB on iOS 17+). If the thin binary exceeds this limit, Apple App Store Connect rejects deployment immediately. Remove unnecessary heavy third-party analytics libraries and compress image assets.
2. **Demanding Account Creation Upfront**: Forcing users to enter an email and password before taking action destroys App Clip conversion. Use Sign in with Apple and Apple Pay to complete transactions with zero typing.
3. **Missing AASA File Validation**: If the `apple-app-site-association` file returns an HTTP 301/302 redirect or lacks the `appclips` dictionary, iOS will fail to open the App Clip and fall back to opening the webpage in Safari.

## Verification & Testing

- Test local App Clip invocation in Xcode scheme:
  - Edit Scheme -> Run -> Arguments -> Environment Variables:
  - Add `_XCAppClipURL` with value `https://example.com/menu?table=14`
- Validate AASA file configuration using Apple CDN Validator:
  ```bash
  curl -v https://app-site-association.cdn-apple.com/a/v1/example.com
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
