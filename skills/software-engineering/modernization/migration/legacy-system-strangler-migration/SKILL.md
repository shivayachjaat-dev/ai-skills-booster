---
name: legacy-system-strangler-migration
description: "Use this skill when incrementally modernizing, decomposing, and replacing legacy monoliths or deprecated backend systems without risky all-at-once cutovers. It guides the agent through the Strangler Fig pattern, reverse proxy intercept routing, parallel run shadow verification, database synchronization, and progressive decommission."
domain: software-engineering
category: modernization
subcategory: migration
tags:
  - software-engineering
  - modernization
  - architecture
  - strangler-fig
  - refactoring
  - legacy-migration
technologies:
  - Nginx
  - Envoy
  - Docker
  - Python
  - TypeScript
complexity: expert
maturity: stable
tools:
  - git
  - curl
dependencies:
  - git >= 2.30
---
# Legacy System Strangler Migration

## Overview

A battle-tested architectural framework for incrementally replacing legacy systems, monolithic codebases, and deprecated services using Martin Fowler's Strangler Fig pattern. Eliminates the catastrophic risk of "big bang" rewrites by gradually carving out business capabilities behind an intercepting proxy until the legacy system can be decommissioned safely.

## When to Use

- Migrating a critical production monolith to modern microservices or a cleaner modular architecture.
- Replacing legacy backend frameworks (PHP 5, Python 2, Ruby on Rails 3, .NET Framework) with modern stacks.
- Transitioning monolithic database tables into dedicated bounded-context databases.
- Migrating services where zero downtime and zero customer disruption are mandatory.

## When NOT to Use

- Small codebases (< 5,000 lines) where an in-place refactor or short weekend cutover carries low risk.
- Greenfield development with no existing production users or data.

## Inputs & Prerequisites

- Working knowledge of legacy system interfaces, endpoints, and database tables.
- Reverse proxy or API gateway (Nginx, Envoy, Cloudflare, Traefik) positioned in front of legacy system.
- Target modern tech stack and deployment pipeline.

## Core Workflow

### 1. Edge Intercept Proxy Positioning
Place an intelligent routing proxy in front of the legacy application without modifying legacy code:
```text
Clients ───► [ Routing Proxy / Gateway ]
                   │              │
         (Migrated Routes)   (Legacy Routes)
                   │              │
                   ▼              ▼
           [ New Service ]  [ Legacy Monolith ]
```

### 2. Capability Slicing (Bounded Context Isolation)
Identify a narrow, high-value, self-contained feature to carve out first:
- Choose a slice with low dependency entanglement (e.g. `Notification Service` or `Authentication`).
- Implement the capability cleanly in the new service with modern test coverage.

### 3. Shadow Traffic & Parallel Run Verification
Before routing real user requests to the new service, verify parity using shadow traffic:
1. Proxy duplicates production requests (`mirroring`).
2. Primary response is served to user from Legacy Monolith.
3. Shadow request is sent asynchronously to New Service.
4. Compare responses: log differences in status codes, latency, and payload bodies.
```nginx
# Nginx Mirroring Example
location /api/v1/orders {
    mirror /mirror_to_new_service;
    proxy_pass http://legacy_monolith;
}
location /mirror_to_new_service {
    internal;
    proxy_pass http://new_service;
}
```

### 4. Incremental Traffic Cutover (Canary)
Once shadow parity achieves 99.99%:
1. Route 1% of live traffic to the new service using feature flags or gateway weights.
2. Monitor error rates, database locks, and latency percentiles (P95/P99).
3. Gradually ramp traffic: 1% $\rightarrow$ 10% $\rightarrow$ 50% $\rightarrow$ 100%.
4. Maintain instant rollback capability to legacy routing if anomalies emerge.

### 5. Data Synchronization & Eventual Decommission
- For stateful migrations, use Change Data Capture (CDC via Debezium) or application dual-writing to keep legacy and new databases in sync during the transition.
- Once 100% of traffic for all carved slices is handled by the new architecture, turn off legacy background cron jobs, archive legacy database tables, and decommission legacy servers.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Discrepancy between legacy and new response | Investigate whether legacy behavior is a documented feature or an undocumented legacy bug that consumers now depend on (Hyrum's Law). |
| Shared monolithic database prevents separation | Access shared DB initially, then create a separate database for the new service and synchronize data asynchronously. |
| User session state shared across legacy and new | Centralize session validation in a shared Redis cache or sign tokens with a shared JWT secret. |

## Validation & Acceptance Criteria

- [ ] Reverse proxy intercepts traffic with zero downtime or performance penalty.
- [ ] Shadow traffic verification achieves zero unexpected payload differences.
- [ ] Canary traffic ramp supports instant 1-click rollback.
- [ ] End-to-end integration tests verify functional parity across boundary interfaces.
- [ ] Legacy code deleted and decommissioned once traffic is completely transitioned.

## Failure Handling & Recovery

- If canary traffic generates unexpected error spikes, adjust gateway routing back to 100% legacy immediately; the user experiences zero outage.

## Expected Output & Artifacts

- Proxy routing configuration manifest (Nginx/Envoy).
- Shadow traffic response diff comparison scripts.
- Phased migration roadmap document.

## Related Skills

- `api-and-interface-design`
- `database-migration-safety`
- `ci-cd-and-automation`
