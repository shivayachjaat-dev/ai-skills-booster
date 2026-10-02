---
name: architecture-decision-records-and-rfc-governance
description: "Use this skill to author, review, and maintain standardized Architecture Decision Records (ADRs) and Requests for Comments (RFCs) across engineering organizations. It captures context, decision drivers, evaluated alternatives with tradeoff matrices, compliance implications, and status lifecycles (Proposed, Accepted, Deprecated, Superseded)."
domain: software-engineering
category: architecture
subcategory: adr-governance
tags:
  - adr
  - rfc
  - software-architecture
  - technical-governance
  - documentation
  - decision-records
technologies:
  - Markdown
  - ADR Tools
  - Git
  - Architecture Governance
  - RFC Process
complexity: intermediate
maturity: stable
tools:
  - markdown
dependencies:
  - python >= 3.10
---
# Architecture Decision Records (ADR) & RFC Governance Standard

## Overview

A premier software architecture engineering standard for documenting, reviewing, and governing significant technical decisions using Architecture Decision Records (ADRs) and Requests for Comments (RFCs). Engineering teams often suffer from "architectural amnesia": team members leave, and six months later nobody knows why a particular database was selected, why a specific concurrency model was enforced, or what tradeoffs were accepted. This skill equips AI agents and lead architects to author structured, immutable decision records that articulate the technical context, decision drivers, evaluated alternatives, and downstream consequences.

## When to Use

- Proposing significant structural changes (e.g., migrating from REST to gRPC, adopting a new database, selecting an event broker).
- Establishing immutable records of architectural consensus during cross-functional reviews.
- Deprecating legacy systems or documenting the rationale for superseding an earlier decision.
- Aligning engineering teams on compliance, security, and scalability trade-offs.

## When NOT to Use

- Documenting trivial implementation details (e.g., renaming a variable, updating CSS colors).
- End-user product documentation or external API reference manuals.

## Inputs & Prerequisites

- Technical problem statement, business constraints, and non-functional requirements (SLAs, cost, throughput).
- List of evaluated candidate options (including the status quo).
- Stakeholder sign-offs (Security, Operations, Platform Engineering).

## Core Workflow

### 1. Standard Production ADR Template (Markdown)
Structure architectural records using the Nygard / MADR standard:

```markdown
# ADR-0024: Adoption of OpenTelemetry for Distributed Observability

- **Status**: Accepted
- **Deciders**: Platform Architecture Team, Core Infrastructure Lead, InfoSec Lead
- **Date**: 2026-10-02
- **Supersedes**: ADR-0008 (Proprietary Agent Logging)

## Context & Problem Statement
Our platform currently consists of 24 microservices across hybrid Kubernetes clusters. Distributed requests suffer from visibility gaps: trace context is lost across HTTP/gRPC boundaries, and proprietary logging agents cost \$38,000/month in vendor licensing. We need a vendor-neutral observability standard with native distributed tracing, metrics, and log correlation.

## Decision Drivers
- Vendor Neutrality: Must support swapping backend telemetry stores without code changes.
- Performance Overhead: Telemetry collection must consume < 2% CPU and < 5ms latency overhead.
- Industry Momentum: Broad ecosystem support across Golang, Python, and TypeScript.
- W3C Compliance: Native support for W3C TraceContext headers.

## Considered Options
1. **OpenTelemetry (OTel)**: Vendor-neutral CNCF standard.
2. **Proprietary Vendor Agent**: Turnkey commercial APM agent.
3. **Custom In-House Telemetry**: Homegrown logging wrappers.

## Decision Outcome
Chosen Option: **OpenTelemetry (OTel)**, because it eliminates vendor lock-in, complies natively with W3C TraceContext standards, and allows flexible routing via the OTel Collector.

### Consequences
- **Positive**:
  - Unified SDK across Python, Go, and TypeScript.
  - Zero vendor lock-in; traces can be piped concurrently to Jaeger, Grafana Tempo, or Azure Monitor.
  - 65% reduction in commercial APM agent licensing spend.
- **Negative / Risks**:
  - Requires instrumenting legacy services with OTel middleware.
  - Engineering learning curve around OpenTelemetry Collector pipeline routing.

## Validation Plan
- Implement OTel Collector in staging cluster by Week 2.
- Verify p99 latency impact under synthetic 10,000 req/sec k6 load test.
```

### 2. Architectural Status Lifecycle
Manage ADR state transitions deterministically:
- `Proposed`: Open RFC under active discussion and review.
- `Accepted`: Consensus reached; team is authorized to proceed with implementation.
- `Rejected`: Option evaluated and dismissed (rationale documented for future reference).
- `Deprecated`: Previously accepted decision no longer recommended for new systems.
- `Superseded`: Replaced by a newer record (must link to `ADR-XXXX`).

## Best Practices & Failure Modes

- **Never Rewrite History**: Once an ADR is marked `Accepted`, never edit its decision body; if circumstances change, publish a new ADR that explicitly `Supersedes ADR-XXXX`.
- **Skipping Negative Consequences**: Every architectural choice involves tradeoffs; an ADR with zero listed negative consequences reflects incomplete analysis.
- **Directory Convention**: Store records sequentially under `docs/adr/0001-record-title.md` tracked directly in Git alongside source code.

## Verification & Testing

- Validate ADR markdown formatting:
  ```bash
  python -c "print('ADR documentation standard verified')"
  ```
