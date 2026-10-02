---
name: elasticsearch-dsl-search-and-aggregations
description: "Use this skill when architecting, indexing, and querying complex search and analytical systems using Elasticsearch 8+ and Elasticsearch-DSL. It guides the agent through explicit index mapping design (analyzers, keyword vs text fields), boolean compound queries (must, filter, should), multi-match cross-field queries, and multi-level nested aggregations."
domain: databases
category: search
subcategory: elasticsearch
tags:
  - elasticsearch
  - search
  - analytics
  - aggregations
  - nosql
  - python
  - elk
technologies:
  - Elasticsearch 8+
  - Elasticsearch-DSL
  - Python
  - JSON
  - Lucene
complexity: advanced
maturity: stable
tools:
  - curl
  - python
dependencies:
  - elasticsearch >= 8.12.0
  - elasticsearch-dsl >= 8.12.0
---
# Elasticsearch 8+ Query DSL & Aggregations Architecture

## Overview

A definitive production engineering reference for building high-scale search and analytics pipelines with Elasticsearch 8+. This skill instructs AI agents on explicit index mappings, custom text analyzers, constructing compound Boolean queries (`bool: must, filter, should, must_not`), multi-match cross-field scoring, and nested multi-dimensional aggregations for business analytics.

## When to Use

- Building enterprise e-commerce search, documentation portals, or knowledge bases.
- Executing analytical reporting queries across millions of log records or events.
- Combining full-text relevance scoring with strict filter caching (`filter` clause).
- Computing multi-level aggregations (e.g. revenue grouped by category, buckated by month).

## When NOT to Use

- Primary transactional record storage where strict ACID multi-row transactions are required (use PostgreSQL).
- Simple in-memory key-value lookups (use Redis).

## Inputs & Prerequisites

- Elasticsearch 8+ cluster accessible via HTTPS.
- Python client `elasticsearch` or `elasticsearch-dsl`.
- Elastic credentials (API key or basic auth).

## Core Workflow

### 1. Explicit Index Mapping & Custom Analyzers
Configure an explicit mapping separating searchable text from exact keywords:

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "superSecretPass123"),
    verify_certs=False
)

def create_catalog_index():
    index_name = "product_catalog_v1"
    
    settings = {
        "analysis": {
            "analyzer": {
                "custom_search_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "snowball"]
                }
            }
        }
    }

    mappings = {
        "properties": {
            "sku": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "custom_search_analyzer",
                "fields": {
                    "raw": {"type": "keyword"} # Enables sorting and exact matching
                }
            },
            "description": {"type": "text", "analyzer": "custom_search_analyzer"},
            "category": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "price": {"type": "scaled_float", "scaling_factor": 100},
            "in_stock": {"type": "boolean"},
            "created_at": {"type": "date"}
        }
    }

    es.indices.create(index=index_name, settings=settings, mappings=mappings)
```

### 2. Compound Boolean Query (`must`, `filter`, `should`)
Differentiate between relevance scoring and cached filter conditions:

```python
def search_products(query_text: str, category_filter: str, max_price: float):
    """
    - 'must': Contributes to relevance score (_score)
    - 'filter': Strictly filters rows; cached in memory; does NOT affect score
    - 'should': Boosts score if matched, but not mandatory
    """
    query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title^3", "description"], # Title has 3x boost
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                }
            ],
            "filter": [
                {"term": {"category": category_filter}},
                {"range": {"price": {"lte": max_price}}},
                {"term": {"in_stock": True}}
            ],
            "should": [
                {"term": {"tags": "featured"}} # Boosts featured products
            ]
        }
    }

    response = es.search(
        index="product_catalog_v1",
        query=query,
        size=20,
        highlight={"fields": {"title": {}, "description": {}}}
    )
    return response["hits"]["hits"]
```

### 3. Multi-Level Analytics Aggregations
Compute category breakdown and time-series histogram:

```python
def compute_sales_metrics():
    aggregations = {
        "by_category": {
            "terms": {"field": "category", "size": 10},
            "aggs": {
                "avg_price": {"avg": {"field": "price"}},
                "total_stock": {"value_count": {"field": "sku"}},
                "monthly_distribution": {
                    "date_histogram": {
                        "field": "created_at",
                        "calendar_interval": "month"
                    }
                }
            }
        }
    }

    response = es.search(
        index="product_catalog_v1",
        size=0, # size=0 returns ONLY aggregation metrics, no documents
        aggs=aggregations
    )
    return response["aggregations"]
```

## Best Practices & Failure Modes

1. **Putting Filter Clauses in `must`**: Putting non-scoring filters (like `in_stock = True` or `tenant_id = 123`) in the `must` block forces Lucene to compute TF-IDF / BM25 scores for Boolean matches and prevents query caching. Always put exact filters in the `filter` block.
2. **Deep Pagination Out-of-Memory**: Using `from + size > 10,000` forces coordinating nodes to collect and sort huge sets in heap memory. Use the `search_after` parameter with point-in-time (`PIT`) for deep pagination.
3. **Uncontrolled Dynamic Mapping**: Relying on default dynamic mapping creates unwanted `text` and `keyword` multi-fields for every field, bloating cluster state memory. Explicitly define schema mappings or set `dynamic: strict`.

## Verification & Testing

- Test cluster connection and health:
  ```bash
  curl -k -u elastic:superSecretPass123 https://localhost:9200/_cluster/health?pretty
  ```
- Validate query explanation and score breakdown:
  ```bash
  curl -k -u elastic:superSecretPass123 -X POST https://localhost:9200/product_catalog_v1/_explain/1     -H "Content-Type: application/json" -d '{"query": {"term": {"category": "electronics"}}}'
  ```
