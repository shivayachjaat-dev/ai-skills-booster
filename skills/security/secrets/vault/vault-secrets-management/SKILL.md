---
name: vault-secrets-management
description: "Use this skill when architecting and managing enterprise secrets using HashiCorp Vault. It guides the agent through dynamic database credentials generation, lease management and renewal, Kubernetes ServiceAccount authentication, PKI on-demand certificate issuance, transit encryption, and disaster recovery replication."
domain: security
category: secrets
subcategory: vault
tags:
  - vault
  - hashicorp-vault
  - secrets-management
  - security
  - dynamic-secrets
  - pki
technologies:
  - HashiCorp Vault
  - Kubernetes
  - PostgreSQL
  - OpenSSL
  - hvac
complexity: advanced
maturity: stable
tools:
  - vault
  - kubectl
dependencies:
  - vault >= 1.14
---
# HashiCorp Vault Enterprise Secrets Management

## Overview

A comprehensive guide for architecting zero-trust secrets management with HashiCorp Vault. Instead of static API keys and hardcoded database passwords, this skill provides agents with concrete blueprints for dynamic database credential generation, automated lease lifecycle management, Kubernetes native authentication, on-the-fly PKI certificate authority issuance, and encryption as a service (Transit engine).

## When to Use

- Eliminating static database passwords in microservices via dynamic, short-lived role credentials.
- Authenticating Kubernetes pods to Vault using service accounts without storing tokens in secrets.
- Setting up internal PKI engines to generate mutual TLS (mTLS) certificates with automated renewals.
- Protecting sensitive customer data (PII/PCI) using Vault Transit secrets engine (envelope encryption).
- Automating secret rotation, lease renewal hooks, and revocation upon breach.

## When NOT to Use

- Simple local development environments where environment variables (`.env`) suffice.
- Public cloud native secrets (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) when cloud vendor lock-in is acceptable and dedicated Vault infrastructure is overkill.

## Inputs & Prerequisites

- Vault 1.14+ server (OSS or Enterprise) running and unsealed.
- Admin token or access policy with capabilities to mount engines and configure auth paths.
- Python client `hvac` or CLI tool `vault`.

## Core Workflow

### 1. Dynamic Database Credentials Engine
Mount and configure the database secrets engine to generate short-lived, per-connection PostgreSQL credentials:

```bash
# Enable database engine
vault secrets enable database

# Configure connection to PostgreSQL
vault write database/config/postgresql-prod \
    plugin_name=postgresql-database-plugin \
    allowed_roles="backend-service-role" \
    connection_url="postgresql://{{username}}:{{password}}@postgres.internal:5432/app_production?sslmode=verify-full" \
    username="vault_admin" \
    password="super-secure-vault-admin-password"

# Define dynamic role with 1-hour TTL and 24-hour max TTL
vault write database/roles/backend-service-role \
    db_name=postgresql-prod \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

### 2. Automated Lease Renewal in Python (`hvac`)
Applications must handle background lease renewal before expiration:

```python
import hvac
import threading
import time
import logging

logger = logging.getLogger("vault-client")

class VaultCredentialsManager:
    def __init__(self, vault_url: str, role_id: str, secret_id: str):
        self.client = hvac.Client(url=vault_url)
        # Authenticate via AppRole
        auth_resp = self.client.auth.approle.login(role_id=role_id, secret_id=secret_id)
        self.client.token = auth_resp["auth"]["client_token"]
        self._stop_event = threading.Event()

    def get_dynamic_db_credentials(self, role_name: str) -> dict:
        creds = self.client.secrets.database.generate_credentials(name=role_name)
        lease_id = creds["lease_id"]
        lease_duration = creds["lease_duration"]
        
        # Start background renewal worker
        renewal_thread = threading.Thread(
            target=self._renew_lease_loop,
            args=(lease_id, lease_duration),
            daemon=True
        )
        renewal_thread.start()
        
        return {
            "username": creds["data"]["username"],
            "password": creds["data"]["password"],
            "lease_id": lease_id
        }

    def _renew_lease_loop(self, lease_id: str, duration: int):
        # Renew at 75% of TTL
        interval = max(int(duration * 0.75), 10)
        while not self._stop_event.wait(interval):
            try:
                renew_resp = self.client.sys.renew_lease(lease_id=lease_id, increment=duration)
                logger.info(f"Renewed lease {lease_id} for {renew_resp['lease_duration']}s")
            except Exception as e:
                logger.error(f"Failed to renew lease {lease_id}: {e}")
                break
```

### 3. Kubernetes Native Authentication
Allow pods to authenticate using their injected ServiceAccount token:

```bash
# Enable kubernetes auth
vault auth enable kubernetes

# Configure Vault with K8s API host and token reviewer JWT
vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc:443"

# Bind ServiceAccount 'orders-api' in namespace 'production' to Vault policy
vault write auth/kubernetes/role/orders-api-role \
    bound_service_account_names=orders-api \
    bound_service_account_namespaces=production \
    policies=orders-db-access \
    ttl=24h
```

### 4. Transit Secrets Engine (Encryption as a Service)
Encrypt customer PII before saving to database:

```bash
# Enable Transit engine
vault secrets enable transit

# Create convergent encryption key
vault write -f transit/keys/customer-ssn type=aes256-gcm96 derived=true
```

```python
import base64

def encrypt_pii(client: hvac.Client, plaintext: str, context: str) -> str:
    encoded_text = base64.b64encode(plaintext.encode()).decode()
    encoded_ctx = base64.b64encode(context.encode()).decode()
    resp = client.secrets.transit.encrypt_data(
        name="customer-ssn",
        plaintext=encoded_text,
        context=encoded_ctx
    )
    return resp["data"]["ciphertext"]
```

## Best Practices & Failure Modes

1. **Lease Expiration / Max TTL**: Dynamic credentials cannot be renewed past `max_ttl`. Applications must detect impending max TTL and establish a new lease connection pool gracefully.
2. **Token Revocation Cascades**: Revoking a parent token revokes all child leases and credentials. Use orphan tokens or AppRole service tokens for background workers.
3. **Audit Devices**: Always enable multiple audit logs (`sys/audit/file` and `sys/audit/syslog`). Vault will refuse write requests if all audit logs are blocked.
4. **Disaster Recovery**: Implement Raft storage with automated automated snapshots (`vault operator raft snapshot save`).

## Verification & Testing

- Verify dynamic credential generation:
  ```bash
  vault read database/creds/backend-service-role
  ```
- Test credential validity against PostgreSQL:
  ```bash
  PGPASSWORD="<generated_password>" psql -h postgres.internal -U "<generated_username>" -d app_production -c "SELECT current_user;"
  ```
- Inspect active leases:
  ```bash
  vault list sys/leases/lookup/database/creds/backend-service-role
  ```
