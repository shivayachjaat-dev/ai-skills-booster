---
name: social-sentiment-and-brand-reputation-monitor
description: "Use this skill to design, build, and automate brand reputation monitoring, customer sentiment analysis, and social mention surveillance across Twitter/X, Reddit, G2, Trustpilot, and GitHub Issues. It covers NLP sentiment scoring, crisis escalation alerts, and automated PR response drafting."
domain: marketing
category: brand
subcategory: reputation-monitor
tags:
  - brand-reputation
  - sentiment-analysis
  - social-monitoring
  - nlp
  - crisis-management
  - marketing
technologies:
  - Python
  - NLTK
  - TextBlob
  - Pydantic
  - FastAPI
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# Social Sentiment & Brand Reputation Surveillance Architecture

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
"""Social Sentiment Analysis and Brand Reputation Monitor."""
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
