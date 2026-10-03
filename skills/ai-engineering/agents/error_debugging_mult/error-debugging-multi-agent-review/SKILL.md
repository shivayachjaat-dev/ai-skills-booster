---
name: error-debugging-multi-agent-review
description: "Coordinate specialized multi-agent reviewer perspectives (trace analysis, concurrency audit, regression tracking) to diagnose complex runtime crashes."
domain: ai-engineering
category: agents
subcategory: error_debugging_mult
tags:
  - ai-engineering
  - agents
  - debugging
  - multi-agent-review
  - root-cause-analysis
technologies:
  - Python
  - Traceback Analysis
  - AST Inspection
  - Concurrency Diagnostics
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Multi-Agent Error Debugging & Triaging Standard

## Overview

The **Error Debugging Multi-Agent Review** skill provides an enterprise standard for investigating, diagnosing, and repairing complex runtime exceptions and elusive production bugs through multi-agent peer review. Single-agent debugging frequently suffers from confirmation bias, where an agent zeroes in on an initial incorrect hypothesis and creates invalid patches.

This skill orchestrates multiple specialized investigative roles—**Trace Analyzer**, **Concurrency Auditor**, and **Regression Investigator**—synthesizing their independent findings into an authoritative Root Cause Analysis (RCA) report and actionable regression-tested remediation patch.

```
+------------------------------------------------------------------------+
|                     Multi-Agent Review Pipeline                        |
|                                                                        |
|  [ Exception & Stack Trace Ingestion ]                                 |
|                         |                                              |
|         +---------------+---------------+                              |
|         |               |               |                              |
|         v               v               v                              |
|   [ Trace Analyzer] [Concurrency] [Regression Hunt]                    |
|         |               |               |                              |
|         +---------------+---------------+                              |
|                         |                                              |
|                         v                                              |
|        [ RCA Synthesis & Patch Generation ]                            |
|                         |                                              |
|                         v                                              |
|        [ Regression Test Strategy & CI Gate ]                          |
+------------------------------------------------------------------------+
```

## When to Use

- When diagnosing non-trivial exceptions, unhandled rejections, or intermittent production crashes.
- When investigating race conditions, thread starvation, or deadlocks in asynchronous distributed architectures.
- When isolating root causes across recent commit histories and dependency upgrades.
- When preparing post-mortem documentation with root cause hypotheses and defensive regression tests.

## When NOT to Use

- Trivial syntax typos or missing import statements that standard linter passes resolve instantaneously.
- Normal deterministic unit test assertions with obvious expected vs actual differences.

## Core Workflow

### 1. Ingest Error Context & Stack Trace
Capture the complete runtime exception details, stack frames, and recent change metadata:

```python
from multi_agent_debugger import ErrorContext, MultiAgentDebugger

context = ErrorContext(
    exception_type="AttributeError",
    message="'NoneType' object has no attribute 'verify_signature'",
    stack_trace="Traceback (most recent call last):\n  File 'auth.py', line 12, in verify\n...",
    recent_changes=["Commit f10e: Migrated auth provider client to async."]
)
```

### 2. Execute Multi-Perspective Triaging
Dispatch the context through the `MultiAgentDebugger` to evaluate frames, concurrency markers, and commit diffs:

```python
debugger = MultiAgentDebugger()
rca_report = debugger.diagnose(context)

print(f"Primary Root Cause: {rca_report.primary_root_cause}")
print(f"Confidence: {rca_report.consensus_confidence * 100}%")
for factor in rca_report.contributing_factors:
    print(f"Contributing Factor: {factor}")
```

### 3. Apply Remediation Patch & Regression Tests
Review the synthesized fix and implement targeted regression unit tests:

```python
print("Suggested Remediation Patch:")
print(rca_report.remediation_patch)

print("Test Strategy:")
print(rca_report.regression_test_strategy)
```

## Verification & Testing

Execute the multi-agent debugging verification suite to test multi-perspective analysis and RCA synthesis:

```bash
python scripts/error-debugging-multi-agent-review_helper.py
```

Expected output:
- Perspectives evaluate stack frames, concurrency signals, and regression changes.
- Root cause identified and synthesized cleanly.
- Status returned cleanly.
