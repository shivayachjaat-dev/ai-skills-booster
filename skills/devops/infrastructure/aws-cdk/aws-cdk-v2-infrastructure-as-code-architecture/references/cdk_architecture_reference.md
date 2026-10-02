# AWS CDK Construct Levels Reference

## Construct Classification
1. **L1 Constructs (Cfn*)**:
   - Direct 1:1 mapping to CloudFormation resources (e.g., `CfnBucket`).
   - Requires manual definition of all CloudFormation properties.
2. **L2 Constructs**:
   - Curated AWS constructs with intelligent defaults, security baselines, and helper methods (e.g., `s3.Bucket`, `bucket.grantRead(role)`).
3. **L3 Constructs (Patterns)**:
   - High-level multi-service architectures combined into a single construct (e.g., `ApplicationLoadBalancedFargateService`).
