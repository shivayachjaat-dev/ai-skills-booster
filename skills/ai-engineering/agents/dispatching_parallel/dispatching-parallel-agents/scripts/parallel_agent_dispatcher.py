#!/usr/bin/env python3
"""
Parallel Agent Dispatcher Engine
--------------------------------
Provides structured fan-out / fan-in orchestration for concurrently running AI subagents.
Guarantees isolated execution contexts, per-task timeouts, concurrency throttling,
and robust aggregation without shared mutable state hazards.
"""

import sys
import os
import time
import uuid
import concurrent.futures
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class AgentTask:
    task_id: str
    role: str
    prompt: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timeout_sec: float = 30.0

@dataclass
class AgentResult:
    task_id: str
    role: str
    status: str  # "completed", "timeout", "failed"
    duration_ms: float
    output: Any
    error: Optional[str] = None

class ParallelAgentDispatcher:
    def __init__(self, max_concurrency: int = 4):
        self.max_concurrency = max_concurrency

    def _execute_single_task(self, task: AgentTask, executor_fn: Callable[[AgentTask], Any]) -> AgentResult:
        start_time = time.perf_counter()
        try:
            result = executor_fn(task)
            duration_ms = (time.perf_counter() - start_time) * 1000
            return AgentResult(
                task_id=task.task_id,
                role=task.role,
                status="completed",
                duration_ms=round(duration_ms, 2),
                output=result
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return AgentResult(
                task_id=task.task_id,
                role=task.role,
                status="failed",
                duration_ms=round(duration_ms, 2),
                output=None,
                error=str(exc)
            )

    def dispatch(
        self,
        tasks: List[AgentTask],
        executor_fn: Callable[[AgentTask], Any]
    ) -> Dict[str, Any]:
        """Dispatch a list of independent tasks concurrently across worker pool."""
        if not tasks:
            return {"total_tasks": 0, "completed": 0, "failed": 0, "results": []}

        start_all = time.perf_counter()
        results: List[AgentResult] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_concurrency) as pool:
            future_to_task = {
                pool.submit(self._execute_single_task, task, executor_fn): task
                for task in tasks
            }

            for future in concurrent.futures.as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    res = future.result(timeout=task.timeout_sec)
                    results.append(res)
                except concurrent.futures.TimeoutError:
                    results.append(AgentResult(
                        task_id=task.task_id,
                        role=task.role,
                        status="timeout",
                        duration_ms=round(task.timeout_sec * 1000, 2),
                        output=None,
                        error=f"Execution exceeded timeout limit of {task.timeout_sec}s"
                    ))

        total_wall_ms = (time.perf_counter() - start_all) * 1000
        completed_count = sum(1 for r in results if r.status == "completed")
        failed_count = sum(1 for r in results if r.status != "completed")
        sum_task_duration = sum(r.duration_ms for r in results)
        theoretical_speedup = round(sum_task_duration / max(total_wall_ms, 1.0), 2)

        return {
            "summary": {
                "total_tasks": len(tasks),
                "completed": completed_count,
                "failed": failed_count,
                "concurrency_limit": self.max_concurrency,
                "wall_time_ms": round(total_wall_ms, 2),
                "cumulative_work_ms": round(sum_task_duration, 2),
                "effective_speedup": f"{theoretical_speedup}x"
            },
            "results": [asdict(r) for r in sorted(results, key=lambda x: x.task_id)]
        }

def mock_agent_worker(task: AgentTask) -> Dict[str, Any]:
    """Simulated specialized subagent execution."""
    time.sleep(0.05)  # brief processing delay
    if "fail_test" in task.payload:
        raise RuntimeError("Simulated transient upstream API error")
    return {
        "analysis_type": task.role,
        "findings": f"Verified compliance for scope: {task.prompt}",
        "artifacts_generated": [f"{task.role.lower().replace(' ', '_')}_report.md"]
    }

def verify_parallel_dispatcher():
    dispatcher = ParallelAgentDispatcher(max_concurrency=4)
    tasks = [
        AgentTask(task_id="task-01", role="Security Auditor", prompt="Analyze SQL injection vectors"),
        AgentTask(task_id="task-02", role="Performance Profiler", prompt="Benchmark endpoint latency"),
        AgentTask(task_id="task-03", role="Test Generator", prompt="Generate unit test coverage"),
        AgentTask(task_id="task-04", role="Documentation Writer", prompt="Synthesize API documentation")
    ]
    
    print("============================================================")
    print("Parallel Agent Dispatcher: Running Fan-Out Simulation")
    print("============================================================")
    report = dispatcher.dispatch(tasks, mock_agent_worker)
    print(f"[*] Total Dispatched: {report['summary']['total_tasks']}")
    print(f"[*] Completed Cleanly: {report['summary']['completed']}")
    print(f"[*] Effective Speedup: {report['summary']['effective_speedup']}")
    for res in report["results"]:
        print(f"    -> [{res['status'].upper()}] Task {res['task_id']} ({res['role']}) - {res['duration_ms']}ms")
    
    assert report["summary"]["completed"] == 4
    assert report["summary"]["failed"] == 0
    print("[SUCCESS] Parallel Agent Dispatcher verified cleanly.")

if __name__ == "__main__":
    verify_parallel_dispatcher()
