---
name: kubernetes-crashloop-debugging
description: "Use this skill when diagnosing and recovering Kubernetes Pods stuck in CrashLoopBackOff, Error, OOMKilled, or Pending states. It guides the agent through inspecting exit codes, previous container logs, describe events, resource limits, readiness/liveness probe misconfigurations, and volume mount failures."
domain: devops
category: kubernetes
subcategory: troubleshooting
tags:
  - kubernetes
  - devops
  - troubleshooting
  - debugging
  - k8s
  - containers
  - observability
technologies:
  - Kubernetes
  - kubectl
  - Docker
  - Linux
complexity: advanced
maturity: stable
tools:
  - kubectl
dependencies:
  - kubectl >= 1.24
---
# Kubernetes CrashLoop Debugging

## Overview

A systematic root-cause diagnosis and resolution workflow for Kubernetes workloads stuck in failure loops. Guides the agent through decoding termination exit codes, inspecting prior crashed instance logs (`--previous`), triaging cluster events, resolving resource limit bottlenecks (OOMKilled), and fixing probe misconfigurations.

## When to Use

- A Kubernetes Pod reports `CrashLoopBackOff`, `Error`, or repeated restarts.
- Pod is killed immediately with exit code `137` (OOMKilled) or `1` (Application Exception).
- A deployment rollout stalls because new replica pods fail readiness checks.
- Pod remains stuck in `Pending` due to scheduling constraints or PVC binding errors.

## When NOT to Use

- Managing underlying physical cluster node hardware or cloud provider control plane upgrades (use `kubernetes-cluster-administration`).
- Initial Helm chart authoring from scratch (use `helm-chart-scaffold`).

## Inputs & Prerequisites

- `kubectl` CLI configured with cluster access and relevant namespace context.
- Target pod name, deployment name, or namespace.

## Core Workflow

### 1. Pod Status & Event Inspection
Query pod state and termination metadata:
```bash
kubectl get pod <POD_NAME> -n <NAMESPACE> -o wide
kubectl describe pod <POD_NAME> -n <NAMESPACE>
```
Inspect the `Last State` and `Events` sections at the bottom of the describe output:
- `Exit Code: 0`: Application finished execution prematurely (process daemon didn't stay in foreground).
- `Exit Code: 1`: Uncaught runtime application exception or syntax error.
- `Exit Code: 137`: Process terminated by SIGKILL, almost always due to OOM (Out Of Memory). Check `OOMKilled: true`.
- `Exit Code: 143`: Process terminated by SIGTERM (graceful shutdown requested or probe failure).

### 2. Previous Container Log Extraction
Extract logs from the crashed container instance before the restart:
```bash
kubectl logs <POD_NAME> -n <NAMESPACE> --previous --tail=100
```
If multiple containers reside in the pod:
```bash
kubectl logs <POD_NAME> -c <CONTAINER_NAME> -n <NAMESPACE> --previous --tail=100
```

### 3. Triage & Fix by Failure Class

#### A. OOMKilled (Exit Code 137)
- Inspect memory limit in the pod spec (`resources.limits.memory`).
- Verify whether the application leaks memory or simply requires a higher baseline limit.
- Patch deployment with an adjusted limit:
  ```bash
  kubectl set resources deployment/<DEPLOYMENT_NAME> -n <NAMESPACE> --limits=memory=1Gi --requests=memory=512Mi
  ```

#### B. Liveness / Readiness Probe Failure
- Inspect probe configuration: `initialDelaySeconds`, `timeoutSeconds`, `periodSeconds`, `httpGet.path`.
- If the application takes 45 seconds to initialize but `initialDelaySeconds` is set to 10s, Kubernetes will kill the pod while it is still starting.
- Increase `initialDelaySeconds` or implement a `startupProbe` to accommodate slow initialization.

#### C. Missing Secrets or ConfigMaps
- In `kubectl describe pod`, check for events like: `MountVolume.SetUp failed for volume "secret-vol" : secret "app-secret" not found`.
- Verify required Secret/ConfigMap exists in the target namespace.

#### D. Foreground Process Missing
- Containers terminate when PID 1 exits. If the entrypoint script runs a background daemon (`nginx &`), the script completes and the container exits with code 0.
- Ensure the main process runs in the foreground (`nginx -g 'daemon off;'`).

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Pod restarts too fast to capture logs | Run an ephemeral debug container with an overridden entrypoint (`sleep 3600`) to inspect filesystem state: `kubectl debug <POD_NAME> -it --image=busybox --target=<CONTAINER>`. |
| Pending status with Unschedulable | Check node resources and nodeSelectors: `kubectl describe node` to verify memory and CPU allocatable headroom. |
| PersistentVolumeClaim unbound | Check storage class provisioner and access modes (`ReadWriteOnce` vs `ReadWriteMany`). |

## Validation & Acceptance Criteria

- [ ] Root cause identified from logs or describe events.
- [ ] Corrective patch applied to Deployment manifest.
- [ ] Pod transitions to `Running` state with `1/1` Ready containers.
- [ ] Zero restarts observed over a 5-minute monitoring window (`kubectl get pod -w`).

## Failure Handling & Recovery

- If new deployment version continues crashing, perform an immediate emergency rollback:
  ```bash
  kubectl rollout undo deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>
  ```

## Expected Output & Artifacts

- Triage diagnostic summary report with root cause analysis.
- Remediation patch manifest (YAML).
- Verification log showing healthy pod restart count.

## Related Skills

- `docker-container-optimization`
- `github-actions-ci-pipeline-optimization`
- `observability-and-instrumentation`
