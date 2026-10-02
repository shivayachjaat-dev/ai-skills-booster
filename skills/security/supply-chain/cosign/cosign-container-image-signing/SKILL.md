---
name: cosign-container-image-signing
description: "Use this skill when designing, implementing, and enforcing cryptographic container image signing and verification using Sigstore Cosign. It covers keyless signing via OIDC (GitHub Actions/GitLab CI), public/private keypair signing, SBOM attestation attachment, and enforcing Kubernetes admission policies with Kyverno or Gatekeeper."
domain: security
category: supply-chain
subcategory: cosign
tags:
  - cosign
  - sigstore
  - supply-chain
  - container-security
  - security
  - kubernetes
  - devsecops
technologies:
  - Cosign
  - Sigstore
  - Rekor
  - Fulcio
  - Kyverno
  - Docker
complexity: advanced
maturity: stable
tools:
  - cosign
  - crane
  - kubectl
dependencies:
  - cosign >= 2.2.0
---
# Sigstore Cosign Container Image Signing & Admission Control

## Overview

A definitive production standard for securing software supply chains by cryptographically signing container images, attaching Software Bill of Materials (SBOM) attestations, and enforcing signature verification at Kubernetes admission time using Sigstore Cosign. This skill instructs AI agents on keyless signing via GitHub Actions OpenID Connect (OIDC), public key-based signing with KMS, and authoring Kyverno admission policies that reject untrusted container images.

## When to Use

- Preventing deployment of unauthorized or tampered container images across staging and production Kubernetes clusters.
- Establishing cryptographic provenance and non-repudiation for images built in CI/CD pipelines.
- Attaching vulnerability scan reports and CycloneDX SBOMs directly to container registries as OCI artifacts.
- Satisfying SLSA (Supply-chain Levels for Software Artifacts) Level 3 requirements.

## When NOT to Use

- Code signing for macOS/Windows desktop binaries (use Apple codesign or Authenticode).
- Encrypting container images (Cosign signs and verifies authenticity; it does not encrypt layer contents).

## Inputs & Prerequisites

- Cosign 2.2+ CLI installed.
- Target container image pushed to an OCI-compliant registry (GHCR, ECR, GCR, Docker Hub).
- CI/CD environment with OIDC identity provider (e.g. GitHub Actions).

## Core Workflow

### 1. Keyless Signing via GitHub Actions (Sigstore OIDC)
Sign container images automatically in CI without managing or rotating private keys:

```yaml
# .github/workflows/build-and-sign.yaml
name: Build and Sign Container Image

on:
  push:
    tags: ['v*']

permissions:
  contents: read
  packages: write
  id-token: write # Required for requesting OIDC token for keyless Sigstore signing

jobs:
  build-sign:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push Docker Image
        id: build-push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}

      - name: Keyless Sign the Container Image
        env:
          TAG: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
        run: |
          cosign sign --yes "${TAG}"
```

### 2. Attaching SBOM Attestations
Attach a vulnerability scan or CycloneDX SBOM to the image in the registry:

```bash
# Attach SBOM attestation signed by CI identity
cosign attest --yes \
    --predicate sbom.cdx.json \
    --type cyclonedx \
    ghcr.io/company-org/app:v1.0.0
```

### 3. Verifying Signatures Locally via CLI
Verify that an image was signed by the specific GitHub repository workflow:

```bash
cosign verify \
    --certificate-identity-regexp "https://github.com/company-org/app/.github/workflows/.*" \
    --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
    ghcr.io/company-org/app:v1.0.0
```

### 4. Kubernetes Admission Enforcement with Kyverno
Block unsigned images from running in production:

```yaml
# kyverno-policy.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: check-image-signatures
  annotations:
    policies.kyverno.io/title: Verify Container Signatures
    policies.kyverno.io/subject: Pod
spec:
  validationFailureAction: Enforce # Strictly blocks pod creation if verification fails
  webhookTimeoutSeconds: 30
  rules:
    - name: verify-sigstore-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
              namespaces:
                - production
      verifyImages:
        - imageReferences:
            - "ghcr.io/company-org/*"
          attestors:
            - entries:
                - keyless:
                    issuer: "https://token.actions.githubusercontent.com"
                    subject: "https://github.com/company-org/app/.github/workflows/build-and-sign.yaml@refs/heads/main"
```

## Best Practices & Failure Modes

1. **Tag-Based Image Verification Vulnerability**: Container tags (`:latest`, `:v1.0.0`) are mutable. An attacker who gains registry access can re-tag a malicious image with a signed tag. Always verify and deploy using immutable SHA256 image digests (`image@sha256:abcd...`).
2. **Registry OCI Artifact Support**: Older registries or air-gapped proxies that do not support OCI image referrers fail when Cosign attempts to push `.sig` or `.att` artifacts. Ensure registry is OCI 1.1 compliant.
3. **Kyverno Webhook Latency**: Sigstore verification calls the public Rekor transparency log. If network latency spikes, the Kubernetes API server webhook times out. Ensure appropriate `webhookTimeoutSeconds: 30` is set.

## Verification & Testing

- Verify signature and inspect cryptographic claims:
  ```bash
  cosign verify ghcr.io/company-org/app:v1.0.0 | jq .
  ```
- Verify SBOM attestation:
  ```bash
  cosign verify-attestation --type cyclonedx ghcr.io/company-org/app:v1.0.0
  ```
