---
name: spiffe-spire-workload-identity
description: "Use this skill when designing and deploying cryptographic zero-trust workload identities across heterogeneous cloud and Kubernetes environments using SPIFFE and SPIRE. It covers SPIFFE ID naming conventions, SPIRE Server and Agent architecture, node attestation (AWS/K8s PSAT), Workload Attestation, and automated X.509 SVID issuance and rotation."
domain: security
category: zero-trust
subcategory: spiffe-spire
tags:
  - spiffe
  - spire
  - zero-trust
  - workload-identity
  - mtls
  - security
  - pki
technologies:
  - SPIFFE
  - SPIRE
  - Kubernetes
  - X.509 SVID
  - Go
complexity: advanced
maturity: stable
tools:
  - spire-server
  - spire-agent
  - kubectl
dependencies:
  - spire >= 1.8.0
---
# SPIFFE & SPIRE Cryptographic Workload Identity Architecture

## Overview

A definitive production architecture standard for establishing zero-trust workload authentication across multi-cloud and Kubernetes environments using SPIFFE (Secure Production Identity Framework for Everyone) and SPIRE (SPIFFE Runtime Environment). This skill instructs AI agents on standardizing SPIFFE IDs, configuring SPIRE Server CAs, performing hardware and platform node attestation, enforcing kernel-level workload attestation, and streaming short-lived X.509 SVIDs (SPIFFE Verifiable Identity Documents) without static API keys.

## When to Use

- Authenticating microservices across heterogeneous platforms (Kubernetes pods talking to bare-metal servers or multi-cloud instances) without sharing long-lived secrets.
- Enforcing mutual TLS (mTLS) with cryptographically verifiable identity embedded in client and server certificates.
- Automating short-lived credential rotation (SVIDs with 1-hour lifetimes renewed continuously).
- Replacing static database passwords with ephemeral dynamic workload credentials.

## When NOT to Use

- End-user identity and access management (IAM / SSO for human users; use OAuth2/OIDC).
- Simple isolated monolithic architectures where network firewalls and private VPCs provide sufficient boundary protection.

## Inputs & Prerequisites

- Kubernetes cluster or Linux virtual machines.
- SPIRE 1.8+ binaries or Helm charts.
- Trust domain established (e.g. `prod.company.internal`).

## Core Workflow

### 1. SPIFFE ID Standardization
Establish strict hierarchical naming schemas:
- **Format**: `spiffe://<trust-domain>/ns/<namespace>/sa/<serviceaccount>`
- **Example**: `spiffe://prod.company.internal/ns/payments/sa/payment-processor`

### 2. Declarative Workload Registration in SPIRE
Register workload identities with specific attestation selectors:

```bash
# Register Payment Processor Pod running on Kubernetes
spire-server entry create \
    -spiffeID spiffe://prod.company.internal/ns/payments/sa/payment-processor \
    -parentID spiffe://prod.company.internal/spire/agent/k8s_psat/prod-cluster \
    -selector k8s:ns:payments \
    -selector k8s:sa:payment-processor \
    -ttl 3600
```

### 3. Consuming SVIDs in Applications via Workload API
Applications retrieve X.509 SVIDs over a local Unix Domain Socket without storing any keys on disk:

```python
import socket
import ssl

# SPIRE Agent exposes the Workload API at a local Unix domain socket
WORKLOAD_SOCKET_PATH = "/tmp/spire-agent/public/api.sock"

def verify_spiffe_peer(cert_der: bytes, expected_spiffe_id: str) -> bool:
    """
    Inspects Subject Alternative Name (SAN) of peer X.509 certificate
    to ensure it matches the authorized SPIFFE ID.
    """
    from cryptography import x509
    cert = x509.load_der_x509_certificate(cert_der)
    sans = cert.extensions.get_extension_for_oid(x509.OID_SUBJECT_ALTERNATIVE_NAME).value
    uris = sans.get_values_for_type(x509.UniformResourceIdentifier)
    
    return expected_spiffe_id in uris
```

### 4. Kubernetes Node Attestation with Projected Service Account Tokens (PSAT)
Configure SPIRE Agent to securely attest against Kubernetes API:

```yaml
# spire-agent-config.yaml
agent:
  data_dir: "/run/spire"
  log_level: "INFO"
  server_address: "spire-server.spire.svc"
  server_port: "8081"
  trust_domain: "prod.company.internal"
  trust_bundle_path: "/run/spire/bundle/bundle.crt"

plugins:
  NodeAttestor "k8s_psat":
    plugin_data:
      cluster: "prod-cluster"

  WorkloadAttestor "k8s":
    plugin_data:
      skip_kubelet_verification: false

  KeyManager "memory":
    plugin_data: {}
```

## Best Practices & Failure Modes

1. **Selector Spoofing via Broad Matching**: Defining an entry with only `k8s:ns:production` allows *any* container in that namespace to assume the identity. Always combine multiple specific selectors: `k8s:ns`, `k8s:sa`, and container image hash.
2. **Missing Clock Synchronization**: SPIFFE SVID certificates have short lifetimes (often 10 minutes to 1 hour). If worker nodes experience NTP clock drift, valid certificates will be rejected as either not-yet-valid or expired. Ensure chrony/NTP runs on all nodes.
3. **Socket Permission Denials**: Containers must mount the SPIRE Agent Unix Domain Socket with appropriate user permissions (`fsGroup: 10001` or read permissions).

## Verification & Testing

- Query SPIRE Agent to verify available identities:
  ```bash
  spire-agent api fetch x509 -socketPath /tmp/spire-agent/public/api.sock
  ```
- Inspect certificate details and SPIFFE ID in SAN:
  ```bash
  openssl x509 -in svid.0.pem -text -noout | grep -A1 "Subject Alternative Name"
  ```
