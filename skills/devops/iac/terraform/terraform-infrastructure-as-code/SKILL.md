---
name: terraform-infrastructure-as-code
description: "Use this skill when writing, refactoring, and maintaining Infrastructure as Code (IaC) using Terraform / OpenTofu. It guides the agent through remote state management with S3/DynamoDB locking, modular component design, variable validation rules, drift detection, resource tagging standards, and blast radius containment."
domain: devops
category: iac
subcategory: terraform
tags:
  - terraform
  - opentofu
  - iac
  - devops
  - cloud
  - aws
  - infrastructure
technologies:
  - Terraform
  - OpenTofu
  - AWS
  - HCL
  - Git
complexity: advanced
maturity: stable
tools:
  - terraform
  - tofu
  - git
dependencies:
  - terraform >= 1.5 or opentofu >= 1.6
---
# Terraform Infrastructure as Code

## Overview

A guide for authoring safe, modular, and maintainable Infrastructure as Code (IaC) using HashiCorp Terraform and OpenTofu. Instructs AI agents on structuring remote state backends, enforcing concurrent execution locking, writing reusable modules, defining variable validation assertions, and mitigating destructive blast radius mistakes during `terraform apply`.

## When to Use

- Provisioning cloud infrastructure (VPCs, subnets, Kubernetes clusters, databases, IAM roles).
- Writing reusable Terraform modules across multiple staging and production environments.
- Investigating infrastructure drift between real cloud resources and Terraform state files.
- Refactoring monolithic `main.tf` files into clean, decoupled service modules.

## When NOT to Use

- Managing application-level software configuration inside running VMs (use Ansible).
- Real-time container orchestration inside a Kubernetes cluster (use Helm/Kubectl).

## Inputs & Prerequisites

- Cloud provider credentials (e.g. AWS IAM role or service account).
- Terraform CLI (v1.5+) or OpenTofu installed.
- Remote state bucket and distributed lock table (e.g. AWS S3 + DynamoDB).

## Core Workflow

### 1. Remote State Backend & State Locking
Never store `terraform.tfstate` in Git or on a local machine. Always configure a remote backend with encryption and atomic state locking:
```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "company-tfstate-production"
    key            = "vpc/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "company-tflocks"
    encrypt        = true
  }
}
```

### 2. Blast Radius Containment & Environment Decoupling
Never manage an entire company's infrastructure in a single state file. Split state by lifecycle, security boundary, and environment:
```text
infrastructure/
├── modules/
│   ├── vpc/
│   └── rds/
└── environments/
    ├── staging/
    │   ├── vpc/
    │   └── services/
    └── production/
        ├── vpc/
        └── services/
```

### 3. Reusable Module Design with Strict Validation
Define inputs with explicit types and custom validation rules:
```hcl
variable "environment" {
  type        = string
  description = "Target deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "instance_count" {
  type        = number
  default     = 2
  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}
```

### 4. Safe Plan & Apply Protocol
Never run `terraform apply` without an inspected, saved plan artifact:
```bash
# 1. Format and validate syntax
terraform fmt -check
terraform validate

# 2. Generate and review plan artifact
terraform plan -out=tfplan.binary

# 3. Apply only the inspected artifact
terraform apply tfplan.binary
```
Carefully inspect the plan summary: look for red `~` modifications or `-` destructions on persistent storage resources (databases, disks).

### 5. Drift Detection & Remediation
Run periodic scheduled drift detection:
```bash
terraform plan -detailed-exitcode
```
- Exit code 0: No changes (in sync).
- Exit code 2: Drift detected (cloud resources diverge from state).

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Modifying state structure (refactoring) | Use `moved` blocks (`moved { from = aws_s3_bucket.old to = aws_s3_bucket.new }`) rather than deleting and recreating resources. |
| Production database recreation warning | Enable `lifecycle { prevent_destroy = true }` on all production persistent state resources. |
| Sensitive credentials in outputs | Mark output variables with `sensitive = true` to prevent secrets printing to CI logs. |

## Validation & Acceptance Criteria

- [ ] State backend configured with S3 encryption and DynamoDB locking.
- [ ] Variables enforce validation constraints and descriptions.
- [ ] `terraform validate` and `terraform fmt` pass with zero errors.
- [ ] Persistent storage resources protected with `prevent_destroy = true`.
- [ ] No plaintext secrets committed in `.tf` files.

## Failure Handling & Recovery

- If a state lock becomes orphaned due to a killed CI process, verify no process is running and release with: `terraform force-unlock <LOCK_ID>`.

## Expected Output & Artifacts

- Modular HCL configuration files (`main.tf`, `variables.tf`, `outputs.tf`).
- Validated execution plan file.
- Module documentation with input/output tables.

## Related Skills

- `docker-container-optimization`
- `kubernetes-crashloop-debugging`
- `secret-leak-detection-and-remediation`
