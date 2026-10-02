---
name: argocd-gitops-continuous-delivery
description: "Use this skill when designing, configuring, and operating GitOps continuous delivery workflows on Kubernetes using Argo CD. It guides the agent through Application and ApplicationSet CRD declarations, automated self-healing and pruning sync policies, sync waves and resource hooks, multi-tenant RBAC, and repository secrets integration."
domain: devops
category: gitops
subcategory: argo-cd
tags:
  - argocd
  - gitops
  - kubernetes
  - continuous-delivery
  - helm
  - kustomize
technologies:
  - Argo CD
  - Kubernetes
  - GitOps
  - Kustomize
  - Helm
complexity: advanced
maturity: stable
tools:
  - argocd
  - kubectl
dependencies:
  - argocd >= 2.9.0
  - kubernetes >= 1.28
---
# Argo CD GitOps Continuous Delivery Architecture

## Overview

A production engineering standard for declarative, automated software delivery on Kubernetes using Argo CD. Following GitOps principles, this skill provides AI agents with specifications for Argo CD Application and ApplicationSet Custom Resource Definitions (CRDs), automated drift detection and self-healing reconciliation, ordered deployment via Sync Waves, pre/post-sync migration hooks, and enterprise RBAC policies.

## When to Use

- Managing multi-cluster, multi-environment Kubernetes deployments directly from Git repositories.
- Eliminating imperative manual `kubectl apply` commands in staging and production.
- Automating database migrations before updating application pods using Argo CD PreSync hooks.
- Enforcing desired state synchronization with automated drift correction (self-healing).

## When NOT to Use

- Deploying non-Kubernetes workloads (virtual machines, serverless lambdas, bare metal).
- Simple single-cluster setups where basic GitHub Actions direct deployment suffices.

## Inputs & Prerequisites

- Kubernetes 1.28+ cluster with Argo CD 2.9+ installed.
- Git repository containing Kubernetes manifests (Kustomize or Helm charts).
- Argo CD CLI (`argocd`) configured with target server endpoint.

## Core Workflow

### 1. Declarative Argo CD Application CRD
Define an application tracking a Git repository branch:

```yaml
# application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: order-service-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: 'https://github.com/company-org/k8s-infrastructure.git'
    targetRevision: main
    path: overlays/production/order-service
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: production
  syncPolicy:
    automated:
      prune: true       # Delete resources removed from Git
      selfHeal: true    # Reconcile manual cluster changes back to Git desired state
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### 2. Multi-Environment ApplicationSet
Deploy across multiple clusters and environments from a single template using `ApplicationSet`:

```yaml
# applicationset.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices-deployer
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: staging
            cluster: staging-cluster
            url: https://api.staging.company.internal
          - env: production
            cluster: production-cluster
            url: https://api.production.company.internal
  template:
    metadata:
      name: '{{env}}-api-gateway'
    spec:
      project: default
      source:
        repoURL: 'https://github.com/company-org/k8s-infrastructure.git'
        targetRevision: main
        path: 'overlays/{{env}}/api-gateway'
      destination:
        server: '{{url}}'
        namespace: '{{env}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

### 3. Sync Waves & Database Migration Hooks
Ensure database migrations execute and finish before updating application deployments:

```yaml
# migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: production
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
    argocd.argoproj.io/sync-wave: "1" # Runs first
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: company/order-service:v2.4.0
          command: ["alembic", "upgrade", "head"]
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  namespace: production
  annotations:
    argocd.argoproj.io/sync-wave: "2" # Runs only AFTER wave 1 succeeded
spec:
  replicas: 3
  # ...
```

## Best Practices & Failure Modes

1. **Missing Resource Finalizer**: Without `resources-finalizer.argocd.argoproj.io`, deleting an Argo CD Application resource leaves orphaned pods, services, and ingresses running in the cluster. Always declare the finalizer.
2. **Infinite Sync Loops with Mutating Webhooks**: If an external controller (like Istio sidecar injector or cert-manager) mutates manifests at runtime, Argo CD detects drift and constantly attempts to re-sync. Use `ignoreDifferences` in Application specs for dynamically mutated fields.
3. **PreSync Hook Deadlocks**: If a PreSync migration job fails, Argo CD halts the sync and never updates the application. Configure `backoffLimit` on the Kubernetes Job to prevent hanging indefinitely.

## Verification & Testing

- Check application synchronization status via CLI:
  ```bash
  argocd app get order-service-production
  ```
- Trigger manual dry-run sync to review planned diffs:
  ```bash
  argocd app sync order-service-production --dry-run
  ```
- Reconcile out-of-sync drift manually:
  ```bash
  argocd app sync order-service-production --prune
  ```
