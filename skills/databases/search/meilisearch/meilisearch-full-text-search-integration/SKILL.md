---
name: meilisearch-full-text-search-integration
description: "Use this skill when designing, indexing, and querying lightning-fast, typo-tolerant full-text search systems using Meilisearch. It guides the agent through index configuration, searchable vs filterable attributes, custom ranking rules, document batching, faceted navigation, and building search-as-you-type frontend experiences."
domain: databases
category: search
subcategory: meilisearch
tags:
  - meilisearch
  - search
  - full-text-search
  - typo-tolerance
  - fast-search
  - faceted-search
technologies:
  - Meilisearch
  - Python meilisearch
  - TypeScript
  - InstantSearch.js
  - Docker
complexity: intermediate
maturity: stable
tools:
  - meilisearch
  - curl
dependencies:
  - meilisearch >= 0.30.0
---
# Meilisearch Full-Text Search Architecture & Indexing

## Overview

A comprehensive guide for implementing ultra-fast, typo-tolerant search experiences with Meilisearch. This skill instructs AI agents on index schema configuration, tuning ranking rules for relevance, configuring filterable and sortable attributes for faceted navigation, optimizing document batch indexing, and managing security keys.

## When to Use

- Building instant "search-as-you-type" user interfaces for e-commerce products, documentation, or catalogs.
- Providing out-of-the-box typo-tolerant search without complex Lucene/Elasticsearch tuning.
- Supporting multi-attribute faceted filtering (e.g. price range, brand, availability) with sub-50ms response times.
- Replacing heavy Elasticsearch clusters for small to medium datasets (< 10 million documents).

## When NOT to Use

- Big data log analytics and distributed petabyte-scale event log search (use Elasticsearch, OpenSearch, or ClickHouse).
- Pure vector similarity embeddings search without keyword matching (use Qdrant or Pinecone).

## Inputs & Prerequisites

- Meilisearch 1.6+ instance running.
- Python client `meilisearch` or Node.js `@meilisearch/instant-meilisearch`.
- API Master Key for admin operations.

## Core Workflow

### 1. Index Creation & Relevance Tuning
Configure attributes, ranking rules, and typo tolerance:

```python
import meilisearch
import os

MEILI_KEY = os.getenv("MEILISEARCH_MASTER_KEY", "masterKey123")
client = meilisearch.Client("http://localhost:7700", MEILI_KEY)

def setup_products_index():
    index = client.index("products")

    # 1. Searchable Attributes (ordered by priority)
    index.update_searchable_attributes([
        "title",
        "brand",
        "description",
        "categories"
    ])

    # 2. Filterable & Sortable Attributes
    index.update_filterable_attributes([
        "brand",
        "category",
        "in_stock",
        "price"
    ])
    index.update_sortable_attributes([
        "price",
        "created_at"
    ])

    # 3. Custom Ranking Rules
    index.update_ranking_rules([
        "words",        # Number of matching words
        "typo",         # Number of typos
        "proximity",    # Distance between query terms in document
        "attribute",    # Importance of attribute where match occurred
        "sort",         # User-requested sorting
        "exactness",    # Exact word match vs prefix match
        "popularity:desc" # Custom business metric tie-breaker
    ])
    
    return index
```

### 2. Batched Document Ingestion
Ingest documents in chunks to maximize throughput without memory spikes:

```python
def ingest_documents_in_batches(index, documents: list, batch_size: int = 1000):
    for i in range(0, len(documents), batch_size):
        chunk = documents[i:i + batch_size]
        task = index.add_documents(chunk, primary_key="id")
        print(f"Enqueued batch {i // batch_size + 1}, Task UID: {task.task_uid}")
```

### 3. Faceted Search Execution
Query with typo tolerance and faceted breakdown:

```python
def execute_faceted_search(index, query_text: str, brand_filter: str = None, max_price: float = None):
    filter_conditions = ["in_stock = true"]
    if brand_filter:
        filter_conditions.append(f'brand = "{brand_filter}"')
    if max_price is not None:
        filter_conditions.append(f"price <= {max_price}")

    results = index.search(
        query_text,
        {
            "filter": " AND ".join(filter_conditions),
            "facets": ["brand", "category"],
            "limit": 20,
            "attributesToHighlight": ["title", "description"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>"
        }
    )
    return results
```

## Best Practices & Failure Modes

1. **Unindexed Filter Queries**: Attempting to filter on an attribute not explicitly added to `filterableAttributes` causes search queries to return an immediate HTTP 400 Bad Request error. Always configure filterable attributes during schema initialization.
2. **Missing Primary Key**: If documents do not have an `id` field and no primary key is specified during index creation, Meilisearch rejects document ingestion.
3. **Master Key Exposure**: Never pass the Meilisearch master key to frontend client applications. Generate scoped, read-only search keys with specific index restrictions for browser consumption (`client.create_key(...)`).

## Verification & Testing

- Check task status to ensure asynchronous document indexing has completed:
  ```bash
  curl -H "Authorization: Bearer masterKey123" http://localhost:7700/tasks/0
  ```
- Test typo tolerance query via curl:
  ```bash
  curl -X POST -H "Authorization: Bearer masterKey123" -H "Content-Type: application/json"     http://localhost:7700/indexes/products/search     -d '{"q": "phne", "limit": 1}'
  # Should successfully match "phone"
  ```
