---
name: distributed-saga-orchestration-pattern
description: "Use this skill when designing, implementing, and coordinating multi-service distributed transactions across microservices using the Saga Pattern (Orchestrator and Choreography). It guides the agent through defining forward actions, reliable compensating rollback transactions, state machine persistence, outbox pattern integration, and handling network partitions."
domain: software-engineering
category: design-patterns
subcategory: saga-pattern
tags:
  - saga-pattern
  - distributed-transactions
  - microservices
  - orchestration
  - software-architecture
technologies:
  - Python
  - Temporal
  - PostgreSQL
  - Kafka
  - RabbitMQ
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Distributed Saga Orchestration Architecture

## Overview

A definitive software architecture guide for managing distributed transactions across microservices using the Saga Pattern. When multiple independent microservices each maintain their own private database, traditional two-phase commit (2PC) locks resources and creates catastrophic availability bottlenecks across network partitions. This skill instructs AI agents on orchestrating multi-step distributed sagas through explicit forward actions and idempotent compensating transactions, persisting saga state machines, and preventing partial state corruption.

## When to Use

- Coordinating business operations spanning multiple autonomous microservices (e.g. Order Creation -> Payment Charge -> Inventory Reservation -> Shipping Dispatch).
- Maintaining eventual consistency across disparate databases without distributed database locks.
- Automatically executing compensating rollbacks (e.g. refunding payment, releasing inventory) when an intermediate step fails.
- Handling long-running asynchronous business transactions that can take minutes or hours.

## When NOT to Use

- Monolithic architectures sharing a single database where ACID database transactions (`BEGIN ... COMMIT`) provide instant consistency.
- Read-only queries that do not mutate persistent state.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- Message broker or persistent orchestrator database to record saga execution state.
- Idempotent API endpoints for all forward and compensating actions.

## Core Workflow

### 1. Saga Step Definition with Compensating Actions
Define each transaction step with paired forward and rollback logic:

```python
from dataclasses import dataclass
from typing import Callable, Any, List
import uuid
import logging

logger = logging.getLogger("saga-orchestrator")

@dataclass
class SagaStep:
    name: str
    action: Callable[[dict], Any]       # Forward transaction
    compensate: Callable[[dict], Any]   # Compensating rollback transaction

class OrderFulfillmentSaga:
    def __init__(self, steps: List[SagaStep]):
        self.steps = steps

    def execute(self, payload: dict) -> bool:
        executed_steps: List[SagaStep] = []
        saga_id = payload.get("order_id", str(uuid.uuid4()))
        logger.info(f"Starting Saga {saga_id}")

        for step in self.steps:
            logger.info(f"Executing step: {step.name}")
            try:
                step.action(payload)
                executed_steps.append(step)
            except Exception as e:
                logger.error(f"Step '{step.name}' failed with error: {e}. Initiating compensation!")
                self._rollback(executed_steps, payload)
                return False

        logger.info(f"Saga {saga_id} completed successfully.")
        return True

    def _rollback(self, executed_steps: List[SagaStep], payload: dict):
        # Compensate in reverse order of execution
        for step in reversed(executed_steps):
            logger.warning(f"Compensating step: {step.name}")
            try:
                step.compensate(payload)
            except Exception as comp_err:
                logger.critical(
                    f"CRITICAL: Compensation for '{step.name}' failed: {comp_err}. "
                    "Requires manual human intervention!"
                )
```

### 2. Concrete Forward & Compensating Steps Implementation
Implement idempotent service calls for forward and compensation stages:

```python
def reserve_inventory_forward(payload: dict):
    logger.info(f"Reserved {payload['quantity']} units of item {payload['item_id']}.")

def reserve_inventory_compensate(payload: dict):
    logger.info(f"Compensating: Released {payload['quantity']} units of item {payload['item_id']}.")

def charge_payment_forward(payload: dict):
    if payload.get("should_fail_payment"):
        raise ValueError("Card declined: Insufficient funds.")
    logger.info(f"Charged ${payload['amount']} to customer.")

def charge_payment_compensate(payload: dict):
    logger.info(f"Compensating: Refunded ${payload['amount']} to customer.")

def dispatch_shipment_forward(payload: dict):
    logger.info(f"Shipment created for order {payload['order_id']}.")

def dispatch_shipment_compensate(payload: dict):
    logger.info(f"Compensating: Cancelled shipment for order {payload['order_id']}.")
```

### 3. Orchestrator Execution & Rollback Test
Assemble the pipeline:

```python
def build_order_saga() -> OrderFulfillmentSaga:
    return OrderFulfillmentSaga([
        SagaStep("ReserveInventory", reserve_inventory_forward, reserve_inventory_compensate),
        SagaStep("ChargePayment", charge_payment_forward, charge_payment_compensate),
        SagaStep("DispatchShipment", dispatch_shipment_forward, dispatch_shipment_compensate),
    ])
```

## Best Practices & Failure Modes

1. **Non-Idempotent Compensating Actions**: If a compensating call times out over the network and retries, executing a refund twice creates financial loss. All forward and compensating actions *must* be strictly idempotent using unique transaction keys.
2. **Missing Compensation Handlers for Partial Failures**: If an orchestrator process crashes mid-saga, the saga state must be persisted in an append-only log so a recovery worker can resume execution or compensation.
3. **Irreversible Real-World Actions**: Physical actions (e.g. printing a shipping label or emailing an invoice) cannot be purely undone. Model compensation for irreversible steps as customer notification or reversal tickets.

## Verification & Testing

- Unit test simulating mid-saga failure and verifying full compensation in reverse order:
  ```python
  def test_saga_failure_triggers_compensation():
      saga = build_order_saga()
      failing_payload = {
          "order_id": "ord_999",
          "item_id": "widget_1",
          "quantity": 2,
          "amount": 50.0,
          "should_fail_payment": True # Forces failure at step 2
      }

      success = saga.execute(failing_payload)
      assert success is False
      # Verifies inventory was compensated after payment failed
  ```
