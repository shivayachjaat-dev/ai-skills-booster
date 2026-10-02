---
name: neo4j-graph-data-modeling-and-cypher
description: "Use this skill when designing, indexing, and querying labeled property graphs using Neo4j 5+ and Cypher query language. It guides the agent through node and relationship property modeling, index and constraint declarations, variable-length path traversal, aggregation with WITH clauses, and optimizing Cypher queries using PROFILE and EXPLAIN."
domain: databases
category: nosql
subcategory: neo4j
tags:
  - neo4j
  - cypher
  - graph-database
  - knowledge-graph
  - nosql
  - graph
technologies:
  - Neo4j 5+
  - Cypher
  - Python neo4j
  - Docker
complexity: advanced
maturity: stable
tools:
  - cypher-shell
  - python
dependencies:
  - neo4j >= 5.15.0
---
# Neo4j Labeled Property Graph Modeling & Cypher Optimization

## Overview

A definitive production engineering reference for architecting high-performance graph databases using Neo4j 5+ and Cypher. Relational databases struggle with deep multi-hop traversals, requiring expensive, slow multi-table recursive JOINs. Neo4j leverages index-free adjacency: nodes point directly to adjacent nodes in physical memory, allowing constant-time traversal regardless of total graph size. This skill instructs AI agents on property graph modeling, defining uniqueness constraints and range indexes, authoring performant Cypher traversal queries, and inspecting execution plans with `PROFILE`.

## When to Use

- Building enterprise Knowledge Graphs, identity graphs, or entity resolution engines.
- Fraud detection systems traversing interconnected accounts, devices, and financial transactions.
- Social networks, permission graphs (RBAC/ReBAC), and dependency tree analysis.
- Powering GraphRAG (Graph-Augmented Generation) combining vector retrieval with structured graph relationship traversals.

## When NOT to Use

- High-frequency tabular time-series writes (use TimescaleDB or ClickHouse).
- Simple key-value document lookups without relationships (use Redis or MongoDB).

## Inputs & Prerequisites

- Neo4j 5+ server running (Enterprise or Community Edition).
- Python client `neo4j` or CLI `cypher-shell`.
- URI: `bolt://localhost:7687` or `neo4j://localhost:7687`.

## Core Workflow

### 1. Schema Constraints & Indexes (Cypher)
Establish node existence/uniqueness constraints and relationship indexes before data ingestion:

```cypher
// 1. Uniqueness Constraints (automatically creates backing index)
CREATE CONSTRAINT unique_customer_id IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT unique_merchant_id IF NOT EXISTS
FOR (m:Merchant) REQUIRE m.id IS UNIQUE;

CREATE CONSTRAINT unique_device_id IF NOT EXISTS
FOR (d:Device) REQUIRE d.id IS UNIQUE;

// 2. Point/Range Indexes for filtered traversals
CREATE INDEX customer_name_idx IF NOT EXISTS
FOR (c:Customer) ON (c.name);

CREATE INDEX transaction_timestamp_idx IF NOT EXISTS
FOR ()-[r:TRANSACTED]->() ON (r.timestamp);
```

### 2. High-Performance Querying with Cypher
Author multi-hop graph traversals without Cartesian product bottlenecks:

```cypher
// Fraud Ring Detection: Find customers sharing devices who sent transactions to the same merchant
MATCH (c1:Customer)-[:USES_DEVICE]->(d:Device)<-[:USES_DEVICE]-(c2:Customer)
WHERE c1.id <> c2.id
MATCH (c1)-[t1:TRANSACTED]->(m:Merchant)<-[t2:TRANSACTED]-(c2)
WHERE t1.amount > 1000 AND t2.amount > 1000
RETURN c1.id AS customer_a, c2.id AS customer_b, d.id AS shared_device, m.name AS merchant, (t1.amount + t2.amount) AS total_volume
ORDER BY total_volume DESC
LIMIT 25;
```

### 3. Programmatic Execution in Python (`neo4j`)
Execute transactional write and read sessions:

```python
from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "superSecretPass123")

class GraphDataService:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

    def close(self):
        self.driver.close()

    def record_transaction(self, cust_id: str, merch_id: str, amount: float):
        query = """
        MERGE (c:Customer {id: $cust_id})
        MERGE (m:Merchant {id: $merch_id})
        CREATE (c)-[:TRANSACTED {amount: $amount, timestamp: datetime()}]->(m)
        """
        with self.driver.session(database="neo4j") as session:
            session.execute_write(lambda tx: tx.run(query, cust_id=cust_id, merch_id=merch_id, amount=amount))

    def find_shortest_path(self, start_id: str, end_id: str):
        query = """
        MATCH (start:Customer {id: $start_id}), (end:Customer {id: $end_id})
        MATCH p = shortestPath((start)-[*]-(end))
        RETURN [node in nodes(p) | coalesce(node.id, labels(node)[0])] AS path_nodes, length(p) AS hops
        """
        with self.driver.session(database="neo4j") as session:
            result = session.execute_read(lambda tx: tx.run(query, start_id=start_id, end_id=end_id).single())
            return result.data() if result else None
```

## Best Practices & Failure Modes

1. **Unbounded Path Traversal Disasters**: Executing `MATCH (a)-[*]->(b)` on a densely connected graph triggers an exponential path explosion that exhausts server RAM. Always specify an upper bound on hops (`MATCH (a)-[*1..4]->(b)`).
2. **Missing `MERGE` vs `CREATE` Distinction**: Using `CREATE (c:Customer {id: "123"})` repeatedly creates duplicate nodes with identical IDs. Use `MERGE (c:Customer {id: "123"}) ON CREATE SET c.created = timestamp()`.
3. **Cartesian Product Warning in Execution Plan**: If multiple unconnected `MATCH` clauses appear without a connecting `WITH` boundary, Cypher computes a Cartesian product. Inspect query plans with `PROFILE` and ensure `NodeIndexSeek` or `Expand` operators appear rather than `CartesianProduct`.

## Verification & Testing

- Inspect query execution plan with `PROFILE`:
  ```bash
  cypher-shell -u neo4j -p superSecretPass123 "PROFILE MATCH (c:Customer {id: 'c1'})-[:TRANSACTED]->(m:Merchant) RETURN m.name;"
  ```
- Check schema constraints status:
  ```bash
  cypher-shell -u neo4j -p superSecretPass123 "SHOW CONSTRAINTS;"
  ```
