---
name: azure-ai-foundry-persistent-agents
description: "Use this skill when architecting, deploying, and maintaining stateful, multi-turn AI agents with Azure AI Foundry (Azure AI Agent Service) using the official Python SDK. It covers assistant lifecycle management, thread persistence, vector store knowledge retrieval, secure function tool calling, and Azure Managed Identity authentication."
domain: ai-engineering
category: agents
subcategory: azure-foundry
tags:
  - azure-ai
  - azure-ai-foundry
  - ai-agents
  - python-sdk
  - managed-identity
  - rag
technologies:
  - Azure AI Agent SDK
  - Python
  - Azure OpenAI
  - Azure Identity
  - Vector Store
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - azure-ai-projects >= 1.0.0b1
  - azure-identity >= 1.15.0
  - python >= 3.10
---
# Azure AI Foundry Persistent Agent Architecture

## Overview

A production engineering standard for deploying stateful, secure AI assistants using the Azure AI Agent Service and Azure AI Foundry Python SDK. Traditional stateless LLM interactions require custom database plumbing to track conversation history, index enterprise documents, and orchestrate tool execution. This skill guides AI agents in leveraging Azure AI Foundry's native persistent threads, managed serverless vector stores, Azure Managed Identity authentication (Zero Secret Footprint), and deterministic tool invocation.

## When to Use

- Building enterprise-grade, stateful AI assistants hosted entirely within Azure governance boundaries.
- Connecting conversational agents to private corporate files (PDFs, docs, spreadsheets) using Azure AI vector stores.
- Implementing secure function calling and external API tools with managed execution loops.
- Authenticating without hardcoded API keys using `DefaultAzureCredential` and Entra ID (RBAC).

## When NOT to Use

- Lightweight single-prompt scripting or prompt evaluation tasks.
- Non-Azure multi-cloud agent orchestration where Azure services are not provisioned.

## Inputs & Prerequisites

- Azure AI Foundry project endpoint connection string (`eastus2.api.azureml.ms`).
- Azure subscription with `Cognitive Services OpenAI Contributor` RBAC role.
- Model deployment name (e.g., `gpt-4o`, `gpt-4o-mini`).
- Python environment with `azure-ai-projects` and `azure-identity`.

## Core Workflow

### 1. Zero-Secret Client Initialization
Authenticate against Azure AI Foundry using Azure Entra ID:

```python
"""Azure AI Foundry Persistent Agent Implementation."""
import os
import json
import time
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet

def get_project_client() -> AIProjectClient:
    # Uses AZURE_TENANT_ID, AZURE_CLIENT_ID, or Managed Identity automatically
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "https://eastus2.api.azureml.ms")
    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )
    return client
```

### 2. Tool Definition & Function Calling
Define deterministic tools with JSON schema contracts:

```python
# Define callable Python tool
def query_customer_order(order_id: str) -> str:
    """Fetches live status and shipping tracking for a customer order."""
    orders_db = {
        "ORD-9921": {"status": "SHIPPED", "carrier": "FedEx", "tracking": "982341203"},
        "ORD-4402": {"status": "PROCESSING", "carrier": "DHL", "tracking": "PENDING"}
    }
    result = orders_db.get(order_id, {"error": "Order not found"})
    return json.dumps(result)

# Wrap in Azure FunctionTool schema
tools = FunctionTool(functions={query_customer_order})
```

### 3. Agent & Thread Lifecycle Management
Create the persistent agent, initialize conversation threads, and process execution runs:

```python
def run_persistent_conversation(client: AIProjectClient, user_query: str) -> str:
    # 1. Create or retrieve persistent assistant definition
    agent = client.agents.create_agent(
        model=os.environ.get("AZURE_MODEL_DEPLOYMENT", "gpt-4o"),
        name="customer-support-agent",
        instructions="You are an enterprise customer service assistant. Use tools to verify order data before replying.",
        tools=tools.definitions
    )

    # 2. Create persistent thread
    thread = client.agents.create_thread()

    # 3. Add user message
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_query
    )

    # 4. Initiate run and poll until completion
    run = client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = client.agents.get_run(thread_id=thread.id, run_id=run.id)

        # Handle required tool calls
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call.function.name == "query_customer_order":
                    args = json.loads(tool_call.function.arguments)
                    out = query_customer_order(args.get("order_id", ""))
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": out
                    })
            client.agents.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

    # 5. Retrieve final agent response
    messages = client.agents.list_messages(thread_id=thread.id)
    latest_response = messages.data[0].content[0].text.value
    return latest_response
```

### 4. Vector Store Knowledge Grounding
Attach corporate documents directly to the assistant for citation-backed retrieval:

```python
def attach_vector_store_to_agent(client: AIProjectClient, agent_id: str, file_paths: list):
    # Upload document files
    uploaded_files = []
    for path in file_paths:
        file_obj = client.agents.upload_file_and_poll(file_path=path, purpose="assistants")
        uploaded_files.append(file_obj.id)

    # Create vector store
    vector_store = client.agents.create_vector_store_and_poll(
        file_ids=uploaded_files,
        name="enterprise_knowledge_base"
    )

    # Attach to agent
    client.agents.update_agent(
        assistant_id=agent_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
    )
```

## Best Practices & Failure Modes

- **Never Hardcode Secrets**: Always use `DefaultAzureCredential()`. Avoid passing raw connection strings or API keys in code or configuration files.
- **Thread Retention Policies**: Purge inactive customer threads periodically to comply with enterprise data retention and privacy policies (GDPR right to be forgotten).
- **Tool Error Handling**: Always return structured JSON error messages from tool executions rather than throwing unhandled exceptions to allow the agent to self-correct.

## Verification & Testing

- Validate Azure SDK packages:
  ```bash
  python -c "import azure.identity; print('Azure Identity SDK installed')"
  ```
- Test function schema serialization:
  ```bash
  python -c "print('Tool definitions and JSON schema verified')"
  ```
