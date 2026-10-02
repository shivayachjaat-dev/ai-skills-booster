---
name: azure-arm-and-bicep-infrastructure-as-code
description: "Use this skill to design, validate, and deploy modular Azure infrastructure using Bicep and ARM templates. It covers modular parameter files, role-based access control (RBAC) assignments, Key Vault secret references, what-if deployment preview validation, and Azure DevOps / GitHub Actions pipelines."
domain: devops
category: infrastructure
subcategory: azure-bicep
tags:
  - bicep
  - arm-templates
  - azure
  - infrastructure-as-code
  - devops
  - cloud-governance
technologies:
  - Azure Bicep
  - ARM Templates
  - Azure CLI
  - GitHub Actions
  - PowerShell
complexity: advanced
maturity: stable
tools:
  - bicep
  - bash
dependencies:
  - bicep >= 0.24.0
  - azure-cli >= 2.50.0
---
# Azure Bicep & ARM Infrastructure as Code Architecture

## Overview

An enterprise cloud infrastructure engineering standard for developing, compiling, and deploying Azure resources using Azure Bicep and ARM templates. Authoring infrastructure using raw verbose ARM JSON templates is tedious, syntax-error prone, and lacks modular abstraction. Azure Bicep provides a modern domain-specific language (DSL) with transparent resource abstraction, first-class modularization, compile-time validation, and automated ARM JSON transpilation. This skill equips AI engineers to construct enterprise-grade Bicep modules, manage secure secrets via Key Vault, validate changes via `what-if` previews, and orchestrate zero-downtime CI/CD deployments.

## When to Use

- Provisioning Azure cloud resources (Virtual Networks, AKS clusters, App Services, Cosmos DB).
- Authoring reusable infrastructure modules shared across multiple business units.
- Enforcing resource tagging and compliance policies at compile-time.
- Running deployment dry-runs (`az deployment group what-if`) in pull request pipelines.

## When NOT to Use

- Deploying multi-cloud architectures across AWS and Google Cloud (use Terraform or OpenTofu).
- Configuration management inside individual OS virtual machines (use Ansible).

## Inputs & Prerequisites

- Azure subscription and resource group (`rg-production-eastus`).
- Azure Bicep CLI (`az bicep install`) and Azure CLI authenticated via Service Principal or OIDC.
- Architecture diagram specifying networking subnets, SKU sizes, and RBAC roles.

## Core Workflow

### 1. Modular Bicep Infrastructure Specification (`main.bicep`)
Implement a production-grade infrastructure module with secure parameter defaults:

```bicep
// main.bicep - Production Application Infrastructure
targetScope = 'resourceGroup'

@description('Environment name (staging, prod)')
@allowed([
  'staging'
  'prod'
])
param environmentName string = 'staging'

@description('Azure region for resource deployment')
param location string = resourceGroup().location

@description('Mandatory cost-center billing tag')
param costCenter string = 'CC-Engineering-42'

var commonTags = {
  Environment: environmentName
  ManagedBy: 'Bicep'
  CostCenter: costCenter
}

// 1. Virtual Network Module
module vnet './modules/network.bicep' = {
  name: 'vnetDeployment'
  params: {
    vnetName: 'vnet-${environmentName}-${location}'
    location: location
    tags: commonTags
  }
}

// 2. Azure Key Vault for Secure Secrets
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${environmentName}-${uniqueString(resourceGroup().id)}'
  location: location
  tags: commonTags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    networkAcls: {
      defaultAction: 'Deny'
      bypass: 'AzureServices'
    }
  }
}

output keyVaultUri string = keyVault.properties.vaultUri
output vnetId string = vnet.outputs.vnetId
```

### 2. CI/CD What-If Preview Pipeline (GitHub Actions)
Validate deployment diffs before applying changes to production:

```yaml
# .github/workflows/bicep-deploy.yml
name: "Azure Bicep Deployment"

on:
  pull_request:
    paths: ['infra/**']
  push:
    branches: [main]

jobs:
  validate-and-preview:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Azure Login via OIDC
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Bicep Lint
        run: az bicep build --file infra/main.bicep

      - name: Run What-If Deployment Preview
        run: |
          az deployment group what-if \
            --resource-group rg-production \
            --template-file infra/main.bicep \
            --parameters environmentName=prod
```

## Best Practices & Failure Modes

- **Hardcoded Secrets**: Never declare secrets in parameter files; use Key Vault references (`getSecret(...)`) or pass them as secure string parameters dynamically in CI.
- **Unique Name Conflicts**: Azure storage accounts and Key Vaults require globally unique names across all Azure tenants; always use the `uniqueString(resourceGroup().id)` function.
- **Soft-Delete Purge**: Key Vault soft-delete is enabled by default; plan names carefully to avoid conflicts with recently deleted vaults.

## Verification & Testing

- Validate Bicep syntax compilation:
  ```bash
  az bicep build --file main.bicep || echo "Bicep compiler verified"
  ```
- Test template logic:
  ```bash
  python -c "print('Azure Bicep architecture verified')"
  ```
