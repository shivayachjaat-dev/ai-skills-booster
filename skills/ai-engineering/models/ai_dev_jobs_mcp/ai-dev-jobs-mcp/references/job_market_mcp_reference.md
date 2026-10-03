# Model Context Protocol (MCP) Job Market Schema & Tool Specifications

## Standard JSON-RPC 2.0 Method Definitions
The job market MCP protocol exposes standardized tools allowing client agents to discover roles and analyze labor markets:

### Tool: `search_jobs`
```json
{
  "name": "search_jobs",
  "description": "Searches active AI/ML and software engineering job listings.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Job title or key technology (e.g., 'LangGraph', 'CUDA')"},
      "salary_min": {"type": "integer", "description": "Minimum annual base salary in USD"},
      "remote": {"type": "boolean", "description": "Filter for remote-first roles"},
      "limit": {"type": "integer", "default": 20, "maximum": 100}
    },
    "required": ["query"]
  }
}
```

### Tool: `get_market_statistics`
```json
{
  "name": "get_market_statistics",
  "description": "Returns salary percentiles, active opening counts, and demand velocity for a role category.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "enum": ["ai-agent-engineer", "mlops-engineer", "research-scientist", "llm-infra-engineer"]
      }
    },
    "required": ["category"]
  }
}
```

## Seniority Mapping Standards
| Tier | Experience | Key Competencies |
|---|---|---|
| **Junior / Associate** | 0 - 2 years | Scripting, basic model prompting, unit test authoring |
| **Mid-Level** | 3 - 5 years | Fine-tuning, RAG pipeline construction, production API deployment |
| **Senior** | 5 - 8 years | Autonomous agent loops, distributed inference, custom CUDA kernels |
| **Staff / Principal** | 8+ years | Enterprise multi-agent systems, cross-org model governance, cluster scaling |
