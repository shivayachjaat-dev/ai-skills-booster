---
name: aws-iam-least-privilege-and-governance-architecture
description: "Use this skill to design, implement, and audit enterprise AWS IAM architectures adhering to least-privilege principles. It covers IAM permission boundaries, Service Control Policies (SCPs) in AWS Organizations, cross-account assume-role delegation with external IDs, ABAC (Attribute-Based Access Control) tagging policies, IAM Access Analyzer integration, and credential rotation."
domain: security
category: cloud-security
subcategory: aws-iam
tags:
  - security
  - aws
  - iam
  - cloud-security
  - least-privilege
  - abac
  - scps
  - permission-boundaries
technologies:
  - AWS IAM
  - AWS Organizations
  - AWS Access Analyzer
  - Python
  - JSON
complexity: advanced
maturity: stable
tools:
  - aws-cli
  - python
  - bash
dependencies:
  - python@>=3.10
  - boto3@>=1.34.0
---
# AWS IAM Least-Privilege & Governance Architecture

## Overview

An enterprise cloud security standard for engineering, auditing, and enforcing least-privilege identity and access management across multi-account AWS environments. Over-privileged IAM roles, wildcard permissions (`*:*`), and unconstrained cross-account trust relationships are the primary root cause of cloud data breaches. This skill establishes rigorous patterns for designing granular IAM policies, implementing multi-tier Permission Boundaries, enforcing organizational Service Control Policies (SCPs), deploying Attribute-Based Access Control (ABAC), and validating trust policies against confused deputy vulnerabilities.

```
+------------------------------------------------------------------------+
|                     AWS IAM Effective Permission Flow                  |
|                                                                        |
|    [ AWS Organizations SCP ] (Hard Organizational Ceiling)             |
|                 |                                                      |
|                 v                                                      |
|    [ IAM Permission Boundary ] (Maximum Delegated Ceiling)             |
|                 |                                                      |
|                 v                                                      |
|    [ Identity-Based IAM Policy ] (Explicit Allow)                      |
|                 |                                                      |
|                 v                                                      |
|    [ Resource-Based Policy (S3 / KMS) ]                                |
|                 |                                                      |
|                 v                                                      |
|    === Effective Permission: Intersection of All Positive Gates ===    |
+------------------------------------------------------------------------+
```

## When to Use

- Architecting IAM role delegation for microservices running in EKS, ECS, or Lambda (IAM Roles for Service Accounts - IRSA).
- Designing cross-account assume-role workflows with external vendor SaaS integrations (preventing Confused Deputy attacks with `sts:ExternalId`).
- Implementing developer self-service provisioning where developers can create IAM roles only within strict Permission Boundaries.
- Enforcing Attribute-Based Access Control (ABAC) where access is dynamically granted based on matching `aws:PrincipalTag` and `aws:ResourceTag`.

## When NOT to Use

- Network-level access restriction (use Security Groups, Network ACLs, or AWS WAF).
- Operating system local user management (use SSH certificates or AWS Systems Manager Session Manager).

## Inputs & Prerequisites

- AWS Account ID and administrative privileges for IAM policy testing.
- Target workload service identities and access requirements.
- Familiarity with AWS IAM policy JSON grammar and condition operators.

## Core Workflow

### Step 1: Crafting Granular Least-Privilege IAM Policies
Eliminate wildcard actions by scoping policies to exact resource ARNs and condition keys:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppDynamoAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/ProductionOrders",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

### Step 2: Permission Boundaries for Safe Delegated Administration
Attach a Permission Boundary to prevent developers from granting themselves administrator rights:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowWorkerActions",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "sqs:SendMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyIAMModification",
      "Effect": "Deny",
      "Action": [
        "iam:*",
        "organizations:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Step 3: Hardened Cross-Account Trust Policy (Confused Deputy Prevention)
Protect cross-account role assumption with mandatory External ID validation:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TrustThirdPartyMonitoringVendor",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::987654321098:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "7f8b9c2a-9e12-4c3a-8b10-abcde1234567"
        }
      }
    }
  ]
}
```

### Step 4: Attribute-Based Access Control (ABAC) Tag Policy
Permit engineers to access resources only when their project tag matches the target resource tag:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessIfTagsMatch",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Project": "${aws:PrincipalTag/Project}"
        }
      }
    }
  ]
}
```

## Best Practices & Failure Modes

- **Never Use Root Account**: Lock root account credentials behind hardware MFA and create dedicated administrative roles.
- **Audit Wildcards Regularly**: Run AWS IAM Access Analyzer and CloudTrail Access Advisor to identify unused permissions and eliminate `Action: "*"`.
- **Enforce TLS via Condition**: Always require `"aws:SecureTransport": "true"` on S3 bucket policies and sensitive API calls.

## Verification & Testing

1. Validate IAM policy syntax with the AWS CLI: `aws iam validate-policy --policy-document file://policy.json`.
2. Simulate authorization actions using IAM Policy Simulator: `aws iam simulate-principal-policy`.
3. Audit external access findings with IAM Access Analyzer: `aws accessanalyzer list-findings`.
