# Gemini Interactions API Technical Reference

## Architectural Migration: From generateContent to Interactions

The **Gemini Interactions API** standardizes multimodal conversational agent interactions, function calling loops, structured output enforcement, and long-horizon thread persistence into a unified runtime model.

### Execution Paradigm

```
                   [ User Interaction Request ]
                                |
                                v
               [ Gemini Interactions Client Engine ]
                                |
            +-------------------+-------------------+
            |                                       |
    [ Tool Invocation ]                     [ Structured Schema ]
    - Evaluates JSON args                   - Pydantic / JSON schema
    - Executes local handler                - Strict output typing
    - Feeds tool output back                        |
            |                                       v
            +-------------------------------------> [ Synthesized Result ]
```

### SDK Best Practices

1. **Tool Execution Handlers**: Register typed functions with clear parameter descriptions. The client handles invoking the tool and appending `tool_results` to the thread automatically.
2. **Deterministic Schemas**: Use standard JSON Schema or Pydantic models with `response_schema` to prevent hallucinated keys.
3. **Session Threading**: Maintain stateful interaction histories across turns to avoid re-transmitting prompt prefixes.
4. **Defensive Rate-Limit Retries**: Implement exponential backoff for `RESOURCE_EXHAUSTED` (HTTP 429) errors.
