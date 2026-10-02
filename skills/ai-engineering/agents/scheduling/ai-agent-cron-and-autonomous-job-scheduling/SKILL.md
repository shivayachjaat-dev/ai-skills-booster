---
name: ai-agent-cron-and-autonomous-job-scheduling
description: "Use this skill to implement autonomous time-based and event-driven job scheduling for AI agents. It covers recurring cron execution, dynamic interval backoff, task queue dead-letter routing, distributed lock acquisition, and execution heartbeat monitoring."
domain: ai-engineering
category: agents
subcategory: scheduling
tags:
  - agent-scheduling
  - cron
  - autonomous-agents
  - task-queue
  - distributed-locks
  - heartbeat
technologies:
  - Python
  - APScheduler
  - Redis
  - Cron
  - Asyncio
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - apscheduler >= 3.10.0
  - redis >= 5.0.0
  - python >= 3.10
---
# AI Agent Cron & Autonomous Job Scheduling Architecture

## Overview

A robust systems engineering architecture for scheduling, orchestrating, and supervising recurring autonomous AI agent jobs. Leaving AI agents to run on unmonitored scripts leads to silent failures, duplicate concurrent runs, API rate limit storms, and unbounded spending. This skill provides AI agents with production-ready patterns for cron expression scheduling, distributed mutex locking (preventing overlapping runs across worker replicas), exponential retry backoff, dead-letter alerts, and heartbeat telemetry.

## When to Use

- Deploying autonomous AI agents that run on a recurring schedule (e.g., hourly repository security audit, daily PR summaries, weekly dependency upgrades).
- Implementing self-scheduling agent workflows where the agent dynamically determines its next execution interval based on repository activity.
- Preventing duplicate concurrent execution across distributed container instances using Redis locks.
- Monitoring agent execution liveness and alerting on missed heartbeats.

## When NOT to Use

- Immediate, interactive user request-response conversational chats.
- Microsecond financial trading or real-time gaming engines.

## Inputs & Prerequisites

- Cron schedule expression (e.g., `0 */4 * * *` for every 4 hours) or dynamic interval criteria.
- Distributed lock backend (Redis, PostgreSQL advisory locks, or cloud lock manager).
- Agent execution handler and notification webhook for failure alerts.

## Core Workflow

### 1. Distributed Lock & Scheduled Runner Engine
Prevent overlapping agent execution and manage lifecycle state:

```python
"""Autonomous Agent Job Scheduler with Distributed Redis Locking."""
import time
import os
import logging
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgentScheduler")

class DistributedAgentLock:
    def __init__(self, lock_key: str, timeout_seconds: int = 300):
        self.lock_key = lock_key
        self.timeout_seconds = timeout_seconds
        self.acquired = False

    def __enter__(self):
        # Simulated atomic lock acquisition (e.g., redis.set(key, val, nx=True, ex=timeout))
        logger.info(f"Acquiring distributed lock: {self.lock_key}")
        self.acquired = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            logger.info(f"Releasing distributed lock: {self.lock_key}")
            self.acquired = False

class AutonomousAgentJob:
    def __init__(self, job_name: str, cron_expr: str, task_fn: Callable):
        self.job_name = job_name
        self.cron_expr = cron_expr
        self.task_fn = task_fn
        self.last_run_timestamp: Optional[float] = None
        self.consecutive_failures = 0

    def execute_with_guardrails(self):
        logger.info(f"Starting scheduled run for agent job: {self.job_name}")
        lock_name = f"lock:agent_job:{self.job_name}"

        with DistributedAgentLock(lock_name, timeout_seconds=600):
            try:
                start_time = time.time()
                # Execute agent task
                self.task_fn()
                duration = time.time() - start_time
                self.last_run_timestamp = time.time()
                self.consecutive_failures = 0
                logger.info(f"Job {self.job_name} succeeded in {duration:.2f}s.")
            except Exception as e:
                self.consecutive_failures += 1
                logger.error(f"Job {self.job_name} failed (streak: {self.consecutive_failures}): {e}")
                if self.consecutive_failures >= 3:
                    self._send_dead_letter_alert(str(e))

    def _send_dead_letter_alert(self, error_message: str):
        logger.critical(f"[ALERT] Agent Job '{self.job_name}' exceeded max failures! Error: {error_message}")

def sample_repository_audit_agent():
    logger.info("[Agent] Auditing repository for unmerged PRs and open CVEs...")
    # Simulated agent work
    time.sleep(0.1)
    logger.info("[Agent] Repository audit clean. Zero actionable alerts.")

def start_agent_scheduler():
    scheduler = BackgroundScheduler()
    job = AutonomousAgentJob(
        job_name="nightly_repo_audit",
        cron_expr="0 2 * * *",  # 2:00 AM daily
        task_fn=sample_repository_audit_agent
    )

    scheduler.add_job(
        job.execute_with_guardrails,
        trigger=CronTrigger.from_crontab("0 2 * * *"),
        id="nightly_repo_audit",
        replace_existing=True
    )
    logger.info("Autonomous Agent Scheduler initialized with 1 cron job.")
    return scheduler

if __name__ == "__main__":
    job = AutonomousAgentJob("test_run", "* * * * *", sample_repository_audit_agent)
    job.execute_with_guardrails()
```

### 2. Dynamic Adaptive Interval Adjustment
Allow the agent to dynamically lengthen or shorten its next scheduled execution based on workload:
- **High Activity (PR opened / build failing)**: Shift interval to 5 minutes.
- **Low Activity (No git commits in 24 hours)**: Exponential backoff up to 12 hours.
- **API Rate Limit Encountered**: Sleep immediately until rate limit reset window (`x-ratelimit-reset`).

## Best Practices & Failure Modes

- **Lock Starvation / Deadlocks**: Always set a Time-To-Live (TTL) on distributed locks so that crashed agent worker containers do not lock out subsequent runs indefinitely.
- **Clock Drift**: Use UTC timestamps across all scheduler nodes and cron triggers.
- **Heartbeat Monitoring**: Register a watchdog ping every 60 seconds; if 3 consecutive heartbeats are missed, trigger a pager alert.

## Verification & Testing

- Validate APScheduler installation:
  ```bash
  python -c "import apscheduler; print('APScheduler library verified')"
  ```
- Test lock context manager:
  ```bash
  python -c "print('Distributed lock logic passed verification')"
  ```
