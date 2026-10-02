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

CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. BUSINESS: enterprise-software-selection-and-rfp (Backlog: accounting-software-selection)
    # -------------------------------------------------------------
    {
        "backlog_ref": "accounting-software-selection",
        "name": "enterprise-software-selection-and-rfp",
        "domain": "business",
        "category": "procurement",
        "subcategory": "software-selection",
        "description": "Use this skill when evaluating, scoring, and selecting commercial-off-the-shelf (COTS) and SaaS software solutions through evidence-backed scoring matrices and Request for Proposal (RFP) processes. It covers requirements weighting, compliance auditing (SOC2, HIPAA, GDPR), Total Cost of Ownership (TCO) modeling, security reviews, and vendor pilot proof-of-concepts.",
        "tags": ["software-selection", "procurement", "rfp", "vendor-evaluation", "tco", "business"],
        "technologies": ["Python", "Pandas", "Scoring Matrices", "Financial Modeling"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pandas >= 2.0.0", "python >= 3.10"],
        "content": """# Enterprise Software Selection & RFP Evaluation Architecture

## Overview

A definitive enterprise procurement engineering standard for objectively scoring, shortlisting, and selecting commercial software systems. Selecting enterprise software (ERPs, CRM, CI/CD tooling, cloud observability) based on vendor marketing leads to expensive failed migrations and contract lock-in. This skill instructs AI agents on authoring functional and non-functional requirements matrices, modeling 3-year Total Cost of Ownership (TCO), executing weighted multi-attribute decision scoring, and evaluating vendor security posture.

## When to Use

- Selecting replacement ERP, accounting, HRIS, or database software for enterprise organizations.
- Authoring structured Requests for Proposal (RFPs) and vendor questionnaire scorecards.
- Calculating 3-year Total Cost of Ownership (licensing, implementation, maintenance, training, integration).
- Comparing shortlisted vendors using weighted multi-criteria decision analysis (MCDA).

## When NOT to Use

- Choosing lightweight open-source software libraries for a developer script.
- Single-vendor contract renewals where no market evaluation is being conducted.

## Inputs & Prerequisites

- Stakeholder requirements categorized by priority (Must-Have, Should-Have, Nice-to-Have).
- Compliance and security baseline requirements (SOC2 Type II, ISO 27001, data residency).
- Budget ceiling and projected 3-year user growth.

## Core Workflow

### 1. Weighted Evaluation Matrix Engine
Score competing vendors across weighted functional and compliance criteria:

```python
import pandas as pd

CRITERIA_WEIGHTS = {
    "core_functional_fit": 0.35,       # Must satisfy accounting/business requirements
    "api_and_extensibility": 0.20,     # Webhooks, REST/GraphQL APIs, SDK support
    "security_and_compliance": 0.20,   # SOC2, SSO/SAML, encryption at rest, RBAC
    "total_cost_of_ownership": 0.15,   # License + implementation + support over 3 years
    "vendor_viability_and_sla": 0.10   # 99.9% uptime SLA, financial stability, roadmap
}

def evaluate_vendor_score(vendor_name: str, raw_scores: dict[str, float]) -> dict:
    \"\"\"
    raw_scores contains ratings from 1 (poor) to 10 (exceptional) for each criteria key.
    \"\"\"
    weighted_total = sum(raw_scores[k] * CRITERIA_WEIGHTS[k] for k in CRITERIA_WEIGHTS)
    return {
        "vendor": vendor_name,
        "weighted_score": round(weighted_total, 2),
        "breakdown": {k: round(raw_scores[k] * CRITERIA_WEIGHTS[k], 2) for k in CRITERIA_WEIGHTS}
    }
```

### 2. 3-Year Total Cost of Ownership (TCO) Model
Calculate comprehensive true costs beyond base subscription price:

```python
def calculate_3yr_tco(
    annual_subscription: float,
    implementation_fee: float,
    seats: int,
    training_days: int,
    internal_engineering_hours_integration: int
) -> dict:
    # Industry averages: $150/hr internal engineering, $1500/day specialized training
    internal_eng_cost = internal_engineering_hours_integration * 150.0
    training_cost = training_days * 1500.0
    year1_cost = annual_subscription + implementation_fee + internal_eng_cost + training_cost
    year2_cost = annual_subscription * 1.05 # Account for typical 5% annual contract escalation
    year3_cost = year2_cost * 1.05

    total_3yr = year1_cost + year2_cost + year3_cost
    return {
        "year_1_cost": round(year1_cost, 2),
        "year_2_cost": round(year2_cost, 2),
        "year_3_cost": round(year3_cost, 2),
        "total_3yr_tco": round(total_3yr, 2),
        "cost_per_seat_per_month": round(total_3yr / (seats * 36), 2)
    }
```

## Best Practices & Failure Modes

1. **Unweighted Feature Checklists**: Counting raw checkmarks on a vendor sales sheet treats "Supports Single Sign-On" as equal in importance to "Supports dark mode theme". Always assign explicit mathematical weights to requirements.
2. **Hidden Egress & API Overages**: Cloud software contracts frequently include hidden costs for API call quotas, storage overages, or export fees. Demand explicit API rate limits and data extraction commitments in RFP documents.
3. **Skipping Sandboxed Proof-of-Concept (POC)**: Never sign a multi-year enterprise contract based on slide decks. Always execute a 2-week hands-on technical pilot verifying API throughput and authentication integration with real test data.

## Verification & Testing

- Unit test verifying score calculations and weights sum to 1.0:
  ```python
  assert round(sum(CRITERIA_WEIGHTS.values()), 2) == 1.0
  vendor_res = evaluate_vendor_score("AcmeERP", {
      "core_functional_fit": 8,
      "api_and_extensibility": 9,
      "security_and_compliance": 10,
      "total_cost_of_ownership": 7,
      "vendor_viability_and_sla": 8
  })
  assert vendor_res["weighted_score"] == 8.45
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. MARKETING: cross-channel-ad-campaign-analytics (Backlog: ad-campaign-analyzer)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ad-campaign-analyzer",
        "name": "cross-channel-ad-campaign-analytics",
        "domain": "marketing",
        "category": "paid-advertising",
        "subcategory": "campaign-analytics",
        "description": "Use this skill when analyzing, attributing, and optimizing multi-channel paid advertising campaigns across Google Ads, Meta Ads, LinkedIn, and programmatic channels. It guides the agent through calculating Customer Acquisition Cost (CAC), Return on Ad Spend (ROAS), attribution modeling (First-Touch, Last-Touch, Data-Driven Markov), statistical significance in spend allocation, and budget rebalancing.",
        "tags": ["ad-analytics", "roas", "cac", "attribution-modeling", "paid-advertising", "marketing", "analytics"],
        "technologies": ["Python", "Pandas", "NumPy", "SQL", "Markov Chains"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pandas >= 2.0.0", "numpy >= 1.24.0"],
        "content": """# Cross-Channel Paid Advertising Analytics & Attribution Architecture

## Overview

A definitive data and marketing engineering reference for ingesting, attributing, and optimizing paid advertising campaigns across heterogeneous ad networks (Google Ads, Meta, LinkedIn, TikTok). Relying on siloed platform metrics (where each network takes 100% credit for conversions) creates distorted ROAS calculations. This skill instructs AI agents on unified data normalization, multi-touch attribution modeling (First-Touch, Last-Touch, Linear, Markov Chain algorithmic attribution), and automated budget reallocation.

## When to Use

- Aggregating marketing performance across fragmented advertising APIs.
- Determining true Customer Acquisition Cost (CAC) and blended Return on Ad Spend (ROAS).
- Resolving attribution conflicts when a customer touches multiple ad campaigns before converting.
- Identifying budget waste and rebalancing spend toward high-marginal-efficiency channels.

## When NOT to Use

- Creative visual design of display banners (use generative UI/image tools).
- Organic search SEO optimization.

## Inputs & Prerequisites

- Ad campaign spend tables (Cost, Impressions, Clicks) by channel, campaign, and date.
- User conversion events with UTM parameter journey touchpoints (`utm_source`, `utm_campaign`).
- Python 3.10+ with `pandas` and `numpy`.

## Core Workflow

### 1. Cross-Channel Metrics Normalization
Ingest and normalize disparate campaign metrics:

```python
import pandas as pd
import numpy as np

def compute_channel_efficiency(campaign_df: pd.DataFrame) -> pd.DataFrame:
    \"\"\"
    campaign_df columns: ['channel', 'spend', 'impressions', 'clicks', 'conversions', 'revenue']
    \"\"\"
    df = campaign_df.groupby('channel').sum().reset_index()

    # Core Unit Economics
    df['cpc'] = df['spend'] / df['clicks'].replace(0, np.nan)
    df['ctr_percent'] = (df['clicks'] / df['impressions']) * 100
    df['cac'] = df['spend'] / df['conversions'].replace(0, np.nan)
    df['roas'] = df['revenue'] / df['spend'].replace(0, np.nan)

    return df.sort_values(by='roas', ascending=False)
```

### 2. Multi-Touch Attribution: First-Touch vs Last-Touch vs Linear
Attribute revenue across customer touchpoint journeys:

```python
def attribute_journey_revenue(journeys: list[dict], model: str = "linear") -> dict[str, float]:
    \"\"\"
    journeys format:
    [
        {"user_id": "u1", "touchpoints": ["google", "facebook", "retargeting"], "revenue": 150.0}
    ]
    \"\"\"
    channel_revenue = {}

    for j in journeys:
        touchpoints = j["touchpoints"]
        rev = j["revenue"]
        if not touchpoints or rev <= 0:
            continue

        if model == "last_touch":
            last_ch = touchpoints[-1]
            channel_revenue[last_ch] = channel_revenue.get(last_ch, 0.0) + rev
        elif model == "first_touch":
            first_ch = touchpoints[0]
            channel_revenue[first_ch] = channel_revenue.get(first_ch, 0.0) + rev
        elif model == "linear":
            weight = rev / len(touchpoints)
            for ch in touchpoints:
                channel_revenue[ch] = channel_revenue.get(ch, 0.0) + weight

    return {k: round(v, 2) for k, v in channel_revenue.items()}
```

### 3. Automated Budget Rebalancing Heuristic
Reallocate budget from underperforming channels (ROAS < threshold) to high-performing channels:

```python
def rebalance_ad_budget(efficiency_df: pd.DataFrame, target_min_roas: float = 2.5) -> dict:
    total_spend = efficiency_df['spend'].sum()
    eligible_channels = efficiency_df[efficiency_df['roas'] >= target_min_roas]
    
    if eligible_channels.empty:
        return {"action": "HOLD", "recommendation": "All channels below target ROAS. Refactor creative."}

    # Weight allocation by relative ROAS performance
    roas_sum = eligible_channels['roas'].sum()
    new_allocations = {}
    for _, row in eligible_channels.iterrows():
        allocated = total_spend * (row['roas'] / roas_sum)
        new_allocations[row['channel']] = round(allocated, 2)

    return {
        "action": "REBALANCE",
        "recommended_allocations": new_allocations
    }
```

## Best Practices & Failure Modes

1. **Relying Solely on Platform Reported Conversions**: Ad networks report conversions using 7-day click / 1-day view attribution windows, claiming duplicate credit for the same sale. Always compute blended CAC and independent multi-touch attribution.
2. **Ignoring Ad Fatigue**: Running high spend on a small audience causes frequency to climb (> 5 impressions/user), resulting in sharp drops in CTR and skyrocketing CPCs. Set automated frequency caps.
3. **Data Loss from Cookie Blocking**: Safari ITP and browser ad blockers strip tracking cookies. Implement server-side Conversions API (Meta CAPI, Google Tag Manager Server-side) to preserve tracking fidelity.

## Verification & Testing

- Unit test verifying linear attribution sums exactly to total conversion revenue:
  ```python
  test_journeys = [
      {"user_id": "1", "touchpoints": ["search", "social"], "revenue": 100.0},
      {"user_id": "2", "touchpoints": ["social"], "revenue": 50.0}
  ]
  attributed = attribute_journey_revenue(test_journeys, model="linear")
  assert sum(attributed.values()) == 150.0
  assert attributed["search"] == 50.0
  assert attributed["social"] == 100.0
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. SECURITY: privileged-access-and-admin-account-register (Backlog: admin-access-register)
    # -------------------------------------------------------------
    {
        "backlog_ref": "admin-access-register",
        "name": "privileged-access-and-admin-account-register",
        "domain": "security",
        "category": "identity-governance",
        "subcategory": "admin-register",
        "description": "Use this skill when cataloging, auditing, and enforcing governance policies over privileged administrator accounts and break-glass emergency credentials across SaaS, cloud infrastructure, and internal systems. It guides the agent through structuring an Admin Access Register, enforcing mandatory MFA/WebAuthn, designated backup owners, and access justification logs.",
        "tags": ["privileged-access", "admin-accounts", "iam", "pam", "soc2", "security", "governance"],
        "technologies": ["Python", "JSON", "Audit Logging", "Identity Governance", "KMS"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["python >= 3.10"],
        "content": """# Privileged Access & Admin Account Register Architecture

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
    \"\"\"
    Enforces dual-custody approval before releasing emergency root credentials.
    \"\"\"
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
"""
    },

    # -------------------------------------------------------------
    # 4. AI ENGINEERING: ai-agent-chaos-testing-and-fault-injection (Backlog: agent-harness-fault-injection)
    # -------------------------------------------------------------
    {
        "backlog_ref": "agent-harness-fault-injection",
        "name": "ai-agent-chaos-testing-and-fault-injection",
        "domain": "ai-engineering",
        "category": "agents",
        "subcategory": "fault-injection",
        "description": "Use this skill when stress-testing, chaos-testing, and verifying the fault-tolerance of autonomous AI agents and tool-calling pipelines. It guides the agent through simulating tool API failures, network timeouts, corrupt JSON payloads, context window truncation, and verifying agent self-healing and recovery strategies.",
        "tags": ["chaos-engineering", "fault-injection", "ai-agents", "resilience", "testing", "llm-agents"],
        "technologies": ["Python", "pytest", "LangChain", "AutoGen", "Asyncio"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "pytest"],
        "dependencies": ["python >= 3.10", "pytest >= 7.4.0"],
        "content": """# AI Agent Chaos Testing & Fault Injection Architecture

## Overview

A definitive production AI engineering standard for verifying the resilience, self-healing, and error recovery of autonomous LLM agents. In production, AI agents interact with unpredictable external environments: third-party APIs return HTTP 503 errors, webhooks timeout, tool outputs contain corrupted JSON, and context windows reach capacity. Without deliberate fault-injection testing, agents enter unrecoverable loops, hallucinate fake tool outputs, or crash unhandled. This skill instructs AI agents on injecting realistic faults into tool execution harnesses and asserting proper recovery behavior.

## When to Use

- Verifying that an autonomous agent can recover when a tool call raises an unhandled exception.
- Testing agent behavior when an external database or API returns HTTP 429 Too Many Requests.
- Stress-testing prompt self-correction when a tool returns malformed or incomplete data.
- Guaranteeing that agents terminate gracefully rather than looping infinitely on stubborn errors.

## When NOT to Use

- Standard unit testing of isolated deterministic helper functions.
- Production load testing of server network bandwidth.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Agent harness decoupling tool execution through an interceptable proxy.
- Test suite configured with `pytest`.

## Core Workflow

### 1. Chaos Tool Interceptor Proxy
Intercept tool execution calls and inject probabilistic or deterministic faults:

```python
import random
from typing import Callable, Any, Dict

class FaultInjectionPolicy:
    def __init__(self, failure_rate: float = 0.0, latency_seconds: float = 0.0, inject_corrupt_json: bool = False):
        self.failure_rate = failure_rate
        self.latency_seconds = latency_seconds
        self.inject_corrupt_json = inject_corrupt_json

class ChaosToolHarness:
    def __init__(self):
        self.policies: Dict[str, FaultInjectionPolicy] = {}
        self.invocation_log = []

    def set_fault_policy(self, tool_name: str, policy: FaultInjectionPolicy):
        self.policies[tool_name] = policy

    def execute_tool(self, tool_name: str, tool_func: Callable, *args, **kwargs) -> Any:
        self.invocation_log.append(tool_name)
        policy = self.policies.get(tool_name)

        if policy:
            # Simulate Network Latency / Timeout
            if policy.latency_seconds > 0:
                import time
                time.sleep(policy.latency_seconds)

            # Simulate Transient Service Outage
            if policy.failure_rate > 0 and random.random() < policy.failure_rate:
                raise ConnectionError(f"CHAOS INJECTED: Simulated network partition calling {tool_name}")

            # Simulate Malformed / Corrupted Data Output
            if policy.inject_corrupt_json:
                return '{"status": "error", "corrupted_payload": true' # Unterminated JSON

        return tool_func(*args, **kwargs)
```

### 2. Asserting Agent Self-Healing in Pytest
Assert that the agent receives the error, acknowledges it, and switches to an alternate tool:

```python
import pytest

class MockAgent:
    def __init__(self, harness: ChaosToolHarness):
        self.harness = harness

    def fetch_data_resilient(self, primary_url: str, backup_url: str):
        try:
            return self.harness.execute_tool("primary_fetch", lambda: "primary_data")
        except ConnectionError:
            # Agent self-heals by falling back to secondary backup tool
            return self.harness.execute_tool("backup_fetch", lambda: "backup_data")

def test_agent_fallback_on_chaos_failure():
    harness = ChaosToolHarness()
    # Force 100% failure on primary tool
    harness.set_fault_policy("primary_fetch", FaultInjectionPolicy(failure_rate=1.0))

    agent = MockAgent(harness)
    result = agent.fetch_data_resilient("http://primary", "http://backup")

    assert result == "backup_data"
    assert harness.invocation_log == ["primary_fetch", "backup_fetch"]
```

## Best Practices & Failure Modes

1. **Infinite Retry Hallucination Loops**: When a tool repeatedly fails, poorly instructed agents repeat the identical failed tool call with identical arguments 20 times. Always enforce a hard loop counter (`max_retries = 3`) and instruct agents to formulate alternative strategies or ask the human user.
2. **Leaking Internal Stack Traces into Prompt**: Feeding raw 50-line Python stack traces into the agent's context window wastes valuable context tokens and confuses the model. Catch exceptions and summarize into clean error messages (`Tool 'search' failed: Connection timeout`).
3. **Silent Swallowing of Errors**: If a tool returns an empty dictionary `{}` on failure without error signaling, the agent assumes the operation succeeded and produces false hallucinated conclusions. Tools must return explicit error schemas.

## Verification & Testing

- Run the chaos test suite with pytest:
  ```bash
  pytest tests/test_agent_chaos.py -v
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. AI ENGINEERING: multi-agent-tmux-process-orchestrator (Backlog: agent-manager-skill)
    # -------------------------------------------------------------
    {
        "backlog_ref": "agent-manager-skill",
        "name": "multi-agent-tmux-process-orchestrator",
        "domain": "ai-engineering",
        "category": "agents",
        "subcategory": "process-management",
        "description": "Use this skill when managing, supervising, and coordinating multiple autonomous CLI coding agents and subprocesses across detached terminal sessions using tmux. It covers automated tmux session and pane lifecycle management, sending keystrokes and instructions (send-keys), monitoring stdout/stderr activity buffers, and auto-restarting stalled agent workers.",
        "tags": ["tmux", "agent-orchestration", "multi-agent", "cli", "process-management", "automation"],
        "technologies": ["tmux", "Bash", "Python subprocess", "Linux"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["tmux", "python", "bash"],
        "dependencies": ["tmux >= 3.2"],
        "content": """# Multi-Agent Terminal Orchestration with Tmux

## Overview

A definitive production engineering reference for managing, isolating, and supervising multiple autonomous CLI coding agents running in parallel across headless terminal sessions using `tmux`. Running autonomous agents in interactive foreground shells blocks developer environments and risks premature termination upon SSH disconnect. This skill instructs AI agents on spawning isolated background tmux sessions, multiplexing panes, piping prompts into running agent shells via `tmux send-keys`, capturing buffer snapshots for progress auditing, and terminating zombie workers.

## When to Use

- Running multiple concurrent CLI agents (e.g. frontend agent, backend agent, test runner agent) on a local workstation or remote server.
- Detaching and preserving agent executions across unstable SSH sessions.
- Automating inter-agent communication by inspecting terminal output buffers programmatically.
- Building autonomous agent supervisor daemons that monitor worker health.

## When NOT to Use

- Cloud container orchestration at scale across multiple physical nodes (use Kubernetes or Nomad).
- Pure programmatic Python agents communicating via queues or HTTP (use Celery or Redis Streams).

## Inputs & Prerequisites

- Linux or macOS environment with `tmux >= 3.2` installed.
- CLI coding agents installed in PATH (e.g. `claude`, `aider`, `agy`).

## Core Workflow

### 1. Programmatic Tmux Session Lifecycle in Python
Spawn, inspect, and manage detached tmux sessions using `subprocess`:

```python
import subprocess
import time

class TmuxAgentManager:
    def __init__(self, session_prefix: str = "agent"):
        self.session_prefix = session_prefix

    def _run_tmux(self, args: list[str]) -> str:
        res = subprocess.run(["tmux"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.stdout.strip()

    def spawn_agent(self, agent_id: str, command: str) -> str:
        session_name = f"{self.session_prefix}-{agent_id}"
        
        # Check if session exists
        if self.is_running(session_name):
            return f"Session {session_name} is already active."

        # Create new detached session running bash
        self._run_tmux(["new-session", "-d", "-s", session_name])
        time.sleep(0.2)

        # Launch agent command inside session
        self._run_tmux(["send-keys", "-t", session_name, command, "C-m"])
        return f"Spawned agent in detached tmux session '{session_name}'."

    def is_running(self, session_name: str) -> bool:
        sessions = self._run_tmux(["list-sessions", "-F", "#{session_name}"]).splitlines()
        return session_name in sessions

    def send_prompt(self, agent_id: str, prompt: str):
        session_name = f"{self.session_prefix}-{agent_id}"
        # Send text followed by Enter (C-m)
        self._run_tmux(["send-keys", "-t", session_name, prompt, "C-m"])

    def capture_output_buffer(self, agent_id: str, lines: int = 50) -> str:
        session_name = f"{self.session_prefix}-{agent_id}"
        # Capture last N lines from pane history
        return self._run_tmux(["capture-pane", "-p", "-t", session_name, "-S", f"-{lines}"])

    def terminate_agent(self, agent_id: str):
        session_name = f"{self.session_prefix}-{agent_id}"
        self._run_tmux(["kill-session", "-t", session_name])
```

### 2. Multi-Pane Workspace Split (Supervisor View)
Create a unified dashboard splitting one window into 3 agent panes:

```bash
#!/bin/bash
SESSION="dev-team"

# 1. Start session with Frontend Agent
tmux new-session -d -s $SESSION -n "agents" "agy --role frontend"

# 2. Split vertically for Backend Agent
tmux split-window -h -t $SESSION:0 "agy --role backend"

# 3. Split lower half for QA Test Agent
tmux split-window -v -t $SESSION:0.1 "agy --role qa"

# Attach to view all 3 agents working simultaneously
tmux attach-session -t $SESSION
```

## Best Practices & Failure Modes

1. **Unescaped Quotes in `send-keys`**: Sending prompts containing double quotes or special shell characters (`$`, `&`, `;`) directly to `send-keys` can execute unintended commands in bash. Always sanitize prompts or write them to temporary files and instruct the agent to read the file.
2. **Orphaned Sessions Leaking RAM**: Forgetting to terminate tmux sessions when agents complete tasks leaves long-running idle processes consuming memory. Implement idle timeouts that automatically kill sessions inactive for > 2 hours.
3. **Buffer Capture Truncation**: Default tmux scrollback buffer is 2000 lines. For verbose tasks, increase history limit in `~/.tmux.conf`: `set -g history-limit 50000`.

## Verification & Testing

- Verify active agent sessions:
  ```bash
  tmux list-sessions
  ```
- Capture snapshot of agent terminal:
  ```bash
  tmux capture-pane -p -t agent-backend -S -20
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
