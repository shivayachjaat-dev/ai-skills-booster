---
name: geo-audit
description: "Perform full website GEO (Generative Engine Optimization) and SEO audits with parallel subagent delegation for technical search and AI answer engines."
domain: ai-engineering
category: agents
subcategory: geo_audit
tags:
  - ai-engineering
  - agents
  - seo
  - geo
  - answer-engines
technologies:
  - Python
  - HTML Parsing
  - Schema.org JSON-LD
  - Parallel Subagents
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Full Website GEO & SEO Audit Standard

## Overview

The **GEO Audit** skill provides an enterprise standard for auditing websites across both traditional Search Engine Optimization (SEO) and modern Generative Engine Optimization (GEO). While traditional SEO focuses on crawler discoverability (meta tags, canonical URLs, and schema markup), GEO optimizes content for citation and synthesis inside AI answer engines like Google AI Overviews, Perplexity, and ChatGPT.

This skill equips autonomous agents with `GeoSeoAuditor`, utilizing parallel subagent delegation to simultaneously evaluate technical metadata, direct-answer definitions, statistical citation density, and structural semantic hierarchy into a composite index.

```
+------------------------------------------------------------------------+
|                         GEO & SEO Audit Pipeline                       |
|                                                                        |
|  [ Inbound URL / HTML Markup ]                                         |
|                   |                                                    |
|                   v                                                    |
|  [ Parallel Subagent Dispatch ]                                        |
|         |                     |                                        |
|         v                     v                                        |
|  [ Technical SEO Scanner ]  [ Generative Engine Auditor ]              |
|  (Meta, Canonicals, Schema) (Definitions, Stats, Headings)             |
|         |                     |                                        |
|         +----------+----------+                                        |
|                    |                                                   |
|                    v                                                   |
|  [ Composite Scoring & Action Plan ]                                   |
+------------------------------------------------------------------------+
```

## When to Use

- When auditing documentation sites, landing pages, or technical blogs for AI engine visibility.
- When verifying that web pages have proper Schema.org JSON-LD structured data and canonical tags.
- When optimizing content to increase citation frequency in AI Overviews and Perplexity search answers.
- When running automated regression audits in continuous deployment pipelines for web assets.

## When NOT to Use

- Private, internal web dashboards or admin tools that intentionally disallow search engine crawling (`noindex`).
- Native mobile applications or non-HTML API endpoints.

## Core Workflow

### 1. Ingest HTML and Initialize Auditor
Load web page markup and configure the parallel subagent engine:

```python
from geo_seo_auditor import GeoSeoAuditor

auditor = GeoSeoAuditor()
html_payload = """
<html>
  <head>
    <title>Autonomous Systems Engineering</title>
    <meta name="description" content="Production guide to agentic systems." />
    <link rel="canonical" href="https://example.com/systems" />
    <script type="application/ld+json">{"@context": "https://schema.org", "@type": "TechArticle"}</script>
  </head>
  <body>
    <h1>Autonomous Systems</h1>
    <p>Autonomous systems are defined as self-governing software processes.</p>
    <p>In 2026, automated audits resolved 94.2% of configuration drifts.</p>
  </body>
</html>
"""
```

### 2. Execute Parallel Multi-Dimension Audit
Run simultaneous SEO and GEO evaluations:

```python
report = auditor.audit_page("https://example.com/systems", html_payload)
print(f"Composite Score: {report.composite_score}/100")
print(f"Technical SEO: {report.technical_seo_score}/100")
print(f"GEO AI Score: {report.geo_readability_score}/100")
```

### 3. Implement Priority Action Items
Review the prioritized recommendations emitted by the subagents:

```python
for action in report.priority_action_items:
    print(f"Action: {action}")
```

## Verification & Testing

Execute the GEO & SEO audit verification suite to test parallel subagent analysis and scoring:

```bash
python scripts/geo-audit_helper.py
```

Expected output:
- Technical SEO and GEO dimensions evaluated concurrently.
- Composite score and priority action items generated.
- Status returned cleanly.
