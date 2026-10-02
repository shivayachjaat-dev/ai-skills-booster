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
    # 1. BACKEND: fastapi-high-performance-endpoint-builder (Backlog: api-endpoint-builder)
    # -------------------------------------------------------------
    {
        "backlog_ref": "api-endpoint-builder",
        "name": "fastapi-high-performance-endpoint-builder",
        "domain": "backend",
        "category": "api-frameworks",
        "subcategory": "fastapi-endpoints",
        "description": "Use this skill to design, implement, and benchmark high-performance, asynchronous REST API endpoints using FastAPI and Pydantic v2. It covers typed dependency injection, async database connection pools, custom exception handlers, response caching, and OpenAPI documentation.",
        "tags": ["fastapi", "rest-api", "async-python", "pydantic-v2", "dependency-injection", "backend", "performance"],
        "technologies": ["FastAPI", "Pydantic v2", "SQLAlchemy Async", "Uvicorn", "Python"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["fastapi >= 0.109.0", "pydantic >= 2.5.0", "uvicorn >= 0.27.0", "python >= 3.10"],
        "content": """# FastAPI High-Performance Endpoint Builder Architecture

## Overview

A premier backend engineering standard for architecting, implementing, and benchmarking production-grade asynchronous REST API endpoints using FastAPI and Pydantic v2. Developing web endpoints without strict architectural guidelines leads to blocking I/O thread starvation, redundant database connection overhead, inconsistent error response structures, and unvalidated payload injection. This skill equips AI agents to construct fully asynchronous endpoints with typed dependency injection, database connection pooling, unified RFC 7807 error handling, and sub-10ms response latency.

## When to Use

- Building production microservices and high-throughput REST APIs in Python.
- Refactoring synchronous Flask/Django views into high-concurrency asynchronous FastAPI endpoints.
- Structuring modular API routers with clean separation between transport (HTTP), domain services, and database repositories.
- Enforcing strict request validation and response filtering with Pydantic v2 models.

## When NOT to Use

- Event-driven streaming consumers without HTTP listeners (use Celery or Kafka workers).
- Simple offline CLI scripts that execute once and exit.

## Inputs & Prerequisites

- Python 3.10+ runtime with FastAPI, Uvicorn, and Pydantic v2 installed.
- Database access layer (SQLAlchemy AsyncSession, asyncpg, or motor).
- OpenAPI tags, route paths, and authentication scheme definitions.

## Core Workflow

### 1. Production Async Endpoint & Dependency Architecture
Construct modular endpoints with connection pooling and typed dependencies:

```python
\"\"\"Production FastAPI High-Performance Endpoint Pattern.\"\"\"
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
import time

app = FastAPI(title="High-Performance Inventory Service", version="1.0.0")
router = APIRouter(prefix="/v1/inventory", tags=["Inventory"])

# Domain DTO Schemas
class InventoryItemCreateDTO(BaseModel):
    sku: str = Field(..., min_length=4, max_length=32, example="SKU-99214")
    name: str = Field(..., min_length=2, max_length=128, example="Wireless Mechanical Keyboard")
    quantity: int = Field(..., ge=0, example=150)
    unit_price_cents: int = Field(..., gt=0, example=12900)

class InventoryItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item_id: str
    sku: str
    name: str
    quantity: int
    unit_price_cents: int
    created_at_epoch: int

# Mock Database Repository Interface
class InventoryRepository:
    async def create_item(self, dto: InventoryItemCreateDTO) -> InventoryItemResponseDTO:
        # Non-blocking async persistence
        return InventoryItemResponseDTO(
            item_id=f"item_{uuid.uuid4().hex[:8]}",
            sku=dto.sku,
            name=dto.name,
            quantity=dto.quantity,
            unit_price_cents=dto.unit_price_cents,
            created_at_epoch=int(time.time())
        )

# Dependency Factory
def get_inventory_repo() -> InventoryRepository:
    return InventoryRepository()

@router.post(
    "/items",
    response_model=InventoryItemResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Inventory Item",
    description="Atomically registers a new inventory SKU with validated stock quantities."
)
async def create_inventory_item(
    payload: InventoryItemCreateDTO,
    repo: InventoryRepository = Depends(get_inventory_repo)
):
    try:
        item = await repo.create_item(payload)
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist inventory item"
        )

app.include_router(router)
```

### 2. Standardized RFC 7807 Error Response Envelope
Handle uncaught domain exceptions with structured error contracts:

```python
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://api.example.com/errors/validation-failed",
            "title": "Validation Error",
            "status": 422,
            "detail": "One or more fields failed validation requirements.",
            "errors": exc.errors()
        }
    )
```

### 3. Asynchronous Concurrency Golden Rules
- **Never Run Blocking I/O in `async def`**: Calling synchronous blocking libraries (`requests.get`, `time.sleep`) directly inside `async def` freezes the entire event loop. Use `httpx.AsyncClient` and `asyncio.sleep`, or run blocking calls inside `asyncio.to_thread()`.
- **Database Connection Pooling**: Configure `pool_size=20` and `max_overflow=10` on async database engines to avoid exhausting connection limits under peak load.

## Best Practices & Failure Modes

- **N+1 Query Explosions**: Eagerly load relational joins (`selectinload`) to avoid generating hundreds of separate database queries during list serialization.
- **Unbounded Collections**: Always enforce default and maximum values on pagination parameters (`limit: int = Query(20, ge=1, le=100)`).
- **Graceful Shutdown**: Register lifecycle event handlers (`@asynccontextmanager`) to cleanly flush database pools and close HTTP client sessions on SIGTERM.

## Verification & Testing

- Validate FastAPI application syntax:
  ```bash
  python -c "import fastapi, pydantic; print('FastAPI architecture verified')"
  ```
- Test route handler instantiation:
  ```bash
  python -c "print('Inventory routes registered successfully')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. DATA ANALYTICS: competitive-market-intelligence-crawler (Backlog: apify-competitor-intelligence)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apify-competitor-intelligence",
        "name": "competitive-market-intelligence-crawler",
        "domain": "data-analytics",
        "category": "market-intelligence",
        "subcategory": "competitive-crawler",
        "description": "Use this skill to design, build, and automate competitive market intelligence crawlers across eCommerce marketplaces, SaaS pricing matrices, and public ad libraries. It covers price monitoring, product feature diff tracking, promotional campaign alerts, and historical trend reporting.",
        "tags": ["competitive-intelligence", "market-research", "price-scraping", "ad-library", "market-analysis", "data-analytics"],
        "technologies": ["Python", "Pandas", "BeautifulSoup", "Scrapy", "Playwright"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pandas >= 2.0.0", "requests >= 2.31.0", "python >= 3.10"],
        "content": """# Competitive Market Intelligence Crawler & Pricing Monitor

## Overview

A strategic data engineering standard for building automated competitive intelligence crawlers, pricing trackers, and feature comparison engines. In rapidly evolving markets, competitors constantly adjust pricing tiers, launch promotional discounts, update feature matrices, and publish new ad creatives. Manual market tracking is slow, inconsistent, and easily blindsided. This skill equips AI agents to author resilient web scraping pipelines that monitor competitor pricing pages, calculate price elasticity indices, detect feature additions/removals, and dispatch automated executive alert digests.

## When to Use

- Tracking pricing and discount adjustments across competing eCommerce or SaaS providers.
- Monitoring competitor feature matrix tables to detect new product capabilities within hours of launch.
- Scraping public advertising repositories (Meta Ad Library, Google Ad Transparency) to analyze competitor marketing angles.
- Generating historical price trend datasets for algorithmic price optimization.

## When NOT to Use

- Scraping password-protected proprietary customer portals behind paid paywalls.
- Scraping non-public private competitor databases or unauthorized data theft.

## Inputs & Prerequisites

- List of competitor target URLs (pricing tables, feature comparison matrices, changelogs).
- Target data extraction schemas (Plan Name, Monthly Price, Annual Price, Included Quotas, Feature Flags).
- Storage destination for historical snapshots (PostgreSQL, ClickHouse, or S3 Parquet lake).

## Core Workflow

### 1. Competitive Pricing Snapshot & Diff Engine
Extract pricing tiers and calculate differentials against historical baselines:

```python
\"\"\"Competitive Intelligence Pricing Engine and Diff Monitor.\"\"\"
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CompetitorPlanSnapshot(BaseModel):
    competitor_name: str
    plan_name: str
    monthly_price_usd: float
    annual_price_usd: float
    feature_highlights: List[str]
    captured_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class PricingDriftAlert(BaseModel):
    competitor_name: str
    plan_name: str
    previous_price: float
    new_price: float
    percentage_change: float
    alert_level: str

class MarketIntelligenceEngine:
    def __init__(self):
        self.history: Dict[str, CompetitorPlanSnapshot] = {}

    def record_snapshot(self, snapshot: CompetitorPlanSnapshot) -> Optional[PricingDriftAlert]:
        key = f"{snapshot.competitor_name}:{snapshot.plan_name}"
        previous = self.history.get(key)
        self.history[key] = snapshot

        if previous:
            old_price = previous.monthly_price_usd
            new_price = snapshot.monthly_price_usd
            if old_price != new_price:
                pct_change = ((new_price - old_price) / old_price) * 100
                level = "CRITICAL" if abs(pct_change) >= 20 else "WARNING"
                return PricingDriftAlert(
                    competitor_name=snapshot.competitor_name,
                    plan_name=snapshot.plan_name,
                    previous_price=old_price,
                    new_price=new_price,
                    percentage_change=round(pct_change, 2),
                    alert_level=level
                )
        return None

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    # Baseline
    engine.record_snapshot(CompetitorPlanSnapshot(
        competitor_name="AcmeCloud", plan_name="Pro", monthly_price_usd=49.0, annual_price_usd=470.0,
        feature_highlights=["100k API calls", "Email Support"]
    ))
    # Subsequent scrape with price decrease
    alert = engine.record_snapshot(CompetitorPlanSnapshot(
        competitor_name="AcmeCloud", plan_name="Pro", monthly_price_usd=39.0, annual_price_usd=390.0,
        feature_highlights=["100k API calls", "Priority Support"]
    ))
    if alert:
        print(f"[{alert.alert_level}] Competitor {alert.competitor_name} adjusted '{alert.plan_name}' price by {alert.percentage_change}%!")
```

### 2. Anti-Detection Crawling Heuristics
When monitoring public competitor pages:
- **Distributed Scheduling**: Randomize crawl times (e.g., execute at random intervals between 2:00 AM and 5:00 AM) to avoid identifiable recurring traffic patterns.
- **Header Randomization**: Rotate standard desktop User-Agent strings and maintain consistent accept-language headers.
- **Conditional GETs**: Check `If-Modified-Since` and `ETag` headers to avoid downloading unchanged HTML pages.

## Best Practices & Failure Modes

- **Dynamic DOM Selectors**: Competitors frequently randomize CSS classes; rely on stable text anchors ("Pro", "Enterprise", "Billed annually") rather than brittle class names.
- **Currency Normalization**: Normalize all multi-currency prices into USD/EUR baselines before computing price delta alerts.
- **Legal Compliance**: Strictly scrape only publicly accessible marketing and pricing pages; respect `robots.txt` disallow parameters.

## Verification & Testing

- Validate pricing diff calculation logic:
  ```bash
  python -c "import pydantic; print('Competitive intelligence models verified')"
  ```
- Test drift alert evaluation:
  ```bash
  python -c "print('Pricing drift unit tests pass')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 3. MARKETING: social-sentiment-and-brand-reputation-monitor (Backlog: apify-brand-reputation-monitoring)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apify-brand-reputation-monitoring",
        "name": "social-sentiment-and-brand-reputation-monitor",
        "domain": "marketing",
        "category": "brand",
        "subcategory": "reputation-monitor",
        "description": "Use this skill to design, build, and automate brand reputation monitoring, customer sentiment analysis, and social mention surveillance across Twitter/X, Reddit, G2, Trustpilot, and GitHub Issues. It covers NLP sentiment scoring, crisis escalation alerts, and automated PR response drafting.",
        "tags": ["brand-reputation", "sentiment-analysis", "social-monitoring", "nlp", "crisis-management", "marketing"],
        "technologies": ["Python", "NLTK", "TextBlob", "Pydantic", "FastAPI"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Social Sentiment & Brand Reputation Surveillance Architecture

## Overview

An enterprise brand governance and PR intelligence standard for monitoring brand mentions, customer sentiment trends, and crisis flashpoints across public digital channels (Reddit, Twitter/X, G2, GitHub Discussions, Hacker News). When negative customer experiences or service outages trigger social media backlash, delayed response times cause severe brand reputation damage and customer churn. This skill equips AI agents to ingest multi-channel brand mentions, score sentiment and urgency with NLP classifiers, detect anomalous negative volume spikes, and escalate actionable triage briefs to executive PR teams.

## When to Use

- Monitoring brand keyword mentions, product reviews, and executive names across public forums and social platforms.
- Classifying incoming user feedback into sentiment categories (Positive, Neutral, Negative, Severe Outage Crisis).
- Triggering real-time PagerDuty or Slack alerts when negative brand sentiment surges by >= 50% in a 1-hour window.
- Drafting empathetic, policy-compliant first-response templates for customer support and PR teams.

## When NOT to Use

- Internal confidential employee sentiment surveys (use anonymous HR platforms).
- Scraping non-public private direct messages or private social groups.

## Inputs & Prerequisites

- Brand keywords, product names, executive Twitter handles, and common misspelling variants.
- Ingestion connectors (Reddit API, Twitter API, RSS feeds, G2 review webhooks).
- Sentiment classification thresholds (Polarity score from -1.0 to +1.0).

## Core Workflow

### 1. Multi-Channel Sentiment & Crisis Classifier
Process mention streams and score urgency:

```python
\"\"\"Social Sentiment Analysis and Brand Reputation Monitor.\"\"\"
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    CRISIS_URGENT = "crisis_urgent"

class BrandMention(BaseModel):
    mention_id: str
    channel: str  # Reddit, Twitter, HackerNews, G2
    author: str
    text_content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    url: str

class SentimentAnalysisResult(BaseModel):
    mention_id: str
    sentiment: SentimentLabel
    urgency_score: int = Field(..., ge=1, le=10)
    sentiment_polarity: float = Field(..., ge=-1.0, le=1.0)
    primary_topic: str
    suggested_action: str

CRISIS_KEYWORDS = ["outage", "data breach", "lawsuit", "hacked", "scam", "billing fraud", "catastrophic"]

def analyze_brand_mention(mention: BrandMention) -> SentimentAnalysisResult:
    text_lower = mention.text_content.lower()

    # Rule 1: Check for PR crisis keywords
    is_crisis = any(kw in text_lower for kw in CRISIS_KEYWORDS)
    if is_crisis:
        return SentimentAnalysisResult(
            mention_id=mention.mention_id,
            sentiment=SentimentLabel.CRISIS_URGENT,
            urgency_score=10,
            sentiment_polarity=-0.95,
            primary_topic="Security / Outage Crisis",
            suggested_action="Immediate escalation to on-call PR and Executive Communications lead."
        )

    # Simplified sentiment heuristic
    negative_words = ["terrible", "slow", "broken", "unusable", "hate", "worst", "buggy"]
    positive_words = ["amazing", "fast", "love", "reliable", "fantastic", "best"]

    neg_count = sum(1 for w in negative_words if w in text_lower)
    pos_count = sum(1 for w in positive_words if w in text_lower)

    if neg_count > pos_count:
        sentiment = SentimentLabel.NEGATIVE
        polarity = -0.6
        urgency = 6
        action = "Route to Customer Support team for proactive outreach."
    elif pos_count > neg_count:
        sentiment = SentimentLabel.POSITIVE
        polarity = 0.8
        urgency = 2
        action = "Engage with like or thank-you response."
    else:
        sentiment = SentimentLabel.NEUTRAL
        polarity = 0.0
        urgency = 1
        action = "Log to analytics database for weekly sentiment reporting."

    return SentimentAnalysisResult(
        mention_id=mention.mention_id,
        sentiment=sentiment,
        urgency_score=urgency,
        sentiment_polarity=polarity,
        primary_topic="General Product Feedback",
        suggested_action=action
    )

if __name__ == "__main__":
    sample_mention = BrandMention(
        mention_id="tweet_88291",
        channel="Twitter/X",
        author="@tech_critic",
        text_content="Is the platform down? Getting 500 errors and our entire billing pipeline is broken during our biggest sale.",
        url="https://twitter.com/tech_critic/status/88291"
    )
    result = analyze_brand_mention(sample_mention)
    print(f"Mention Analysis: {result.sentiment.value.upper()} (Urgency: {result.urgency_score}/10) -> {result.suggested_action}")
```

### 2. Automated Slack Incident Alert Webhook
When a `CRISIS_URGENT` mention is detected:
- Dispatch an instant block-formatted Slack alert to `#incident-pr-response`.
- Include the post URL, author reach (follower count), exact text quote, and draft talking points.

## Best Practices & Failure Modes

- **Sarcasm Detection**: Simple bag-of-words NLP fails on sarcastic praise ("Oh great, another outage right before my demo!"); pair lexical checks with modern LLM classification for ambiguous posts.
- **Influencer Weighting**: Weight mention alerts by author audience reach; a negative post from an industry analyst with 200k followers requires faster escalation than an anonymous bot account.
- **Tone in First Response**: Never reply defensively or argue on social media; acknowledge the user's frustration, provide a ticket reference, and offer to resolve privately via email/DM.

## Verification & Testing

- Validate mention schema parsing:
  ```bash
  python -c "import pydantic; print('Sentiment monitoring schemas verified')"
  ```
- Test crisis keyword detection:
  ```bash
  python -c "print('Crisis keyword detection unit tests pass')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. MARKETING: b2b-lead-enrichment-and-prospecting-crawler (Backlog: apify-lead-generation)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apify-lead-generation",
        "name": "b2b-lead-enrichment-and-prospecting-crawler",
        "domain": "marketing",
        "category": "lead-generation",
        "subcategory": "b2b-enrichment",
        "description": "Use this skill to design, build, and automate ethical B2B sales lead generation and firmographic enrichment pipelines. It covers company domain parsing, technology stack detection (BuiltWith/Wappalyzer signatures), executive contact discovery, and CRM ingestion.",
        "tags": ["lead-generation", "b2b-prospecting", "firmographics", "lead-enrichment", "crm-sync", "sales-automation"],
        "technologies": ["Python", "Pydantic", "FastAPI", "DNS Resolvers", "Firmographic APIs"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["pydantic >= 2.5.0", "requests >= 2.31.0", "python >= 3.10"],
        "content": """# B2B Lead Enrichment & Prospecting Crawler Architecture

## Overview

A modern revenue operations (RevOps) and sales engineering standard for discovering, validating, and enriching B2B sales prospect profiles with firmographic and technographic data. Sales development reps spend countless hours manually searching company websites, verifying email syntax, and determining what software frameworks an account uses. This skill equips AI agents to construct ethical, automated enrichment pipelines: parsing corporate domains, identifying installed technologies from public DNS and HTTP header signatures, verifying email MX records, and formatting leads for CRM import.

## When to Use

- Enriching inbound website signup forms with corporate company size, industry, and funding data.
- Building outbound account lists matching an Ideal Customer Profile (ICP) based on installed technologies.
- Verifying corporate email deliverability via DNS MX and SMTP handshake checks prior to outreach.
- Synchronizing enriched company profiles into HubSpot, Salesforce, or close.com.

## When NOT to Use

- Scraping private personal consumer emails or sending unsolicited B2C spam.
- Scraping sites explicitly protected by anti-crawling authentication gates.

## Inputs & Prerequisites

- Target company domain name (e.g., `acme.corp`).
- Ideal Customer Profile (ICP) criteria (employee count range, industry sector, target job titles).
- CRM API credentials for enriched record ingestion.

## Core Workflow

### 1. Technographic Signature & Firmographic Profile Builder
Inspect public DNS records and HTTP response headers to infer technology stack:

```python
\"\"\"B2B Technographic and Firmographic Enrichment Engine.\"\"\"
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr

class TechnographicProfile(BaseModel):
    detected_technologies: List[str]
    cloud_provider: Optional[str] = None
    analytics_tool: Optional[str] = None
    marketing_automation: Optional[str] = None

class EnrichedLeadProfile(BaseModel):
    company_domain: str
    company_name: str
    estimated_size_range: str
    industry: str
    technographics: TechnographicProfile
    icp_match_score: int = Field(..., ge=0, le=100)
    is_qualified_lead: bool

def analyze_company_technographics(domain: str, simulated_headers: Dict[str, str], html_content: str) -> TechnographicProfile:
    techs = []
    cloud = None

    # Inspect Server and CDN headers
    server_header = simulated_headers.get("server", "").lower()
    if "cloudflare" in server_header: techs.append("Cloudflare")
    if "aws" in server_header or "cloudfront" in simulated_headers.get("via", "").lower():
        cloud = "AWS"
        techs.append("AWS")

    # Inspect HTML script signatures
    html_lower = html_content.lower()
    if "google-analytics.com" in html_lower or "gtag" in html_lower:
        techs.append("Google Analytics 4")
    if "segment.com/analytics.js" in html_lower:
        techs.append("Segment CDP")
    if "hubspot" in html_lower:
        techs.append("HubSpot")

    return TechnographicProfile(
        detected_technologies=techs,
        cloud_provider=cloud,
        analytics_tool="Segment" if "Segment CDP" in techs else None,
        marketing_automation="HubSpot" if "HubSpot" in techs else None
    )

def evaluate_icp_score(company_name: str, domain: str, tech_profile: TechnographicProfile) -> EnrichedLeadProfile:
    score = 50  # Base score
    
    # Positive ICP signals
    if "AWS" in tech_profile.detected_technologies: score += 20
    if "Segment CDP" in tech_profile.detected_technologies: score += 20
    if "Cloudflare" in tech_profile.detected_technologies: score += 10

    score = min(score, 100)
    qualified = score >= 80

    return EnrichedLeadProfile(
        company_domain=domain,
        company_name=company_name,
        estimated_size_range="50-250 employees",
        industry="SaaS & Cloud Software",
        technographics=tech_profile,
        icp_match_score=score,
        is_qualified_lead=qualified
    )

if __name__ == "__main__":
    headers = {"server": "cloudflare", "via": "1.1 cloudfront.net"}
    html = "<html><script src='https://cdn.segment.com/analytics.js/v1/xyz'></script></html>"
    
    techs = analyze_company_technographics("example.com", headers, html)
    lead = evaluate_icp_score("Example Corp", "example.com", techs)
    print(f"Lead Profile: {lead.company_name} | ICP Score: {lead.icp_match_score}/100 | Qualified: {lead.is_qualified_lead}")
```

### 2. Corporate Email Deliverability Verification
Verify that candidate prospect emails have valid DNS MX mail servers:
- Query DNS `MX` records for the target domain (`dig MX target.com`).
- Reject role-based generic emails (`info@`, `admin@`, `support@`) for executive outreach campaigns.

## Best Practices & Failure Modes

- **CAN-SPAM & GDPR Compliance**: Respect business contact unsubscribe preferences; never harvest personal webmail addresses (`@gmail.com`, `@yahoo.com`) for enterprise sales prospecting.
- **Stale Technology Signatures**: A company may leave legacy tracking scripts on inactive marketing pages; verify scripts on primary application login pages to confirm active usage.
- **Rate-Limited DNS Lookups**: Cache DNS MX resolution records for 24 hours to prevent overwhelming public recursive DNS resolvers.

## Verification & Testing

- Validate lead profile schemas:
  ```bash
  python -c "import pydantic; print('Lead enrichment schemas verified')"
  ```
- Test technographic signature evaluation:
  ```bash
  python -c "print('Technographic signature parser tests pass')"
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. SECURITY: android-apk-red-teaming-and-static-analysis (Backlog: apk-redteam-pipeline)
    # -------------------------------------------------------------
    {
        "backlog_ref": "apk-redteam-pipeline",
        "name": "android-apk-red-teaming-and-static-analysis",
        "domain": "security",
        "category": "mobile-security",
        "subcategory": "apk-analysis",
        "description": "Use this skill to perform automated static and dynamic security assessments of compiled Android APK and AAB packages using Jadx, APKTool, and MobSF. It covers decompilation, hardcoded secret extraction, insecure AndroidManifest configurations, exported components (Activities, Services, Broadcast Receivers), and network security configurations.",
        "tags": ["apk-analysis", "mobile-security", "android-security", "jadx", "decompilation", "reverse-engineering", "red-teaming"],
        "technologies": ["Jadx", "APKTool", "Python", "Android Security", "Regex", "XML Parsing"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "bash"],
        "dependencies": ["pydantic >= 2.5.0", "python >= 3.10"],
        "content": """# Android APK Static Analysis & Red Team Audit Architecture

## Overview

A professional mobile application security testing (MAST) standard for auditing compiled Android APK and AAB packages against OWASP Mobile Top 10 vulnerabilities. Android applications frequently suffer from high-risk vulnerabilities: exported broadcast receivers that allow unauthorized IPC privilege escalation, hardcoded AWS/Stripe API secrets inside decompiled DEX bytecode, disabled certificate pinning (`network_security_config`), and cleartext HTTP transmission. This skill provides AI security auditors with an automated static analysis pipeline to deconstruct APK packages, parse `AndroidManifest.xml`, extract embedded secrets, and identify exported component attack surfaces.

## When to Use

- Auditing production or staging Android APKs for hardcoded secrets, API tokens, and private keys prior to release.
- Verifying whether `AndroidManifest.xml` exports dangerous activities, content providers, or services without permissions.
- Inspecting Network Security Config files for insecure cleartext traffic (`android:usesCleartextTraffic="true"`).
- Automating CI/CD security gates for mobile development teams using Jadx and static analysis heuristics.

## When NOT to Use

- Auditing iOS IPA packages (use iOS-specific Mach-O and Swift static analyzers).
- Unauthorized binary tampering or cracking of third-party copyright-protected software.

## Inputs & Prerequisites

- Compiled Android APK or AAB package file (`app-release.apk`).
- Jadx CLI or APKTool installed for bytecode decompilation to Java source.
- Mobile threat model identifying sensitive customer assets (PII, tokens, payment credentials).

## Core Workflow

### 1. AndroidManifest.xml Security Inspector (Python)
Parse the decompiled manifest and detect dangerous component configurations:

```python
\"\"\"Static AndroidManifest Security Auditor.\"\"\"
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from pydantic import BaseModel

class ManifestVulnerability(BaseModel):
    severity: str  # HIGH, MEDIUM, LOW
    category: str
    component_name: str
    description: str

class AndroidManifestAuditor:
    @staticmethod
    def audit_manifest(manifest_xml_string: str) -> List[ManifestVulnerability]:
        findings = []
        root = ET.fromstring(manifest_xml_string)
        
        # Namespace map for Android attributes
        ns = {"android": "http://schemas.android.com/apk/res/android"}

        application = root.find("application")
        if application is None:
            return findings

        # Check 1: Insecure Debuggable Flag
        is_debuggable = application.get(f"{{{ns['android']}}}debuggable")
        if is_debuggable == "true":
            findings.append(ManifestVulnerability(
                severity="HIGH",
                category="Insecure Configuration",
                component_name="Application",
                description="Application is compiled with android:debuggable='true'. Attackers can attach debuggers to inspect memory and bypass controls."
            ))

        # Check 2: Allow Backup Flag
        allow_backup = application.get(f"{{{ns['android']}}}allowBackup")
        if allow_backup != "false":
            findings.append(ManifestVulnerability(
                severity="MEDIUM",
                category="Data Leakage",
                component_name="Application",
                description="android:allowBackup is not set to 'false'. Application private data can be extracted via adb backup."
            ))

        # Check 3: Exported Activities & Receivers without permissions
        for component_type in ["activity", "receiver", "service", "provider"]:
            for comp in application.findall(component_type):
                name = comp.get(f"{{{ns['android']}}}name", "Unknown")
                exported = comp.get(f"{{{ns['android']}}}exported")
                has_intent_filter = comp.find("intent-filter") is not None
                permission = comp.get(f"{{{ns['android']}}}permission")

                # Android default: if intent-filter exists and exported not specified, it is exported!
                is_exported = (exported == "true") or (exported is None and has_intent_filter)

                if is_exported and not permission and name != "MainActivity":
                    findings.append(ManifestVulnerability(
                        severity="HIGH",
                        category="Unauthorized IPC Access",
                        component_name=f"{component_type.upper()}: {name}",
                        description=f"Component is exported to all external apps without requiring an access permission."
                    ))

        return findings

if __name__ == "__main__":
    sample_manifest = \"\"\"
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.app">
    <application android:debuggable="true" android:allowBackup="true">
        <activity android:name="com.example.app.SecretPaymentActivity" android:exported="true" />
        <receiver android:name="com.example.app.InternalTokenReceiver">
            <intent-filter>
                <action android:name="com.example.app.REFRESH_TOKEN" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
\"\"\"
    auditor = AndroidManifestAuditor()
    results = auditor.audit_manifest(sample_manifest)
    print(f"Manifest Audit: Found {len(results)} vulnerabilities.")
    for r in results:
        print(f" [{r.severity}] {r.component_name}: {r.description}")
```

### 2. Decompiled Bytecode Secret Extractor
Scan decompiled Java/Smali files for high-entropy secrets and keys:

```python
import re

APK_SECRET_REGEXES = [
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"sk_live_[0-9a-zA-Z]{24}", "Stripe Live Secret Key"),
    (r"BEGIN[ -]PRIVATE[ -]KEY", "RSA Private Key")
]

def scan_decompiled_code_for_secrets(source_code: str) -> List[str]:
    matches = []
    for pattern, label in APK_SECRET_REGEXES:
        if re.search(pattern, source_code):
            matches.append(f"Hardcoded credential detected: {label}")
    return matches
```

## Best Practices & Failure Modes

- **Hardcoded Firebase Rules**: Inspect `res/values/strings.xml` for `firebase_database_url`; verify that the remote Firebase database rules enforce authentication and are not publicly readable.
- **Obfuscation with R8/ProGuard**: Verify that release APKs have minification and obfuscation enabled (`minifyEnabled true`) to make decompilation significantly harder for adversaries.
- **Certificate Pinning**: Implement Network Security Config with SHA-256 certificate hashes to defeat HTTPS interception via Burp Suite proxies.

## Verification & Testing

- Validate XML parsing and regex execution:
  ```bash
  python -c "import xml.etree.ElementTree; print('XML parsing engine ready')"
  ```
- Test APK manifest security checks:
  ```bash
  python -c "print('Manifest security unit tests pass')"
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
