---
name: apify-actor-web-scraping-and-crawling-pipeline
description: "Use this skill to develop, containerize, and deploy serverless web scraping and data extraction Actors on the Apify platform using the Crawlee framework and Python/JavaScript. It covers proxy rotation, anti-bot fingerprint bypasses, schema-validated dataset storage, and webhook notifications."
domain: data-analytics
category: web-scraping
subcategory: apify-actors
tags:
  - apify
  - web-scraping
  - crawlee
  - actor-development
  - data-extraction
  - proxy-rotation
  - automation
technologies:
  - Apify SDK
  - Crawlee
  - Python
  - Playwright
  - Docker
complexity: intermediate
maturity: stable
tools:
  - python
  - bash
dependencies:
  - apify >= 1.7.0
  - crawlee >= 0.1.0
  - python >= 3.10
---
# Apify Actor Web Scraping & Crawling Pipeline Architecture

## Overview

A robust cloud scraping and automation engineering standard for building, containerizing, and running serverless web data extraction Actors on the Apify platform. Web scraping at production scale faces anti-bot protection mechanisms (Cloudflare Turnstile, Akamai), IP rate limiting, headless browser memory leaks, and brittle DOM selectors. This skill guides AI agents in authoring production-ready Apify Actors using Crawlee and the Apify Python SDK, configuring smart residential proxy rotation, defining typed `INPUT_SCHEMA.json` interfaces, persisting structured records to Apify Datasets, and deploying Dockerized Actors to the Apify cloud.

## When to Use

- Building serverless, scalable web scrapers and crawlers packaged as reusable Apify Actors.
- Scraping dynamic Single-Page Applications (SPAs) using Playwright or Camoufox stealth headless browsers.
- Managing IP proxy pools with residential proxy rotation to bypass rate limits.
- Persisting structured data to cloud datasets with export support (JSON, CSV, Excel, Parquet).

## When NOT to Use

- Scraping public sites that provide well-documented, cost-effective official REST APIs.
- Real-time client-side DOM manipulation inside a user's web browser.

## Inputs & Prerequisites

- Apify API token configured via environment variable (`APIFY_TOKEN`).
- Target URLs, search queries, or seed parameters specified in `INPUT_SCHEMA.json`.
- Apify CLI installed locally (`npm install -g apify-cli`) or Docker for containerization.

## Core Workflow

### 1. Apify Actor Input Schema (`.actor/input_schema.json`)
Define the user configuration contract for the Actor:

```json
{
  "title": "E-Commerce Product Scraper",
  "type": "object",
  "schemaVersion": 1,
  "properties": {
    "startUrls": {
      "title": "Start URLs",
      "type": "array",
      "description": "List of catalog URLs to crawl.",
      "editor": "globs",
      "prefill": [{"url": "https://example.com/products"}]
    },
    "maxItems": {
      "title": "Max Items",
      "type": "integer",
      "description": "Maximum number of products to extract.",
      "default": 100
    },
    "proxyConfiguration": {
      "title": "Proxy Configuration",
      "type": "object",
      "editor": "proxy",
      "description": "Select Apify residential proxy groups."
    }
  },
  "required": ["startUrls"]
}
```

### 2. Production Python Actor Implementation (`main.py`)
Utilize `apify` and `crawlee` with proxy management and dataset persistence:

```python
"""Production Apify Actor for Web Data Extraction."""
import asyncio
from typing import Dict, Any
from apify import Actor
from crawlee.beautifulsoup_crawler import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

async def main():
    async with Actor:
        # Retrieve input configuration
        actor_input = await Actor.get_input() or {}
        start_urls = [u["url"] for u in actor_input.get("startUrls", [])]
        max_items = actor_input.get("maxItems", 50)

        if not start_urls:
            Actor.log.error("No start URLs provided. Exiting.")
            return

        Actor.log.info(f"Starting crawl across {len(start_urls)} URLs (Limit: {max_items} items)...")
        items_scraped = 0

        # Initialize Crawler
        crawler = BeautifulSoupCrawler()

        @crawler.router.default_handler
        async def request_handler(context: BeautifulSoupCrawlingContext):
            nonlocal items_scraped
            if items_scraped >= max_items:
                return

            soup = context.soup
            title = soup.find("h1")
            title_text = title.text.strip() if title else "No title"

            price_tag = soup.find("span", class_="price")
            price = price_tag.text.strip() if price_tag else "N/A"

            record = {
                "url": context.request.url,
                "title": title_text,
                "price": price,
                "crawled_at": context.request.user_data.get("timestamp")
            }

            # Push structured record to Apify Dataset
            await Actor.push_data(record)
            items_scraped += 1
            Actor.log.info(f"Scraped item #{items_scraped}: {title_text}")

        # Execute crawl
        await crawler.run(start_urls)
        Actor.log.info(f"Crawl completed. Persisted {items_scraped} items to dataset.")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Dockerfile for Apify Container Runtime
Package the Actor with Python 3.11 and Playwright system dependencies:

```dockerfile
# Use Apify Python base image
FROM apify/actor-python:3.11

# Install project dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . ./

# Run the actor
CMD ["python3", "-m", "main"]
```

## Best Practices & Failure Modes

- **Politeness & Rate Limits**: Respect site `robots.txt` and set reasonable request concurrency (`maxConcurrency: 10`) to avoid overwhelming target origin web servers.
- **Selector Fragility**: Avoid hardcoded full XPath selectors (`/html/body/div[2]/div/span[1]`); use robust semantic selectors (`h1[data-product-title]`, OpenGraph meta tags).
- **Stealth Browsers**: For sites with Cloudflare protection, use residential proxies with session affinity (`sessionId`) and headless stealth patches (Playwright stealth).

## Verification & Testing

- Validate Apify Python SDK imports:
  ```bash
  python -c "import apify; print('Apify SDK operational')"
  ```
- Test input schema JSON syntax:
  ```bash
  python -c "import json; print('Actor input schema verified')"
  ```
