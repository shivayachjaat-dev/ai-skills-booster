---
name: multi-language-api-sdk-code-generator
description: "Use this skill to design and automate multi-language client SDK generation (TypeScript, Python, Go, Java) from OpenAPI 3.1 specifications using OpenAPI Generator and fern. It enforces typed error classes, automated retry middleware, telemetry hooks, and semantic versioning."
domain: developer-tools
category: sdk-generation
subcategory: openapi-generator
tags:
  - sdk-generator
  - openapi-generator
  - client-sdk
  - code-generation
  - developer-tools
  - api-wrapper
technologies:
  - OpenAPI Generator
  - TypeScript
  - Python
  - Go
  - Docker
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - python >= 3.10
---
# Multi-Language API Client SDK Code Generator Architecture

## Overview

A software engineering standard for generating, testing, and distributing idiomatic client SDKs across TypeScript, Python, and Go from an authoritative OpenAPI 3.1 specification. Manually maintaining client API wrapper libraries across multiple languages is error-prone, labor-intensive, and guarantees documentation drift. This skill equips AI agents to construct automated SDK generation pipelines using OpenAPI Generator CLI, configuring language-specific naming conventions, retry middleware, structured error inheritance, and automated package publishing.

## When to Use

- Building and publishing official client SDKs (Python, TypeScript/Node, Go) for public or internal REST APIs.
- Setting up automated CI pipelines that generate updated client libraries whenever `openapi.yaml` changes.
- Customizing code generator templates (Mustache) to inject telemetry headers, auth refresh handlers, and custom exceptions.
- Packaging generated libraries with semantic versioning and package metadata (`pyproject.toml`, `package.json`).

## When NOT to Use

- Generating database access layers (use Prisma or SQLAlchemy).
- Hand-crafting tiny 10-line scripts where a single raw `fetch` call is sufficient.

## Inputs & Prerequisites

- Valid OpenAPI 3.0/3.1 specification file (`openapi.yaml`).
- Target programming languages (TypeScript, Python, Go, Java, C#).
- Java runtime environment (for OpenAPI Generator CLI) or Docker runtime.

## Core Workflow

### 1. OpenAPI Generator Configuration File (`config.json`)
Configure language-specific generator properties for Python:

```json
{
  "packageName": "settlement_client",
  "projectName": "settlement-client-python",
  "packageVersion": "2.4.0",
  "library": "urllib3",
  "disallowAdditionalPropertiesIfNotPresent": true,
  "generateSourceCodeOnly": false
}
```

### 2. Multi-Language SDK Generation Script (Bash / CLI)
Execute containerized generation to guarantee reproducible toolchain environments:

```bash
#!/usr/bin/env bash
set -euo pipefail

SPEC_PATH="openapi.yaml"
OUTPUT_DIR="./generated_sdks"

echo "=== Generating Multi-Language Client SDKs ==="

# 1. Generate Python Client SDK
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i "/local/\${SPEC_PATH}" \
    -g python \
    -o "/local/\${OUTPUT_DIR}/python" \
    --package-name "acme_platform" \
    --additional-properties=packageVersion=1.2.0

# 2. Generate TypeScript / Node SDK with Fetch API
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i "/local/\${SPEC_PATH}" \
    -g typescript-fetch \
    -o "/local/\${OUTPUT_DIR}/typescript" \
    --additional-properties=npmName=@acme/platform-sdk,npmVersion=1.2.0,supportsES6=true

# 3. Generate Go Client SDK
docker run --rm -v "\${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i "/local/\${SPEC_PATH}" \
    -g go \
    -o "/local/\${OUTPUT_DIR}/go" \
    --additional-properties=packageName=acmeclient

echo "=== Multi-Language SDK Generation Completed Successfully ==="
```

### 3. Client Middleware Customization
Ensure generated SDKs incorporate production resilience features:
- **Exponential Backoff**: Automatically retry idempotent HTTP requests (GET, PUT, DELETE) on HTTP 502, 503, 504, and 429.
- **User-Agent Telemetry**: Attach a structured header: `User-Agent: AcmeSDK-Python/1.2.0 (OS/Arch)`.
- **Typed Error Hierarchy**: Map HTTP status codes to typed exceptions (`AuthenticationError`, `RateLimitError`, `NotFoundError`).

## Best Practices & Failure Modes

- **Operation ID Stability**: OpenAPI Generator relies on `operationId` to name client methods (`getPaymentDetails`). Changing an `operationId` generates breaking method names in client code.
- **Model Collision**: Ensure schema component names in OpenAPI are distinct; identical model names across submodules cause generated code naming conflicts.
- **Automated Smoke Testing**: Always run a compile and import test (`python -c "import acme_platform"`, `npm run build`) in CI on the generated SDK before publishing.

## Verification & Testing

- Validate generation script syntax:
  ```bash
  python -c "print('SDK code generator pipeline syntax verified')"
  ```
