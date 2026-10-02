---
name: flagger-canary-progressive-delivery
description: "Use this skill when designing, configuring, and automating canary progressive delivery on Kubernetes using Flagger and service meshes (Istio/Linkerd). It covers Canary CRD resource declarations, automated metric analysis (request success rate, P99 latency via Prometheus), progressive traffic stepping (10% to 50%), automated rollback on anomalies, and webhook alerting."
domain: devops
category: continuous-delivery
subcategory: flagger
tags:
  - flagger
  - canary
  - progressive-delivery
  - kubernetes
  - istio
  - gitops
  - devops
technologies:
  - Flagger
  - Kubernetes
  - Istio
  - Prometheus
  - Slack Webhooks
complexity: advanced
maturity: stable
tools:
  - kubectl
  - helm
dependencies:
  - flagger >= 1.35.0
  - kubernetes >= 1.28
---
# Flagger Automated Canary Progressive Delivery on Kubernetes

## Overview

A definitive production engineering reference for automating progressive delivery and automated canary deployments on Kubernetes using Flagger. Instead of risky all-at-once updates, Flagger gradually shifts traffic from primary to canary pods while continuously analyzing real-time Prometheus metrics (HTTP 5xx error rate and P99 latency). If metrics remain healthy, Flagger promotes the canary; if an anomaly occurs, it halts traffic and rolls back automatically within seconds.

## When to Use

- Rolling out high-risk production microservice releases without user-facing downtime.
- Automating canary progression directly based on real-time Prometheus SLI/SLO metrics.
- Enforcing zero-touch automated rollbacks when new application versions degrade latency or error rates.
- Coordinating canary traffic splitting via Istio VirtualService, NGINX Ingress, or AWS App Mesh.

## When NOT to Use

- Stateless batch processing jobs or background queue consumers (canary traffic shifting applies to HTTP/gRPC ingress traffic).
- Clusters lacking a service mesh or advanced ingress controller supporting weighted traffic routing.

## Inputs & Prerequisites

- Kubernetes 1.28+ cluster.
- Service Mesh (Istio 1.20+) or ingress controller with Flagger installed.
- Prometheus server collecting request metrics (`http_requests_total`, `http_request_duration_seconds_bucket`).

## Core Workflow

### 1. Declarative Canary Custom Resource (`canary.yaml`)
Define the canary progression, step weights, and Prometheus metric thresholds:

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: order-service
  namespace: production
spec:
  # Target Kubernetes Deployment managed by Flagger
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  
  # Service mesh routing configuration (Istio)
  provider: istio
  service:
    port: 8080
    targetPort: 8080
    gateways:
      - mesh
      - public-gateway.istio-system.svc.cluster.local
    hosts:
      - orders.company.internal

  # Progressive traffic shifting schedule
  analysis:
    interval: 1m           # Evaluation interval
    threshold: 5           # Max consecutive failed metric checks before rolling back
    maxWeight: 50          # Max canary traffic percentage before final promotion
    stepWeight: 10         # Increment traffic by 10% per interval (10% -> 20% -> 30% -> 40% -> 50%)
    
    # Automated Prometheus Metric Verification Checks
    metrics:
      - name: request-success-rate
        thresholdRange:
          min: 99.0        # Must maintain >= 99% HTTP 2xx/3xx success rate
        interval: 1m
      - name: request-duration
        thresholdRange:
          max: 500         # P99 latency must remain under 500 milliseconds
        interval: 1m

    # Automated Webhook Acceptance Testing during Canary Stage
    webhooks:
      - name: integration-smoke-tests
        type: pre-rollout
        url: http://flagger-loadtester.testing/
        timeout: 15s
        metadata:
          type: bash
          cmd: "curl -s http://order-service-canary.production:8080/healthz | grep ok"

      - name: load-test
        type: rollout
        url: http://flagger-loadtester.testing/
        timeout: 5s
        metadata:
          cmd: "hey -z 1m -q 10 -c 2 http://order-service-canary.production:8080/api/orders"
```

### 2. Flagger Deployment Lifecycle
1. Flagger creates `order-service-primary` (stable production deployment) and `order-service` (target tracking Git updates).
2. Updating the image in `order-service` triggers Flagger:
   - Scales up canary pods.
   - Runs `pre-rollout` integration smoke tests.
   - Increments canary traffic from 10% to 50% over 5 intervals.
   - Evaluates Prometheus metrics every minute.
   - **On Success**: Scales primary deployment to new version, shifts 100% traffic to primary, scales canary to 0.
   - **On Anomaly**: Automatically sets canary traffic weight to 0% immediately and notifies on Slack.

## Best Practices & Failure Modes

1. **Directly Editing Primary Deployments**: Never edit `order-service-primary` manually. Any changes made to primary are overwritten by Flagger. Always update the target deployment (`order-service`).
2. **Missing In-Flight Traffic on Low-Volume Endpoints**: If an endpoint has low natural traffic, 10% of 2 requests/min is too small for statistical significance. Always configure `flagger-loadtester` in rollout webhooks to generate steady synthetic traffic.
3. **Threshold Sensitivity**: Setting `threshold: 1` causes an immediate rollback if a single transient network packet drops. Set `threshold: 3` to `5` to allow brief transient spikes while catching sustained degradations.

## Verification & Testing

- Monitor canary rollout status and traffic weights in real time:
  ```bash
  kubectl -n production get canaries
  kubectl -n production describe canary order-service
  ```
- Inspect Flagger controller reconciliation logs:
  ```bash
  kubectl -n flagger-system logs deployment/flagger -f
  ```
