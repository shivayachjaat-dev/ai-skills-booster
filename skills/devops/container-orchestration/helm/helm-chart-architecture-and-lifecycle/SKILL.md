---
name: helm-chart-architecture-and-lifecycle
description: "Use this skill when architecting, authoring, and managing production-grade Kubernetes packages with Helm 3+. It guides the agent through chart file structures, named template helpers (_helpers.tpl), strict values schema validation using values.schema.json, dependency subcharts, test suites (helm test), and semantic versioning release workflows."
domain: devops
category: container-orchestration
subcategory: helm
tags:
  - helm
  - kubernetes
  - devops
  - package-management
  - helm3
  - charts
technologies:
  - Helm 3+
  - Kubernetes
  - JSON Schema
  - YAML
  - Go Templates
complexity: intermediate
maturity: stable
tools:
  - helm
  - kubectl
dependencies:
  - helm >= 3.12.0
  - kubernetes >= 1.28
---
# Helm 3 Chart Architecture & Lifecycle Management

## Overview

A comprehensive engineering guide for authoring production-grade Kubernetes packages using Helm 3. This skill instructs agents on organizing chart hierarchies, authoring reusable named templates in `_helpers.tpl`, enforcing input validation via `values.schema.json`, managing external subchart dependencies, writing automated validation hooks (`helm test`), and implementing zero-downtime upgrades.

## When to Use

- Packaging microservice applications and infrastructure components for standardized deployment across Kubernetes clusters.
- Parameterizing Kubernetes manifests for multi-environment deployments (dev, staging, production).
- Preventing accidental production outages by validating `values.yaml` inputs against strict JSON Schemas.
- Bundling dependent infrastructure (e.g. Redis, PostgreSQL) as configurable subcharts.

## When NOT to Use

- Simple single-cluster setups where vanilla Kustomize overlays provide sufficient configuration without Go templating complexity.
- Non-Kubernetes cloud infrastructure (use Terraform or Pulumi).

## Inputs & Prerequisites

- Helm 3.12+ CLI installed.
- Access to a Kubernetes cluster via `kubectl`.
- Basic knowledge of Kubernetes primitives (Deployments, Services, ConfigMaps, Ingress).

## Core Workflow

### 1. Production Chart Directory Structure
```text
my-app/
├── Chart.yaml                  # Chart metadata and semver version
├── values.yaml                 # Default parameter values
├── values.schema.json          # JSON Schema validating values.yaml
├── templates/
│   ├── _helpers.tpl            # Reusable Go template partials
│   ├── deployment.yaml         # Main application Deployment
│   ├── service.yaml            # ClusterIP / NodePort Service
│   ├── ingress.yaml            # Ingress controller routing
│   └── tests/
│       └── test-connection.yaml# Helm test pod verification
└── charts/                     # Subchart dependencies
```

### 2. Named Template Helpers (`templates/_helpers.tpl`)
Create DRY, consistent resource labels and names:

```gotemplate
{{/*
Expand the name of the chart.
*/}}
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Standard Common Labels
*/}}
{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.name" . }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

### 3. Strict Schema Validation (`values.schema.json`)
Reject invalid deployment inputs before applying to the cluster:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Values",
  "type": "object",
  "required": ["replicaCount", "image"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50
    },
    "image": {
      "type": "object",
      "required": ["repository", "tag", "pullPolicy"],
      "properties": {
        "repository": { "type": "string" },
        "tag": { "type": "string" },
        "pullPolicy": { "enum": ["Always", "IfNotPresent", "Never"] }
      }
    }
  }
}
```

### 4. Integration Test Verification Hook (`templates/tests/test-connection.yaml`)
Validate deployment health after installation:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  containers:
    - name: wget
      image: busybox:1.36
      command: ['wget']
      args: ['{{ include "my-app.fullname" . }}:{{ .Values.service.port }}/healthz']
  restartPolicy: Never
```

## Best Practices & Failure Modes

1. **Missing `values.schema.json`**: Without a schema, passing a misspelled value (e.g. `replicas: 3` instead of `replicaCount: 3`) fails silently at template rendering, deploying with dangerous defaults. Always enforce JSON Schema validation.
2. **Template Truncation**: Kubernetes resource names cannot exceed 63 characters. Failure to truncate named helpers with `trunc 63` causes pods and services to fail creation with `metadata.name: Invalid value` errors.
3. **Hardcoding Release Namespaces**: Never hardcode `namespace: default` inside manifest templates. Let the user define the target namespace via `helm install --namespace <target>`.

## Verification & Testing

- Lint chart for syntax and best practices:
  ```bash
  helm lint ./my-app
  ```
- Render templates locally to inspect generated YAML:
  ```bash
  helm template test-release ./my-app --values ./my-app/values.yaml
  ```
- Execute post-install verification test hook:
  ```bash
  helm test test-release
  ```
