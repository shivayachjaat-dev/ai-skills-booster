---
name: redis-streams-event-processing
description: "Use this skill when architecting, implementing, and operating event-driven stream processing systems using Redis Streams. It guides the agent through appending events with XADD, managing competing Consumer Groups with XREADGROUP, tracking the Pending Entries List (PEL), dead-lettering abandoned messages via XAUTOCLAIM, and stream memory trimming with MAXLEN."
domain: backend
category: caching
subcategory: redis-streams
tags:
  - redis
  - redis-streams
  - event-driven
  - message-queue
  - caching
  - streaming
technologies:
  - Redis 7+
  - Python redis-py
  - Go go-redis
  - Node.js ioredis
complexity: advanced
maturity: stable
tools:
  - redis-cli
  - python
dependencies:
  - redis >= 5.0.0
---
# Redis Streams Event Processing & Consumer Groups Architecture

## Overview

A definitive production engineering reference for architecting high-throughput, ordered, and fault-tolerant event streams using Redis Streams. This skill instructs AI agents on appending structured events (`XADD`), orchestrating competing consumer groups (`XREADGROUP`), inspecting and acknowledging processed messages (`XACK`), reclaiming crashed worker messages using `XAUTOCLAIM`, and controlling memory growth via approximate stream trimming (`MAXLEN ~`).

## When to Use

- Building distributed task or event processing systems requiring Kafka-like consumer groups without running heavy JVM/Zookeeper/KRaft clusters.
- Real-time audit log streaming where event ordering and message replay are required.
- Coordinating asynchronous worker pools where each event must be processed by exactly one worker in a consumer group.
- Processing up to hundreds of thousands of events per second with sub-millisecond dispatch.

## When NOT to Use

- Ephemeral pub/sub where missed messages on disconnect are tolerable (use Redis Pub/Sub).
- Multi-terabyte long-term message retention spanning months (use Apache Kafka or AWS Kinesis).

## Inputs & Prerequisites

- Redis 7.0+ server.
- Redis client library (`redis-py` for Python, `go-redis` for Go).
- Connection parameters (`REDIS_URL`).

## Core Workflow

### 1. Appending Events with Approximate Trimming (`XADD`)
Produce structured events while capping total stream memory:

```python
import redis
import time
import json

r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)

STREAM_NAME = "events:orders"

def publish_order_event(order_id: str, action: str, data: dict) -> str:
    """
    XADD appends an entry to the stream.
    maxlen=100000 with approximate=True ('~') keeps memory bounded
    without incurring high CPU costs on every append.
    """
    message_id = r.xadd(
        name=STREAM_NAME,
        fields={
            "order_id": order_id,
            "action": action,
            "payload": json.dumps(data),
            "timestamp": str(int(time.time()))
        },
        maxlen=100000,
        approximate=True
    )
    return message_id
```

### 2. Creating Consumer Groups & Consuming Messages (`XREADGROUP`)
Initialize a persistent consumer group and read new unassigned entries:

```python
GROUP_NAME = "order_workers_group"

def initialize_consumer_group():
    try:
        # Create group starting from beginning ('0') or new events only ('$')
        r.xgroup_create(name=STREAM_NAME, groupname=GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            pass # Group already exists
        else:
            raise e

def run_consumer_worker(worker_id: str):
    initialize_consumer_group()
    print(f"Worker {worker_id} started listening on {STREAM_NAME}...")

    while True:
        # Read up to 10 new messages assigned to this consumer
        entries = r.xreadgroup(
            groupname=GROUP_NAME,
            consumername=worker_id,
            streams={STREAM_NAME: ">"}, # '>' means unread messages
            count=10,
            block=2000 # Wait up to 2 seconds for new messages
        )

        if not entries:
            continue

        for stream, messages in entries:
            for msg_id, fields in messages:
                try:
                    # Execute business processing
                    process_event(msg_id, fields)
                    # Acknowledge message upon successful completion
                    r.xack(STREAM_NAME, GROUP_NAME, msg_id)
                except Exception as exc:
                    print(f"Error processing {msg_id}: {exc}. Left in PEL for auto-claim.")

def process_event(msg_id: str, fields: dict):
    print(f"Processing order: {fields['order_id']} action: {fields['action']}")
```

### 3. Reclaiming Abandoned Messages (`XAUTOCLAIM`)
Reclaim and reassign messages from crashed workers that have remained in the Pending Entries List (PEL) for over 60 seconds:

```python
def reclaim_abandoned_messages(worker_id: str):
    """
    Scans the Pending Entries List (PEL) for messages idle > 60000ms
    and transfers ownership to this worker.
    """
    start_id = "0-0"
    while True:
        next_id, claimed_messages, deleted_ids = r.xautoclaim(
            name=STREAM_NAME,
            groupname=GROUP_NAME,
            consumername=worker_id,
            min_idle_time=60000, # 60 seconds
            start_id=start_id,
            count=10
        )

        for msg_id, fields in claimed_messages:
            try:
                process_event(msg_id, fields)
                r.xack(STREAM_NAME, GROUP_NAME, msg_id)
            except Exception as e:
                print(f"Failed reclaimed message {msg_id}: {e}")

        if next_id == "0-0":
            break
        start_id = next_id
```

## Best Practices & Failure Modes

1. **Unacknowledged Message Memory Leak**: Failing to call `XACK` on processed messages leaves entries permanently in the Pending Entries List (PEL), consuming Redis RAM indefinitely. Always acknowledge processed messages.
2. **Missing `approximate=True` on `MAXLEN`**: Running exact trimming (`MAXLEN 100000`) forces Redis to reallocate and compact radical tree nodes on every write. Always use approximate trimming (`MAXLEN ~ 100000`) for 10x higher write throughput.
3. **Poison Pill Crash Loops**: If an unprocessable message crashes workers, `XAUTOCLAIM` will repeatedly assign it to surviving workers. Inspect the delivery count in `XPENDING` and route messages with > 5 attempts to a Dead Letter Stream.

## Verification & Testing

- Inspect stream length and consumer groups via CLI:
  ```bash
  redis-cli XINFO STREAM events:orders
  redis-cli XINFO GROUPS events:orders
  ```
- Inspect Pending Entries List (PEL) summary:
  ```bash
  redis-cli XPENDING events:orders order_workers_group
  ```
