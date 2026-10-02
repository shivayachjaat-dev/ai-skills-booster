---
name: fastapi-async-api-design
description: "Use this skill when building high-performance, asynchronous REST APIs with FastAPI, Pydantic v2, and async database drivers. It guides the agent through dependency injection patterns, async/await event loop blocking prevention, structured error handlers, lifespan context managers, and OpenAPI schema generation."
domain: backend
category: fastapi
subcategory: async-architecture
tags:
  - fastapi
  - python
  - asyncio
  - backend
  - pydantic
  - rest-api
  - performance
technologies:
  - FastAPI
  - Python
  - Pydantic v2
  - SQLAlchemy 2.0
  - Uvicorn
complexity: advanced
maturity: stable
tools:
  - python
  - uvicorn
dependencies:
  - fastapi >= 0.110
  - pydantic >= 2.6
---
# FastAPI Async API Design

## Overview

A production-grade architectural guide for designing scalable, type-safe, asynchronous REST APIs using Python's FastAPI framework and Pydantic v2. Enforces non-blocking event loop execution, modular dependency injection hierarchies, lifecycle connection management, and declarative data validation.

## When to Use

- Building new backend microservices or REST API endpoints in Python.
- Refactoring legacy Flask or synchronous Django views to async FastAPI routers.
- Integrating high-throughput asynchronous databases (PostgreSQL via `asyncpg`, MongoDB via `motor`).
- Designing clean dependency injection patterns for authentication, database sessions, and configuration.

## When NOT to Use

- Pure CPU-bound mathematical operations or heavy machine learning model training (use background Celery workers or multiprocessing).
- Simple monolithic server-side HTML rendering without API consumers.

## Inputs & Prerequisites

- Python 3.10+ runtime.
- FastAPI and Pydantic v2 installed (`pip install fastapi uvicorn pydantic`).
- ASGI web server (Uvicorn or Granian).

## Core Workflow

### 1. Application Lifespan & Connection Management
Use modern async context managers for resource setup and teardown rather than deprecated `@app.on_event`:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connection pool, redis clients
    app.state.db_pool = await create_async_pool()
    yield
    # Shutdown: Close pools cleanly
    await app.state.db_pool.close()

app = FastAPI(title="Core Commerce Service", lifespan=lifespan)
```

### 2. Never Block the Asyncio Event Loop
- **The Golden Rule**: An `async def` route runs directly on the single-threaded asyncio event loop. Calling synchronous blocking I/O (e.g. `requests.get()`, `time.sleep()`, synchronous DB drivers) halts all concurrent requests across the entire server process!
- If an operation is async, use `await` with an async client (`httpx.AsyncClient`, `asyncpg`).
- If an operation is legacy synchronous/blocking, declare the endpoint with regular `def` (FastAPI automatically runs regular `def` routes in an external threadpool):
```python
# GOOD: Pure async I/O
@router.get("/data")
async def get_data(client: AsyncClient = Depends(get_http_client)):
    resp = await client.get("https://api.external.com/items")
    return resp.json()

# GOOD: Sync I/O running in external threadpool
@router.post("/legacy-process")
def process_sync_report(payload: ReportPayload):
    time.sleep(2)  # Does NOT block event loop
    return {"status": "processed"}
```

### 3. Pydantic v2 Declarative Schemas
Define strict input and response models:
```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    tier: str = Field(default="standard", pattern="^(standard|premium|enterprise)$")

    model_config = {
        "extra": "forbid",  # Reject unannounced fields
        "str_strip_whitespace": True
    }

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
```

### 4. Hierarchical Dependency Injection (`Depends`)
Compose modular authentication and database access:
```python
from fastapi import Depends, HTTPException, status

async def get_db_session(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        yield conn

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db_session)):
    user = await authenticate_token(token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

@router.get("/profile", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    return user
```

### 5. Global Exception Handlers & Standard Errors
Map domain exceptions to predictable HTTP status codes:
```python
@app.exception_handler(EntityNotFoundError)
async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": str(exc)}}
    )
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Background task required after sending response | Use FastAPI `BackgroundTasks` for lightweight email dispatch; use Celery/Redis for long-running batch jobs. |
| Streaming large file downloads | Use `StreamingResponse` with an async generator to avoid buffering gigabytes into memory. |
| Request body parsing performance | Keep Pydantic models compact and avoid heavy nested validation logic inside field validators. |

## Validation & Acceptance Criteria

- [ ] All async endpoints strictly avoid blocking synchronous I/O calls.
- [ ] Request models enforce Pydantic v2 schema constraints with extra fields forbidden.
- [ ] Database sessions injected via generator dependencies and closed upon completion.
- [ ] Global exception handlers return structured machine-readable error responses.
- [ ] Auto-generated Swagger UI (`/docs`) renders clean schemas and status codes.

## Failure Handling & Recovery

- If event loop lag spikes, use `asyncio.get_event_loop().slow_callback_duration` to identify rogue blocking calls.

## Expected Output & Artifacts

- Modular FastAPI router module.
- Type-safe Pydantic request and response schemas.
- Integration tests using `httpx.AsyncClient` with `ASGITransport`.

## Related Skills

- `api-and-interface-design`
- `api-rate-limiting-and-throttling`
- `postgres-query-performance-analysis`
