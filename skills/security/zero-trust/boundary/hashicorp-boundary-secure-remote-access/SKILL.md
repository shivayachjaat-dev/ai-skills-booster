---
name: hashicorp-boundary-secure-remote-access
description: "Use this skill when designing, configuring, and operating identity-aware secure remote access architectures using HashiCorp Boundary. It guides the agent through defining Scopes (Global, Org, Project), dynamic host catalogs (AWS/K8s), targets (SSH, PostgreSQL, Kubernetes), credential brokering with Vault, and session recording."
domain: security
category: zero-trust
subcategory: boundary
tags:
  - boundary
  - hashicorp
  - zero-trust
  - remote-access
  - ssh
  - security
  - bastion
technologies:
  - HashiCorp Boundary
  - HashiCorp Vault
  - PostgreSQL
  - SSH
  - Kubernetes
complexity: advanced
maturity: stable
tools:
  - boundary
  - ssh
dependencies:
  - boundary >= 0.14.0
---
# HashiCorp Boundary Zero-Trust Remote Access Architecture

## Overview

A comprehensive engineering guide for replacing legacy VPNs and bastion jump hosts with HashiCorp Boundary. Boundary enables identity-based, least-privilege remote access to private infrastructure (databases, SSH servers, Kubernetes clusters) without exposing internal network IP ranges or distributing static credentials. This skill instructs AI agents on scope hierarchies, dynamic cloud host catalogs, credential brokering with Vault, and target session authorization.

## When to Use

- Providing developers and operators with secure access to private RDS databases, internal web applications, or SSH instances.
- Eliminating fragile, unmonitored bastion jump hosts and static SSH private keys.
- Brokering dynamic, single-use database credentials directly upon session connection via Vault integration.
- Auditing and recording interactive terminal sessions for SOC2 / ISO 27001 compliance.

## When NOT to Use

- Automated microservice-to-microservice traffic (use SPIFFE/SPIRE or Istio mTLS).
- Public web application edge reverse proxying (use Cloudflare or NGINX).

## Inputs & Prerequisites

- HashiCorp Boundary 0.14+ Controller and Worker cluster running.
- Authenticated identity provider (OIDC via Okta/AzureAD/GitHub or Password auth).
- Boundary CLI installed (`boundary`).

## Core Workflow

### 1. Boundary Scope Hierarchy & Project Setup
Organize infrastructure into administrative and project scopes:

```bash
# 1. Create Organization Scope
boundary scopes create -scope-id global \
    -name "Engineering" \
    -description "Engineering Operations Organization"

# 2. Create Project Scope inside Org
boundary scopes create -scope-id <org_id> \
    -name "Production-Infra" \
    -description "Production Infrastructure Project"
```

### 2. Defining Targets with Credential Brokering via Vault
Create a PostgreSQL target that automatically retrieves dynamic credentials from HashiCorp Vault:

```bash
# 1. Configure Vault Credential Store in Boundary
boundary credential-stores create vault \
    -scope-id <project_id> \
    -vault-address "https://vault.internal:8200" \
    -vault-token "<boundary-vault-token>"

# 2. Configure Credential Library mapping to Vault dynamic DB role
boundary credential-libraries create vault \
    -credential-store-id <cred_store_id> \
    -vault-path "database/creds/analyst-role" \
    -name "PostgreSQL Dynamic Analyst Credentials"

# 3. Create Boundary Target bound to Host and Credential Library
boundary targets create tcp \
    -scope-id <project_id> \
    -name "production-postgres" \
    -default-port 5432 \
    -session-connection-limit -1 \
    -session-max-seconds 14400 \
    -brokered-credential-source-id <cred_lib_id>
```

### 3. Connecting to Targets via Developer CLI
Developers connect securely through an authenticated local proxy without knowing database passwords:

```bash
# Authenticate to Boundary via OIDC / SSO
boundary authenticate oidc -auth-method-id <auth_method_id>

# Connect to target: Boundary sets up local listening proxy and prints injected credentials
boundary connect postgres -target-id <target_id> -dbname app_production
```

### 4. Interactive SSH Session with Session Recording
Record full terminal input/output for security auditing:

```bash
# Create SSH Target with Session Recording Enabled
boundary targets create ssh \
    -scope-id <project_id> \
    -name "k8s-worker-nodes" \
    -default-port 22 \
    -enable-session-recording=true \
    -storage-bucket-id <s3_recording_bucket_id>

# Developer connects via standard SSH client through Boundary
boundary connect ssh -target-id <ssh_target_id> -- -l ubuntu
```

## Best Practices & Failure Modes

1. **Direct Network Exposure Vulnerability**: If internal target servers have public IP addresses or unrestricted security groups, users can bypass Boundary entirely. Ensure target security groups accept traffic *only* from the private IPs of Boundary Workers.
2. **Worker Registration Latency**: Boundary Controllers assign sessions only to healthy Workers. Ensure Workers have outbound network access to Controllers on port 9201 and target servers on requested ports.
3. **Session Leakage**: Always configure `session-max-seconds` (e.g. 4 hours) and `session-connection-limit` to prevent abandoned developer sessions from remaining open indefinitely.

## Verification & Testing

- Inspect active session telemetry:
  ```bash
  boundary sessions list -scope-id <project_id>
  ```
- Terminate a suspicious active session administratively:
  ```bash
  boundary sessions cancel -id <session_id>
  ```
