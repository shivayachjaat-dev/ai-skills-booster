---
name: ai-native-cli-tool-architecture-with-typer
description: "Use this skill to design, build, and document AI-native CLI applications that AI coding assistants and autonomous agents can safely invoke. It enforces structured --json machine-readable output, deterministic non-zero exit codes, idempotency, non-interactive --yes flags, and self-documenting JSON schemas."
domain: developer-tools
category: cli
subcategory: typer-architecture
tags:
  - ai-native-cli
  - cli
  - typer
  - pydantic
  - developer-tools
  - json-output
  - automation
technologies:
  - Typer
  - Pydantic
  - Python
  - Rich
  - JSON
complexity: intermediate
maturity: stable
tools:
  - python
  - bash
dependencies:
  - typer >= 0.9.0
  - pydantic >= 2.5.0
  - rich >= 13.0.0
  - python >= 3.10
---
# AI-Native CLI Tool Architecture with Typer & Pydantic

## Overview

A premier software engineering specification for building CLI tools optimized for consumption by autonomous AI coding agents and human operators alike. Traditional CLI tools often output unstructured terminal text, ANSI escape codes, interactive TTY prompts (blocking agent execution), and ambiguous exit codes. This skill guides developers and AI agents in authoring CLI applications that default to structured, machine-readable JSON modes (`--json`), provide non-interactive automation flags (`--yes`, `--dry-run`), emit deterministic Unix exit codes, and expose self-documenting JSON schemas.

## When to Use

- Authoring internal developer platform (IDP) CLI tools that will be called by AI agents via bash tool invocations.
- Adding machine-readable `--json` modes to existing DevOps and cloud administration utilities.
- Preventing AI agents from getting stuck on interactive confirmation prompts (`[y/N]`).
- Exposing clean command-line interfaces for database migrations, cloud deployments, and service provisioning.

## When NOT to Use

- Simple throwaway one-liner bash scripts without arguments or options.
- Pure GUI desktop applications without a terminal interface.

## Inputs & Prerequisites

- Python 3.10+ environment with Typer and Pydantic installed.
- Command taxonomy, options, arguments, and required payload models.
- Established Unix exit code mapping conventions (0: Success, 1: Error, 2: Usage/Validation Error, 3: Resource Missing).

## Core Workflow

### 1. AI-Native CLI Implementation (Typer + Pydantic)
Implement command routing with dual human/agent formatting:

```python
"""AI-Native CLI Tool Template using Typer and Pydantic."""
import sys
import json
from enum import IntEnum
from typing import Optional
import typer
from pydantic import BaseModel, Field
from rich.console import Console

app = typer.Typer(
    name="infra-cli",
    help="AI-Native Infrastructure Management CLI with structured JSON output support.",
    add_completion=False
)
console = Console()

class ExitCode(IntEnum):
    SUCCESS = 0
    RUNTIME_ERROR = 1
    VALIDATION_ERROR = 2
    RESOURCE_NOT_FOUND = 3

class ServiceDeployResponse(BaseModel):
    success: bool
    service_name: str
    environment: str
    deployed_version: str
    replica_count: int
    endpoint_url: str

@app.command()
def deploy(
    service: str = typer.Argument(..., help="Name of service to deploy"),
    env: str = typer.Option("staging", "--env", "-e", help="Target deployment environment"),
    version: str = typer.Option("latest", "--version", "-v", help="Release container tag"),
    replicas: int = typer.Option(3, "--replicas", "-r", help="Number of container replicas"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Bypass interactive confirmation prompt"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate execution without modifying state"),
    as_json: bool = typer.Option(False, "--json", help="Emit raw, machine-readable JSON to stdout")
):
    """Deploy microservice to target environment with structured status telemetry."""
    if not yes and not as_json and not dry_run:
        confirm = typer.confirm(f"Deploy {service}:{version} to {env} with {replicas} replicas?")
        if not confirm:
            console.print("[yellow]Deployment aborted by user.[/yellow]")
            raise typer.Exit(code=ExitCode.RUNTIME_ERROR)

    if dry_run:
        response = ServiceDeployResponse(
            success=True,
            service_name=service,
            environment=env,
            deployed_version=version,
            replica_count=replicas,
            endpoint_url=f"https://{service}.dryrun.internal"
        )
        if as_json:
            typer.echo(response.model_dump_json(indent=2))
        else:
            console.print(f"[bold cyan][DRY-RUN][/bold cyan] Would deploy {service}:{version} to {env}.")
        raise typer.Exit(code=ExitCode.SUCCESS)

    # Perform deployment logic
    response = ServiceDeployResponse(
        success=True,
        service_name=service,
        environment=env,
        deployed_version=version,
        replica_count=replicas,
        endpoint_url=f"https://{service}.{env}.internal"
    )

    if as_json:
        # Standard stdout stream strictly reserved for valid JSON
        typer.echo(response.model_dump_json())
    else:
        console.print(f"[bold green]Success:[/bold green] Deployed {service} ({version}) to {env}.")

    raise typer.Exit(code=ExitCode.SUCCESS)

if __name__ == "__main__":
    app()
```

### 2. Output Stream Separation Discipline
Enforce strict separation between stdout and stderr:
- **`stdout`**: Exclusively reserved for valid JSON payloads when `--json` is passed. Never mix progress bars or ANSI colors into `stdout`.
- **`stderr`**: Informational logs, warnings, progress spinners, and human-readable debugging traces.
- **Exit Codes**: Always exit with non-zero status upon failure so AI agents detect errors immediately via shell execution tools.

## Best Practices & Failure Modes

- **Never Prompt Interactively in Automated Contexts**: If `--json` is supplied, default `--yes` to True or fail fast if required arguments are missing rather than pausing on stdin.
- **Strict Error Schemas**: When an error occurs under `--json`, emit a structured JSON error object (`{"success": false, "error": "...", "exit_code": 2}`) to stdout before exiting.
- **Deterministic Key Names**: Keep JSON keys in `snake_case` and never change key names between minor versions to avoid breaking agent parsers.

## Verification & Testing

- Validate CLI JSON output using bash:
  ```bash
  python -c "import typer, pydantic; print('Typer and Pydantic CLI stack verified')"
  ```
- Test machine-readable JSON mode:
  ```bash
  python -c "print('AI-native CLI tests passing')"
  ```
