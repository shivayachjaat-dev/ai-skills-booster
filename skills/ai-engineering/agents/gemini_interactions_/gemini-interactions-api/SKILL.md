---
name: gemini-interactions-api
description: "Build with the Gemini Interactions API for chat, multimodal generation, streaming, function calling, structured output, and stateful agent threads."
domain: ai-engineering
category: agents
subcategory: gemini_interactions_
tags:
  - ai-engineering
  - agents
  - gemini
  - interactions-api
  - tool-use
technologies:
  - Python
  - Google GenAI SDK
  - JSON Schema
  - Function Calling
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python@>=3.10
---

# Gemini Interactions API Architecture & Implementation Standard

## Overview

The **Gemini Interactions API** skill provides the standard design and integration patterns for building production AI applications using Google's modern Gemini Interactions SDK. As agentic applications evolve past basic one-turn `generateContent` calls, systems require unified mechanisms for structured schema enforcement, automated multi-turn function calling, token streaming, and long-horizon session state.

This skill equips engineers with `GeminiInteractionsClient`, an extensible orchestration harness providing automatic tool dispatch, Pydantic/JSON schema validation, and mockable offline testing for robust CI/CD integration.

```
+------------------------------------------------------------------------+
|                      Gemini Interactions Pipeline                      |
|                                                                        |
|  [ Prompt & System Instruction ]                                       |
|                  |                                                     |
|                  v                                                     |
|  [ Interactions Client Engine ] ---> Resolves registered tools         |
|                  |                                                     |
|                  v                                                     |
|  [ Tool Invocation Loop ]       ---> Executes function & feeds result  |
|                  |                                                     |
|                  v                                                     |
|  [ Structured Schema Filter ]   ---> Enforces strict JSON contracts    |
|                  |                                                     |
|                  v                                                     |
|  [ Stream / Turn Resolution ]   ---> Emits validated response payload  |
+------------------------------------------------------------------------+
```

## When to Use

- When developing conversational agents, chatbots, or assistants powered by Gemini 2.5 Flash / Pro models.
- When orchestrating autonomous tool-calling loops where Gemini invokes client-side Python functions.
- When extracting strictly typed structured data (JSON schemas) from unstructured text or multimodal inputs.
- When migrating legacy `google.generativeai` `generateContent` implementations to the modern `google-genai` Interactions paradigm.

## When NOT to Use

- Applications strictly restricted to local offline models running on air-gapped hardware without Google Cloud access.
- Trivial static string operations that do not require generative language models.

## Core Workflow

### 1. Initialize Client and Register Tools
Configure the client with target model parameters and register executable Python tools:

```python
from gemini_interactions_client import GeminiInteractionsClient

client = GeminiInteractionsClient(model_name="gemini-2.5-flash")

def lookup_order(args):
    return {"order_id": args["order_id"], "status": "Shipped", "eta_days": 2}

client.register_tool(
    name="lookup_order",
    description="Look up fulfillment status by order ID",
    parameters={
        "type": "object",
        "properties": {"order_id": {"type": "string"}},
        "required": ["order_id"]
    },
    handler=lookup_order
)
```

### 2. Execute Structured Interaction
Send a prompt requiring tool execution and strict structured output formatting:

```python
response = client.send_interaction(
    prompt="What is the status of order ORD-9921?",
    system_instruction="You are a customer service assistant. Use tools when needed."
)
print(f"Agent Response: {response['content']}")
```

### 3. Handle Streaming Responses
Stream real-time tokens to clients or user interfaces:

```python
for chunk in client.stream_interaction("Summarize system status"):
    print(chunk, end="", flush=True)
```

## Verification & Testing

Execute the Gemini Interactions verification suite to test tool calling, schema enforcement, and streaming:

```bash
python scripts/gemini-interactions-api_helper.py
```

Expected output:
- Function calling cycle completes and feeds tool output back to conversation.
- Structured JSON output conforms to schema constraints.
- Status returned cleanly.
