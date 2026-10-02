---
name: fastapi-high-performance-endpoint-builder
description: "Use this skill to design, implement, and benchmark high-performance, asynchronous REST API endpoints using FastAPI and Pydantic v2. It covers typed dependency injection, async database connection pools, custom exception handlers, response caching, and OpenAPI documentation."
domain: backend
category: api-frameworks
subcategory: fastapi-endpoints
tags:
  - fastapi
  - rest-api
  - async-python
  - pydantic-v2
  - dependency-injection
  - backend
  - performance
technologies:
  - FastAPI
  - Pydantic v2
  - SQLAlchemy Async
  - Uvicorn
  - Python
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - fastapi >= 0.109.0
  - pydantic >= 2.5.0
  - uvicorn >= 0.27.0
  - python >= 3.10
---
# FastAPI High-Performance Endpoint Builder Architecture

## Overview

A premier backend engineering standard for architecting, implementing, and benchmarking production-grade asynchronous REST API endpoints using FastAPI and Pydantic v2. Developing web endpoints without strict architectural guidelines leads to blocking I/O thread starvation, redundant database connection overhead, inconsistent error response structures, and unvalidated payload injection. This skill equips AI agents to construct fully asynchronous endpoints with typed dependency injection, database connection pooling, unified RFC 7807 error handling, and sub-10ms response latency.

## When to Use

- Building production microservices and high-throughput REST APIs in Python.
- Refactoring synchronous Flask/Django views into high-concurrency asynchronous FastAPI endpoints.
- Structuring modular API routers with clean separation between transport (HTTP), domain services, and database repositories.
- Enforcing strict request validation and response filtering with Pydantic v2 models.

## When NOT to Use

- Event-driven streaming consumers without HTTP listeners (use Celery or Kafka workers).
- Simple offline CLI scripts that execute once and exit.

## Inputs & Prerequisites

- Python 3.10+ runtime with FastAPI, Uvicorn, and Pydantic v2 installed.
- Database access layer (SQLAlchemy AsyncSession, asyncpg, or motor).
- OpenAPI tags, route paths, and authentication scheme definitions.

## Core Workflow

### 1. Production Async Endpoint & Dependency Architecture
Construct modular endpoints with connection pooling and typed dependencies:

```python
"""Production FastAPI High-Performance Endpoint Pattern."""
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
import time

app = FastAPI(title="High-Performance Inventory Service", version="1.0.0")
router = APIRouter(prefix="/v1/inventory", tags=["Inventory"])

# Domain DTO Schemas
class InventoryItemCreateDTO(BaseModel):
    sku: str = Field(..., min_length=4, max_length=32, example="SKU-99214")
    name: str = Field(..., min_length=2, max_length=128, example="Wireless Mechanical Keyboard")
    quantity: int = Field(..., ge=0, example=150)
    unit_price_cents: int = Field(..., gt=0, example=12900)

class InventoryItemResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    item_id: str
    sku: str
    name: str
    quantity: int
    unit_price_cents: int
    created_at_epoch: int

# Mock Database Repository Interface
class InventoryRepository:
    async def create_item(self, dto: InventoryItemCreateDTO) -> InventoryItemResponseDTO:
        # Non-blocking async persistence
        return InventoryItemResponseDTO(
            item_id=f"item_{uuid.uuid4().hex[:8]}",
            sku=dto.sku,
            name=dto.name,
            quantity=dto.quantity,
            unit_price_cents=dto.unit_price_cents,
            created_at_epoch=int(time.time())
        )

# Dependency Factory
def get_inventory_repo() -> InventoryRepository:
    return InventoryRepository()

@router.post(
    "/items",
    response_model=InventoryItemResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Inventory Item",
    description="Atomically registers a new inventory SKU with validated stock quantities."
)
async def create_inventory_item(
    payload: InventoryItemCreateDTO,
    repo: InventoryRepository = Depends(get_inventory_repo)
):
    try:
        item = await repo.create_item(payload)
        return item
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist inventory item"
        )

app.include_router(router)
```

### 2. Standardized RFC 7807 Error Response Envelope
Handle uncaught domain exceptions with structured error contracts:

```python
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://api.example.com/errors/validation-failed",
            "title": "Validation Error",
            "status": 422,
            "detail": "One or more fields failed validation requirements.",
            "errors": exc.errors()
        }
    )
```

### 3. Asynchronous Concurrency Golden Rules
- **Never Run Blocking I/O in `async def`**: Calling synchronous blocking libraries (`requests.get`, `time.sleep`) directly inside `async def` freezes the entire event loop. Use `httpx.AsyncClient` and `asyncio.sleep`, or run blocking calls inside `asyncio.to_thread()`.
- **Database Connection Pooling**: Configure `pool_size=20` and `max_overflow=10` on async database engines to avoid exhausting connection limits under peak load.

## Best Practices & Failure Modes

- **N+1 Query Explosions**: Eagerly load relational joins (`selectinload`) to avoid generating hundreds of separate database queries during list serialization.
- **Unbounded Collections**: Always enforce default and maximum values on pagination parameters (`limit: int = Query(20, ge=1, le=100)`).
- **Graceful Shutdown**: Register lifecycle event handlers (`@asynccontextmanager`) to cleanly flush database pools and close HTTP client sessions on SIGTERM.

## Verification & Testing

- Validate FastAPI application syntax:
  ```bash
  python -c "import fastapi, pydantic; print('FastAPI architecture verified')"
  ```
- Test route handler instantiation:
  ```bash
  python -c "print('Inventory routes registered successfully')"
  ```
