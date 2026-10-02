---
name: distributed-rate-limiting-token-bucket
description: "Use this skill when designing, implementing, and deploying high-performance distributed rate limiters using the Token Bucket and Sliding Window algorithms with Redis and Lua. It guides the agent through atomic Redis Lua script execution, burst handling, tier-based limits (per IP, per API key, per tenant), and standard HTTP 429 response headers (X-RateLimit-* and Retry-After)."
domain: backend
category: resilience
subcategory: rate-limiter-token-bucket
tags:
  - rate-limiting
  - token-bucket
  - redis
  - lua
  - resilience
  - api-gateway
  - fastapi
technologies:
  - Redis
  - Lua
  - Python
  - FastAPI
  - Go
complexity: advanced
maturity: stable
tools:
  - redis-cli
  - python
dependencies:
  - redis >= 5.0.0
---
# Distributed Rate Limiting: Token Bucket with Redis & Lua

## Overview

A definitive production engineering reference for building atomic, horizontally scalable distributed rate limiters using Redis and Lua. In distributed architectures with multiple API gateway instances, naive multi-step check-and-set operations introduce race conditions that allow clients to exceed burst limits. This skill instructs AI agents on authoring single-roundtrip atomic Lua scripts implementing the Token Bucket algorithm, supporting tiered client quotas, and injecting standard RFC 6585 headers.

## When to Use

- Protecting backend APIs and databases from volumetric abuse, DDoS, and scraping.
- Enforcing subscription plan quotas (Free tier: 60 req/min, Pro tier: 1000 req/min).
- Throttling resource-intensive endpoints (AI completions, payment submissions, password resets).
- Providing deterministic HTTP 429 Too Many Requests responses with accurate `Retry-After` headers.

## When NOT to Use

- Single-instance monolithic apps where an in-memory lock or library (e.g. `slowapi` with in-memory storage) is adequate without Redis.
- Long-term billing quotas spanning months (use database counters or billing events).

## Inputs & Prerequisites

- Redis 7+ server accessible to API instances.
- Python client `redis` or Go `go-redis`.
- Identification mechanism for requests (Client IP, API Key, or Bearer JWT Subject).

## Core Workflow

### 1. Atomic Token Bucket Lua Script
The token bucket algorithm replenishes tokens continuously at a refill rate while allowing bursts up to bucket capacity:

```lua
-- rate_limiter.lua
-- KEYS[1]: Rate limit key (e.g. "rate:orders:client_123")
-- ARGV[1]: Max bucket capacity (burst capacity)
-- ARGV[2]: Refill rate in tokens per second
-- ARGV[3]: Requested tokens (usually 1)
-- ARGV[4]: Current timestamp (Unix epoch in seconds)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local requested = tonumber(ARGV[3])
local now = tonumber(ARGV[4])

local data = redis.call('HMGET', key, 'tokens', 'last_updated')
local tokens = tonumber(data[1])
local last_updated = tonumber(data[2])

if tokens == nil then
    -- Bucket initialization
    tokens = capacity
    last_updated = now
else
    -- Compute replenished tokens based on elapsed time
    local elapsed = math.max(0, now - last_updated)
    tokens = math.min(capacity, tokens + (elapsed * refill_rate))
    last_updated = now
end

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_updated', last_updated)
    -- Expire bucket after time required to refill completely from empty
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
    -- Return: 1 (allowed), remaining tokens, 0 (no retry delay needed)
    return {1, math.floor(tokens), 0}
else
    local needed = requested - tokens
    local retry_after = math.ceil(needed / refill_rate)
    -- Return: 0 (rejected), remaining tokens, retry_after seconds
    return {0, math.floor(tokens), retry_after}
end
```

### 2. FastAPI Rate Limiting Middleware
Execute the compiled Lua script atomically on every request:

```python
import time
import redis
from fastapi import FastAPI, Request, Response, HTTPException, status

app = FastAPI()
r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)

# Register and cache the Lua script SHA on Redis startup
with open("rate_limiter.lua", "r") as f:
    LUA_SCRIPT_TEXT = f.read()
rate_limit_sha = r.script_load(LUA_SCRIPT_TEXT)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Identify client by API Key or IP address
    api_key = request.headers.get("X-API-Key")
    client_id = api_key if api_key else request.client.host
    rate_key = f"rate:api:{client_id}"

    # Parameters: Capacity = 60 tokens, Refill = 1 token/sec (60 req/min with burst of 60)
    capacity = 60
    refill_rate = 1.0
    now = time.time()

    res = r.evalsha(rate_limit_sha, 1, rate_key, capacity, refill_rate, 1, now)
    allowed, remaining, retry_after = res[0], res[1], res[2]

    if allowed == 0:
        return Response(
            content='{"error": "Too Many Requests. Rate limit exceeded."}',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            media_type="application/json",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(capacity),
                "X-RateLimit-Remaining": "0"
            }
        )

    response: Response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(capacity)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
```

## Best Practices & Failure Modes

1. **Race Conditions from Non-Atomic Operations**: Reading token counts with `HGET` and writing back with `HSET` in Python code fails under concurrent traffic (two concurrent requests read `tokens=1`, both decrement and write `tokens=0`, granting 2 requests when only 1 should be allowed). Always use a Lua script or Redis module.
2. **Clock Skew across Application Servers**: If application nodes provide differing `now` timestamps, bucket replenishment jumps unpredictably. In ultra-strict environments, use Redis server time via `redis.call('TIME')` inside the Lua script.
3. **Failing Open vs Failing Closed**: When Redis is temporarily down, determine whether to allow requests through (fail-open for better availability) or reject them (fail-closed for strict security).

## Verification & Testing

- High-concurrency load test to verify exact bucket enforcement:
  ```bash
  # Send 70 rapid requests; exactly 60 should succeed (HTTP 200) and 10 should receive HTTP 429
  hey -n 70 -c 10 http://localhost:8000/api/items
  ```
- Inspect Redis keys and TTL:
  ```bash
  redis-cli HGETALL rate:api:127.0.0.1
  redis-cli TTL rate:api:127.0.0.1
  ```
