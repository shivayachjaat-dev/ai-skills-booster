---
name: redis-caching-patterns
description: "Use this skill when designing, implementing, and optimizing caching strategies using Redis. It guides the agent through selecting appropriate patterns (Cache-Aside, Write-Through, Write-Behind), mitigating cache stampedes (dogpiling) using probabilistic early expiration (XFetch) or mutex locks, avoiding cache penetration with Bloom filters, and configuring TTL jitter."
domain: databases
category: redis
subcategory: caching
tags:
  - redis
  - caching
  - databases
  - performance
  - backend
  - scalability
technologies:
  - Redis
  - Python
  - Node.js
  - SQL
complexity: advanced
maturity: stable
tools:
  - redis-cli
  - python
  - node
dependencies:
  - redis >= 6.2
---
# Redis Caching Patterns

## Overview

A comprehensive guide for building high-performance, resilient caching architectures using Redis. Instructs AI agents on designing data invalidation lifecycles, selecting optimal caching topologies (Cache-Aside vs Write-Through), and neutralizing systemic caching failures including cache stampedes (dogpiling), cache penetration, and cache breakdown.

## When to Use

- Database read query load threatens database capacity or causes high latency.
- Frequently queried entities (user profiles, product catalogs, permissions) rarely change.
- Preventing catastrophic database overload when high-traffic cache keys expire simultaneously.
- Structuring key namespaces, memory eviction policies, and TTL expiration strategies.

## When NOT to Use

- High-frequency write-heavy transactional data where every write must be strictly consistent immediately.
- Storing primary persistent state without a durable relational database backing.

## Inputs & Prerequisites

- Redis instance or cluster configured with adequate memory headroom.
- Read/write access patterns and acceptable data staleness tolerance (e.g. 60 seconds).

## Core Workflow

### 1. Pattern Selection: Cache-Aside (Lazy Loading)
For most web applications, implement the Cache-Aside pattern:
1. Application queries Redis for key `cache:user:123`.
2. **Cache Hit**: Return data immediately from Redis.
3. **Cache Miss**: Query database, write result to Redis with TTL, and return data to caller.
```python
def get_user_profile(user_id: str, db, redis_client):
    cache_key = f"cache:user:{user_id}"
    
    # 1. Check Redis
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
        
    # 2. Cache Miss: Query Database
    user = db.query_user(user_id)
    if not user:
        # Cache negative result briefly (30s) to prevent Cache Penetration
        redis_client.setex(cache_key, 30, json.dumps(None))
        return None
        
    # 3. Set with Jittered TTL to prevent Cache Avalanche
    ttl = 300 + random.randint(-30, 30)  # 5 min +/- 30s
    redis_client.setex(cache_key, ttl, json.dumps(user))
    return user
```

### 2. Neutralizing the Cache Stampede (Dogpiling)
When a hot key accessed by 5,000 req/sec expires, all concurrent requests miss and hammer the database simultaneously. Neutralize using the **XFetch Probabilistic Early Recomputation Algorithm**:
$$\Delta eta \ln(	ext{rand}()) > 	ext{expiry} - 	ext{now}$$
```python
import math, random, time

def should_recompute_early(delta_ms, beta, expiry_timestamp):
    # delta_ms: time taken to compute value from DB
    # beta: aggressiveness factor (usually 1.0)
    rand = random.random()
    if rand == 0:
        return True
    return -(delta_ms * beta * math.log(rand)) > (expiry_timestamp - time.time())
```
Alternatively, use a distributed Redis mutex lock (`SET key val NX EX 10`) so only ONE thread recomputes the database value while others wait.

### 3. Preventing Cache Penetration (Bloom Filters)
If attackers request millions of non-existent IDs (`user_999999999`), queries bypass cache and strike the database directly:
- Maintain a **Redis Bloom Filter** containing all valid IDs (`BF.ADD valid_users user_123`).
- Before querying cache or database, test membership (`BF.EXISTS valid_users user_id`). If false, reject immediately.

### 4. Memory Eviction Policy Configuration
Configure `maxmemory-policy` in `redis.conf`:
- `allkeys-lru`: Evicts least-recently-used keys first when memory limit is hit. Recommended for general caching.
- `volatile-lru`: Evicts LRU keys among those with an explicit TTL set.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Entity updated in database | Invalidate cache immediately (`DEL cache:user:123`) rather than updating cache inline to prevent race condition inconsistencies. |
| Massive number of keys expire at the same second | Apply TTL Jitter (add random variance: `TTL = base_ttl + rand(0, 60)`) to distribute database refresh load. |
| Large nested JSON objects | Use Redis Hashes (`HSET`, `HGETALL`) if specific fields are read/updated independently to avoid full-object serialization overhead. |

## Validation & Acceptance Criteria

- [ ] Cache hit ratio exceeds 85% under sustained load.
- [ ] TTL configured on every cache write; zero perpetual keys without TTL.
- [ ] TTL jitter applied to prevent synchronized expirations.
- [ ] Stampede mitigation (XFetch or mutex locking) verified under simulated concurrent load.
- [ ] Negative results cached briefly to block penetration attacks.

## Failure Handling & Recovery

- If Redis crashes or experiences network partition, the application must degrade gracefully by falling back directly to database reads with circuit breakers to prevent DB collapse.

## Expected Output & Artifacts

- Caching middleware or service module.
- Stampede-resistant cache access wrapper.
- Cache invalidation event hooks.

## Related Skills

- `postgres-query-performance-analysis`
- `api-rate-limiting-and-throttling`
- `fastapi-async-api-design`
