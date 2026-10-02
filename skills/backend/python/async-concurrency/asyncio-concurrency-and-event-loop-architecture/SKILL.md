---
name: asyncio-concurrency-and-event-loop-architecture
description: "Use this skill to design, implement, and debug high-performance asynchronous Python systems using standard asyncio. It covers structured concurrency with asyncio.TaskGroup (Python 3.11+), resilient cancellation semantics, worker queues with backpressure, thread/process pool offloading with run_in_executor, event loop latency profiling, and avoiding blocking I/O pitfalls."
domain: backend
category: python
subcategory: async-concurrency
tags:
  - backend
  - python
  - asyncio
  - concurrency
  - event-loop
  - taskgroup
  - multithreading
  - performance
technologies:
  - Python
  - asyncio
  - uvloop
  - concurrent.futures
complexity: expert
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.11
  - uvloop@>=0.19.0
---
# Python AsyncIO Concurrency & Event Loop Architecture

## Overview

A systems-level engineering standard for building robust, high-throughput asynchronous services and event-driven architectures in modern Python (3.11+). While Python's `asyncio` delivers massive I/O concurrency without thread overhead, production systems frequently suffer from unhandled task cancellations, silent task failures, blocking CPU operations that freeze the event loop, and queue memory leaks. This skill establishes clean patterns for structured concurrency (`asyncio.TaskGroup`), bounded worker pools, graceful process shutdown, and low-latency profiling.

```
+------------------------------------------------------------------------+
|                          AsyncIO Single-Thread Event Loop              |
|                                                                        |
|  +--------------------+     +--------------------+                     |
|  | Coroutine Task A   |     | Coroutine Task B   |  (Non-blocking I/O) |
|  | (Network Socket)   |     | (Database Client)  |                     |
|  +--------------------+     +--------------------+                     |
|            |                          |                                |
|            v                          v                                |
|  [ Structured Concurrency: asyncio.TaskGroup / ExceptionGroup ]        |
|                               |                                        |
|  [ Bounded Worker Queues ]    |   [ ThreadPoolExecutor Offloading ]    |
|   (asyncio.Queue maxsize=100) |    (CPU-bound / Legacy Blocking SDKs)  |
|                               |                                        |
+-------------------------------+----------------------------------------+
```

## When to Use

- Building high-concurrency microservices, network proxies, stream processors, or web scraping pipelines handling thousands of open sockets.
- Implementing worker pools where work generation must pause when downstream processing is saturated (backpressure).
- Refactoring legacy code with `asyncio.gather()` to modern structured concurrency (`asyncio.TaskGroup`) for bulletproof exception propagation.
- Offloading synchronous or CPU-intensive operations (cryptography, image manipulation, file I/O) to thread/process executors without stalling the event loop.

## When NOT to Use

- Pure CPU-bound parallel number crunching (use `multiprocessing`, Ray, or PySpark instead).
- Simple scripts with strictly linear, sequential tasks where synchronous execution is clearer and faster to maintain.

## Inputs & Prerequisites

- Python 3.11 or higher (leveraging `asyncio.TaskGroup` and `ExceptionGroup`).
- Async-compatible network and database drivers (`httpx`, `aiohttp`, `asyncpg`, `aiosqlite`).

## Core Workflow

### Step 1: Structured Concurrency with TaskGroup
Eliminate orphan tasks and race conditions by replacing `asyncio.gather()` with `asyncio.TaskGroup`. If any subtask raises an exception, remaining tasks are automatically cancelled:

```python
import asyncio
import logging

logger = logging.getLogger(__name__)

async def fetch_telemetry(device_id: str) -> dict:
    await asyncio.sleep(0.1) # Simulate network fetch
    if device_id == "sensor-invalid":
        raise ValueError(f"Telemetry corruption on {device_id}")
    return {"device_id": device_id, "status": "online"}

async def ingest_device_fleet(device_ids: list[str]) -> list[dict]:
    results = []
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(fetch_telemetry(did)) for did in device_ids]
            
        # All tasks completed successfully if we reach here
        results = [t.result() for t in tasks]
    except* ValueError as eg:
        for exc in eg.exceptions:
            logger.error("Fleet ingestion validation error: %s", exc)
        raise
    return results
```

### Step 2: Bounded Worker Pool with Backpressure
Prevent memory exhaustion under traffic surges by using `asyncio.Queue` with a strict `maxsize`:

```python
import asyncio
import random

async def worker(worker_id: int, queue: asyncio.Queue):
    while True:
        job = await queue.get()
        try:
            # Process job
            await asyncio.sleep(random.uniform(0.05, 0.2))
            print(f"Worker {worker_id} processed job {job['id']}")
        except asyncio.CancelledError:
            # Clean up before exit
            raise
        except Exception as e:
            print(f"Worker {worker_id} encountered job error: {e}")
        finally:
            queue.task_done()

async def producer(queue: asyncio.Queue, total_jobs: int):
    for i in range(total_jobs):
        # When queue reaches maxsize, producer will asynchronously pause here
        await queue.put({"id": i, "payload": f"data_{i}"})
    print("Producer finished enqueuing all jobs.")

async def run_pipeline():
    queue = asyncio.Queue(maxsize=50) # Strict backpressure buffer
    
    # Spawn 5 worker coroutines
    workers = [asyncio.create_task(worker(i, queue)) for i in range(5)]
    
    await producer(queue, total_jobs=200)
    await queue.join() # Wait until all items are processed
    
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
```

### Step 3: Offloading Blocking Synchronous Calls
Never execute blocking I/O (e.g., standard `requests.get()`, `time.sleep()`, disk writes) directly in the event loop:

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=8)

def blocking_legacy_computation(data: bytes) -> bytes:
    # CPU or blocking disk operation
    time.sleep(0.5)
    return data.upper()

async def safe_async_wrapper(data: bytes) -> bytes:
    loop = asyncio.get_running_loop()
    # Runs in worker thread, leaving event loop unblocked
    result = await loop.run_in_executor(executor, blocking_legacy_computation, data)
    return result
```

### Step 4: Graceful Signal Handling and Teardown
Handle `SIGINT` / `SIGTERM` cleanly to allow ongoing requests to finish within a timeout:

```python
import signal

def setup_graceful_shutdown(loop, stop_event: asyncio.Event):
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(handle_exit(s, stop_event)))
        except NotImplementedError:
            # Windows fallback
            pass

async def handle_exit(sig, stop_event: asyncio.Event):
    print(f"\nReceived signal {sig.name}. Initiating graceful shutdown...")
    stop_event.set()
```

## Best Practices & Failure Modes

- **Event Loop Starvation**: Avoid any operation taking > 10ms without an `await`. Use Python's `-X dev` or `PYTHONASYNCIODEBUG=1` to detect slow callbacks automatically.
- **CancelledError Swallowing**: Never catch `except Exception:` without re-raising `asyncio.CancelledError`, or tasks will become un-cancellable zombies.
- **ContextVars Thread-Safety**: When using `asyncio.create_task()`, context variables (`contextvars`) are copied shallowly to child tasks.
- **uvloop in Production**: On Linux/macOS production servers, install `uvloop` and call `uvloop.install()` before running the event loop for a 2-4x speedup.

## Verification & Testing

1. Test cancellation semantics using `pytest-asyncio` with explicit task timeout wrappers.
2. Run loop debug mode: `python -X dev server.py` and ensure zero `Executing <Task ...> took 0.XXX seconds` warnings appear.
3. Verify leak prevention: Run memory profiling during sustained load to confirm `asyncio.all_tasks()` count remains bounded.
