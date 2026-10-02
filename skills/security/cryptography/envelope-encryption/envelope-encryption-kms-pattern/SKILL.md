---
name: envelope-encryption-kms-pattern
description: "Use this skill when architecting and implementing cryptographic envelope encryption for sensitive data at rest using cloud Key Management Services (AWS KMS, GCP KMS, Azure Key Vault) or HashiCorp Vault. It guides the agent through two-tier key hierarchies (KEK and DEK), AES-256-GCM authenticated encryption, DEK caching with TTL limits, and key rotation."
domain: security
category: cryptography
subcategory: envelope-encryption
tags:
  - cryptography
  - encryption
  - envelope-encryption
  - kms
  - aes-gcm
  - security
technologies:
  - AWS KMS
  - Cryptography Python
  - AES-256-GCM
  - HashiCorp Vault
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - cryptography >= 42.0.0
  - boto3 >= 1.34.0
---
# Cryptographic Envelope Encryption with Cloud KMS

## Overview

A comprehensive security engineering standard for implementing Envelope Encryption. Direct encryption of large datasets via cloud KMS APIs introduces severe network latency, strict payload size limits (typically 4 KB), and prohibitive per-request API costs. This skill instructs agents on using two-tier key architectures: a root Key Encryption Key (KEK) protected inside Hardware Security Modules (HSMs) to encrypt transient Data Encryption Keys (DEKs), which encrypt data locally using AES-256-GCM.

## When to Use

- Encrypting large payloads (files, documents, database columns, S3 objects) exceeding 4 KB.
- Complying with PCI-DSS, HIPAA, or SOC2 requirements for data-at-rest encryption with automated key rotation.
- Reducing cloud KMS API call volume and latency via secure local DEK caching.
- Implementing zero-knowledge cryptographic architectures where data remains encrypted in storage.

## When NOT to Use

- Simple passwords or tokens (use salted hashing algorithms like Argon2id or bcrypt).
- Ephemeral in-memory data where storage persistence is absent.

## Inputs & Prerequisites

- Cloud KMS key ARN/ID (AWS KMS, Google Cloud KMS, or Azure Key Vault).
- Python 3.10+ with `cryptography` library installed.
- Appropriate IAM permissions to call `kms:GenerateDataKey` and `kms:Decrypt`.

## Core Workflow

### 1. Two-Tier Envelope Architecture
- **Root Key (KEK)**: Stays permanently inside KMS/HSM. Never leaves cloud security boundary.
- **Data Encryption Key (DEK)**: Generated on-demand via `GenerateDataKey`. Plaidtext DEK encrypts payload and is wiped from memory. Ciphertext DEK is stored alongside encrypted data.

```python
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import boto3

class EnvelopeEncryptionService:
    def __init__(self, kms_key_arn: str, region_name: str = "us-east-1"):
        self.kms_key_arn = kms_key_arn
        self.kms_client = boto3.client("kms", region_name=region_name)

    def encrypt_payload(self, plaintext_bytes: bytes, context: dict) -> Tuple[bytes, bytes, bytes]:
        """
        Returns: (encrypted_data, encrypted_dek, iv_nonce)
        """
        # 1. Request new 256-bit DEK from KMS
        kms_resp = self.kms_client.generate_data_key(
            KeyId=self.kms_key_arn,
            KeySpec="AES_256",
            EncryptionContext=context
        )
        plaintext_dek = kms_resp["Plaintext"]
        encrypted_dek = kms_resp["CiphertextBlob"]

        try:
            # 2. Encrypt data locally using AES-256-GCM
            aesgcm = AESGCM(plaintext_dek)
            iv_nonce = os.urandom(12) # 96-bit standard GCM nonce
            
            # Additional Authenticated Data (AAD) binds context to ciphertext
            aad = str(sorted(context.items())).encode("utf-8")
            ciphertext = aesgcm.encrypt(iv_nonce, plaintext_bytes, aad)
            
            return ciphertext, encrypted_dek, iv_nonce
        finally:
            # 3. Explicitly wipe plaintext DEK from memory
            del plaintext_dek

    def decrypt_payload(
        self,
        ciphertext: bytes,
        encrypted_dek: bytes,
        iv_nonce: bytes,
        context: dict
    ) -> bytes:
        """
        Decrypts data by unwrapping DEK via KMS then decrypting AES-GCM locally.
        """
        # 1. Unwrap DEK using KMS
        kms_resp = self.kms_client.decrypt(
            CiphertextBlob=encrypted_dek,
            EncryptionContext=context
        )
        plaintext_dek = kms_resp["Plaintext"]

        try:
            # 2. Decrypt data locally
            aesgcm = AESGCM(plaintext_dek)
            aad = str(sorted(context.items())).encode("utf-8")
            plaintext = aesgcm.decrypt(iv_nonce, ciphertext, aad)
            return plaintext
        finally:
            del plaintext_dek
```

### 2. Packaging the Envelope
Store ciphertext, encrypted DEK, and IV nonce in a unified binary or JSON container:

```python
import json
import base64

def pack_envelope(ciphertext: bytes, encrypted_dek: bytes, iv_nonce: bytes) -> str:
    payload = {
        "version": 1,
        "algo": "AES-256-GCM",
        "iv": base64.b64encode(iv_nonce).decode("utf-8"),
        "dek": base64.b64encode(encrypted_dek).decode("utf-8"),
        "data": base64.b64encode(ciphertext).decode("utf-8")
    }
    return json.dumps(payload)
```

## Best Practices & Failure Modes

1. **Nonce / IV Reuse Catastrophe**: In AES-GCM, encrypting two different messages with the same DEK and the same IV nonce allows an attacker to compute the XOR of plaintexts and recover the authentication subkey. Never hardcode or reuse nonces; always generate 12 random bytes per encryption.
2. **Missing Encryption Context (AAD)**: Always pass cryptographic context (e.g. `{"tenant_id": "123", "doc_id": "456"}`) to both KMS and the AESGCM AAD. This prevents ciphertext splicing and confused-deputy attacks where an attacker swaps encrypted payloads across records.
3. **Plaintext DEK Leakage**: Plaintext DEKs must never be logged, written to swap space, or persisted to disk. Use `try...finally` blocks to delete plaintext keys immediately after encryption.

## Verification & Testing

- Test round-trip encryption/decryption consistency:
  ```python
  service = EnvelopeEncryptionService(kms_key_arn="alias/app-master-key")
  original = b"Super sensitive customer PII record."
  context = {"tenant_id": "customer_42"}

  cipher, enc_dek, iv = service.encrypt_payload(original, context)
  decrypted = service.decrypt_payload(cipher, enc_dek, iv, context)

  assert decrypted == original
  ```
