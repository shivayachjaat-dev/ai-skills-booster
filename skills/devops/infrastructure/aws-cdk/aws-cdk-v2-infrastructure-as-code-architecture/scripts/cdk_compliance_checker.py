#!/usr/bin/env python3
import json
import os
import sys

def check_cdk_template(template_path):
    if not os.path.exists(template_path):
        print(f"Error: Template '{template_path}' not found.")
        sys.exit(1)

    print("=" * 65)
    print(f"Auditing Synthesized CDK Template: {template_path}")
    print("=" * 65)

    with open(template_path, 'r', encoding='utf-8') as f:
        template = json.load(f)

    resources = template.get("Resources", {})
    print(f"Total CloudFormation Resources: {len(resources)}\n")

    violations = []
    for res_id, res_data in resources.items():
        res_type = res_data.get("Type", "")
        props = res_data.get("Properties", {})

        # Check S3 Public Access
        if res_type == "AWS::S3::Bucket":
            pab = props.get("PublicAccessBlockConfiguration", {})
            if not (pab.get("BlockPublicAcls") and pab.get("BlockPublicPolicy")):
                violations.append((res_id, res_type, "S3 Bucket lacks full PublicAccessBlockConfiguration"))

        # Check Security Groups for 0.0.0.0/0
        if res_type == "AWS::EC2::SecurityGroup":
            for rule in props.get("SecurityGroupIngress", []):
                if rule.get("CidrIp") == "0.0.0.0/0" and rule.get("FromPort") in [22, 3389]:
                    violations.append((res_id, res_type, f"Security group opens port {rule.get('FromPort')} to 0.0.0.0/0!"))

    if violations:
        print(f"[COMPLIANCE FAILED] {len(violations)} security violations detected:")
        for r_id, r_type, issue in violations:
            print(f"  - [{r_type}] {r_id}: {issue}")
        sys.exit(1)
    else:
        print("SUCCESS: Synthesized CDK template passed all security guardrail checks.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cdk_compliance_checker.py <cdk.out/StackName.template.json>")
        sys.exit(1)
    check_cdk_template(sys.argv[1])
