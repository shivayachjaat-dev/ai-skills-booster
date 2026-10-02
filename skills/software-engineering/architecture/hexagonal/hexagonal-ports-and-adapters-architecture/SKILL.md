---
name: hexagonal-ports-and-adapters-architecture
description: "Use this skill when architecting backend systems using Hexagonal Architecture (Ports and Adapters / Clean Architecture). It guides the agent through domain model isolation, designing driving (inbound) and driven (outbound) port interfaces, implementing swappable adapters (FastAPI, CLI, PostgreSQL, Mock), and structuring dependency injection."
domain: software-engineering
category: architecture
subcategory: hexagonal
tags:
  - hexagonal-architecture
  - clean-architecture
  - ports-and-adapters
  - domain-driven-design
  - software-architecture
technologies:
  - Python
  - TypeScript
  - Domain-Driven Design
  - Dependency Injection
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Hexagonal Architecture (Ports & Adapters) Standard

## Overview

A definitive software architecture guide for designing maintainable, long-lived applications using Hexagonal Architecture (Ports and Adapters). Grounded in the principle of Dependency Inversion, this skill instructs AI agents on isolating pure domain business logic from external frameworks, databases, and third-party APIs. By modeling interactions through Driving (Inbound) and Driven (Outbound) ports, systems become trivially testable without mocks, and infrastructure components can be swapped without altering business rules.

## When to Use

- Building enterprise applications where business logic must outlive database choices, web frameworks, and external APIs.
- Systems requiring ultra-fast unit testing of core business rules without spinning up databases, Docker containers, or network mocks.
- Microservices that must be invoked via multiple entrypoints simultaneously (e.g. REST API, CLI tool, Kafka consumer, and cron jobs).
- Implementing Domain-Driven Design (DDD) aggregates and entities cleanly.

## When NOT to Use

- Simple CRUD microservices or prototypes where layer indirection introduces unnecessary boilerplate.
- Small automation scripts or single-file utilities.

## Inputs & Prerequisites

- Object-Oriented programming language supporting abstract interfaces (Python `typing.Protocol` / `abc`, TypeScript, Java, or Go).
- Clear understanding of the Dependency Inversion Principle.

## Core Workflow

### 1. Hexagonal Layer Hierarchy
```text
src/
├── domain/                  # 1. Pure Domain (Zero external dependencies)
│   ├── entities.py          # Entities & Value Objects
│   └── exceptions.py        # Domain-specific business exceptions
├── application/             # 2. Application Core (Use Cases & Ports)
│   ├── ports/
│   │   ├── inbound.py       # Driving Ports (Use case interfaces)
│   │   └── outbound.py      # Driven Ports (Repository / Service interfaces)
│   └── use_cases.py         # Business workflow orchestrators
└── infrastructure/          # 3. Adapters (Implementation details)
    ├── adapters/
    │   ├── api/             # Driving Adapter (FastAPI / Express)
    │   ├── db/              # Driven Adapter (PostgreSQL / SQLAlchemy)
    │   └── payments/        # Driven Adapter (Stripe client)
    └── container.py         # Dependency Injection Composition Root
```

### 2. Defining Ports & Pure Domain
The core never imports frameworks like FastAPI or SQLAlchemy:

```python
# application/ports/outbound.py (Driven Ports)
from typing import Protocol, Optional
from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class Order:
    id: str
    customer_id: str
    total_cents: int
    status: str

class OrderRepositoryPort(Protocol):
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        ...
    async def save(self, order: Order) -> None:
        ...

class PaymentGatewayPort(Protocol):
    async def process_payment(self, order_id: str, amount_cents: int) -> bool:
        ...
```

```python
# application/use_cases.py (Application Service)
from application.ports.outbound import OrderRepositoryPort, PaymentGatewayPort, Order

class CheckoutOrderUseCase:
    def __init__(self, order_repo: OrderRepositoryPort, payment_gateway: PaymentGatewayPort):
        self.order_repo = order_repo
        self.payment_gateway = payment_gateway

    async def execute(self, order_id: str) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} does not exist.")
        if order.status == "PAID":
            raise ValueError("Order is already paid.")

        success = await self.payment_gateway.process_payment(order.id, order.total_cents)
        if not success:
            raise RuntimeError("Payment processing failed.")

        updated_order = Order(
            id=order.id,
            customer_id=order.customer_id,
            total_cents=order.total_cents,
            status="PAID"
        )
        await self.order_repo.save(updated_order)
        return updated_order
```

### 3. Implementing Adapters (Infrastructure)
Implement the driven ports with concrete technologies:

```python
# infrastructure/adapters/db/in_memory_order_repo.py (Driven Adapter for Testing)
from application.ports.outbound import OrderRepositoryPort, Order

class InMemoryOrderRepository(OrderRepositoryPort):
    def __init__(self):
        self._storage = {}

    async def get_by_id(self, order_id: str) -> Order | None:
        return self._storage.get(order_id)

    async def save(self, order: Order) -> None:
        self._storage[order.id] = order
```

```python
# infrastructure/adapters/api/fastapi_controller.py (Driving Adapter)
from fastapi import FastAPI, Depends, HTTPException
from application.use_cases import CheckoutOrderUseCase

def create_checkout_router(use_case: CheckoutOrderUseCase):
    app = FastAPI()

    @app.post("/orders/{order_id}/checkout")
    async def checkout_endpoint(order_id: str):
        try:
            order = await use_case.execute(order_id)
            return {"status": "success", "order_id": order.id, "order_status": order.status}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=502, detail=str(e))

    return app
```

## Best Practices & Failure Modes

1. **Domain Model Framework Contamination**: Allowing ORM annotations (`@Column`, `mapped_column`) or API validation types (`BaseModel`) inside the inner domain layer violates the boundary. Keep domain entities pure dataclasses or standard classes.
2. **Adapter Direct Communication**: An adapter (e.g. FastAPI route) must never import or call another adapter (e.g. Postgres repository) directly. All interactions must pass through the Application Use Case port.
3. **Over-Engineering Anemic CRUD**: Applying full hexagonal ports and adapters to trivial endpoints that merely read a row from SQL and serialize it to JSON adds unnecessary layer overhead. Reserve hexagonal patterns for rich business domains.

## Verification & Testing

- Write fast unit tests verifying use case business logic with zero database dependencies:
  ```python
  import pytest

  class FakePaymentGateway:
      async def process_payment(self, order_id: str, amount_cents: int) -> bool:
          return True

  @pytest.mark.asyncio
  async def test_order_checkout_success():
      repo = InMemoryOrderRepository()
      gateway = FakePaymentGateway()
      use_case = CheckoutOrderUseCase(order_repo=repo, payment_gateway=gateway)

      await repo.save(Order("ord-1", "cust-1", 5000, "PENDING"))
      result = await use_case.execute("ord-1")

      assert result.status == "PAID"
      saved = await repo.get_by_id("ord-1")
      assert saved.status == "PAID"
  ```
