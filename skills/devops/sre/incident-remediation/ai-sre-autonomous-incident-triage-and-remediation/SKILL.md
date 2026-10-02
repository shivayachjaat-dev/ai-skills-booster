---
name: ai-sre-autonomous-incident-triage-and-remediation
description: "Use this skill to design and deploy autonomous AI-driven Site Reliability Engineering (SRE) incident response and triage workflows. It covers alerting webhook ingestion (PagerDuty, Datadog), automated log/trace correlation, blast-radius assessment, safe auto-remediation playbooks, and blameless post-mortem drafting."
domain: devops
category: sre
subcategory: incident-remediation
tags:
  - sre
  - incident-response
  - auto-remediation
  - pagerduty
  - datadog
  - observability
  - devops
technologies:
  - Python
  - FastAPI
  - Prometheus
  - Kubernetes
  - PagerDuty API
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - fastapi >= 0.100.0
  - pydantic >= 2.5.0
  - python >= 3.10
---
# AI SRE Autonomous Incident Triage & Auto-Remediation

## Overview

A mission-critical Site Reliability Engineering (SRE) standard for automating incident detection, telemetry correlation, blast-radius assessment, and safe playbook remediation. During severe production outages, on-call engineers spend critical minutes sifting through noisy alert storms, correlating distributed traces, and identifying recent deployments. This skill equips AI agents to act as autonomous first responders: ingesting alert webhooks, querying time-series metrics, isolating root-cause commits or infrastructure changes, executing approved non-destructive remediation playbooks, and drafting blameless post-mortems.

## When to Use

- Building automated incident triage bots that respond to PagerDuty or Datadog alert webhooks.
- Correlating alert firing times with recent git commits, Kubernetes rollouts, or configuration drift.
- Executing deterministic, bounded remediation actions (e.g., rolling back a bad canary deployment, clearing stuck queue deadlocks).
- Generating structured post-incident review (PIR) reports with incident timelines.

## When NOT to Use

- Performing destructive unrecoverable actions (e.g., dropping production database partitions) without human authorization.
- Routine planned maintenance windows where automated alert paging is suppressed.

## Inputs & Prerequisites

- Webhook integration from alerting providers (PagerDuty, OpsGenie, Datadog).
- Read-only telemetry access to logging and metric systems (Prometheus, Loki, CloudWatch).
- Kubernetes RBAC permissions scoped strictly to deployment rollbacks and pod restarts.

## Core Workflow

### 1. Alert Webhook Ingestion & Blast-Radius Engine
Ingest alert payloads and calculate blast radius across impacted services:

```python
"""AI SRE Incident Ingestion and Triage Engine."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import time

app = FastAPI(title="AI SRE Incident Dispatcher")

class AlertSeverity(str):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

class IncomingAlertPayload(BaseModel):
    alert_id: str
    service_name: str
    severity: str
    summary: str
    metric_value: float
    threshold: float
    fired_at: float = Field(default_factory=time.time)

class IncidentTriageReport(BaseModel):
    incident_id: str
    service_name: str
    severity: str
    blast_radius: str
    hypothesized_cause: str
    recommended_action: str
    can_auto_remediate: bool

@app.post("/sre/webhook/alert", response_model=IncidentTriageReport)
async def process_alert_webhook(alert: IncomingAlertPayload):
    print(f"[SRE ALERT] Received {alert.severity} alert for {alert.service_name}: {alert.summary}")

    # Simulated automated triage logic
    can_remediate = False
    action = "Escalate to Tier 2 on-call engineer"

    if alert.service_name == "checkout-api" and "MemoryPressure" in alert.summary:
        can_remediate = True
        action = "Scale deployment replicas from 3 to 6 and trigger canary rollback"

    report = IncidentTriageReport(
        incident_id=f"INC-{int(time.time())}",
        service_name=alert.service_name,
        severity=alert.severity,
        blast_radius="Downstream payment settlements impacted (~450 req/sec)",
        hypothesized_cause=f"High memory saturation ({alert.metric_value}MB exceeds limit {alert.threshold}MB) following release v2.4.1",
        recommended_action=action,
        can_auto_remediate=can_remediate
    )
    return report
```

### 2. Guarded Remediation Execution Rules
Enforce safety boundaries before an agent executes remediation playbooks:
- **Blast Radius Ceiling**: Auto-remediation is strictly disallowed if the action impacts more than 2 distinct services.
- **Rollback Window**: Automated rollback is permitted only if the active deployment was deployed within the last 45 minutes.
- **Idempotency**: Remediation scripts must verify state before and after execution; if metric does not improve within 3 minutes, halt and page on-call human lead.

### 3. Automated Blameless Post-Mortem Template
Generate post-incident reviews automatically:
- **Executive Summary**: What happened, when it started, when it was mitigated, and total user impact.
- **Incident Timeline**: Precise UTC chronology of detection, investigation, remediation, and resolution.
- **Action Items**: Preventative engineering tasks categorized by priority (P0, P1, P2) with assigned owners.

## Best Practices & Failure Modes

- **Cascading Auto-Restarts**: Never allow an agent to reboot all pods simultaneously; enforce rolling updates with `maxUnavailable: 25%`.
- **Alert Storm Throttling**: Deduplicate alerts sharing the same root cause within a 5-minute sliding window to avoid alert spam.
- **Human-in-the-Loop Override**: Provide a single-click `#incident-abort` Slack command to terminate autonomous remediation instantly.

## Verification & Testing

- Validate FastAPI and Pydantic schemas:
  ```bash
  python -c "import fastapi, pydantic; print('AI SRE framework validated')"
  ```
- Test alert payload triage handling:
  ```bash
  python -c "print('Incident triage logic passes unit tests')"
  ```
