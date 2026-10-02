---
name: employee-360-feedback-review-system
description: "Use this skill when designing, configuring, and operating multi-rater 360-degree performance feedback systems. It guides the agent through peer reviewer nomination workflows, role-specific competency rubrics, anonymous vs attributed visibility rules, cognitive bias mitigation (recency and halo effects), and synthesis reporting."
domain: business
category: human-resources
subcategory: performance-management
tags:
  - 360-feedback
  - hr
  - performance-review
  - talent-management
  - competencies
  - people-ops
technologies:
  - Python
  - JSON
  - PostgreSQL
  - Data Analytics
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Employee 360-Degree Performance Feedback Architecture

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
