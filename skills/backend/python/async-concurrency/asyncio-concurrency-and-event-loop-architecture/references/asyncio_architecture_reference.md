# AsyncIO Engineering Patterns & Antipatterns

## Critical Antipatterns
1. **Unbounded `asyncio.gather(*tasks)` with thousands of elements**:
   - Spawns thousands of concurrent sockets immediately, exhausting file descriptors (`ulimit -n`).
   - Fix: Use `asyncio.Semaphore(max_concurrent)` or an `asyncio.Queue` worker pool.

2. **Synchronous File I/O in Async Handlers**:
   - `open('large.json', 'r').read()` blocks the main thread completely.
   - Fix: Use `anyio.to_thread.run_sync` or `aiofiles`.

3. **Silent Exception Loss**:
   - Spawning fire-and-forget tasks with `asyncio.create_task(coro())` without retaining references. If the task fails, the exception is only printed when garbage collected.
   - Fix: Retain task references or use `TaskGroup`.
