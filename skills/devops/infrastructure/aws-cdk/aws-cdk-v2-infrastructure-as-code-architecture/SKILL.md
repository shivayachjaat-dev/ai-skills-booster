---
name: aws-cdk-v2-infrastructure-as-code-architecture
description: "Use this skill to design, build, and deploy production AWS cloud infrastructure using the AWS Cloud Development Kit (CDK v2) in TypeScript and Python. It covers L1/L2/L3 construct composition, multi-account multi-region pipelines (cdk-pipelines), automated compliance enforcement with CDK Aspects (IAspect), unit and snapshot testing with @aws-cdk/assertions, and drift remediation."
domain: devops
category: infrastructure
subcategory: aws-cdk
tags:
  - devops
  - aws
  - aws-cdk
  - infrastructure-as-code
  - typescript
  - cloudformation
  - cdk-pipelines
  - compliance-aspects
technologies:
  - AWS CDK v2
  - TypeScript
  - Python
  - CloudFormation
  - AWS CodePipeline
  - Jest
complexity: advanced
maturity: stable
tools:
  - cdk
  - npm
  - node
dependencies:
  - aws-cdk@^2.130.0
  - typescript@^5.0.0
---
# AWS CDK v2 Infrastructure as Code & Pipeline Architecture

## Overview

An enterprise cloud infrastructure engineering standard for provisioning, governing, and testing AWS environments using the AWS Cloud Development Kit (CDK v2). By modeling infrastructure in familiar programming languages (TypeScript, Python, Go) rather than static YAML/JSON, teams achieve modular construct reuse, compile-time type validation, and integrated unit testing. This skill guides platform engineers, DevSecOps architects, and AI coding agents in designing hierarchical construct trees (L1, L2, L3 constructs), building self-mutating continuous delivery pipelines (`cdk-pipelines`), and enforcing organization-wide security baselines via CDK Aspects.

```
+------------------------------------------------------------------------+
|                      AWS CDK v2 Architecture Hierarchy                 |
|                                                                        |
|  [ App Root (cdk.App) ]                                                |
|      |                                                                 |
|      +---> [ Stage: Production (Environment: us-east-1, Account A) ]   |
|      |         |                                                       |
|      |         +---> [ Stack: NetworkStack (VPC, NAT, Subnets) ]       |
|      |         +---> [ Stack: DatabaseStack (RDS Aurora Postgres) ]    |
|      |         +---> [ Stack: ComputeStack (ECS Fargate + ALB) ]       |
|      |                                                                 |
|      v                                                                 |
|  [ CDK Aspects (IAspect) ] ---> (Enforce Encryption, Tags, No 0.0.0.0) |
|      |                                                                 |
|      v                                                                 |
|  [ CloudFormation Synthesis (cdk synth) ] ---> [ CloudFormation Engine]|
+------------------------------------------------------------------------+
```

## When to Use

- Architecting multi-account AWS topologies (Networking, Shared Services, Dev/Staging/Production).
- Creating reusable organizational construct libraries (e.g., standard encrypted S3 bucket construct, hardened ECS microservice construct).
- Enforcing security policies at synthesis time before resources reach cloud environments using CDK Aspects.
- Setting up self-mutating CI/CD deployment pipelines that automatically adapt when new stacks are added to code.

## When NOT to Use

- Multi-cloud infrastructure requiring identical syntax across GCP, Azure, and AWS (prefer Terraform or Pulumi).
- Ephemeral single-script resource provisioning where standard AWS CLI or Boto3 is sufficient.

## Inputs & Prerequisites

- Node.js 18.x+ and npm/pnpm.
- AWS CDK CLI installed globally: `npm install -g aws-cdk`.
- Authenticated AWS credentials with permissions for target AWS accounts (`aws sts get-caller-identity`).

## Core Workflow

### Step 1: L3 Pattern Construct Authoring
Create reusable, high-level architectural constructs encapsulating organizational best practices:

```typescript
// lib/constructs/secure-bucket.ts
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as kms from 'aws-cdk-lib/aws-kms';
import { RemovalPolicy, Duration } from 'aws-cdk-lib';

export interface SecureBucketProps {
  bucketName?: string;
  lifecycleRetentionDays?: number;
}

export class SecureBucket extends Construct {
  public readonly bucket: s3.Bucket;
  public readonly key: kms.Key;

  constructor(scope: Construct, id: string, props: SecureBucketProps = {}) {
    super(scope, id);

    this.key = new kms.Key(this, 'BucketKey', {
      enableKeyRotation: true,
      description: `KMS customer managed key for ${id}`,
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.bucket = new s3.Bucket(this, 'Resource', {
      bucketName: props.bucketName,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: this.key,
      enforceSSL: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      removalPolicy: RemovalPolicy.RETAIN,
      lifecycleRules: props.lifecycleRetentionDays ? [
        {
          expiration: Duration.days(props.lifecycleRetentionDays),
        }
      ] : undefined,
    });
  }
}
```

### Step 2: Policy-as-Code Enforcement with CDK Aspects
Implement an `IAspect` to guarantee every DynamoDB table and S3 bucket across the app is encrypted:

```typescript
// lib/aspects/security-aspect.ts
import { IAspect } from 'aws-cdk-lib';
import { IConstruct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Annotations } from 'aws-cdk-lib';

export class EnforceS3EncryptionAspect implements IAspect {
  public visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        Annotations.of(node).addError('Compliance Failure: S3 Bucket must have server-side encryption enabled.');
      }
    }
  }
}
```

### Step 3: Self-Mutating Multi-Stage Pipeline
Define continuous deployment pipelines using `aws-cdk-lib/pipelines`:

```typescript
// lib/pipeline-stack.ts
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as pipelines from 'aws-cdk-lib/pipelines';

export class DeploymentPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
      pipelineName: 'EnterpriseCorePipeline',
      synth: new pipelines.ShellStep('Synth', {
        input: pipelines.CodePipelineSource.gitHub('org/repo', 'main'),
        commands: ['npm ci', 'npm run build', 'npx cdk synth'],
      }),
    });

    // Add Production Deployment Stage
    // pipeline.addStage(new ApplicationStage(this, 'Prod', { env: { account: '123456789012', region: 'us-east-1' } }));
  }
}
```

### Step 4: Fine-Grained Unit Testing with Assertions
Test CloudFormation template outputs before deployment using `@aws-cdk/assertions`:

```typescript
// test/secure-bucket.test.ts
import { App, Stack } from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { SecureBucket } from '../lib/constructs/secure-bucket';

test('SecureBucket enforces KMS encryption and blocks public access', () => {
  const app = new App();
  const stack = new Stack(app, 'TestStack');

  new SecureBucket(stack, 'MySecureBucket');

  const template = Template.fromStack(stack);

  // Assert S3 bucket properties
  template.hasResourceProperties('AWS::S3::Bucket', {
    PublicAccessBlockConfiguration: {
      BlockPublicAcls: true,
      BlockPublicPolicy: true,
      IgnorePublicAcls: true,
      RestrictPublicBuckets: true,
    },
    BucketEncryption: Match.objectLike({
      ServerSideEncryptionConfiguration: Match.anyValue(),
    }),
  });
});
```

## Best Practices & Failure Modes

- **Never Hardcode Secrets**: Use `secretsmanager.Secret.fromSecretNameV2` or SSM Dynamic References (`resolve:ssm:...`).
- **Construct ID Immutability**: Changing a construct's logical ID changes its CloudFormation logical resource ID, triggering resource replacement (and possible data loss).
- **Environment Agnosticism**: Keep constructs environment-agnostic; pass account/region parameters via stack environment configuration (`env: { account, region }`).

## Verification & Testing

1. Validate CloudFormation synthesis: `cdk synth` and confirm template generation without errors.
2. Run Jest assertion tests: `npm test` to verify resource configurations and Aspect validations.
3. Perform drift and diff review: `cdk diff` to inspect intended changes before running `cdk deploy`.
