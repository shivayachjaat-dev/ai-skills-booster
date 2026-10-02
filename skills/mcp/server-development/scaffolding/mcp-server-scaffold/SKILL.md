---
name: mcp-server-scaffold
description: "Use this skill when scaffolding, implementing, and validating a Model Context Protocol (MCP) server from scratch using TypeScript or Python. It guides the agent through configuring tool schemas, resource providers, prompt templates, stdio/SSE transports, error boundaries, and integration tests."
domain: mcp
category: server-development
subcategory: scaffolding
tags:
  - mcp
  - model-context-protocol
  - agent-tools
  - typescript
  - python
  - api-integration
technologies:
  - Model Context Protocol
  - TypeScript
  - Node.js
  - Python
complexity: advanced
maturity: stable
tools:
  - node
  - npm
  - python
dependencies:
  - @modelcontextprotocol/sdk or mcp-python
---
# MCP Server Scaffold

## Overview

A complete architectural guide for scaffolding, implementing, and validating Model Context Protocol (MCP) servers. Enables AI agents to expose clean, safe, and discoverable tools, resources, and prompt templates to client applications like Claude Code, Cursor, Windsurf, and Antigravity.

## When to Use

- Building a new custom MCP server to connect an agent to an internal API, database, or local utility.
- Exposing local system capabilities (filesystem, Git, docker, hardware) to an AI agent via standardized MCP schemas.
- Converting legacy CLI tools into standardized MCP tools with JSON schema validation.
- Establishing test harnesses and integration benchmarks for MCP servers.

## When NOT to Use

- Consuming an existing third-party MCP server (use `mcp-server-integration`).
- Building standard REST or GraphQL public web APIs (use `api-and-interface-design`).

## Inputs & Prerequisites

- Choice of runtime: TypeScript/Node.js (`@modelcontextprotocol/sdk`) or Python (`mcp`).
- Transport selection: `stdio` (for local CLI integration) or `SSE` (for remote network services).
- Tool definitions including JSON Schema specifications for inputs and return types.

## Core Workflow

### 1. Project Initialization & Dependencies
For TypeScript:
```bash
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
npx tsc --init
```

### 2. Server Architecture Setup
Create standard project layout:
```text
mcp-server/
├── src/
│   ├── index.ts          # Server initialization & transport binding
│   ├── tools/            # Individual tool implementations
│   ├── resources/        # Resource providers
│   └── schemas/          # Zod validation schemas
├── package.json
└── tsconfig.json
```

### 3. Tool Implementation with Strict Validation
Define tools using type-safe schemas:
```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
  name: "custom-utility-server",
  version: "1.0.0"
});

server.tool(
  "query_database",
  "Executes a parameterized read-only SQL query against the application database",
  {
    query: z.string().describe("The SQL query to execute (SELECT only)"),
    params: z.array(z.any()).optional().describe("Query parameters")
  },
  async ({ query, params }) => {
    if (!query.trim().toUpperCase().startsWith("SELECT")) {
      return {
        isError: true,
        content: [{ type: "text", text: "Error: Only read-only SELECT queries are permitted." }]
      };
    }
    // Execution logic...
    return {
      content: [{ type: "text", text: JSON.stringify({ rows: [] }) }]
    };
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
main().catch(console.error);
```

### 4. Resource & Prompt Registration
- Register resources using URI patterns (e.g. `system://metrics`, `repo://config`).
- Expose reusable prompt templates with parameterized arguments.

### 5. Transport Configuration & Verification
Verify that `stdio` transport does not write raw `console.log` messages to stdout, as this corrupts MCP JSON-RPC frames:
- Redirect internal debug logs to `stderr` (`console.error`).
- Test with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector npx tsx src/index.ts
```

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Large response payloads (> 100KB) | Paginate results or return a resource URI pointer instead of dumping large blobs into tool results. |
| Tool encounters runtime exception | Return `{ isError: true, content: [{ type: "text", text: error.message }] }` rather than crashing the MCP server process. |
| Stdio stdout corruption | Ensure all logging libraries are strictly configured to log to stderr or a disk file. |

## Validation & Acceptance Criteria

- [ ] MCP Server boots cleanly and connects over stdio without crashing.
- [ ] Tools correctly expose their JSON Schema definitions with field descriptions.
- [ ] Input validation rejects malformed parameters with clear error messages.
- [ ] No debug statements output to stdout.
- [ ] Verified compatible with MCP Inspector.

## Failure Handling & Recovery

- If client fails to discover tools, inspect `stderr` logs for schema validation failures during tool registration.

## Expected Output & Artifacts

- Complete runnable MCP server repository with package configs.
- Client configuration snippet (e.g. for `claude_desktop_config.json` or `antigravity.json`).

## Related Skills

- `mcp-server-debugging`
- `mcp-security-audit`
- `api-and-interface-design`
