---
name: istio-service-mesh-traffic-routing
description: "Use this skill when implementing advanced traffic management, security policies, and canary deployments using the Istio Service Mesh. It guides the agent through VirtualService routing rules, DestinationRule subset definitions, mutual TLS (mTLS) PeerAuthentication enforcement, fault injection, and Envoy sidecar proxy tuning."
domain: devops
category: service-mesh
subcategory: istio
tags:
  - istio
  - service-mesh
  - kubernetes
  - canary
  - mtls
  - traffic-management
technologies:
  - Istio
  - Kubernetes
  - Envoy
  - Kiali
  - Helm
complexity: advanced
maturity: stable
tools:
  - istioctl
  - kubectl
dependencies:
  - istio >= 1.20
  - kubernetes >= 1.28
---
# Istio Service Mesh Traffic Routing & Security

## Overview

A comprehensive guide for managing service-to-service traffic, zero-trust cryptographic identities, and progressive rollouts using Istio on Kubernetes. This skill provides AI agents with standard configurations for VirtualService path/header matching, DestinationRule subsets and traffic policies, strict mutual TLS (`STRICT` mode), canary weight splitting, and circuit breaking via outlier detection.

## When to Use

- Executing automated canary deployments with fine-grained HTTP traffic splitting (e.g. 90% v1 / 10% v2).
- Enforcing strict mutual TLS (mTLS) across all namespace pod communications.
- Routing traffic based on HTTP request headers (e.g. `x-beta-user: true` or mobile user agents).
- Injecting chaos testing faults (delays or aborts) to test downstream resilience.
- Setting connection pool limits and outlier detection to isolate unhealthy upstream pods.

## When NOT to Use

- Simple Kubernetes clusters with a single ingress controller (e.g., NGINX Ingress) where microservice-to-microservice traffic is minimal.
- Latency-critical systems where the Envoy sidecar CPU and microsecond network overhead cannot be tolerated.

## Inputs & Prerequisites

- Kubernetes 1.28+ cluster with Istio 1.20+ installed.
- Namespace labeled for sidecar injection: `kubectl label namespace default istio-injection=enabled`.
- Application deployments with version labels (`app: payments, version: v1` and `app: payments, version: v2`).

## Core Workflow

### 1. Canary Traffic Splitting with VirtualService & DestinationRule
Define subsets in `DestinationRule` and split traffic in `VirtualService`:

```yaml
# destination-rule.yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service
  namespace: production
spec:
  host: payment-service.production.svc.cluster.local
  subsets:
    - name: v1
      labels:
        version: "1.0.0"
    - name: v2
      labels:
        version: "2.0.0"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 3
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
```

```yaml
# virtual-service.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service
  namespace: production
spec:
  hosts:
    - payment-service.production.svc.cluster.local
  http:
    # Header-based routing for internal QA / Beta testers
    - match:
        - headers:
            x-qa-tester:
              exact: "true"
      route:
        - destination:
            host: payment-service.production.svc.cluster.local
            subset: v2

    # Weighted canary rollout: 90% v1, 10% v2
    - route:
        - destination:
            host: payment-service.production.svc.cluster.local
            subset: v1
          weight: 90
        - destination:
            host: payment-service.production.svc.cluster.local
            subset: v2
          weight: 10
      timeout: 3s
      retries:
        attempts: 3
        perTryTimeout: 1s
        retryOn: "5xx,connect-failure,refused-stream"
```

### 2. Strict Mutual TLS Enforcement
Enforce cryptographic mutual TLS across all pod-to-pod communications:

```yaml
# peer-authentication.yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
```

### 3. Fault Injection for Chaos Testing
Validate resilience by injecting 5-second delays on 20% of calls from frontend:

```yaml
# fault-injection.yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-chaos
  namespace: production
spec:
  hosts:
    - ratings.production.svc.cluster.local
  http:
    - fault:
        delay:
          percentage:
            value: 20.0
          fixedDelay: 5s
      route:
        - destination:
            host: ratings.production.svc.cluster.local
            subset: v1
```

## Best Practices & Failure Modes

1. **Port Naming Convention**: Istio relies on container port names to determine protocol handling (e.g., `name: http-web` or `name: grpc-api`). If an HTTP port is named `web` without protocol prefix, Istio treats it as raw TCP, disabling HTTP routing, retries, and metrics.
2. **Missing Subsets in DestinationRule**: Pointing a `VirtualService` to a subset that does not exist in `DestinationRule` causes HTTP 503 Service Unavailable errors immediately. Always apply `DestinationRule` before updating `VirtualService`.
3. **mTLS Mode Mismatch**: Setting `STRICT` PeerAuthentication when legacy non-mesh clients (like external Prometheus or Kubernetes health probes) call the service causes immediate connection resets. Configure plaintext probe exemption or `PERMISSIVE` mode during migration.

## Verification & Testing

- Verify proxy synchronization status:
  ```bash
  istioctl proxy-status
  ```
- Validate route resolution and cluster configuration:
  ```bash
  istioctl proxy-config routes <pod-name>.production
  ```
- Confirm strict mTLS communication:
  ```bash
  istioctl authn tls-check <pod-name>.production payment-service.production.svc.cluster.local
  ```
