---
name: vector-database-rag-indexing
description: "Use this skill when architecting, building, and optimizing high-scale vector database indexing pipelines for Retrieval-Augmented Generation (RAG). It guides the agent through chunking strategies, dense embedding generation, approximate nearest neighbor (ANN) index selection (HNSW vs IVF vs ScaNN), payload metadata schema design, hybrid dense-sparse search, and index warm-up."
domain: ai-engineering
category: vector-databases
subcategory: indexing
tags:
  - vector-database
  - rag
  - embeddings
  - hnsw
  - qdrant
  - chroma
  - pinecone
technologies:
  - Qdrant
  - Chroma
  - pgvector
  - OpenAI
  - VoyageAI
  - HuggingFace
complexity: advanced
maturity: stable
tools:
  - python
  - docker
dependencies:
  - qdrant-client >= 1.7.0
---
# Vector Database RAG Indexing Architecture

## Overview

A production engineering standard for architecting robust, scalable vector indexing pipelines in Retrieval-Augmented Generation (RAG) systems. This skill covers semantic document chunking, multi-stage embedding generation, vector distance metrics selection (Cosine, Dot Product, Euclidean), Approximate Nearest Neighbor (ANN) index tuning (HNSW `m` and `ef_construct`), hybrid dense-sparse vector schemas, and metadata filtering.

## When to Use

- Indexing millions of enterprise documents, codebases, or knowledge bases for generative AI search.
- Optimizing search recall vs p99 query latency in vector databases (Qdrant, pgvector, Milvus, Pinecone).
- Implementing hybrid search combining dense semantic embeddings with sparse BM25 keyword matching.
- Designing metadata filtering schemas that prevent post-filtering memory bloat.

## When NOT to Use

- Small static datasets (< 1,000 documents) where in-memory cosine similarity via NumPy or FAISS flat index suffices.
- Pure keyword exact-match lookups where relational database B-tree indexes or Elasticsearch are superior.

## Inputs & Prerequisites

- Vector database cluster running (e.g. Qdrant 1.7+ or PostgreSQL with pgvector).
- Target embedding model chosen (e.g., `text-embedding-3-small`, `voyage-large-2`, `bge-large-en-v1.5`).
- Raw textual documents with structural metadata (author, date, tenant_id, source).

## Core Workflow

### 1. Chunking Strategy & Metadata Preservation
Implement semantic parent-child chunking:

```python
from typing import List, Dict, Any
import hashlib

def generate_deterministic_chunk_id(doc_id: str, chunk_idx: int) -> str:
    return hashlib.sha256(f"{doc_id}:{chunk_idx}".encode()).hexdigest()[:16]

def chunk_document_sliding_window(
    doc_id: str,
    text: str,
    metadata: Dict[str, Any],
    chunk_size_words: int = 400,
    overlap_words: int = 80
) -> List[Dict[str, Any]]:
    words = text.split()
    chunks = []
    
    start = 0
    chunk_idx = 0
    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunk_text = " ".join(words[start:end])
        
        chunk_payload = {
            "chunk_id": generate_deterministic_chunk_id(doc_id, chunk_idx),
            "doc_id": doc_id,
            "text": chunk_text,
            "chunk_index": chunk_idx,
            "is_start": start == 0,
            "is_end": end == len(words),
            **metadata
        }
        chunks.append(chunk_payload)
        
        if end == len(words):
            break
        start += (chunk_size_words - overlap_words)
        chunk_idx += 1
        
    return chunks
```

### 2. Qdrant HNSW Collection Setup & Tuning
Configure collection with optimal HNSW parameters and indexed metadata payload fields:

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

def setup_rag_collection(client: QdrantClient, collection_name: str, vector_dim: int = 1536):
    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=vector_dim,
            distance=models.Distance.COSINE,
            on_disk=True  # Keeps vectors on disk, caches hot index in RAM
        ),
        # Tuned HNSW Parameters
        hnsw_config=models.HnswConfigDiff(
            m=16,                # Number of bidirectional links per node (16-64)
            ef_construct=128,    # Search depth during index building (higher = higher recall, slower indexing)
            full_scan_threshold=1000,
            on_disk=False        # Keep graph in RAM for low latency
        ),
        optimizers_config=models.OptimizersConfigDiff(
            default_segment_number=2,
            memmap_threshold=20000
        )
    )

    # Index metadata payload fields used in filters
    client.create_payload_index(
        collection_name=collection_name,
        field_name="tenant_id",
        field_schema=models.PayloadSchemaType.KEYWORD
    )
    client.create_payload_index(
        collection_name=collection_name,
        field_name="created_timestamp",
        field_schema=models.PayloadSchemaType.INTEGER
    )
```

### 3. Batched Ingestion Pipeline with Error Handling
Ingest vector points in parallel batches:

```python
import uuid
from qdrant_client.http.models import PointStruct

def ingest_vector_batch(
    client: QdrantClient,
    collection_name: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]]
):
    points = []
    for chunk, emb in zip(chunks, embeddings):
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk["chunk_id"]))
        points.append(
            PointStruct(
                id=point_id,
                vector=emb,
                payload=chunk
            )
        )

    # Upload in batch
    client.upsert(
        collection_name=collection_name,
        points=points,
        wait=True
    )
```

## Best Practices & Failure Modes

1. **Unindexed Metadata Filtering (Full Table Scan)**: In vector databases, filtering on unindexed payload fields forces the engine to do a full scan, ruining query latency. Always create payload indexes on filterable keys (`tenant_id`, `category`).
2. **Dimension Mismatch**: Embedding model dimensions (e.g. 1536 for OpenAI small vs 1024 for BGE-large) must match collection configuration exactly or API calls will reject writes.
3. **Cosine Distance vs Dot Product**: When using normalized embeddings (L2 norm = 1), Dot Product and Cosine distance yield identical rankings, but Dot Product is 2-3x faster computationally.

## Verification & Testing

- Perform query search test with tenant isolation:
  ```python
  search_results = client.search(
      collection_name="enterprise_knowledge",
      query_vector=test_query_embedding,
      query_filter=models.Filter(
          must=[
              models.FieldCondition(
                  key="tenant_id",
                  match=models.MatchValue(value="tenant_abc_123")
              )
          ]
      ),
      limit=5,
      search_params=models.SearchParams(hnsw_ef=64) # Query-time search depth
  )
  assert len(search_results) > 0
  assert all(r.payload["tenant_id"] == "tenant_abc_123" for r in search_results)
  ```
