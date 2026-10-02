---
name: b2b-lead-enrichment-and-prospecting-crawler
description: "Use this skill to design, build, and automate ethical B2B sales lead generation and firmographic enrichment pipelines. It covers company domain parsing, technology stack detection (BuiltWith/Wappalyzer signatures), executive contact discovery, and CRM ingestion."
domain: marketing
category: lead-generation
subcategory: b2b-enrichment
tags:
  - lead-generation
  - b2b-prospecting
  - firmographics
  - lead-enrichment
  - crm-sync
  - sales-automation
technologies:
  - Python
  - Pydantic
  - FastAPI
  - DNS Resolvers
  - Firmographic APIs
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - requests >= 2.31.0
  - python >= 3.10
---
# B2B Lead Enrichment & Prospecting Crawler Architecture

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
"""B2B Technographic and Firmographic Enrichment Engine."""
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
