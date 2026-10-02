---
name: celery-distributed-task-processing
description: "Use this skill when designing, configuring, and operating asynchronous distributed task queues using Celery in Python. It covers broker connection tuning (Redis/RabbitMQ), exponential backoff retry strategies, task canvas workflows (chains, groups, chords), task deduplication, and worker concurrency optimization."
domain: backend
category: background-tasks
subcategory: celery
tags:
  - celery
  - python
  - background-tasks
  - redis
  - rabbitmq
  - distributed-systems
technologies:
  - Celery 5+
  - Redis
  - RabbitMQ
  - Python
  - Flower
complexity: advanced
maturity: stable
tools:
  - celery
  - python
dependencies:
  - celery >= 5.3.0
  - redis >= 5.0.0
---
# Celery Distributed Task Processing & Canvas Architecture

## Overview

A definitive production engineering reference for building scalable, resilient asynchronous background processing pipelines using Celery in Python. This skill instructs AI agents on broker connection optimization, reliable error recovery with exponential jitter, composing complex execution graphs using Celery Canvas primitives (`chain`, `group`, `chord`), task idempotency, and concurrency model tuning (prefork vs gevent).

## When to Use

- Offloading long-running jobs (video encoding, report generation, PDF exports, batch emails) outside HTTP request-response cycles.
- Coordinating multi-step distributed workflows where steps depend on the results of concurrent child tasks.
- Enforcing rate limits on third-party API integrations across multiple worker nodes.
- Handling transient network or service failures with exponential backoff retries.

## When NOT to Use

- High-frequency microsecond tasks (< 1ms) where queue serialization and network latency overhead are unacceptable.
- Simple synchronous multi-threading within a single process.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Broker running (Redis 7+ or RabbitMQ 3.12+).
- Result backend configured (Redis or PostgreSQL).

## Core Workflow

### 1. Robust Celery Configuration
Configure Celery with late acknowledgments and worker prefetch limits to prevent lost tasks on worker crashes:

```python
from celery import Celery
import os

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app = Celery("app_tasks", broker=BROKER_URL, backend=RESULT_BACKEND)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Reliability settings
    task_acks_late=True,                 # Acknowledge task AFTER completion, preventing loss if worker dies
    task_reject_on_worker_lost=True,     # Requeue task if worker process terminates unexpectedly
    worker_prefetch_multiplier=1,        # Stop workers from hoarding tasks; promotes fair distribution
    
    # Rate Limiting & Routing
    task_routes={
        "app_tasks.emails.*": {"queue": "emails_queue"},
        "app_tasks.reports.*": {"queue": "reports_queue"},
    },
    result_expires=86400                 # Results expire in 24 hours
)
```

### 2. Resilient Task with Exponential Backoff
Implement automatic retries with jitter and custom exception handling:

```python
import random
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class TransientNetworkError(Exception):
    pass

@app.task(
    bind=True,
    max_retries=5,
    autoretry_for=(TransientNetworkError,),
    retry_backoff=True,         # Exponential backoff: 2s, 4s, 8s, 16s...
    retry_backoff_max=300,      # Max delay 5 minutes
    retry_jitter=True           # Adds randomized jitter to delay
)
def process_webhook_notification(self, webhook_url: str, payload: dict):
    logger.info(f"Dispatching webhook to {webhook_url} (Attempt {self.request.retries + 1})")
    try:
        # Simulate network request
        # response = requests.post(webhook_url, json=payload, timeout=5)
        # response.raise_for_status()
        return {"status": "delivered", "url": webhook_url}
    except Exception as exc:
        logger.warning(f"Webhook dispatch failed: {exc}. Retrying...")
        raise TransientNetworkError(exc)
```

### 3. Celery Canvas Workflows: Chain, Group, and Chord
Compose complex asynchronous processing graphs:

```python
from celery import chain, group, chord

@app.task
def fetch_chunk(batch_id: int):
    return [10 * batch_id + i for i in range(5)]

@app.task
def process_item(item: int):
    return item * 2

@app.task
def aggregate_results(results: list):
    return sum(results)

def orchestrate_batch_pipeline():
    """
    A Chord executes a Group of tasks in parallel, and passes
    all their results to a final Callback task once every task completes.
    """
    # Parallel group: process 4 items concurrently
    parallel_jobs = group(process_item.s(i) for i in range(10))
    
    # Chord: Run group in parallel, then invoke aggregate_results with output list
    pipeline = chord(parallel_jobs)(aggregate_results.s())
    return pipeline.id
```

## Best Practices & Failure Modes

1. **Passing Heavy Objects as Task Arguments**: Never pass large database querysets, files, or model instances as arguments (`process_order.delay(order_instance)`). Objects become stale while waiting in queue. Pass only lightweight primary keys (`order_id: int`) and re-query fresh state in the worker.
2. **Missing `task_acks_late=True`**: With default early ACKs, Celery acknowledges the message immediately upon receiving it. If the worker process runs out of memory or gets SIGKILL-ed during task execution, the job is permanently lost.
3. **Deadlocks in Synchronous Subtasks (`task.get()`)**: Calling `.get()` inside a running task to wait for another task blocks a worker concurrency slot. If all worker slots are waiting on subtasks, the queue deadlocks completely. Always use Canvas `chain` or `chord` instead of synchronous waiting.

## Verification & Testing

- Run Celery worker with event monitoring:
  ```bash
  celery -A app_tasks worker --loglevel=INFO --concurrency=4 -E
  ```
- Inspect active queues and worker health via CLI:
  ```bash
  celery -A app_tasks inspect ping
  celery -A app_tasks inspect active
  ```
- Launch Flower web dashboard for real-time visual inspection:
  ```bash
  celery -A app_tasks flower --port=5555
  ```
