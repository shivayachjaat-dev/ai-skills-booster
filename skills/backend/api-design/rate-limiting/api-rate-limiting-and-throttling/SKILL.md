---
name: api-rate-limiting-and-throttling
description: "Use this skill when designing, implementing, and tuning API rate limiters and request throttling systems. It guides the agent through algorithm selection (Token Bucket, Leaky Bucket, Sliding Window Counter), distributed synchronization with Redis, HTTP 429 response formatting, Tier-based limits, and atomic Lua script execution to prevent race conditions."
domain: backend
category: api-design
subcategory: rate-limiting
tags:
  - backend
  - api-security
  - rate-limiting
  - redis
  - throttling
  - scalability
technologies:
  - Redis
  - Node.js
  - Python
  - Lua
  - FastAPI
complexity: advanced
maturity: stable
tools:
  - redis-cli
  - python
  - node
dependencies:
  - redis >= 6.0
---
# API Rate Limiting and Throttling

## Overview

A robust architecture for implementing distributed API rate limiting, protecting backend infrastructure from denial-of-service spikes, brute-force credential stuffing, abusive scrapers, and cascading downstream failures while ensuring equitable resource distribution among consumers.

## When to Use

- Protecting public APIs from abuse, scraping, and denial-of-service traffic.
- Implementing tiered monetization tiers (e.g. Free: 60 req/min, Pro: 1,000 req/min).
- Safeguarding authentication endpoints (`/login`, `/signup`, `/forgot-password`) from credential brute-forcing.
- Throttling calls to expensive downstream dependencies (LLM APIs, payment processors).

## When NOT to Use

- Long-term database concurrency locks (use relational database row locks or optimistic locking).
- Client-side request debouncing in browser UI.

## Inputs & Prerequisites

- Distributed in-memory datastore (Redis cluster or standalone Redis instance).
- API gateway or middleware execution point (Express, FastAPI, Envoy, Nginx).
- Defined rate limits: capacity, refill rate, window duration, and key identification strategy.

## Core Workflow

### 1. Algorithm Selection
Select the rate limiting algorithm matching traffic characteristics:
- **Token Bucket**: Allows short traffic bursts up to bucket capacity while enforcing a smooth steady-state token refill rate. Best for general REST APIs.
- **Sliding Window Counter**: Smooths boundary reset spikes (which plague fixed-window limiters) by interpolating between the current window and previous window counts. Best for strict compliance.
- **Leaky Bucket**: Enforces a constant output rate regardless of ingress bursts. Best for queue processing and downstream smoothing.

### 2. Atomic Distributed Sliding Window in Redis (Lua Script)
Fixed-window counters suffer from "double burst" attacks at window boundaries. Use an atomic Sliding Window Log/Counter in Redis with Lua:
```lua
-- KEYS[1]: rate_limit_key (e.g. rate:user_123:minute)
-- ARGV[1]: current_timestamp (milliseconds)
-- ARGV[2]: window_size_ms (e.g. 60000 for 1 minute)
-- ARGV[3]: max_requests (e.g. 100)

local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local clear_before = now - window

-- 1. Remove timestamps outside the sliding window
redis.call('ZREMRANGEBYSCORE', key, 0, clear_before)

-- 2. Count requests remaining in the current window
local current_requests = redis.call('ZCARD', key)

if current_requests < limit then
    -- 3. Add current request timestamp
    redis.call('ZADD', key, now, now)
    redis.call('PEXPIRE', key, window)
    return {1, limit - current_requests - 1} -- Allowed, remaining
else
    return {0, 0} -- Blocked
end
```

### 3. Key Identification Strategy
Never rate-limit solely by `X-Forwarded-For` IP, as proxies or shared NAT gateways aggregate thousands of legitimate users:
- **Authenticated Requests**: Rate-limit by `account_id` or `api_key_id`.
- **Unauthenticated / Auth Endpoints**: Rate-limit by a composite key: `hash(ip_address + user_agent + endpoint)`.

### 4. Standard HTTP Header Specification
When requests are processed, return standard IETF rate limit headers:
- `RateLimit-Limit`: Maximum requests permitted per window.
- `RateLimit-Remaining`: Remaining request quota in the active window.
- `RateLimit-Reset`: Seconds remaining until quota resets.
- When blocked, return `HTTP 429 Too Many Requests` with `Retry-After: <seconds>`:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please wait 15 seconds before retrying.",
    "retry_after_seconds": 15
  }
}
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Redis becomes unavailable | Implement a "fail-open" strategy with local in-memory fallback to avoid taking down the entire API when cache nodes restart. |
| High burst of simultaneous parallel requests (race condition) | Lua scripts execute atomically in Redis single-threaded engine, guaranteeing zero race condition overages. |
| Webhook delivery to third parties | Apply rate limiting per destination domain to avoid getting IP-blocked by recipient endpoints. |

## Validation & Acceptance Criteria

- [ ] Rate limits enforced accurately across concurrent requests without race condition leaks.
- [ ] Standard HTTP 429 status code returned with valid `Retry-After` header.
- [ ] Sliding window prevents double-quota spikes at window boundaries.
- [ ] Redis keys configure automatic TTL expiration to prevent memory leaks.
- [ ] Graceful degradation path active if Redis connection fails.

## Failure Handling & Recovery

- If Redis cluster enters read-only failover, fall back to process-local LRU memory limiting with reduced thresholds.

## Expected Output & Artifacts

- Middleware rate-limiting implementation file.
- Redis Lua script file.
- Automated concurrency stress tests simulating parallel burst traffic.

## Related Skills

- `api-and-interface-design`
- `postgres-query-performance-analysis`
- `owasp-api-security-top-10`
