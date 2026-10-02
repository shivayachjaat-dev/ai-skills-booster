---
name: zero-trust-network-architecture
description: "Use this skill when designing, assessing, and enforcing Zero Trust Network Architecture (ZTNA) across distributed services. It guides the agent through eliminating implicit perimeter trust, mutual TLS (mTLS) service mesh identity, ephemeral device attestation, microsegmentation policies, and continuous context-aware authorization."
domain: security
category: architecture
subcategory: zero-trust
tags:
  - security
  - zero-trust
  - ztna
  - mtls
  - network-security
  - cloud-security
technologies:
  - mTLS
  - SPIFFE/SPIRE
  - Istio
  - WireGuard
  - OIDC
complexity: expert
maturity: stable
tools:
  - openssl
  - curl
dependencies:
  - openssl >= 1.1.1
---
# Zero Trust Network Architecture

## Overview

An enterprise security engineering guide for eliminating implicit trust within cloud and hybrid network perimeters. Guided by the core Zero Trust axiom *"Never Trust, Always Verify"*, this skill instructs AI agents on implementing cryptographic workload identities (SPIFFE/SPIRE), enforcing ubiquitous mutual TLS (mTLS), enacting granular microsegmentation, and evaluating continuous context-aware authorization policies.

## When to Use

- Replacing vulnerable legacy VPN perimeters with identity-aware Zero Trust Network Access (ZTNA).
- Hardening service-to-service communication within Kubernetes or multi-cloud topologies.
- Implementing cryptographic workload attestation and short-lived certificate lifecycles.
- Meeting compliance standards requiring internal network encryption and least-privilege microsegmentation (NIST SP 800-207).

## When NOT to Use

- Monolithic single-server hobby projects where all processes communicate strictly via local UNIX domain sockets.
- Standard client-facing browser TLS termination (use reverse proxy ingress guides).

## Inputs & Prerequisites

- Workload identity platform or PKI infrastructure (HashiCorp Vault, SPIRE, or cloud Certificate Authority).
- Service mesh or proxy layer (Istio, Linkerd, Envoy, or Cilium).
- Defined workload inventory and network communication dependency graphs.

## Core Workflow

### 1. Cryptographic Workload Identity (SPIFFE/SPIRE)
Never authenticate services based on mutable network attributes (IP addresses or subnet CIDRs). Assign every workload a verifiable cryptographic identity:
- Workload receives a SPIFFE ID: `spiffe://company.internal/ns/production/sa/payment-service`.
- Identity provider issues an X.509 SVID (SPIFFE Verifiable Identity Document) with short validity (e.g. 1 hour).
- SVID is automatically rotated before expiration without application restarts.

### 2. Ubiquitous Mutual TLS (mTLS) Enactment
Enforce bidirectional cryptographic authentication between all communicating services:
- Client verifies Server certificate against internal trusted CA root.
- Server validates Client certificate and extracts caller SPIFFE ID.
- Wire traffic is encrypted with modern ciphers (TLS 1.3 with ChaCha20-Poly1305 or AES-GCM).

### 3. Microsegmentation & Strict Default-Deny Policies
Configure service mesh or CNI network policies with an explicit default-deny posture:
```yaml
# Istio AuthorizationPolicy Example
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-access-control
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["spiffe://company.internal/ns/production/sa/checkout-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/v1/charge"]
```
Any caller not explicitly declared in `principals` is rejected with `HTTP 403 Forbidden` at the proxy layer.

### 4. Continuous Adaptive Authorization
Authentication is not a one-time check at connection establishment. Evaluate contextual risk continuously:
- **Device Health / Attestation**: Verify endpoint complies with disk encryption and EDR agent status.
- **Geographic Anomaly**: Flag sudden location hops or impossible travel velocity.
- **Session Duration & Inactivity**: Expire sessions after idle timeout, requiring step-up authentication for high-risk actions.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Legacy service cannot terminate mTLS | Deploy Envoy sidecar proxy alongside legacy container to terminate mTLS and forward plaintext over localhost loopback. |
| CA root certificate rotation | Implement dual-root trust anchors during transition: trust both old and new CA roots before retiring the old root. |
| Cross-cluster / multi-cloud communication | Establish SPIFFE trust domain federation (`SPIFFE Federation`) using public bundle endpoints. |

## Validation & Acceptance Criteria

- [ ] All inter-service traffic encrypted using TLS 1.3.
- [ ] Network policies enforce default-deny across all namespaces.
- [ ] Service identities cryptographically attested via X.509 SVIDs (< 2-hour lifespan).
- [ ] Unauthorized traffic blocked at proxy layer with zero packets reaching application containers.
- [ ] Continuous audit logs capture every authorization decision.

## Failure Handling & Recovery

- If certificate authority distribution fails, ensure cached SVIDs remain valid for grace period while raising urgent high-priority alerts to prevent traffic blackout.

## Expected Output & Artifacts

- Microsegmentation NetworkPolicy and AuthorizationPolicy YAML manifests.
- SPIFFE/SPIRE workload registration definitions.
- Zero Trust compliance verification report.

## Related Skills

- `oauth2-jwt-authentication-flow`
- `kubernetes-crashloop-debugging`
- `docker-container-optimization`
