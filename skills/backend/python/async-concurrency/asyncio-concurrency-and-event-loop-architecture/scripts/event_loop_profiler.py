#!/usr/bin/env python3
import asyncio
import time
import sys

async def jitter_monitor(interval=0.05, threshold=0.03):
    print(f"Monitoring event loop jitter (interval={interval}s, warning threshold={threshold}s)...")
    lag_samples = []
    
    try:
        while True:
            target = time.perf_counter() + interval
            await asyncio.sleep(interval)
            now = time.perf_counter()
            drift = now - target
            
            if drift > threshold:
                print(f"[EVENT LOOP STALL DETECTED]: Delay={drift*1000:.2f}ms above baseline!")
            
            lag_samples.append(drift)
            if len(lag_samples) >= 50:
                avg_lag = sum(lag_samples) / len(lag_samples) * 1000
                max_lag = max(lag_samples) * 1000
                print(f"Metrics (last 50 ticks): Avg Jitter={avg_lag:.2f}ms | Max Stall={max_lag:.2f}ms")
                lag_samples.clear()
    except asyncio.CancelledError:
        print("Jitter monitor stopped cleanly.")

async def simulate_workload():
    await asyncio.sleep(1.0)
    print("Simulating brief blocking operation to verify detector...")
    time.sleep(0.08) # Deliberate 80ms block
    await asyncio.sleep(2.0)

async def main():
    monitor_task = asyncio.create_task(jitter_monitor())
    workload_task = asyncio.create_task(simulate_workload())
    
    await workload_task
    monitor_task.cancel()
    await asyncio.gather(monitor_task, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
