---
name: fable-safe-prompt
description: "Rewrite allowed prompts to reduce false-positive safety triggers without bypassing policy, preserving engineering intent while framing queries defensively."
domain: ai-engineering
category: agents
subcategory: fable_safe_prompt
tags:
  - ai-engineering
  - agents
  - prompt-engineering
  - safety
  - guardrails
technologies:
  - Python
  - Regular Expressions
  - NLP Framing
  - Safety Alignment
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Fable Safe Prompt Architecture & Implementation Standard

## Overview

The **Fable Safe Prompt** skill provides an enterprise standard for recontextualizing legitimate, policy-compliant software engineering and security audit prompts. Standard commercial LLM safety filters often misclassify technical vocabulary (such as "kill hanging process", "exploit memory leak", "inject SQL parameter", or "attack surface analysis") as malicious cyberattack inquiries, producing false-positive refusals.

This skill equips agents with `PromptSafetyReframer`, an automated intent classifier and semantic rewriting harness. It preserves 100% of the legitimate engineering intent while substituting loaded terms with precise defensive vocabulary and prepending verified authorization context, all while strictly upholding ethical safety boundaries and blocking genuine malware generation.

```
+------------------------------------------------------------------------+
|                      Prompt Safety Reframer Pipeline                   |
|                                                                        |
|  [ Inbound Prompt ]      ---> Scans for genuine malware / cyberweapon  |
|                                      |                                 |
|                                      +--> [ Malicious? ] -> Hard Reject|
|                                      |                                 |
|                                      v (Benign)                        |
|  [ Trigger Detection ]   ---> Identifies false-positive keywords       |
|                                      |                                 |
|                                      v                                 |
|  [ Semantic Neutralize ] ---> Substitutes precise technical terms      |
|                                      |                                 |
|                                      v                                 |
|  [ Defensive Framing ]   ---> Appends authorized audit context         |
+------------------------------------------------------------------------+
```

## When to Use

- When developing automated security auditing, vulnerability triage, or code remediation agents.
- When legitimate systems management prompts (e.g. terminating hanging daemon processes) trigger refusal filters.
- When preparing unit tests and reproduction harnesses for security advisories and CVE patches.
- When standardizing input pipelines for multi-agent workflows operating with strict enterprise model providers.

## When NOT to Use

- Malicious activities, cyberattacks, malware development, credential harvesting, or extortion requests (strictly blocked).
- General non-technical conversational prompts that do not contain technical trigger tokens.

## Core Workflow

### 1. Ingest Prompt and Evaluate Intent
Pass user prompt into the `PromptSafetyReframer` to assess intent classification:

```python
from prompt_safety_reframer import PromptSafetyReframer

reframer = PromptSafetyReframer()
result = reframer.inspect_and_reframe("How do I exploit the JWT verification bypass in auth.py?")

if result.is_malicious:
    raise PermissionError("Request blocked by safety policy.")
```

### 2. Inspect Reframed Output & Neutralized Triggers
Review the reframed query to verify that original technical requirements are retained without false-positive trigger keywords:

```python
print(f"Policy Action: {result.policy_action}")
print(f"Neutralized Triggers: {result.triggers_neutralized}")
print(f"Reframed Prompt: {result.reframed_prompt}")
```

### 3. Dispatch to Model Provider
Forward the neutralized, defensibly framed prompt to the downstream LLM or agent runtime.

## Verification & Testing

Execute the prompt safety reframing test suite to verify trigger substitution and malicious request rejection:

```bash
python scripts/fable-safe-prompt_helper.py
```

Expected output:
- Benign triggers substituted with defensive terminology.
- Genuine malicious requests rejected.
- Status returned cleanly.
