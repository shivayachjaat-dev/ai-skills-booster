# AWS IAM Policy Evaluation Logic

## Evaluation Order
1. **Explicit Deny**: Any matching Deny immediately halts evaluation and denies access.
2. **Organizations SCPs**: If present, must evaluate to Allow.
3. **Resource-Based Policies**: Can grant direct access across accounts.
4. **IAM Permissions Boundary**: Sets maximum boundary on effective permissions.
5. **Session Policies**: Applied during temporary credential generation (`AssumeRole`).
6. **Identity-Based Policies**: Grants explicit Allow.
7. **Default**: Implicit Deny if no explicit Allow is found.
