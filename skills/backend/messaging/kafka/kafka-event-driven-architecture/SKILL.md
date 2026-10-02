---
name: kafka-event-driven-architecture
description: "Use this skill when designing, implementing, and tuning event-driven architectures with Apache Kafka. It guides the agent through partition key selection, consumer group rebalance minimization, exactly-once processing semantics (EOS), schema evolution with Avro/Protobuf, dead letter queues (DLQ), and producer idempotency."
domain: backend
category: messaging
subcategory: kafka
tags:
  - kafka
  - event-driven
  - backend
  - messaging
  - distributed-systems
  - streaming
technologies:
  - Apache Kafka
  - Java
  - Python
  - Avro
  - Docker
complexity: expert
maturity: stable
tools:
  - python
  - docker
dependencies:
  - confluent-kafka or kafka-python
---
# Kafka Event-Driven Architecture

## Overview

A comprehensive guide for building high-throughput, fault-tolerant event-driven microservices using Apache Kafka. Instructs AI agents on partition key strategy, preventing consumer lag, achieving idempotent producer delivery, handling consumer group rebalances, and implementing poison-pill dead letter queue (DLQ) patterns.

## When to Use

- Decoupling asynchronous microservices via distributed publish-subscribe event logs.
- High-volume transaction streaming (> 10,000 events/sec) requiring durable ordering per entity.
- Designing event sourcing and CQRS (Command Query Responsibility Segregation) event streams.
- Preventing data loss or duplicate processing across consumer crash-and-restart scenarios.

## When NOT to Use

- Simple task queue dispatch with low throughput (< 50 events/sec) where Redis streams or RabbitMQ suffice.
- Direct synchronous request-response queries (use gRPC or REST).

## Inputs & Prerequisites

- Running Apache Kafka cluster or broker endpoint.
- Schema Registry endpoint (for Avro/Protobuf serialization).
- Target topic configuration: replication factor, partition count, cleanup policy.

## Core Workflow

### 1. Partition Key Strategy & Message Ordering
Kafka guarantees message order strictly within a single partition, NOT across the entire topic:
- **Order by Entity**: Choose a high-cardinality partition key that groups related events into the same partition:
  `partition_key = order_id` (guarantees `OrderCreated` $\rightarrow$ `OrderPaid` $\rightarrow$ `OrderShipped` are processed sequentially).
- **Avoid Key Skew**: Never use low-cardinality keys (like `country` or `status`) that concentrate 90% of traffic onto a single partition, overwhelming one consumer thread.

### 2. Idempotent & Reliable Producer Configuration
Prevent duplicate delivery during network timeouts and retries:
```python
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True,     # Guarantees exactly-once delivery per session
    'acks': 'all',                  # Require acknowledgment from all in-sync replicas
    'retries': 5,
    'max.in.flight.requests.per.connection': 5, # Safe when idempotence is true
    'compression.type': 'snappy',   # Slashes network bandwidth
    'linger.ms': 20,                # Micro-batching window for high throughput
}
producer = Producer(conf)
```

### 3. Resilient Consumer Groups & Rebalance Minimization
Configure consumer processing loops to prevent heartbeat timeouts and catastrophic stop-the-world rebalance storms:
- Keep message batch processing times well below `max.poll.interval.ms` (default 300,000ms).
- Commit offsets only after downstream persistence succeeds:
```python
from confluent_kafka import Consumer

consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'order-fulfillment-service',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False,    # Explicit manual commit
    'partition.assignment.strategy': 'cooperative-sticky' # Non-blocking rebalances
}
consumer = Consumer(consumer_conf)
```

### 4. Poison Pill Handling & Dead Letter Queues (DLQ)
When a consumer encounters an unparseable or schema-violating message:
1. Never crash in an infinite retry loop on the same corrupted offset.
2. Route the failed message along with error metadata (stack trace, timestamp, retry count) to `<topic>.DLQ`.
3. Manually commit the offset on the primary topic and continue processing the next message.

### 5. Schema Evolution with Schema Registry
- Enforce `BACKWARD` or `FULL` compatibility rules in Confluent Schema Registry.
- Add optional fields with default values; never remove required fields without deprecation cycles.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Consumer lag growing steadily | Increase topic partition count and spin up additional consumer instances in the consumer group (up to partition count). |
| High consumer processing latency | Offload CPU-heavy processing to an internal async worker threadpool, committing offsets as work completes. |
| Duplicate consumer processing after crash | Implement idempotency at the database layer (e.g. `INSERT ... ON CONFLICT DO NOTHING` keyed by `event_id`). |

## Validation & Acceptance Criteria

- [ ] Producers configured with `enable.idempotence=True` and `acks='all'`.
- [ ] Partition keys selected with high cardinality to ensure uniform traffic distribution.
- [ ] Consumers utilize `cooperative-sticky` rebalance strategy.
- [ ] Manual offset commits executed after successful processing.
- [ ] Dead Letter Queue active for schema validation failures.

## Failure Handling & Recovery

- If a broker goes down, verify that remaining in-sync replicas (`min.insync.replicas >= 2`) continue serving traffic without producer acknowledgment failures.

## Expected Output & Artifacts

- Idempotent Kafka producer module.
- Resilient Kafka consumer worker module with DLQ error handling.
- Topic configuration and partition sizing documentation.

## Related Skills

- `api-and-interface-design`
- `postgres-query-performance-analysis`
- `fastapi-async-api-design`
