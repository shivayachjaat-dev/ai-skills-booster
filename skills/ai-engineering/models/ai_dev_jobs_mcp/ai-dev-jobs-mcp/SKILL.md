---
name: ai-dev-jobs-mcp
description: "Use this skill to query, analyze, and match AI/ML engineering job listings, compensation benchmarks, and hiring company data via the Model Context Protocol (MCP). It covers JSON-RPC tool integration, role-to-profile skill matching algorithms, remote-work filtering, and market compensation trend analysis."
domain: ai-engineering
category: models
subcategory: ai_dev_jobs_mcp
tags:
  - ai-engineering
  - mcp
  - model-context-protocol
  - job-market
  - career-intelligence
  - recruiting-automation
  - compensation-analysis
technologies:
  - Model Context Protocol
  - JSON-RPC 2.0
  - Python
  - Pydantic
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
  - requests@>=2.31.0
version: 1.0.0
author: Antigravity Team
---

# AI & ML Developer Jobs MCP Client & Market Intelligence Architecture

## Overview

A standardized client architecture and market intelligence protocol for querying, filtering, and analyzing AI/ML engineering job markets via the Model Context Protocol (MCP). Engineering agents assisting candidates or recruiting teams require structured access to live role indexes, salary distributions, equity expectations, remote-first policies, and required tech stacks (e.g., PyTorch, CUDA, vLLM, LangGraph). This skill establishes clean integration patterns for communicating with job market MCP servers over JSON-RPC (stdio and Server-Sent Events [SSE]), parsing structured listing payloads, and executing semantic candidate-to-role matching.

```
+--------------------------------------------------------------------------------+
|                        Job Market MCP Interaction Flow                         |
|                                                                                |
|  [ User Prompt / Candidate Profile ] ---> [ Intent Parsing & Filter Extraction ]|
|                                                     |                          |
|                                                     v                          |
|                           [ MCP JSON-RPC Request (tools/call) ]                |
|                            (Method: search_jobs / match_roles)                 |
|                                                     |                          |
|                                                     v                          |
|                           [ Remote / Local MCP Server Dispatch ]               |
|                            (stdio / SSE Transport over TLS)                    |
|                                                     |                          |
|                                                     v                          |
|                           [ Listing Normalization & Salary Scoring ]           |
|                                                     |                          |
|                                                     v                          |
|                           [ Candidate Skill-Overlap Matching (Jaccard/Cosine) ]|
|                                                     |                          |
|                                                     v                          |
|                           [ Structured Opportunity Report & Digest ]           |
+--------------------------------------------------------------------------------+
```

## When to Use

- Querying live AI/ML, MLOps, Data Engineering, and Research Scientist job listings via MCP tools.
- Calculating market salary percentiles ($P_{25}, P_{50}, P_{90}$) across regions and seniority levels.
- Matching a candidate's resume or skill profile against open role requirements using weighted keyword matching.
- Monitoring industry hiring trends (e.g., shifts from fine-tuning to inference optimization or agentic engineering).

## When NOT to Use

- Non-technical recruitment outside software, data, or AI engineering disciplines.
- Automated mass job application submissions (spamming ATS portals without candidate review).

## Inputs & Prerequisites

- Python 3.10+ runtime with `requests` or `httpx` installed.
- Target MCP server endpoint (stdio executable or remote HTTPS/SSE URI).
- Standard candidate profile structure (technologies, years of experience, target compensation, remote preference).

## Core Workflow

### Step 1: MCP Server Configuration & Handshake
Configure the agent environment with the target job board MCP server via `mcp_config.json`:

```json
{
  "mcpServers": {
    "ai-jobs": {
      "command": "python",
      "args": ["-m", "job_market_mcp_server"],
      "env": {
        "JOB_BOARD_API_KEY": "${JOB_BOARD_API_KEY}"
      }
    }
  }
}
```

### Step 2: Querying Roles via JSON-RPC Tools Protocol
Construct standard MCP `tools/call` JSON-RPC payloads:

```python
import json
import requests

def search_ai_jobs(endpoint_url: str, role_title: str, min_salary: int = 180000, remote_only: bool = True) -> list[dict]:
    """Queries job market MCP server using standard JSON-RPC 2.0."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_jobs",
            "arguments": {
                "query": role_title,
                "salary_min": min_salary,
                "remote": remote_only,
                "limit": 10
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    response = requests.post(endpoint_url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    
    result = response.json()
    return result.get("result", {}).get("content", [])
```

### Step 3: Candidate Skill Matching Algorithm
Compute weighted technical alignment between a candidate profile and role requirements:

```python
def calculate_skill_match(candidate_skills: set[str], role_required_skills: set[str]) -> dict:
    """Calculates Jaccard overlap and missing skill gaps."""
    cand_norm = {s.lower().strip() for s in candidate_skills}
    role_norm = {s.lower().strip() for s in role_required_skills}

    matching = cand_norm & role_norm
    missing = role_norm - cand_norm

    match_percentage = (len(matching) / len(role_norm) * 100) if role_norm else 100.0

    return {
        "match_percentage": round(match_percentage, 1),
        "matching_skills": sorted(list(matching)),
        "missing_skills": sorted(list(missing)),
        "is_strong_fit": match_percentage >= 75.0
    }
```

### Step 4: Compensation Benchmarking
Evaluate salary and total compensation offerings against market distributions:

```python
def benchmark_compensation(offered_salary: int, market_median: int = 210000, market_p90: int = 285000) -> str:
    """Evaluates compensation relative to market benchmarks."""
    if offered_salary >= market_p90:
        return "Top Tier (>= 90th percentile)"
    elif offered_salary >= market_median:
        return "Competitive (>= Median)"
    else:
        return "Below Market Median"
```

## Best Practices & Failure Modes

- **Never Hardcode Provider Secrets**: Use environment variable interpolation (`${JOB_BOARD_API_KEY}`) in MCP client configuration manifests.
- **Graceful MCP Server Disconnects**: Implement backoff retries when connecting to remote SSE endpoints; fallback to local cached job listings if connection fails.
- **Candidate Privacy**: Never send unredacted PII (full name, phone number, address) to third-party MCP endpoints during initial role discovery.

## Verification & Testing

1. Test MCP client parsing: Run `python scripts/job_market_mcp_client.py --test-client` to verify JSON-RPC payload serialization and response handling.
2. Verify skill matching logic: Run `python scripts/job_market_mcp_client.py --match-skills --candidate "Python, PyTorch, LangGraph, Docker" --role-skills "Python, PyTorch, CUDA, Kubernetes"`.
3. Check market percentiles: Validate that salary classifications align with published market bands.
