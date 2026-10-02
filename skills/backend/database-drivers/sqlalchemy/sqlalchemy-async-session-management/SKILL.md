---
name: sqlalchemy-async-session-management
description: "Use this skill when architecting asynchronous database access layers in Python using SQLAlchemy 2.0+ and asyncpg. It guides the agent through AsyncEngine configuration, connection pooling with pool_pre_ping, scoped async session lifecycles, eager loading strategies (selectinload vs joinedload), and atomic transaction context managers."
domain: backend
category: database-drivers
subcategory: sqlalchemy
tags:
  - sqlalchemy
  - asyncio
  - python
  - asyncpg
  - orm
  - database
  - postgresql
technologies:
  - SQLAlchemy 2.0+
  - asyncpg
  - Python asyncio
  - PostgreSQL
  - Pydantic
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - sqlalchemy >= 2.0.25
  - asyncpg >= 0.29.0
---
# SQLAlchemy 2.0 Async Session Management & Performance Architecture

## Overview

A definitive engineering guide for building high-performance, non-blocking database access layers using SQLAlchemy 2.0+ and `asyncpg`. This skill instructs AI agents on configuring the `AsyncEngine`, managing session lifecycles without connection leaks, mastering eager loading strategies to avoid `MissingGreenlet` errors, and executing atomic Unit-of-Work transactions.

## When to Use

- Building asynchronous microservices with FastAPI, Litestar, or BlackSheep backed by PostgreSQL.
- Eliminating synchronous blocking database calls in Python async event loops.
- Preventing `sqlalchemy.exc.MissingGreenlet: await_only() error` when navigating lazy-loaded relationships.
- Tuning connection pool parameters (`pool_size`, `max_overflow`, `pool_pre_ping`) for resilient reconnections.

## When NOT to Use

- Synchronous web applications (Django ORM or synchronous Flask).
- Raw SQL pipelines where lightweight drivers like `asyncpg` directly without an ORM are preferred for microsecond throughput.

## Inputs & Prerequisites

- Python 3.10+ with `asyncio`.
- PostgreSQL database running.
- Dependencies: `pip install "sqlalchemy[asyncio]>=2.0" asyncpg`.

## Core Workflow

### 1. Robust Engine & SessionFactory Factory
Configure `create_async_engine` with health checks and strict session scoping:

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, select
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://app_user:app_pass@localhost:5432/app_db"
)

# 1. Configure Async Engine with Pre-Ping and Bounded Pool
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,               # Maximum steady-state connections
    max_overflow=10,            # Temporary surge connections allowed
    pool_timeout=30,            # Seconds to wait for an available connection
    pool_pre_ping=True,         # Emits "SELECT 1" before checkout to prune dead connections
    pool_recycle=1800           # Recycle connections every 30 minutes
)

# 2. Async Sessionmaker
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,     # CRITICAL: Prevents MissingGreenlet on post-commit attribute access
    autoflush=False
)

# 3. Dependency for FastAPI / Request Lifecycles
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 2. Avoiding `MissingGreenlet` with Eager Loading (`selectinload`)
In async SQLAlchemy, navigating unloaded relationships synchronously raises `MissingGreenlet`. Always specify eager loading explicitly:

```python
from sqlalchemy.orm import selectinload, joinedload

class Base(DeclarativeBase):
    pass

class CustomerModel(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    orders: Mapped[list["OrderModel"]] = relationship(back_populates="customer")

class OrderModel(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    total_amount: Mapped[int] = mapped_column(Integer)
    customer: Mapped[CustomerModel] = relationship(back_populates="orders")

async def get_customer_with_orders(session: AsyncSession, customer_id: int) -> CustomerModel | None:
    # Use selectinload for 1:N collections (executes optimized 2-step SELECT IN query)
    stmt = (
        select(CustomerModel)
        .where(CustomerModel.id == customer_id)
        .options(selectinload(CustomerModel.orders))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
```

### 3. Atomic Transaction Context Manager
Ensure operations across multiple models are atomic:

```python
async def transfer_balance(session: AsyncSession, from_id: int, to_id: int, amount: int):
    async with session.begin():  # Manages BEGIN / COMMIT / ROLLBACK automatically
        from_stmt = select(CustomerModel).where(CustomerModel.id == from_id).with_for_update()
        to_stmt = select(CustomerModel).where(CustomerModel.id == to_id).with_for_update()

        from_cust = (await session.execute(from_stmt)).scalar_one()
        to_cust = (await session.execute(to_stmt)).scalar_one()

        # Update entities
        # from_cust.balance -= amount
        # to_cust.balance += amount
        # Automatically committed on block exit, or rolled back on exception
```

## Best Practices & Failure Modes

1. **`expire_on_commit=True` Trap**: By default in SQLAlchemy, attributes are expired after commit. Accessing `customer.name` after commit in async mode triggers a lazy load without an active greenlet, crashing the application. Always set `expire_on_commit=False`.
2. **Missing `pool_pre_ping`**: If a cloud database (AWS RDS, Neon) drops idle connections, subsequent requests fail with `asyncpg.exceptions.ConnectionDoesNotExistError`. Always enable `pool_pre_ping=True`.
3. **Session Leaks in Task Groups**: Never share a single `AsyncSession` instance across parallel `asyncio.gather` tasks. An `AsyncSession` is not thread-safe or concurrent-task-safe. Each concurrent coroutine must own its own session.

## Verification & Testing

- Test session lifecycle and relationship loading:
  ```python
  import pytest

  @pytest.mark.asyncio
  async def test_session_eager_loading():
      async with AsyncSessionFactory() as session:
          customer = await get_customer_with_orders(session, 1)
          if customer:
              # Accessing orders should NOT raise MissingGreenlet
              assert isinstance(customer.orders, list)
  ```
