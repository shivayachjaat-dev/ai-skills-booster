#!/usr/bin/env python3
"""
Full Website GEO (Generative Engine Optimization) & SEO Auditor
---------------------------------------------------------------
Dispatches parallel subagent analyzers to evaluate technical SEO (meta tags,
canonical links, JSON-LD schema) and Generative Engine Optimization (citation
density, direct-answer definitions, entity clarity) for modern search and AI engines.
"""

import sys
import os
import re
import json
import concurrent.futures
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class AuditDimensionResult:
    dimension_name: str
    score: float  # 0.0 to 100.0
    passed_checks: List[str]
    failed_checks: List[str]
    recommendations: List[str]

@dataclass
class FullAuditReport:
    target_url: str
    composite_score: float  # 0.0 to 100.0
    technical_seo_score: float
    geo_readability_score: float
    dimensions: List[AuditDimensionResult]
    priority_action_items: List[str]

class GeoSeoAuditor:
    def __init__(self):
        pass

    def _audit_technical_seo(self, html: str) -> AuditDimensionResult:
        passed = []
        failed = []
        recs = []
        score = 0.0

        # Title check
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match and len(title_match.group(1).strip()) > 10:
            passed.append(f"Title tag present: '{title_match.group(1).strip()[:40]}...'")
            score += 25.0
        else:
            failed.append("Missing or inadequate <title> tag.")
            recs.append("Add descriptive 50-60 character <title> tag.")

        # Meta description
        meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
        if meta_desc and len(meta_desc.group(1).strip()) > 20:
            passed.append("Meta description present and informative.")
            score += 25.0
        else:
            failed.append("Missing or short meta description.")
            recs.append("Author a concise 140-160 character meta description.")

        # Canonical
        if re.search(r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE):
            passed.append("Canonical link tag defined.")
            score += 25.0
        else:
            failed.append("Missing canonical link.")
            recs.append("Add <link rel='canonical'> to prevent duplicate indexing.")

        # JSON-LD Schema
        if "application/ld+json" in html.lower():
            passed.append("Structured data schema (application/ld+json) detected.")
            score += 25.0
        else:
            failed.append("No JSON-LD structured schema found.")
            recs.append("Implement Schema.org JSON-LD (Article, WebPage, or Organization).")

        return AuditDimensionResult(
            dimension_name="Technical SEO",
            score=score,
            passed_checks=passed,
            failed_checks=failed,
            recommendations=recs
        )

    def _audit_geo_ai_readability(self, html: str) -> AuditDimensionResult:
        passed = []
        failed = []
        recs = []
        score = 0.0

        # Direct definition check
        if re.search(r'\b(is defined as|refers to|is an? [a-zA-Z\s]+ that)\b', html, re.IGNORECASE):
            passed.append("Direct answer definitions present for LLM retrieval.")
            score += 35.0
        else:
            failed.append("Lacks clear direct-answer definitions.")
            recs.append("Provide concise definitions in opening paragraphs for AI snippet synthesis.")

        # Statistics & factual citations
        if re.search(r'\b\d{1,3}(?:\.\d+)?%\b|\b\d{4}\b', html):
            passed.append("Numerical statistics and quantitative claims detected.")
            score += 35.0
        else:
            failed.append("Few or no quantitative statistics detected.")
            recs.append("Incorporate verifiable numerical data points to boost citation probability.")

        # Heading hierarchy
        h1_count = len(re.findall(r'<h1\b', html, re.IGNORECASE))
        if h1_count == 1:
            passed.append("Clean H1 semantic heading hierarchy.")
            score += 30.0
        else:
            failed.append(f"Found {h1_count} <h1> tags (expected exactly 1).")
            recs.append("Enforce single canonical <h1> per document.")

        return AuditDimensionResult(
            dimension_name="Generative Engine Optimization (GEO)",
            score=score,
            passed_checks=passed,
            failed_checks=failed,
            recommendations=recs
        )

    def audit_page(self, target_url: str, html_content: str) -> FullAuditReport:
        """Run parallel subagent audit across SEO and GEO dimensions."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut_seo = executor.submit(self._audit_technical_seo, html_content)
            fut_geo = executor.submit(self._audit_geo_ai_readability, html_content)

            seo_res = fut_seo.result()
            geo_res = fut_geo.result()

        composite = round((seo_res.score * 0.5) + (geo_res.score * 0.5), 1)
        priority_actions = seo_res.recommendations[:2] + geo_res.recommendations[:2]

        return FullAuditReport(
            target_url=target_url,
            composite_score=composite,
            technical_seo_score=seo_res.score,
            geo_readability_score=geo_res.score,
            dimensions=[seo_res, geo_res],
            priority_action_items=priority_actions
        )

def verify_geo_auditor():
    auditor = GeoSeoAuditor()
    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Autonomous AI Engineering - Architecture and Tools</title>
        <meta name="description" content="Comprehensive guide to autonomous AI software engineering and multi-agent systems." />
        <link rel="canonical" href="https://example.com/ai-engineering" />
        <script type="application/ld+json">{"@context": "https://schema.org", "@type": "TechArticle"}</script>
    </head>
    <body>
        <h1>Autonomous AI Engineering</h1>
        <p>An autonomous agent is defined as an entity that perceives its environment and takes actions to maximize success.</p>
        <p>In 2026, benchmark evaluations showed a 48.5% improvement in multi-agent bug resolution latency.</p>
    </body>
    </html>
    """

    print("============================================================")
    print("GEO & SEO Auditor: Executing Multi-Dimensional Analysis")
    print("============================================================")
    report = auditor.audit_page("https://example.com/ai-engineering", sample_html)
    print(f"[*] Target: {report.target_url}")
    print(f"[*] Composite Score: {report.composite_score}/100")
    print(f"[*] Technical SEO Score: {report.technical_seo_score}/100")
    print(f"[*] GEO AI Score: {report.geo_readability_score}/100")
    print(f"[*] Priority Actions: {report.priority_action_items}")

    assert report.composite_score == 100.0
    print("[SUCCESS] GEO & SEO Auditor verified cleanly.")

if __name__ == "__main__":
    verify_geo_auditor()
