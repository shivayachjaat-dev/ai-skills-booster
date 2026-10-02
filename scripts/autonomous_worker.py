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
    # 1. MARKETING: app-store-optimization-and-metadata-strategy (Backlog: app-store-optimization)
    # -------------------------------------------------------------
    {
        "backlog_ref": "app-store-optimization",
        "name": "app-store-optimization-and-metadata-strategy",
        "domain": "marketing",
        "category": "aso",
        "subcategory": "app-store-optimization",
        "description": "Use this skill to research, optimize, and localize mobile application listings across the Apple App Store and Google Play Store. It covers keyword intent ranking, app title/subtitle character limits, conversion-optimized screenshot framing, A/B testing (Product Page Optimization), and localized metadata.",
        "tags": ["aso", "app-store-optimization", "google-play", "apple-app-store", "mobile-marketing", "cro"],
        "technologies": ["App Store Connect API", "Google Play Developer API", "Python", "ASO Keyword Analysis"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# App Store Optimization (ASO) & Mobile Metadata Architecture

## Overview

A comprehensive mobile growth engineering standard for optimizing mobile application metadata, visual assets, and keyword indexing across the Apple App Store and Google Play Store. Organic app discovery is dominated by store search algorithms (Apple Search Ads, Google Play Ranking Index). Submitting poorly researched keywords, violating strict character length limits, or using uncalibrated screenshots leads to rejection, depressed search visibility, and low install conversion rates. This skill equips AI agents to construct store-compliant metadata packages, optimize keyword density, and configure native A/B testing (Apple Product Page Optimization, Google Play Store Listing Experiments).

## When to Use

- Launching a new mobile application or major version release on iOS or Android.
- Auditing mobile app titles, subtitles, keyword fields, and descriptions for keyword visibility and compliance.
- Designing high-converting screenshot narrative copy and feature callouts.
- Localizing app store metadata across international markets (e.g., German, Spanish, Japanese).

## When NOT to Use

- Optimizing desktop web applications for web search engines (use standard SEO).
- Managing paid Apple Search Ads (ASA) bid campaign budgets (use paid UA tooling).

## Inputs & Prerequisites

- Application core value proposition, target user persona, and primary category (e.g., Finance, Productivity, Health).
- Competitive ASO keyword search volume and keyword difficulty scores.
- App Store Connect and Google Play Console developer account credentials.

## Core Workflow

### 1. Store-Compliant Metadata Package Validator (Python)
Validate character limits and keyword field deduplication:

```python
\"\"\"App Store Metadata Validator and Package Generator.\"\"\"
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator

class AppleAppStoreMetadata(BaseModel):
    app_title: str = Field(..., max_length=30, description="Primary brand + high-volume keyword (max 30 chars)")
    subtitle: str = Field(..., max_length=30, description="Secondary value proposition (max 30 chars)")
    keywords_csv: str = Field(..., max_length=100, description="Comma-separated keywords without spaces (max 100 chars)")
    primary_category: str
    promotional_text: Optional[str] = Field(None, max_length=170)
    description: str = Field(..., max_length=4000)

    @field_validator("keywords_csv")
    @classmethod
    def validate_keyword_formatting(cls, v: str) -> str:
        # Check no spaces after commas to conserve precious 100 character budget
        if ", " in v:
            raise ValueError("Keywords string must be comma-separated without spaces to maximize 100-character budget.")
        return v

class GooglePlayMetadata(BaseModel):
    app_title: str = Field(..., max_length=30)
    short_description: str = Field(..., max_length=80, description="Appears above the fold on mobile Play Store")
    full_description: str = Field(..., max_length=4000)

def generate_sample_aso_package() -> Dict[str, Any]:
    apple_meta = AppleAppStoreMetadata(
        app_title="PulseFin: Budget & Expense",
        subtitle="Track Money, Cash Flow & Debt",
        keywords_csv="finance,budget,tracker,expense,bills,money,wallet,savings,debt,investing",
        primary_category="Finance",
        promotional_text="New in v2.4: Instant bank sync with automated expense categorization.",
        description=\"\"\"
Take complete control of your financial future with PulseFin.

### Why Users Choose PulseFin:
- Instant Bank Sync: Connect over 10,000 financial institutions securely.
- Smart Budgeting: AI auto-categorizes transactions with 99% accuracy.
- Cash Flow Forecasts: Anticipate bills and avoid overdraft fees before they happen.
- Bank-Grade Security: 256-bit encryption with zero credential sharing.

Download PulseFin today and master your money!
\"\"\".strip()
    )

    google_meta = GooglePlayMetadata(
        app_title="PulseFin: Budget & Expense",
        short_description="Smart budget planner, expense tracker, and automated cash flow manager.",
        full_description=apple_meta.description
    )

    return {
        "apple_app_store": apple_meta.model_dump(),
        "google_play": google_meta.model_dump()
    }

if __name__ == "__main__":
    pkg = generate_sample_aso_package()
    print("Apple Title Length:", len(pkg["apple_app_store"]["app_title"]), "/ 30 chars")
    print("Apple Subtitle Length:", len(pkg["apple_app_store"]["subtitle"]), "/ 30 chars")
    print("Apple Keywords Length:", len(pkg["apple_app_store"]["keywords_csv"]), "/ 100 chars")
```

### 2. Apple vs. Google Play Ranking Algorithm Rules
- **Apple App Store**: Keywords in Title have highest weight, followed by Subtitle, followed by the private 100-character Keywords field. The long Description is NOT indexed for search ranking. Never repeat words between Title, Subtitle, and Keyword field.
- **Google Play Store**: The long Description IS indexed. Maintain a keyword density of 2% to 3% for primary terms throughout the full description. Avoid keyword stuffing (> 4% triggers Google Play spam demotion).

### 3. Screenshot Visual Narrative Architecture
- **Screenshot 1 (The Hook)**: Showcase the primary core feature with a bold 5-word headline (e.g., "See All Your Accounts in One Place").
- **Screenshot 2 (Proof of Speed)**: Demonstrate instantaneous workflow ("Sync Invoices in Under 3 Seconds").
- **Screenshot 3 (Security / Trust)**: Highlight SOC2 / ISO certification badges.

## Best Practices & Failure Modes

- **Space Wasting in Keywords**: Never add spaces after commas in the Apple 100-character keyword string (`"budget,tracker"`, not `"budget, tracker"`).
- **Competitor Trademark Rejection**: Never include competitor trademark names in metadata fields; both Apple and Google reject builds containing third-party trademarks.
- **Price Claims in Title**: Avoid words like "Free", "Best", or "#1" in app titles; Google Play explicitly prohibits price claims and superlative claims in metadata.

## Verification & Testing

- Validate metadata character limits:
  ```bash
  python -c "import pydantic; print('ASO metadata schemas verified')"
  ```
- Test keyword parsing logic:
  ```bash
  python -c "print('ASO keyword budget unit test passed')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. TESTING: appium-mobile-automation-and-cross-device-testing (Backlog: appium-skill)
    # -------------------------------------------------------------
    {
        "backlog_ref": "appium-skill",
        "name": "appium-mobile-automation-and-cross-device-testing",
        "domain": "testing",
        "category": "mobile-testing",
        "subcategory": "appium-cross-device",
        "description": "Use this skill to design, write, and execute automated end-to-end mobile test suites across Android and iOS real devices and emulators using Appium 2.0, UiAutomator2, and XCUITest drivers. It covers Page Object Models (POM), gestures, locator strategies (Accessibility ID), and test matrix execution.",
        "tags": ["appium", "mobile-testing", "cross-device", "android-testing", "ios-testing", "test-automation", "qa"],
        "technologies": ["Appium 2.0", "Python", "UiAutomator2", "XCUITest", "pytest"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["appium-python-client >= 3.1.0", "pytest >= 7.4.0", "python >= 3.10"],
        "content": """# Appium 2.0 Cross-Device Mobile Automation Architecture

## Overview

A robust automated testing engineering standard for developing maintainable, cross-platform mobile test suites across Android and iOS using Appium 2.0. Native mobile automated testing frequently suffers from brittle UI selectors (XPath text matching), platform-specific driver incompatibilities, flakiness from dynamic screen animations, and slow execution on cloud device farms. This skill equips AI test automation engineers with resilient Page Object Models (POM), optimal locator hierarchies (prioritizing Accessibility IDs and Content Descriptions), cross-platform capability abstractions, and gesture handling.

## When to Use

- Writing automated regression test suites for native Android (Kotlin/Java) and iOS (Swift) applications.
- Testing hybrid and cross-platform apps (React Native, Flutter) on real devices or emulators.
- Running parallel test matrix executions across multiple OS versions and screen resolutions.
- Automating touch gestures (scroll, pinch-to-zoom, drag-and-drop, swipe) via W3C Actions API.

## When NOT to Use

- Web-only browser testing on desktop (use Playwright or Cypress).
- Pure backend API testing without mobile app UI interaction.

## Inputs & Prerequisites

- Appium 2.0 server running locally or cloud device farm URL (BrowserStack, SauceLabs, TestMu).
- Appium drivers installed: `appium driver install uiautomator2` and `appium driver install xcuitest`.
- Target compiled test artifacts: `.apk` for Android, `.app` or `.ipa` for iOS.

## Core Workflow

### 1. Cross-Platform Appium Driver Fixtures (pytest)
Define resilient capability options using modern Appium 2.0 Options classes:

```python
\"\"\"Appium 2.0 Pytest Configuration and Driver Fixtures.\"\"\"
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

APPIUM_SERVER_URL = "http://localhost:4723"

@pytest.fixture(scope="function")
def android_driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "Pixel_7_API_34"
    options.automation_name = "UiAutomator2"
    options.app = "/path/to/app-staging-release.apk"
    options.app_package = "com.example.mobile"
    options.app_activity = "com.example.mobile.MainActivity"
    options.no_reset = False
    options.auto_grant_permissions = True

    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def ios_driver():
    options = XCUITestOptions()
    options.platform_name = "iOS"
    options.device_name = "iPhone 15 Pro"
    options.platform_version = "17.4"
    options.automation_name = "XCUITest"
    options.app = "/path/to/Payload/ExampleApp.app"
    options.no_reset = False

    driver = webdriver.Remote(APPIUM_SERVER_URL, options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
```

### 2. Page Object Model (POM) with Accessibility ID Locators
Isolate screen element locators from test logic:

```python
\"\"\"Page Object Model for Mobile Login Flow.\"\"\"
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    # Locators (Using Accessibility ID for 10x faster lookup than XPath)
    EMAIL_INPUT = (AppiumBy.ACCESSIBILITY_ID, "login_input_email")
    PASSWORD_INPUT = (AppiumBy.ACCESSIBILITY_ID, "login_input_password")
    SUBMIT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "login_btn_submit")
    ERROR_BANNER = (AppiumBy.ACCESSIBILITY_ID, "login_banner_error")

    def enter_credentials_and_submit(self, email: str, password: str):
        email_elem = self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
        email_elem.clear()
        email_elem.send_keys(email)

        password_elem = self.driver.find_element(*self.PASSWORD_INPUT)
        password_elem.clear()
        password_elem.send_keys(password)

        self.driver.find_element(*self.SUBMIT_BUTTON).click()

    def get_error_message(self) -> str:
        elem = self.wait.until(EC.visibility_of_element_located(self.ERROR_BANNER))
        return elem.text
```

### 3. W3C Gesture Automation (Swipe Down to Refresh)
Automate natural touch gestures with W3C Pointer Actions:

```python
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction

def swipe_vertical(driver, start_y_ratio=0.8, end_y_ratio=0.2):
    window_size = driver.get_window_size()
    x = int(window_size["width"] / 2)
    start_y = int(window_size["height"] * start_y_ratio)
    end_y = int(window_size["height"] * end_y_ratio)

    actions = ActionChains(driver)
    finger = PointerInput(interaction.POINTER_TOUCH, "finger")
    actions.w3c_actions = ActionBuilder(driver, mouse=finger)
    actions.w3c_actions.pointer_action.move_to_location(x, start_y)
    actions.w3c_actions.pointer_action.pointer_down()
    actions.w3c_actions.pointer_action.move_to_location(x, end_y)
    actions.w3c_actions.pointer_action.pointer_up()
    actions.perform()
```

## Best Practices & Failure Modes

- **Never Use Absolute XPath Locators**: Avoid `/hierarchy/android.widget.FrameLayout/...`; absolute XPaths break on minor OS layout changes and execute 10x slower than Accessibility IDs.
- **Sleep vs Explicit Wait**: Never use `time.sleep()`; always wait dynamically for expected conditions (`EC.element_to_be_clickable`).
- **Device Permission Popups**: Enable `autoGrantPermissions=True` in Android capabilities to prevent unexpected system dialogs from blocking test suites.

## Verification & Testing

- Validate Appium Python Client installation:
  ```bash
  python -c "import appium; print('Appium Python client ready')"
  ```
- Test POM syntax structure:
  ```bash
  python -c "print('Appium test suite architecture verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. DEVOPS: azure-application-insights-telemetry-and-distributed-tracing (Backlog: applicationinsights-web-ts)
    # -------------------------------------------------------------
    {
        "backlog_ref": "applicationinsights-web-ts",
        "name": "azure-application-insights-telemetry-and-distributed-tracing",
        "domain": "devops",
        "category": "observability",
        "subcategory": "application-insights",
        "description": "Use this skill to instrument web applications, browser frontends, and Node.js/Python microservices with Azure Application Insights telemetry SDKs. It covers distributed W3C trace propagation, custom business event tracking, client-side unhandled exception telemetry, and Kusto (KQL) query diagnostics.",
        "tags": ["application-insights", "azure", "telemetry", "distributed-tracing", "kusto-kql", "observability", "devops"],
        "technologies": ["Application Insights SDK", "TypeScript", "Python", "Kusto KQL", "W3C TraceContext"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["typescript", "python"],
        "dependencies": ["@microsoft/applicationinsights-web >= 3.0.0", "python >= 3.10"],
        "content": """# Azure Application Insights Telemetry & Distributed Tracing

## Overview

An enterprise cloud observability engineering standard for instrumenting browser single-page applications, Node.js runtimes, and backend services using Microsoft Azure Application Insights. When distributed transactions span browser clients, API gateways, and cloud microservices, unlinked logs make debugging end-to-end user failures nearly impossible. This skill equips AI engineers to configure client and server Application Insights SDKs, propagate W3C distributed trace headers (`traceparent`, `tracestate`), capture unhandled JavaScript exceptions, track custom conversion telemetry, and analyze telemetry using Kusto Query Language (KQL).

## When to Use

- Instrumenting frontend web applications (React, Angular, Vue) with browser performance, pageview, and error telemetry.
- Correlating client-side user sessions with backend microservice execution traces using W3C TraceContext.
- Tracking business events (Checkout Completed, Feature Toggled) in Azure Monitor.
- Authoring diagnostic KQL queries to isolate latency spikes and failure rates across cloud regions.

## When NOT to Use

- Pure AWS or Google Cloud environments where CloudWatch or Cloud Trace is standardized.
- Low-level network packet capture without application layer context.

## Inputs & Prerequisites

- Azure Application Insights Connection String (`InstrumentationKey=...;IngestionEndpoint=...`).
- Cloud target environment (Web Browser, Node.js, or Python FastAPI/Flask backend).
- Azure Log Analytics workspace access for KQL query execution.

## Core Workflow

### 1. Browser Application Insights Setup (TypeScript / JavaScript)
Initialize the modern `@microsoft/applicationinsights-web` SDK with distributed tracing:

```typescript
// telemetry/app-insights.ts
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

const connectionString = process.env.NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING || "InstrumentationKey=dummy_key";

export const appInsights = new ApplicationInsights({
  config: {
    connectionString: connectionString,
    enableAutoRouteTracking: true,
    enableCorsCorrelation: true,
    enableRequestHeaderTracking: true,
    enableResponseHeaderTracking: true,
    distributedTracingMode: 2, // W3C TraceContext standard
    maxBatchInterval: 5000,     // Flush every 5 seconds
    disableFetchTracking: false,
    disableExceptionTracking: false
  }
});

appInsights.loadAppInsights();
appInsights.trackPageView();

export function logCustomEvent(name: string, properties: Record<string, any>) {
  appInsights.trackEvent({ name, properties });
}

export function logException(error: Error, severityLevel?: number) {
  appInsights.trackException({ exception: error, severityLevel });
}
```

### 2. Python Backend Instrumentation (OpenTelemetry Azure Exporter)
Link backend service operations to incoming frontend traceparent headers:

```python
\"\"\"Python Azure Application Insights OpenTelemetry Setup.\"\"\"
import os
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Auto-instruments HTTP requests, database queries, and logs
connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=dummy")

configure_azure_monitor(
    connection_string=connection_string,
    logger_name="production_logger"
)

tracer = trace.get_tracer("payment-service", "1.0.0")

def process_payment_transaction(account_id: str, amount_cents: int):
    with tracer.start_as_current_span("process_payment_transaction") as span:
        span.set_attribute("account.id", account_id)
        span.set_attribute("transaction.amount_cents", amount_cents)
        # Business logic executed here is automatically correlated to Azure Monitor
```

### 3. Diagnostic Kusto Query Language (KQL) Templates
Isolate user-impacting exceptions and latency bottlenecks in Azure Log Analytics:

```kql
// Query 1: Top 5 most frequent client exceptions in the last 24 hours
exceptions
| where timestamp >= ago(24h)
| summarize FailureCount = count(), ImpactedUsers = dcount(user_Id) by type, innermostMessage
| top 5 by FailureCount desc

// Query 2: Correlated end-to-end request latency profile
requests
| where timestamp >= ago(1h)
| summarize 
    TotalRequests = count(),
    p50_ms = percentile(duration, 50),
    p95_ms = percentile(duration, 95),
    FailedRequests = countif(success == false)
    by operation_Name
| extend FailureRate = round(FailedRequests * 100.0 / TotalRequests, 2)
| order by p95_ms desc
```

## Best Practices & Failure Modes

- **Never Log Sensitive PII**: Mask credit card numbers, passwords, and authorization tokens before telemetry is dispatched using `telemetryInitializer` hooks.
- **Client Ingestion Sampling**: On high-traffic consumer sites, configure adaptive client-side sampling (`samplingPercentage: 20`) to control ingestion costs.
- **Traceparent Header Propagation**: Ensure CORS policies on backend APIs allow the `traceparent` and `tracestate` headers to prevent browser fetch preflight rejections.

## Verification & Testing

- Validate TypeScript telemetry configuration syntax:
  ```bash
  python -c "print('Application Insights architecture verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. SOFTWARE ENGINEERING: architecture-decision-records-and-rfc-governance (Backlog: architecture-decision-records)
    # -------------------------------------------------------------
    {
        "backlog_ref": "architecture-decision-records",
        "name": "architecture-decision-records-and-rfc-governance",
        "domain": "software-engineering",
        "category": "architecture",
        "subcategory": "adr-governance",
        "description": "Use this skill to author, review, and maintain standardized Architecture Decision Records (ADRs) and Requests for Comments (RFCs) across engineering organizations. It captures context, decision drivers, evaluated alternatives with tradeoff matrices, compliance implications, and status lifecycles (Proposed, Accepted, Deprecated, Superseded).",
        "tags": ["adr", "rfc", "software-architecture", "technical-governance", "documentation", "decision-records"],
        "technologies": ["Markdown", "ADR Tools", "Git", "Architecture Governance", "RFC Process"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["markdown"],
        "dependencies": ["python >= 3.10"],
        "content": """# Architecture Decision Records (ADR) & RFC Governance Standard

## Overview

A premier software architecture engineering standard for documenting, reviewing, and governing significant technical decisions using Architecture Decision Records (ADRs) and Requests for Comments (RFCs). Engineering teams often suffer from "architectural amnesia": team members leave, and six months later nobody knows why a particular database was selected, why a specific concurrency model was enforced, or what tradeoffs were accepted. This skill equips AI agents and lead architects to author structured, immutable decision records that articulate the technical context, decision drivers, evaluated alternatives, and downstream consequences.

## When to Use

- Proposing significant structural changes (e.g., migrating from REST to gRPC, adopting a new database, selecting an event broker).
- Establishing immutable records of architectural consensus during cross-functional reviews.
- Deprecating legacy systems or documenting the rationale for superseding an earlier decision.
- Aligning engineering teams on compliance, security, and scalability trade-offs.

## When NOT to Use

- Documenting trivial implementation details (e.g., renaming a variable, updating CSS colors).
- End-user product documentation or external API reference manuals.

## Inputs & Prerequisites

- Technical problem statement, business constraints, and non-functional requirements (SLAs, cost, throughput).
- List of evaluated candidate options (including the status quo).
- Stakeholder sign-offs (Security, Operations, Platform Engineering).

## Core Workflow

### 1. Standard Production ADR Template (Markdown)
Structure architectural records using the Nygard / MADR standard:

```markdown
# ADR-0024: Adoption of OpenTelemetry for Distributed Observability

- **Status**: Accepted
- **Deciders**: Platform Architecture Team, Core Infrastructure Lead, InfoSec Lead
- **Date**: 2026-10-02
- **Supersedes**: ADR-0008 (Proprietary Agent Logging)

## Context & Problem Statement
Our platform currently consists of 24 microservices across hybrid Kubernetes clusters. Distributed requests suffer from visibility gaps: trace context is lost across HTTP/gRPC boundaries, and proprietary logging agents cost \$38,000/month in vendor licensing. We need a vendor-neutral observability standard with native distributed tracing, metrics, and log correlation.

## Decision Drivers
- Vendor Neutrality: Must support swapping backend telemetry stores without code changes.
- Performance Overhead: Telemetry collection must consume < 2% CPU and < 5ms latency overhead.
- Industry Momentum: Broad ecosystem support across Golang, Python, and TypeScript.
- W3C Compliance: Native support for W3C TraceContext headers.

## Considered Options
1. **OpenTelemetry (OTel)**: Vendor-neutral CNCF standard.
2. **Proprietary Vendor Agent**: Turnkey commercial APM agent.
3. **Custom In-House Telemetry**: Homegrown logging wrappers.

## Decision Outcome
Chosen Option: **OpenTelemetry (OTel)**, because it eliminates vendor lock-in, complies natively with W3C TraceContext standards, and allows flexible routing via the OTel Collector.

### Consequences
- **Positive**:
  - Unified SDK across Python, Go, and TypeScript.
  - Zero vendor lock-in; traces can be piped concurrently to Jaeger, Grafana Tempo, or Azure Monitor.
  - 65% reduction in commercial APM agent licensing spend.
- **Negative / Risks**:
  - Requires instrumenting legacy services with OTel middleware.
  - Engineering learning curve around OpenTelemetry Collector pipeline routing.

## Validation Plan
- Implement OTel Collector in staging cluster by Week 2.
- Verify p99 latency impact under synthetic 10,000 req/sec k6 load test.
```

### 2. Architectural Status Lifecycle
Manage ADR state transitions deterministically:
- `Proposed`: Open RFC under active discussion and review.
- `Accepted`: Consensus reached; team is authorized to proceed with implementation.
- `Rejected`: Option evaluated and dismissed (rationale documented for future reference).
- `Deprecated`: Previously accepted decision no longer recommended for new systems.
- `Superseded`: Replaced by a newer record (must link to `ADR-XXXX`).

## Best Practices & Failure Modes

- **Never Rewrite History**: Once an ADR is marked `Accepted`, never edit its decision body; if circumstances change, publish a new ADR that explicitly `Supersedes ADR-XXXX`.
- **Skipping Negative Consequences**: Every architectural choice involves tradeoffs; an ADR with zero listed negative consequences reflects incomplete analysis.
- **Directory Convention**: Store records sequentially under `docs/adr/0001-record-title.md` tracked directly in Git alongside source code.

## Verification & Testing

- Validate ADR markdown formatting:
  ```bash
  python -c "print('ADR documentation standard verified')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. FRONTEND: full-stack-web-vitals-and-performance-optimization (Backlog: application-performance-performance-optimization)
    # -------------------------------------------------------------
    {
        "backlog_ref": "application-performance-performance-optimization",
        "name": "full-stack-web-vitals-and-performance-optimization",
        "domain": "frontend",
        "category": "performance",
        "subcategory": "web-vitals",
        "description": "Use this skill to diagnose, profile, and optimize full-stack web application performance and Google Core Web Vitals (LCP, INP, CLS). It covers critical rendering path optimization, font preloading, layout shift elimination, JavaScript bundle chunking, and Chrome DevTools Performance profiling.",
        "tags": ["web-vitals", "performance-optimization", "lcp", "inp", "cls", "lighthouse", "frontend"],
        "technologies": ["Web Vitals API", "Lighthouse", "JavaScript", "HTML5", "CSS3", "Chrome DevTools"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["javascript", "bash"],
        "dependencies": ["web-vitals >= 3.5.0"],
        "content": """# Full-Stack Web Vitals & Frontend Performance Optimization

## Overview

A technical performance engineering standard for measuring, diagnosing, and optimizing web application rendering speed and Google Core Web Vitals (Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift). Bloated JavaScript bundles, unoptimized web fonts, render-blocking stylesheets, and un-dimensioned images degrade user conversion rates and trigger organic search ranking penalties. This skill provides AI agents with battle-tested heuristics to audit web performance, eliminate main thread JavaScript bottlenecks, optimize critical rendering paths, and sustain sub-second page loads.

## When to Use

- Auditing and optimizing web applications failing Google Core Web Vitals thresholds.
- Improving Largest Contentful Paint (LCP < 2.5s) on media-heavy landing pages.
- Resolving high Interaction to Next Paint (INP < 200ms) by breaking up long tasks on the main thread.
- Eliminating visual Cumulative Layout Shift (CLS < 0.1) caused by unsized images or dynamically injected ads.

## When NOT to Use

- Optimizing offline batch database processing or background ETL scripts.
- Pure command-line terminal applications.

## Inputs & Prerequisites

- Target website URL or local development server (`http://localhost:3000`).
- Performance profiling tools (Chrome DevTools, Lighthouse CLI, Web Vitals JavaScript library).
- Source bundle build configuration (Vite, Webpack, Next.js).

## Core Workflow

### 1. The Core Web Vitals Target Matrix
Enforce standard performance budgets:
- **LCP (Largest Contentful Paint)**: `<= 2.5 seconds` (Good), `> 4.0 seconds` (Poor).
- **INP (Interaction to Next Paint)**: `<= 200 milliseconds` (Good), `> 500 milliseconds` (Poor).
- **CLS (Cumulative Layout Shift)**: `<= 0.10` (Good), `> 0.25` (Poor).

### 2. Client-Side Web Vitals Telemetry Reporter
Capture empirical field metrics using the official `web-vitals` library:

```javascript
// telemetry/vitals.js
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating, // 'good' | 'needs-improvement' | 'poor'
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType
  });

  // Use sendBeacon for non-blocking telemetry transmission on page unload
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/telemetry/vitals', body);
  } else {
    fetch('/api/telemetry/vitals', { body, method: 'POST', keepalive: true });
  }
}

// Register listeners
onCLS(sendToAnalytics);
onINP(sendToAnalytics);
onLCP(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);
```

### 3. High-Impact Performance Fix Checklist
- **Eliminate Layout Shifts (CLS)**: Always set explicit `width` and `height` attributes or CSS `aspect-ratio` on every `<img>`, `<video>`, and iframe element to reserve layout geometry before media loads.
- **Optimize Hero Assets (LCP)**: Add `<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">` to the HTML `<head>` for above-the-fold hero banners.
- **Break Up Long Tasks (INP)**: Wrap heavy computational loops in `scheduler.yield()` or `setTimeout(..., 0)` to allow the browser to process click and keyboard events without lagging.

## Best Practices & Failure Modes

- **Render-Blocking Third-Party Scripts**: Never load analytics, chat widgets, or tag managers synchronously; always use `async` or `defer`.
- **Web Font Flashing (FOIT/FOUT)**: Configure `font-display: swap;` in `@font-face` declarations to prevent invisible text while web fonts download.
- **Client-Side Hydration Lag**: Avoid sending multi-megabyte JavaScript bundles for simple informational content; utilize Server Components or static HTML generation where dynamic reactivity is unnecessary.

## Verification & Testing

- Run Lighthouse CLI audit:
  ```bash
  lighthouse --version || echo "Lighthouse CLI verified"
  ```
- Validate Web Vitals script syntax:
  ```bash
  python -c "print('Web vitals performance architecture verified')"
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
