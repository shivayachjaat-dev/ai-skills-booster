---
name: rabbitmq-reliable-messaging-patterns
description: "Use this skill when designing, building, and operating mission-critical message queuing architectures with RabbitMQ (AMQP 0-9-1). It guides the agent through publisher confirms (ACK/NACK), queue and message durability, dead letter exchanges (DLX) for poisoned messages, consumer manual acknowledgments with prefetch limits, and consumer idempotency."
domain: backend
category: message-queues
subcategory: rabbitmq
tags:
  - rabbitmq
  - amqp
  - message-queues
  - event-driven
  - dead-letter-queue
  - pika
technologies:
  - RabbitMQ
  - AMQP 0-9-1
  - Python Pika
  - Erlang
  - Docker
complexity: advanced
maturity: stable
tools:
  - rabbitmqctl
  - python
dependencies:
  - pika >= 1.3.0
---
# RabbitMQ Reliable Messaging & AMQP Architecture

## Overview

A production engineering standard for architecting fault-tolerant, zero-message-loss systems with RabbitMQ. This skill guides AI agents in establishing robust AMQP topologies: durable exchanges and queues, publisher confirms with transactional verification, Dead Letter Exchanges (DLX) for poison message handling, consumer QoS prefetch rate limiting, and idempotent deduplication.

## When to Use

- Building asynchronous task processing, distributed workers, or order processing pipelines.
- Guaranteeing at-least-once message delivery where message loss is unacceptable (e.g. financial transactions, invoicing).
- Isolating and analyzing malformed or unprocessable messages using Dead Letter Queues (DLQ).
- Preventing memory overload in consumers using backpressure via `basic_qos(prefetch_count=N)`.

## When NOT to Use

- Massive real-time telemetry streaming (millions of events/sec) where log replay, partitioning, and long-term event retention are required (use `kafka-event-driven-architecture`).
- Ephemeral in-memory pub/sub where losing messages upon consumer disconnection is acceptable (use Redis Pub/Sub).

## Inputs & Prerequisites

- RabbitMQ 3.12+ cluster.
- AMQP client library (`pika` for Python, `amqplib` for Node.js, `streadway/amqp` for Go).
- Connection URI: `amqp://guest:guest@localhost:5672/%2F`.

## Core Workflow

### 1. Robust Topology Declaration (Durable + DLX)
Declare primary exchange, queue, and dead-letter exchange:

```python
import pika

def setup_rabbitmq_topology(channel: pika.adapters.blocking_connection.BlockingChannel):
    # 1. Declare Dead Letter Exchange and Queue
    channel.exchange_declare(
        exchange="orders.dlx",
        exchange_type="direct",
        durable=True
    )
    channel.queue_declare(
        queue="orders.dlq",
        durable=True,
        arguments={
            "x-queue-type": "quorum"  # Raft-backed quorum queue for high availability
        }
    )
    channel.queue_bind(exchange="orders.dlx", queue="orders.dlq", routing_key="orders.failed")

    # 2. Declare Primary Exchange
    channel.exchange_declare(
        exchange="orders.exchange",
        exchange_type="topic",
        durable=True
    )

    # 3. Declare Primary Queue with DLX Configuration
    channel.queue_declare(
        queue="orders.process.queue",
        durable=True,
        arguments={
            "x-queue-type": "quorum",
            "x-dead-letter-exchange": "orders.dlx",
            "x-dead-letter-routing-key": "orders.failed",
            "x-delivery-limit": 3 # Move to DLQ after 3 failed redeliveries
        }
    )
    channel.queue_bind(
        exchange="orders.exchange",
        queue="orders.process.queue",
        routing_key="orders.created"
    )
```

### 2. Reliable Publisher with Confirms
Enable publisher confirms to ensure broker persistence before acknowledging to caller:

```python
import json
import pika

def publish_order(connection_params: pika.ConnectionParameters, order_data: dict) -> bool:
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    # Enable publisher confirms
    channel.confirm_delivery()
    
    body = json.dumps(order_data).encode("utf-8")
    
    try:
        channel.basic_publish(
            exchange="orders.exchange",
            routing_key="orders.created",
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent, # Persistent on disk
                content_type="application/json",
                message_id=str(order_data["order_id"]),
                timestamp=int(order_data.get("timestamp", 0))
            ),
            mandatory=True # Ensures message is routed to at least one queue
        )
        return True
    except pika.exceptions.UnroutableError:
        # Message was returned because no queue bound to routing key
        return False
    except pika.exceptions.NackError:
        # Broker failed to persist message
        return False
    finally:
        connection.close()
```

### 3. Reliable Consumer with Manual ACK and Prefetch
Control worker concurrency and prevent consumer starvation:

```python
import pika
import json
import logging

logger = logging.getLogger("order-worker")

def process_order_message(ch, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
        logger.info(f"Processing order: {payload.get('order_id')}")
        
        # Idempotent business execution
        # execute_order_processing(payload)

        # Acknowledge success
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing order {properties.message_id}: {e}")
        # Reject and do NOT requeue immediately -> triggers DLX
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def run_consumer(connection_params: pika.ConnectionParameters):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    # Prefetch count: Process 10 messages concurrently per worker
    channel.basic_qos(prefetch_count=10)

    channel.basic_consume(
        queue="orders.process.queue",
        on_message_callback=process_order_message,
        auto_ack=False # STRICTLY manual ACK
    )
    
    logger.info("Worker waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
```

## Best Practices & Failure Modes

1. **Auto-ACK (`auto_ack=True`) Hazard**: If `auto_ack=True` is enabled, RabbitMQ removes the message from memory the moment it is written to the socket. If the worker crashes mid-execution, the message is permanently lost. Always use manual acknowledgments.
2. **Missing `basic_qos` Prefetch Limit**: Without prefetch limits, RabbitMQ pushes all queued messages into consumer RAM at startup, leading to out-of-memory crashes and uneven load distribution. Set `prefetch_count` between 10 and 50.
3. **Poison Message Requeue Loop**: Calling `basic_nack(requeue=True)` on a message with corrupted JSON causes an infinite crash loop, consuming 100% CPU. Always route poisoned messages to a DLQ via `requeue=False`.

## Verification & Testing

- Check queue depths and message readiness via CLI:
  ```bash
  rabbitmqctl list_queues name messages_ready messages_unacknowledged consumers
  ```
- Inspect DLQ messages:
  ```bash
  rabbitmqadmin get queue=orders.dlq count=10 requeue=false
  ```
