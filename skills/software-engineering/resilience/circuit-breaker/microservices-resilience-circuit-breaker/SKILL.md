---
name: microservices-resilience-circuit-breaker
description: "Use this skill when designing, implementing, and tuning resilience patterns for distributed microservices. It guides the agent through Circuit Breaker state machines (Closed, Open, Half-Open), sliding window error rate calculation, exponential backoff with full jitter, bulkheads, fallback degradation, and health check probe integration."
domain: software-engineering
category: resilience
subcategory: circuit-breaker
tags:
  - resilience
  - circuit-breaker
  - microservices
  - fault-tolerance
  - retry
  - fallback
technologies:
  - Python
  - Go
  - Resilience4j
  - Envoy
  - Polly
complexity: advanced
maturity: stable
tools:
  - python
  - go
dependencies:
  - python >= 3.10
---
# Microservices Resilience & Circuit Breaker Architecture

## Overview

A definitive pattern guide for preventing catastrophic cascading failures in distributed architectures. This skill instructs AI agents in implementing robust Circuit Breakers, Bulkheads, Exponential Backoff with Jitter, and Graceful Fallback mechanisms to safeguard services from upstream outages and resource exhaustion.

## When to Use

- Calling external third-party APIs (payment gateways, notification providers) that can suffer transient degradations.
- Preventing cascading service failures across microservice call graphs.
- Halting outgoing HTTP/RPC calls when remote dependencies fail consistently, giving them time to recover.
- Enforcing resource isolation between critical and non-critical service operations.

## When NOT to Use

- In-process internal method calls within the same application memory space.
- Idempotent database reads against high-availability replicas where simple short timeouts suffice.

## Inputs & Prerequisites

- Understanding of distributed failure modes (timeout, connection reset, HTTP 503, thread pool exhaustion).
- Application handling network requests over HTTP/gRPC.

## Core Workflow

### 1. Circuit Breaker State Machine Pattern
A finite state machine with three states:
1. **CLOSED**: Requests pass through. Error counts are tracked within a sliding window.
2. **OPEN**: Requests fail fast immediately without making network calls.
3. **HALF-OPEN**: After a reset timeout, a limited trial batch of requests is admitted to evaluate recovery.

```python
import time
import threading
from enum import Enum
from typing import Callable, Any, Optional

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_time_seconds: float = 30.0,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time_seconds = recovery_time_seconds
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.half_open_success_count = 0
        self.lock = threading.Lock()

    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        with self.lock:
            now = time.time()
            
            # Transition from OPEN to HALF_OPEN if recovery time passed
            if self.state == CircuitState.OPEN:
                if now - self.last_failure_time >= self.recovery_time_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_success_count = 0
                else:
                    raise CircuitBreakerOpenException(f"Circuit '{self.name}' is OPEN. Fast-failing request.")

        # Attempt function call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_success_count += 1
                if self.half_open_success_count >= self.half_open_max_calls:
                    # Service recovered
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                if self.failure_count >= self.failure_threshold or self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.OPEN
```

### 2. Exponential Backoff with Full Jitter
Prevent thundering herds by randomizing retry delays:

```python
import random
import asyncio

async def retry_with_exponential_backoff_jitter(
    coroutine_func: Callable,
    max_retries: int = 4,
    base_delay_ms: float = 100,
    max_delay_ms: float = 3000
):
    attempt = 0
    while True:
        try:
            return await coroutine_func()
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                raise e
            
            # Exponential backoff: base * 2^attempt
            ceiling = min(max_delay_ms, base_delay_ms * (2 ** attempt))
            # Full jitter: Uniform(0, ceiling)
            sleep_duration = random.uniform(0, ceiling) / 1000.0
            
            await asyncio.sleep(sleep_duration)
```

### 3. Graceful Fallback Pattern
Always provide graceful degradation when remote calls fail:

```python
def get_user_recommendations(user_id: str, circuit: CircuitBreaker) -> list:
    try:
        return circuit.execute(call_recommendation_ml_service, user_id)
    except (CircuitBreakerOpenException, Exception) as e:
        # Fallback: Return cached popular items instead of erroring 500
        return get_cached_trending_items()
```

## Best Practices & Failure Modes

1. **Retry Storms**: Retrying without jitter synchronizes retries across thousands of clients, delivering a DDoS attack to an already struggling upstream service. Always combine retries with jitter and circuit breaking.
2. **Missing Timeouts**: A circuit breaker cannot detect failures if the network call hangs indefinitely. Always set aggressive connection and socket read timeouts (e.g. 500ms - 2s).
3. **Threshold Tuning**: Setting `failure_threshold` too low causes spurious tripping on intermittent single-packet drops. Use sliding-window percentage error rates in high-throughput systems.

## Verification & Testing

- Inject simulated network failure in test suite and verify circuit transition:
  ```python
  breaker = CircuitBreaker("test-service", failure_threshold=2, recovery_time_seconds=0.1)
  
  def faulty_call():
      raise ConnectionError("Service down")

  # Trigger failures
  for _ in range(2):
      try: breaker.execute(faulty_call)
      except ConnectionError: pass

  # Next call should fail fast with CircuitBreakerOpenException immediately
  import pytest
  with pytest.raises(CircuitBreakerOpenException):
      breaker.execute(faulty_call)
  ```
