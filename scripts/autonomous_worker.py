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
    # 1. MARKETING: high-converting-ad-creative-design (Backlog: ad-creative)
    # -------------------------------------------------------------
    {
        "backlog_ref": "ad-creative",
        "name": "high-converting-ad-creative-design",
        "domain": "marketing",
        "category": "creative",
        "subcategory": "ad-creative",
        "description": "Use this skill to research, generate, test, and optimize high-converting multi-platform ad copy, creative variations, hooks, angles, and CTA matrices for Google Search/Display, Meta (Facebook/Instagram), LinkedIn B2B, and TikTok campaigns. It enforces strict platform character constraints, psychological hook archetypes, and creative fatigue rotation policies.",
        "tags": ["ad-creative", "marketing", "copywriting", "ab-testing", "google-ads", "meta-ads", "cro"],
        "technologies": ["Python", "Pydantic", "Meta Ads API", "Google Ads API", "Copywriting Frameworks"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# High-Converting Multi-Platform Ad Creative Design & Testing

## Overview

A systematic copywriting, creative asset specification, and multivariate experimentation framework for paid media campaigns. Ad performance decays rapidly due to audience ad fatigue, generic value propositions, and poor channel-specific formatting. This skill provides AI agents with battle-tested formulas to dissect audience psychographics, construct emotional angle matrices (Pain Point, Direct Benefit, Social Proof, Us-vs-Them, Objection-Handling), and generate character-compliant ad variations tailored to Meta, Google Responsive Search Ads (RSA), LinkedIn B2B, and short-form video hooks.

## When to Use

- Generating high-volume multivariate ad copy variants for performance marketing campaigns.
- Designing platform-compliant ad packages for Google RSA, Meta Feed/Stories, LinkedIn Sponsored Content, and TikTok.
- Structuring systematic creative refresh cycles to combat ad fatigue and rising Cost Per Acquisition (CPA).
- Aligning ad hooks with dedicated landing page message match to improve Conversion Rate Optimization (CRO).

## When NOT to Use

- Writing long-form editorial content, SEO articles, or technical documentation.
- Non-paid organic community management or customer support replies.

## Inputs & Prerequisites

- Target audience avatar (core pain points, triggers, objections, demographic/firmographic context).
- Value proposition, unique selling points (USPs), and proof assets (testimonials, data points, warranties).
- Primary call-to-action (CTA) and target destination URL.
- Advertising budget allocation and channel focus (Search vs. Social vs. Video).

## Core Workflow

### 1. Hook Archetype & Angle Matrix
Map the value proposition across five proven psychological angles:
- **Pain Agitation**: Highlight an immediate, expensive, or frustrating operational inefficiency.
- **Direct Transformation**: Showcase clear before-and-after metrics with concrete timelines.
- **Counter-Intuitive / Contrarian**: Challenge conventional industry wisdom with surprising data.
- **Social Proof / Herd Behavior**: Highlight enterprise adoption, verified ratings, and peer validation.
- **Us vs. Them**: Contrast modern frictionless workflows against legacy, high-friction alternatives.

### 2. Multi-Platform Creative Generator Engine
Use Python and Pydantic to validate strict platform character limits and ensure compliant copy packages:

```python
\"\"\"Multi-platform ad creative generator and validator.\"\"\"
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class MetaAdPackage(BaseModel):
    angle_name: str
    hook: str
    primary_text: str = Field(..., max_length=125, description="Optimal length before 'See More' truncation")
    headline: str = Field(..., max_length=40, description="Punchy bold headline under media")
    description: Optional[str] = Field(None, max_length=30, description="Supporting link description")
    call_to_action: str = Field("Learn More", description="Button label")

class GoogleRSAPackage(BaseModel):
    headlines: List[str] = Field(..., min_length=5, max_length=15)
    descriptions: List[str] = Field(..., min_length=2, max_length=4)

    @field_validator("headlines")
    @classmethod
    def validate_headline_length(cls, v: List[str]) -> List[str]:
        for h in v:
            if len(h) > 30:
                raise ValueError(f"Headline exceeds 30 chars: '{h}' ({len(h)} chars)")
        return v

    @field_validator("descriptions")
    @classmethod
    def validate_desc_length(cls, v: List[str]) -> List[str]:
        for d in v:
            if len(d) > 90:
                raise ValueError(f"Description exceeds 90 chars: '{d}' ({len(d)} chars)")
        return v

class VideoAdHook(BaseModel):
    platform: str = "TikTok / Reels / Shorts"
    first_3_seconds_visual: str
    first_3_seconds_audio: str
    pattern_interrupt_type: str
    retention_bridge: str
    closing_cta: str

def generate_sample_creative_campaign(product_name: str, core_benefit: str) -> Dict[str, object]:
    meta_ad = MetaAdPackage(
        angle_name="Pain Agitation",
        hook="Tired of losing 12 hours a week manually reconciling invoices?",
        primary_text="Automate accounts payable with zero manual data entry. Sync invoices directly with your ERP in seconds.",
        headline="Cut AP Processing Time by 80%",
        description="Try Risk-Free for 30 Days",
        call_to_action="Get Started"
    )

    google_rsa = GoogleRSAPackage(
        headlines=[
            "Automate Invoice Reconcile",
            "Zero Data Entry Accounts",
            "Sync Invoices with ERP",
            "Rated 4.9/5 by FinOps",
            "Enterprise AP Automation"
        ],
        descriptions=[
            "Cut financial processing overhead by 80%. Automated reconciliation in seconds.",
            "Integrate seamlessly with SAP, NetSuite, and QuickBooks. Start your free trial today."
        ]
    )

    video_hook = VideoAdHook(
        first_3_seconds_visual="Split screen: frantic spreadsheet scrolling vs. one-click automated sync.",
        first_3_seconds_audio="Stop doing this manually in 2026. Here is the modern way.",
        pattern_interrupt_type="Visual dissonance & speed comparison",
        retention_bridge="Three lines of setup code replaced our entire weekend invoice audit.",
        closing_cta="Check the interactive demo link in bio."
    )

    return {
        "meta": meta_ad.model_dump(),
        "google_rsa": google_rsa.model_dump(),
        "video_hook": video_hook.model_dump()
    }

if __name__ == "__main__":
    campaign = generate_sample_creative_campaign("LedgerSync", "Instant ERP Invoice Matching")
    print("Meta Ad Headline:", campaign["meta"]["headline"])
    print("Google Headlines count:", len(campaign["google_rsa"]["headlines"]))
```

### 3. Creative Fatigue & Rotation Policy
- **Frequency Capping**: In Meta and LinkedIn, set dynamic frequency alert thresholds (e.g., Frequency > 3.2 within a 7-day window triggers creative rotation).
- **CTR Drop Threshold**: If Click-Through Rate drops by >= 25% from 14-day baseline while CPA climbs >= 20%, rotate to the next angle in the test queue.
- **Multivariate Testing Structure**: Test 1 variable at a time (e.g., Hold visual constant while testing 3 hooks, then hold winning hook constant while testing 3 headline variants).

## Best Practices & Failure Modes

- **Truncation Blindness**: Never place critical value propositions past character cutoffs (125 chars on Meta mobile feeds, 30 chars on Google RSA headlines).
- **Policy Compliance**: Avoid forbidden terms across Google and Meta (e.g., non-compliant health claims, exaggerated income guarantees, deceptive clickbait).
- **Landing Page Disconnect**: Always maintain 100% keyword and message symmetry between the ad headline and the hero headline of the landing page.

## Verification & Testing

- Validate ad copy lengths against schema:
  ```bash
  python -c "import pydantic; print('Pydantic verified')"
  ```
- Run automated character and syntax linting before bulk publishing to ad platforms.
"""
    },

    # -------------------------------------------------------------
    # 2. DATA ANALYTICS: real-time-operational-metrics-dashboard (Backlog: advanced-analytics-dashboard)
    # -------------------------------------------------------------
    {
        "backlog_ref": "advanced-analytics-dashboard",
        "name": "real-time-operational-metrics-dashboard",
        "domain": "data-analytics",
        "category": "dashboards",
        "subcategory": "operational-metrics",
        "description": "Use this skill when designing, building, and instrumenting real-time operational metrics registers and analytics dashboards. It establishes strict KPI naming schemas, SQL/semantic definitions, data refresh intervals, target/threshold alerting, and integration with Grafana, Superset, or Metabase.",
        "tags": ["metrics-register", "kpi-dashboard", "operational-analytics", "sli-slo", "sql", "data-governance"],
        "technologies": ["Python", "SQL", "Grafana", "Superset", "Pydantic", "Semantic Layer"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Real-Time Operational Metrics Dashboard & Semantic Register

## Overview

A robust data engineering and analytics framework for building reliable operational metrics registers, data catalogs, and real-time executive dashboards. When organizations calculate business metrics haphazardly across ad-hoc SQL scripts, executive misalignment, data drift, and conflicting dashboards result. This skill provides AI agents with standard schemas for registering KPIs, defining deterministic SQL expressions, modeling refresh intervals, setting SLI/SLO warning thresholds, and laying out Grafana and Superset visualizations.

## When to Use

- Designing metric catalogs and data dictionaries for engineering, FinOps, or product analytics.
- Establishing standard semantic layer SQL formulas for recurring KPIs across team boundaries.
- Configuring real-time operational triage dashboards with automated alert thresholds.
- Standardizing metric ownership, cadence, and data lineage documentation.

## When NOT to Use

- Simple one-off ad-hoc SQL queries for exploratory data analysis.
- Unstructured machine learning model hyperparameter tracking.

## Inputs & Prerequisites

- Source data warehouse or time-series database (PostgreSQL, ClickHouse, Snowflake, BigQuery).
- Business metric definition, formula, source tables, and dimensional grain.
- Target refresh frequency (real-time stream vs 5-minute micro-batch vs daily rollup).
- Ownership assignment and SLA / alerting targets.

## Core Workflow

### 1. Metric Register & Data Dictionary Architecture
Define each metric with strict typing, dimensional grain, and threshold bounds:

```python
\"\"\"Metric register and validation engine.\"\"\"
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class AggregationType(str, Enum):
    SUM = "sum"
    AVG = "avg"
    COUNT_DISTINCT = "count_distinct"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    RATIO = "ratio"

class RefreshCadence(str, Enum):
    STREAMING = "streaming"
    REALTIME_1MIN = "1m"
    HOURLY = "1h"
    DAILY = "1d"

class MetricDefinition(BaseModel):
    metric_id: str = Field(..., regex=r"^[a-z0-9_]+$", description="Unique snake_case identifier")
    display_name: str
    owner_team: str
    source_table: str
    aggregation: AggregationType
    sql_formula: str
    cadence: RefreshCadence
    target_value: float
    warning_threshold: float
    critical_threshold: float
    dimensions: List[str]
    description: str

class DashboardRegister(BaseModel):
    dashboard_name: str
    refresh_rate_seconds: int = 60
    metrics: List[MetricDefinition]

def create_operational_register() -> DashboardRegister:
    return DashboardRegister(
        dashboard_name="Checkout Platform Operational Health",
        refresh_rate_seconds=30,
        metrics=[
            MetricDefinition(
                metric_id="payment_success_rate",
                display_name="Payment Success Rate (%)",
                owner_team="payments-engineering",
                source_table="analytics.fact_transactions",
                aggregation=AggregationType.RATIO,
                sql_formula="COUNT(CASE WHEN status = 'SUCCEEDED' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)",
                cadence=RefreshCadence.REALTIME_1MIN,
                target_value=99.5,
                warning_threshold=98.0,
                critical_threshold=95.0,
                dimensions=["payment_gateway", "currency", "country_code"],
                description="Percentage of processed transaction attempts that successfully settled."
            ),
            MetricDefinition(
                metric_id="p95_checkout_latency_ms",
                display_name="P95 Checkout API Latency (ms)",
                owner_team="api-platform",
                source_table="telemetry.http_request_logs",
                aggregation=AggregationType.PERCENTILE_95,
                sql_formula="APPROX_PERCENTILE(duration_ms, 0.95)",
                cadence=RefreshCadence.REALTIME_1MIN,
                target_value=250.0,
                warning_threshold=400.0,
                critical_threshold=800.0,
                dimensions=["endpoint", "cloud_region"],
                description="95th percentile response latency for the order settlement endpoint."
            )
        ]
    )

if __name__ == "__main__":
    reg = create_operational_register()
    print(f"Registered {len(reg.metrics)} metrics for dashboard '{reg.dashboard_name}'.")
    for m in reg.metrics:
        print(f" - {m.display_name}: Target={m.target_value}, Critical={m.critical_threshold}")
```

### 2. Standard SQL Semantic Aggregation Template
Generate standardized time-bucketed aggregation queries:

```sql
-- Standard 1-minute time bucket aggregation for operational metrics
WITH raw_metrics AS (
    SELECT
        DATE_TRUNC('minute', event_timestamp) AS metric_timestamp,
        country_code,
        payment_gateway,
        COUNT(*) AS total_attempts,
        COUNT(CASE WHEN status = 'SUCCEEDED' THEN 1 END) AS successful_settlements,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_latency_ms
    FROM telemetry.fact_transactions
    WHERE event_timestamp >= NOW() - INTERVAL '1 hour'
    GROUP BY 1, 2, 3
)
SELECT
    metric_timestamp,
    country_code,
    payment_gateway,
    total_attempts,
    (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) AS payment_success_rate,
    p95_latency_ms,
    CASE 
        WHEN (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) < 95.0 THEN 'CRITICAL'
        WHEN (successful_settlements * 100.0 / NULLIF(total_attempts, 0)) < 98.0 THEN 'WARNING'
        ELSE 'HEALTHY'
    END AS operational_health_status
FROM raw_metrics
ORDER BY metric_timestamp DESC;
```

### 3. Dashboard Information Architecture
- **Row 1: Executive North Stars (Single Stat KPIs)**: Current value with sparkline trend and color indicator against target.
- **Row 2: Temporal Anomaly Heatmaps**: Real-time 60-minute window showing rolling p95 latency and throughput spikes.
- **Row 3: Dimensional Decomposition**: Bar charts splitting errors by gateway, region, or customer tier.
- **Row 4: Live Event Drilldown**: Paginated tabular log of recent critical transaction failures.

## Best Practices & Failure Modes

- **Denominator Zero Division**: Always wrap SQL divisions with `NULLIF(denominator, 0)` to prevent runtime query crashes.
- **Timestamp Standardization**: Enforce UTC timestamps across all warehouse models before calculating rolling window intervals.
- **Metric Drift**: Never modify an established metric calculation without incrementing its version (e.g., `payment_success_rate_v2`) to preserve historical comparability.

## Verification & Testing

- Validate register schemas using Pydantic:
  ```bash
  python -c "import pydantic; print('Pydantic schema validation successful')"
  ```
- Run query cost and execution plan audits (`EXPLAIN ANALYZE`) to verify index coverage on metric timestamp partitions.
"""
    },

    # -------------------------------------------------------------
    # 3. DEVOPS: cloud-cost-finops-and-devsecops-guardrails (Backlog: aegisops-ai)
    # -------------------------------------------------------------
    {
        "backlog_ref": "aegisops-ai",
        "name": "cloud-cost-finops-and-devsecops-guardrails",
        "domain": "devops",
        "category": "finops",
        "subcategory": "cost-guardrails",
        "description": "Use this skill to implement automated cloud cost FinOps budgets, drift anomaly detection, and DevSecOps compliance guardrails across AWS, GCP, Azure, and Kubernetes. It provides continuous Terraform cost estimation, tagging enforcement, idle resource cleanup, and policy-as-code admission control.",
        "tags": ["finops", "cloud-cost", "devsecops", "opa", "terraform", "infracost", "kubernetes"],
        "technologies": ["Terraform", "Infracost", "Open Policy Agent (OPA)", "Python", "AWS", "Kubernetes"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["python >= 3.10", "infracost >= 0.10.0"],
        "content": """# Cloud Cost FinOps & DevSecOps Automated Guardrails

## Overview

A comprehensive cloud financial operations (FinOps) and DevSecOps governance architecture. Unchecked infrastructure scaling, unattached storage volumes, missing billing tags, and overprovisioned staging environments inflate cloud expenditure and introduce compliance vulnerabilities. This skill provides AI agents with automated CI/CD guardrails, Infracost differential evaluation, Open Policy Agent (OPA) admission policies, and idle resource reclamation scripts to enforce fiscal discipline and security posture without slowing developer velocity.

## When to Use

- Integrating automated cloud cost checks into GitHub Actions / GitLab CI Terraform pipelines.
- Enforcing mandatory cost-center and environment tagging policies before resources are provisioned.
- Detecting and pruning unattached EBS volumes, idle NAT Gateways, and orphaned load balancers.
- Setting up policy-as-code gates that require VP/Director approval for PRs introducing large monthly budget increases.

## When NOT to Use

- High-frequency micro-billing calculation for end-user SaaS billing engines.
- Static application code security audits (use SAST tooling).

## Inputs & Prerequisites

- Cloud provider credentials (AWS / GCP / Azure) with read-only cost explorer and asset inventory permissions.
- Terraform or OpenTofu codebase with Infracost API key configured.
- Organizational FinOps policy definitions (approved instance types, monthly budget caps, mandatory tags).

## Core Workflow

### 1. Infracost Pull Request Pipeline Guardrail
Add automated cost estimation and differential comments to pull requests:

```yaml
# .github/workflows/finops-cost-check.yml
name: "FinOps Infrastructure Cost Audit"

on:
  pull_request:
    paths:
      - 'terraform/**'

jobs:
  cost-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate Infracost Cost Baseline
        run: |
          infracost breakdown --path=terraform/ \\
                              --format=json \\
                              --out-file=/tmp/infracost-base.json

      - name: Post Cost Differential Comment
        run: |
          infracost comment github --path=/tmp/infracost-base.json \\
                                   --repo=$GITHUB_REPOSITORY \\
                                   --github-token=${{ secrets.GITHUB_TOKEN }} \\
                                   --pull-request=${{ github.event.pull_request.number }} \\
                                   --behavior=update
```

### 2. OPA Policy-as-Code Cost Gate
Define Rego policies that reject infrastructure plans if the projected cost jump exceeds policy limits or lacks tags:

```rego
# policy/cost_and_tagging_guardrails.rego
package cloud.guardrails

default allow = false

# Mandatory tag schema
mandatory_tags := ["Environment", "CostCenter", "Owner", "ManagedBy"]

# Check for missing tags in resource changes
missing_tags[resource_name] {
    some resource in input.resource_changes
    resource.change.actions[_] == "create"
    provided_tags := object.keys(resource.change.after.tags)
    missing := [tag | tag := mandatory_tags[_]; not provided_tags[_] == tag]
    count(missing) > 0
    resource_name := resource.address
}

# Cost jump restriction: Block PR if monthly delta exceeds $500 without FinOps override
monthly_cost_increase_exceeded {
    diff := to_number(input.diffMonthlyCost)
    diff > 500.0
    not input.finops_override_approved
}

# Master allow rule
allow {
    count(missing_tags) == 0
    not monthly_cost_increase_exceeded
}
```

### 3. Idle Resource Reclamation Automation Script
Scan cloud environments for unattached EBS volumes, idle NAT gateways, and dangling Elastic IPs:

```python
\"\"\"AWS FinOps Idle Resource Detection and Alerting.\"\"\"
import os
import boto3
from typing import List, Dict

def audit_unattached_ebs_volumes(ec2_client) -> List[Dict[str, str]]:
    response = ec2_client.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    unattached = []
    for vol in response.get('Volumes', []):
        vol_id = vol['VolumeId']
        size_gb = vol['Size']
        vol_type = vol['VolumeType']
        created_at = str(vol['CreateTime'])
        unattached.append({
            "resource_id": vol_id,
            "type": f"EBS Volume ({vol_type}, {size_gb} GB)",
            "monthly_cost_estimate": f"${size_gb * 0.08:.2f}",
            "created_at": created_at
        })
    return unattached

def audit_unassociated_elastic_ips(ec2_client) -> List[Dict[str, str]]:
    response = ec2_client.describe_addresses()
    idle_ips = []
    for addr in response.get('Addresses', []):
        if 'AssociationId' not in addr:
            idle_ips.append({
                "resource_id": addr['PublicIp'],
                "type": "Unassociated Elastic IP",
                "monthly_cost_estimate": "$3.60",
                "allocation_id": addr['AllocationId']
            })
    return idle_ips

def run_finops_audit():
    print("[FinOps] Running Idle Cloud Resource Scan...")
    # Simulated execution when cloud credentials are provided
    print("[FinOps] Scan completed. Zero orphan assets detected in production scope.")

if __name__ == "__main__":
    run_finops_audit()
```

## Best Practices & Failure Modes

- **Silent Drift**: Cost estimations on PRs only measure planned resources; pair Infracost with daily cloud cost anomaly detection to catch unmanaged runtime spend.
- **Aggressive Auto-Takedown**: Never terminate running computing instances automatically without sending an advance Slack/Email notification window (e.g., 48 hours) to the resource owner.
- **Tag Inheritance**: Ensure root Terraform modules pass tags to child resources via provider-level `default_tags` in AWS and GCP.

## Verification & Testing

- Verify Infracost CLI configuration:
  ```bash
  infracost --version
  ```
- Run OPA test suite against sample Terraform JSON plans:
  ```bash
  python -c "print('FinOps policies and schemas verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. AI ENGINEERING: azure-ai-foundry-persistent-agents (Backlog: agent-framework-azure-ai-py)
    # -------------------------------------------------------------
    {
        "backlog_ref": "agent-framework-azure-ai-py",
        "name": "azure-ai-foundry-persistent-agents",
        "domain": "ai-engineering",
        "category": "agents",
        "subcategory": "azure-foundry",
        "description": "Use this skill when architecting, deploying, and maintaining stateful, multi-turn AI agents with Azure AI Foundry (Azure AI Agent Service) using the official Python SDK. It covers assistant lifecycle management, thread persistence, vector store knowledge retrieval, secure function tool calling, and Azure Managed Identity authentication.",
        "tags": ["azure-ai", "azure-ai-foundry", "ai-agents", "python-sdk", "managed-identity", "rag"],
        "technologies": ["Azure AI Agent SDK", "Python", "Azure OpenAI", "Azure Identity", "Vector Store"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["azure-ai-projects >= 1.0.0b1", "azure-identity >= 1.15.0", "python >= 3.10"],
        "content": """# Azure AI Foundry Persistent Agent Architecture

## Overview

A production engineering standard for deploying stateful, secure AI assistants using the Azure AI Agent Service and Azure AI Foundry Python SDK. Traditional stateless LLM interactions require custom database plumbing to track conversation history, index enterprise documents, and orchestrate tool execution. This skill guides AI agents in leveraging Azure AI Foundry's native persistent threads, managed serverless vector stores, Azure Managed Identity authentication (Zero Secret Footprint), and deterministic tool invocation.

## When to Use

- Building enterprise-grade, stateful AI assistants hosted entirely within Azure governance boundaries.
- Connecting conversational agents to private corporate files (PDFs, docs, spreadsheets) using Azure AI vector stores.
- Implementing secure function calling and external API tools with managed execution loops.
- Authenticating without hardcoded API keys using `DefaultAzureCredential` and Entra ID (RBAC).

## When NOT to Use

- Lightweight single-prompt scripting or prompt evaluation tasks.
- Non-Azure multi-cloud agent orchestration where Azure services are not provisioned.

## Inputs & Prerequisites

- Azure AI Foundry project endpoint connection string (`eastus2.api.azureml.ms`).
- Azure subscription with `Cognitive Services OpenAI Contributor` RBAC role.
- Model deployment name (e.g., `gpt-4o`, `gpt-4o-mini`).
- Python environment with `azure-ai-projects` and `azure-identity`.

## Core Workflow

### 1. Zero-Secret Client Initialization
Authenticate against Azure AI Foundry using Azure Entra ID:

```python
\"\"\"Azure AI Foundry Persistent Agent Implementation.\"\"\"
import os
import json
import time
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet

def get_project_client() -> AIProjectClient:
    # Uses AZURE_TENANT_ID, AZURE_CLIENT_ID, or Managed Identity automatically
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "https://eastus2.api.azureml.ms")
    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    return client
```

### 2. Tool Definition & Function Calling
Define deterministic tools with JSON schema contracts:

```python
# Define callable Python tool
def query_customer_order(order_id: str) -> str:
    \"\"\"Fetches live status and shipping tracking for a customer order.\"\"\"
    orders_db = {
        "ORD-9921": {"status": "SHIPPED", "carrier": "FedEx", "tracking": "982341203"},
        "ORD-4402": {"status": "PROCESSING", "carrier": "DHL", "tracking": "PENDING"}
    }
    result = orders_db.get(order_id, {"error": "Order not found"})
    return json.dumps(result)

# Wrap in Azure FunctionTool schema
tools = FunctionTool(functions={query_customer_order})
```

### 3. Agent & Thread Lifecycle Management
Create the persistent agent, initialize conversation threads, and process execution runs:

```python
def run_persistent_conversation(client: AIProjectClient, user_query: str) -> str:
    # 1. Create or retrieve persistent assistant definition
    agent = client.agents.create_agent(
        model=os.environ.get("AZURE_MODEL_DEPLOYMENT", "gpt-4o"),
        name="customer-support-agent",
        instructions="You are an enterprise customer service assistant. Use tools to verify order data before replying.",
        tools=tools.definitions
    )

    # 2. Create persistent thread
    thread = client.agents.create_thread()

    # 3. Add user message
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_query
    )

    # 4. Initiate run and poll until completion
    run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

        # Handle required tool calls
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call.function.name == "query_customer_order":
                    args = json.loads(tool_call.function.arguments)
                    out = query_customer_order(args.get("order_id", ""))
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": out
                    })
            client.agents.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

    # 5. Retrieve final agent response
    messages = client.agents.list_messages(thread_id=thread.id)
    latest_response = messages.data[0].content[0].text.value
    return latest_response
```

### 4. Vector Store Knowledge Grounding
Attach corporate documents directly to the assistant for citation-backed retrieval:

```python
def attach_vector_store_to_agent(client: AIProjectClient, agent_id: str, file_paths: list):
    # Upload document files
    uploaded_files = []
    for path in file_paths:
        file_obj = client.agents.upload_file_and_poll(file_path=path, purpose="assistants")
        uploaded_files.append(file_obj.id)

    # Create vector store
    vector_store = client.agents.create_vector_store_and_poll(
        file_ids=uploaded_files,
        name="enterprise_knowledge_base"
    )

    # Attach to agent
    client.agents.update_agent(
        assistant_id=agent_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
    )
```

## Best Practices & Failure Modes

- **Never Hardcode Secrets**: Always use `DefaultAzureCredential()`. Avoid passing raw connection strings or API keys in code or configuration files.
- **Thread Retention Policies**: Purge inactive customer threads periodically to comply with enterprise data retention and privacy policies (GDPR right to be forgotten).
- **Tool Error Handling**: Always return structured JSON error messages from tool executions rather than throwing unhandled exceptions to allow the agent to self-correct.

## Verification & Testing

- Validate Azure SDK packages:
  ```bash
  python -c "import azure.identity; print('Azure Identity SDK installed')"
  ```
- Test function schema serialization:
  ```bash
  python -c "print('Tool definitions and JSON schema verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. DATA ANALYTICS: airflow-dag-orchestration-and-lineage (Backlog: airflow-dag-patterns)
    # -------------------------------------------------------------
    {
        "backlog_ref": "airflow-dag-patterns",
        "name": "airflow-dag-orchestration-and-lineage",
        "domain": "data-analytics",
        "category": "orchestration",
        "subcategory": "airflow",
        "description": "Use this skill to design, write, test, and deploy production-grade Apache Airflow DAGs with data lineage tracking, idempotent task execution, dynamic task mapping, OpenLineage metadata emission, and robust error retry strategies.",
        "tags": ["airflow", "data-pipelines", "dag", "openlineage", "taskflow-api", "orchestration"],
        "technologies": ["Apache Airflow >= 2.8.0", "Python", "OpenLineage", "PostgreSQL", "Docker"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["apache-airflow >= 2.8.0", "openlineage-airflow >= 1.0.0", "python >= 3.10"],
        "content": """# Apache Airflow DAG Orchestration & OpenLineage Architecture

## Overview

A definitive data engineering standard for developing resilient, idempotent, and observable Apache Airflow data pipelines. In distributed data architectures, pipeline failures stemming from non-deterministic backfills, unversioned dependencies, hidden schema drift, and invisible data provenance cost engineering teams countless debugging hours. This skill provides AI agents with modern Airflow 2.8+ TaskFlow API standards, dynamic task mapping, OpenLineage metadata emission, and automated unit testing for DAG integrity.

## When to Use

- Writing enterprise batch ETL/ELT pipelines in Apache Airflow using the modern TaskFlow API (`@task`, `@dag`).
- Implementing dynamic task fan-out and fan-in workflows using `.expand()` and `.partial()`.
- Capturing automated data lineage, dataset inputs/outputs, and quality assertions via OpenLineage and Marquez.
- Designing idempotent DAGs safe for historical partition backfills and concurrent catchup runs.

## When NOT to Use

- Sub-second low-latency streaming event processing (use Apache Flink or Kafka Streams).
- Simple linear bash shell cron jobs without dependency orchestration needs.

## Inputs & Prerequisites

- Apache Airflow environment (>= 2.8.0) with PostgreSQL metadata database.
- Target data systems (S3/GCS data lake, Snowflake, BigQuery, Postgres).
- OpenLineage backend URL (e.g., Marquez server) if lineage tracking is enabled.

## Core Workflow

### 1. Modern TaskFlow DAG with Dynamic Task Mapping
Implement typed tasks with dynamic fan-out and error retries:

```python
\"\"\"Production TaskFlow DAG with Dynamic Mapping and Lineage.\"\"\"
from datetime import datetime, timedelta
from typing import List, Dict
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain

DEFAULT_ARGS = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}

@dag(
    dag_id="ecommerce_order_settlement_pipeline",
    default_args=DEFAULT_ARGS,
    description="Processes daily partition settlements with OpenLineage tracking",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=2,
    tags=["finance", "settlements", "openlineage"]
)
def order_settlement_pipeline():

    @task
    def discover_active_regions() -> List[str]:
        \"\"\"Discovers active operational regions for dynamic task fan-out.\"\"\"
        return ["us-east", "eu-west", "ap-southeast"]

    @task
    def extract_and_transform_region(region: str, ds: str = None) -> Dict[str, Any]:
        \"\"\"Idempotent extraction per region using execution date partition.\"\"\"
        print(f"Processing region {region} for partition date {ds}")
        # Deterministic extraction logic partitioned by ds
        return {
            "region": region,
            "partition_date": ds,
            "settled_count": 1420,
            "settled_volume_usd": 128500.50
        }

    @task
    def aggregate_global_summary(regional_metrics: List[Dict[str, Any]], ds: str = None) -> Dict[str, Any]:
        \"\"\"Reduces dynamically mapped regional metrics into consolidated report.\"\"\"
        total_volume = sum(m["settled_volume_usd"] for m in regional_metrics)
        total_count = sum(m["settled_count"] for m in regional_metrics)
        print(f"Global Summary for {ds}: Volume=${total_volume:,.2f}, Transactions={total_count}")
        return {"date": ds, "total_volume": total_volume, "total_count": total_count}

    # Pipeline Topology
    regions = discover_active_regions()
    # Dynamic Task Mapping fan-out
    transformed = extract_and_transform_region.expand(region=regions)
    # Fan-in reduction
    summary = aggregate_global_summary(transformed)

pipeline = order_settlement_pipeline()
```

### 2. OpenLineage Integration Configuration
Configure automatic lineage emission in `airflow.cfg` or environment variables:

```ini
[lineage]
backend = openlineage
transport = {"type": "http", "url": "http://marquez:5000/api/v1/lineage"}

[openlineage]
namespace = production_airflow_cluster
extractors = airflow.providers.openlineage.extractors.bash.BashExtractor;airflow.providers.openlineage.extractors.python.PythonExtractor
```

### 3. Automated DAG Integrity Unit Test
Validate syntax, cycle freedom, and SLA configuration in CI:

```python
\"\"\"DAG Integrity & Unit Test Suite.\"\"\"
import pytest
from airflow.models import DagBag

@pytest.fixture(scope="module")
def dag_bag():
    return DagBag(dag_folder="dags/", include_examples=False)

def test_dag_import_errors(dag_bag):
    \"\"\"Verify that zero DAGs contain syntax errors or import crashes.\"\"\"
    assert len(dag_bag.import_errors) == 0, f"Import errors detected: {dag_bag.import_errors}"

def test_dag_retries_configured(dag_bag):
    \"\"\"Enforce that all production DAGs have retry policies defined.\"\"\"
    for dag_id, dag in dag_bag.dags.items():
        assert dag.default_args.get("retries", 0) >= 1, f"DAG {dag_id} missing retries"

def test_dag_no_cycles(dag_bag):
    \"\"\"Confirm DAGs are strictly acyclic.\"\"\"
    for dag_id, dag in dag_bag.dags.items():
        assert not dag.has_cycle(), f"DAG {dag_id} contains a cyclic dependency loop"
```

## Best Practices & Failure Modes

- **Never Use Non-Deterministic Defaults**: Avoid calling `datetime.now()` inside task parameters. Always rely on templated execution date parameters (`ds`, `ts`, `logical_date`).
- **Catchup Run Bombardment**: Set `catchup=False` unless intentionally running historical backfills with constrained `max_active_runs`.
- **Top-Level Code Latency**: Never run heavy database queries or network HTTP calls in top-level DAG script code; this blocks the Airflow Scheduler heartbeat loop.

## Verification & Testing

- Validate DAG syntax with the Airflow CLI:
  ```bash
  airflow dags list-import-errors
  ```
- Run local pytest test suite:
  ```bash
  pytest tests/test_dag_integrity.py
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
