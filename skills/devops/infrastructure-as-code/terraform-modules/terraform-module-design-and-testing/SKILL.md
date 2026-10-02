---
name: terraform-module-design-and-testing
description: "Use this skill when architecting, authoring, and testing reusable Infrastructure as Code (IaC) modules with Terraform and OpenTofu. It guides the agent through root and child module contracts, custom input variable validations, structured outputs, dynamic blocks, version pinning, and automated integration testing using Terratest in Go."
domain: devops
category: infrastructure-as-code
subcategory: terraform-modules
tags:
  - terraform
  - opentofu
  - iac
  - modules
  - terratest
  - cloud-engineering
  - aws
technologies:
  - Terraform >= 1.5
  - OpenTofu
  - Go Terratest
  - AWS Provider
  - HCL
complexity: advanced
maturity: stable
tools:
  - terraform
  - tofu
  - go
dependencies:
  - terraform >= 1.5.0
---
# Terraform Reusable Module Design & Terratest Architecture

## Overview

A definitive production engineering reference for developing clean, decoupled, and testable Infrastructure as Code (IaC) modules using Terraform and OpenTofu. This skill instructs AI agents on designing standard module interfaces, enforcing input validations at plan time, crafting predictable output contracts, handling optional object types, and executing automated end-to-end integration tests using Terratest in Go.

## When to Use

- Building centralized, shared Terraform module registries for enterprise cloud engineering teams.
- Refactoring sprawling monolithic Terraform root modules into modular, reusable components.
- Validating infrastructure configurations programmatically before applying them to cloud accounts.
- Enforcing resource tagging and compliance policies at the module interface boundary.

## When NOT to Use

- Simple one-off ad-hoc deployments where abstraction provides no reuse benefit.
- Operating system software configuration inside VMs (use Ansible).

## Inputs & Prerequisites

- Terraform 1.5+ or OpenTofu 1.6+ installed.
- Target cloud provider credentials configured (AWS, Azure, or GCP).
- Go 1.21+ installed (for Terratest).

## Core Workflow

### 1. Standard Module Anatomy
```text
modules/aws-s3-secure-bucket/
├── main.tf                 # Primary resource declarations
├── variables.tf            # Input variables with validation rules
├── outputs.tf              # Structured output attributes
├── versions.tf             # Terraform & provider version constraints
└── README.md               # Generated module documentation (terraform-docs)
```

### 2. Strict Input Validation (`variables.tf`)
Reject invalid parameters at `terraform plan` time:

```hcl
variable "bucket_name" {
  type        = string
  description = "Globally unique name for the S3 bucket."
  
  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$", var.bucket_name))
    error_message = "Bucket name must be between 3 and 63 characters, lowercase alphanumeric with hyphens or dots."
  }
}

variable "environment" {
  type        = string
  description = "Target deployment environment."

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "lifecycle_rules" {
  type = list(object({
    id      = string
    enabled = bool
    days    = number
  }))
  default     = []
  description = "Optional lifecycle expiration rules."
}
```

### 3. Resource Implementation with Encrypted Defaults (`main.tf`)
```hcl
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

### 4. Automated Integration Testing with Terratest (Go)
Provision real infrastructure in a test account, assert properties, and guarantee teardown:

```go
// test/s3_module_test.go
package test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/assert"
)

func TestS3SecureBucketModule(t *testing.T) {
	t.Parallel()

	expectedBucketName := fmt.Sprintf("terratest-bucket-%s", strings.ToLower(random.UniqueId()))

	terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
		TerraformDir: "../modules/aws-s3-secure-bucket",
		Vars: map[string]interface{}{
			"bucket_name": expectedBucketName,
			"environment": "development",
		},
	})

	// Ensure cleanup at end of test
	defer terraform.Destroy(t, terraformOptions)

	// Deploy module
	terraform.InitAndApply(t, terraformOptions)

	// Validate outputs
	bucketArn := terraform.Output(t, terraformOptions, "bucket_arn")
	assert.Contains(t, bucketArn, expectedBucketName)
}
```

## Best Practices & Failure Modes

1. **Unconstrained Provider Versions**: Omitting version constraints in `versions.tf` allows provider major releases to break module syntax unpredictably. Always pin minimum and patch ranges (`~> 5.0`).
2. **Hardcoded Account IDs / Regions**: Never hardcode AWS region or account numbers inside modules. Use `data "aws_caller_identity"` and `data "aws_region"`.
3. **Leaked Terratest Resources**: If a test panics or crashes without calling `terraform.Destroy`, orphaned cloud resources accrue billing costs. Always register cleanup in `defer terraform.Destroy(t, terraformOptions)`.

## Verification & Testing

- Format and validate HCL syntax:
  ```bash
  terraform fmt -check -recursive
  terraform validate
  ```
- Run automated Terratest suite:
  ```bash
  cd test && go test -v -timeout 30m
  ```
