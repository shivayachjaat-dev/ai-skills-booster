---
name: event-sourcing-and-cqrs-architecture
description: "Use this skill when architecting and implementing Event Sourcing and Command Query Responsibility Segregation (CQRS) systems. It guides the agent through aggregate root design, immutable append-only event streams, optimistic concurrency control via sequence numbers, read model projections, and snapshotting strategies."
domain: software-engineering
category: design-patterns
subcategory: event-sourcing
tags:
  - event-sourcing
  - cqrs
  - architecture
  - domain-driven-design
  - event-driven
  - aggregates
technologies:
  - Python
  - PostgreSQL
  - EventStoreDB
  - Kafka
  - Domain-Driven Design
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Event Sourcing & CQRS Enterprise Architecture

## Overview

A comprehensive architectural standard for building audit-compliant, fault-tolerant systems using Event Sourcing and Command Query Responsibility Segregation (CQRS). This skill guides AI agents in modeling state changes as immutable domain events, enforcing optimistic concurrency control, rebuilding Aggregate Root states from event streams, generating read-model projections, and optimizing replay performance via snapshotting.

## When to Use

- Systems requiring complete, tamper-evident audit logs (banking, healthcare, legal, trading).
- Applications with high write contention where traditional row-locking degrades throughput.
- Architectures where business domains benefit from temporal queries (time travel debugging, state reconstruction at any historical point).
- Decoupling complex read views from transactional write operations (CQRS).

## When NOT to Use

- Simple CRUD applications where entity history has zero business or regulatory value.
- Small teams without distributed systems experience, due to eventual consistency complexities.

## Inputs & Prerequisites

- Append-only event store (PostgreSQL event table, EventStoreDB, or Kafka).
- Domain-Driven Design (DDD) concepts: Aggregate Root, Command, Domain Event, Projection.

## Core Workflow

### 1. Domain Events & Aggregate Root Pattern
Model domain events as immutable dataclasses and define state transitions:

```python
from dataclasses import dataclass, field
from typing import List, Optional
import uuid
import datetime

# --- Domain Events ---
@dataclass(frozen=True)
class AccountCreated:
    account_id: str
    owner_id: str
    currency: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass(frozen=True)
class MoneyDeposited:
    account_id: str
    amount: float
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass(frozen=True)
class MoneyWithdrawn:
    account_id: str
    amount: float
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

# --- Aggregate Root ---
class BankAccountAggregate:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance: float = 0.0
        self.owner_id: Optional[str] = None
        self.version: int = 0
        self.uncommitted_events: List[object] = []

    # Command: Open Account
    def create(self, owner_id: str, currency: str):
        if self.version > 0:
            raise ValueError("Account already exists.")
        event = AccountCreated(account_id=self.account_id, owner_id=owner_id, currency=currency)
        self._apply_and_record(event)

    # Command: Deposit
    def deposit(self, amount: float):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        event = MoneyDeposited(account_id=self.account_id, amount=amount)
        self._apply_and_record(event)

    # Command: Withdraw
    def withdraw(self, amount: float):
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")
        if self.balance < amount:
            raise ValueError(f"Insufficient funds: Balance is {self.balance}, requested {amount}.")
        event = MoneyWithdrawn(account_id=self.account_id, amount=amount)
        self._apply_and_record(event)

    # State Mutator (Internal Replay)
    def apply_event(self, event: object):
        if isinstance(event, AccountCreated):
            self.owner_id = event.owner_id
        elif isinstance(event, MoneyDeposited):
            self.balance += event.amount
        elif isinstance(event, MoneyWithdrawn):
            self.balance -= event.amount
        self.version += 1

    def _apply_and_record(self, event: object):
        self.apply_event(event)
        self.uncommitted_events.append(event)
```

### 2. Append-Only Event Store with Concurrency Control
Enforce optimistic concurrency control to prevent split-brain aggregate state:

```sql
-- event_store_schema.sql
CREATE TABLE IF NOT EXISTS event_stream (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_id VARCHAR(64) NOT NULL,
    stream_version INT NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Enforce that version within an aggregate stream is strictly sequential
    CONSTRAINT uq_stream_version UNIQUE (stream_id, stream_version)
);
```

### 3. Read Model Projection (CQRS)
Project events asynchronously into a denormalized query table:

```python
class AccountSummaryProjection:
    def __init__(self, db_connection):
        self.conn = db_connection

    def handle(self, event: object):
        with self.conn.cursor() as cursor:
            if isinstance(event, AccountCreated):
                cursor.execute(
                    "INSERT INTO account_read_model (id, owner_id, current_balance) VALUES (%s, %s, 0.0)",
                    (event.account_id, event.owner_id)
                )
            elif isinstance(event, MoneyDeposited):
                cursor.execute(
                    "UPDATE account_read_model SET current_balance = current_balance + %s WHERE id = %s",
                    (event.amount, event.account_id)
                )
            elif isinstance(event, MoneyWithdrawn):
                cursor.execute(
                    "UPDATE account_read_model SET current_balance = current_balance - %s WHERE id = %s",
                    (event.amount, event.account_id)
                )
            self.conn.commit()
```

## Best Practices & Failure Modes

1. **Event Schema Evolution (Upcasting)**: Once an event is appended to the store, its schema is permanent. Never modify historical event payloads in place. Use upcasters to translate legacy event versions (v1 -> v2) on the fly during replay.
2. **Replay Performance Degradation**: Replaying an aggregate with 50,000 historical events takes seconds. Implement snapshots every 100 events: load snapshot at version 50,000, then replay remaining events since the snapshot.
3. **Optimistic Locking Collisions**: When concurrent writers attempt to append to the same aggregate version, the database unique constraint `(stream_id, stream_version)` raises an error. The application must reload the latest stream, re-verify business rules, and retry.

## Verification & Testing

- Test aggregate replay determinism:
  ```python
  # Replay test
  account = BankAccountAggregate("acc-123")
  events = [
      AccountCreated("acc-123", "user-1", "USD"),
      MoneyDeposited("acc-123", 100.0),
      MoneyWithdrawn("acc-123", 40.0)
  ]
  for e in events:
      account.apply_event(e)
  
  assert account.balance == 60.0
  assert account.version == 3
  ```
