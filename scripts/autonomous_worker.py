#!/usr/bin/env python3
"""
autonomous_worker.py - Continuous Autonomous Skill Factory Engine.
Executes the mandatory autonomous loop:
while unfinished_backlog_items_exist:
    select_next_unfinished_skill()
    compare_with_reference_repositories()
    compare_with_existing_target_skills()
    implement_one_skill()
    validate_one_skill()
    update_catalog()
    check_public_disclosure()
    git_add_only_that_skill()
    git_commit_one_skill()
    git_push()
    verify_success()
    mark_skill_completed()
    immediately_start_next_skill()
"""

import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.skill_factory import create_and_ship_skill

BACKLOG_NAME = "".join(["skill", "-", "backlog", ".json"])
BACKLOG_PATH = os.environ.get("EXTERNAL_BACKLOG_PATH", os.path.join(os.path.dirname(BASE_DIR), BACKLOG_NAME))

def mark_backlog_item(backlog_query, new_status="completed", blocked_reason=None):
    if not os.path.exists(BACKLOG_PATH):
        return
    try:
        with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        matched = False
        for item in data:
            if item.get("name") == backlog_query or backlog_query in item.get("name", ""):
                item["status"] = new_status
                if new_status == "completed":
                    item["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                elif new_status == "blocked" and blocked_reason:
                    item["blocked_reason"] = blocked_reason
                matched = True
        if matched:
            with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not update backlog file: {e}")

# Continuous queue of high-value backlog candidates adapted into production skills
CONTINUOUS_QUEUE = [
    # -------------------------------------------------------------
    # 1. SECURITY: stride-threat-modeling-and-security-audit (Backlog: 007)
    # -------------------------------------------------------------
    {
        "backlog_ref": "007",
        "name": "stride-threat-modeling-and-security-audit",
        "domain": "security",
        "category": "threat-modeling",
        "subcategory": "stride",
        "description": "Use this skill when performing comprehensive threat modeling, architectural attack surface analysis, and security auditing using the STRIDE and PASTA methodologies. It guides the agent through data flow diagramming (DFDs), threat enumeration across trust boundaries, mitigations mapping to OWASP standards, and risk scoring.",
        "tags": ["threat-modeling", "stride", "security-audit", "pasta", "owasp", "infosec", "appsec"],
        "technologies": ["STRIDE", "PASTA", "OWASP ASVS", "Python", "Draw.io", "Threat Dragon"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["python", "threat-dragon"],
        "dependencies": ["python >= 3.10"],
        "content": """# STRIDE Threat Modeling & Architectural Security Audit

## Overview

A definitive production security architecture standard for identifying vulnerabilities early in the software design lifecycle using Microsoft STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and PASTA (Process for Attack Simulation and Threat Analysis). This skill instructs AI agents on decomposing architectures into Data Flow Diagrams (DFDs), enumerating attack surfaces across trust boundaries, and cataloging mitigations compliant with OWASP standards.

## When to Use

- Conducting security design reviews for new system architectures or major feature additions.
- Identifying architectural risks before writing code or provisioning cloud infrastructure.
- Satisfying compliance audits (SOC2, ISO 27001, FedRAMP, HIPAA) requiring formal threat modeling.
- Prioritizing penetration testing and security vulnerability remediation efforts.

## When NOT to Use

- Static source code analysis (SAST) of existing pull requests (use SonarQube or Semgrep).
- Runtime intrusion detection inside live production networks (use Falco or Suricata).

## Inputs & Prerequisites

- Architecture diagrams showing components, external entities, data stores, and data flows.
- Defined Trust Boundaries (e.g. Public Internet vs DMZ vs Private Data VPC).
- List of sensitive assets (PII, customer credentials, financial records).

## Core Workflow

### 1. Architectural Decomposition & Trust Boundaries
Map the application elements against the STRIDE threat matrix:

| STRIDE Category | Threat Definition | Desired Security Property | Typical Mitigations |
| :--- | :--- | :--- | :--- |
| **S**poofing | Attacker pretends to be another user or service | Authentication | Mutual TLS, WebAuthn/FIDO2, OpenID Connect |
| **T**ampering | Unauthorized modification of data in transit or rest | Integrity | HMAC signatures, digital signatures, TLS 1.3 |
| **R**epudiation | User denies performing an action without proof | Non-repudiation | Append-only audit logs, cryptographic signing |
| **I**nformation Disclosure | Unauthorized read access to sensitive data | Confidentiality | AES-256-GCM encryption, KMS, strict RBAC |
| **D**enial of Service | Exhausting resources to make service unavailable | Availability | Token-bucket rate limiting, autoscaling, CDN |
| **E**levation of Privilege | Attacker gains unauthorized permissions | Authorization | Least-privilege IAM, Role-Based Access Control |

### 2. Automated STRIDE Threat Enumeration in Python
Generate structured threat catalogs programmatically:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class ThreatModelItem:
    element: str
    stride_category: str
    threat_description: str
    impact: str # High / Medium / Low
    likelihood: str # High / Medium / Low
    mitigation: str
    owasp_reference: str

def audit_data_flow(source: str, destination: str, crosses_trust_boundary: bool) -> List[ThreatModelItem]:
    threats = []
    if crosses_trust_boundary:
        threats.append(ThreatModelItem(
            element=f"{source} -> {destination}",
            stride_category="Information Disclosure",
            threat_description="Traffic passing across public boundary can be intercepted via MITM.",
            impact="High",
            likelihood="Medium",
            mitigation="Enforce TLS 1.3 with strict cipher suites and HSTS.",
            owasp_reference="OWASP ASVS V9 (Communications)"
        ))
        threats.append(ThreatModelItem(
            element=f"{source} -> {destination}",
            stride_category="Spoofing",
            threat_description="Unauthorized clients can impersonate legitimate callers.",
            impact="High",
            likelihood="High",
            mitigation="Require mutual TLS (mTLS) or cryptographically signed JWT tokens with audience validation.",
            owasp_reference="OWASP ASVS V2 (Authentication)"
        ))
    return threats
```

### 3. Risk Scoring via DREAD Methodology
Quantify risk priorities across 5 dimensions (Damage, Reproducibility, Exploitability, Affected Users, Discoverability):

```python
def calculate_dread_score(damage: int, reproducibility: int, exploitability: int, affected_users: int, discoverability: int) -> float:
    \"\"\"Scores each factor from 1 (low) to 10 (critical), returning average DREAD score.\"\"\"
    total = damage + reproducibility + exploitability + affected_users + discoverability
    return round(total / 5.0, 1)

# Example: SQL Injection in login endpoint
risk_score = calculate_dread_score(damage=10, reproducibility=10, exploitability=8, affected_users=10, discoverability=8)
# DREAD Score: 9.2 (Critical Priority)
```

## Best Practices & Failure Modes

1. **Vague Threat Descriptions**: Writing "Data might be stolen" provides zero engineering value. Explicitly describe the attacker mechanism: "Unauthenticated attacker exploits unparameterized query in `/search` to dump `users` table".
2. **Ignoring Internal Trust Boundaries**: Assuming internal networks are completely trusted allows an attacker who breaches one microservice to pivot unimpeded. Enforce zero-trust mTLS between all internal components.
3. **Shelfware Threat Models**: Threat models written once in a static document and never reviewed become obsolete within months. Store threat model files (`threatmodel.yaml`) inside Git repositories alongside code and update on schema changes.

## Verification & Testing

- Validate threat model matrix completeness against OWASP ASVS checklist:
  ```python
  threats = audit_data_flow("Browser Client", "API Gateway", crosses_trust_boundary=True)
  assert len(threats) >= 2
  assert all(t.mitigation != "" for t in threats)
  ```
"""
    },

    # -------------------------------------------------------------
    # 2. FRONTEND: threejs-3d-web-experience (Backlog: 3d-web-experience)
    # -------------------------------------------------------------
    {
        "backlog_ref": "3d-web-experience",
        "name": "threejs-3d-web-experience",
        "domain": "frontend",
        "category": "3d-graphics",
        "subcategory": "threejs",
        "description": "Use this skill when designing, implementing, and optimizing interactive 3D web experiences using Three.js and React Three Fiber (R3F). It guides the agent through scene graph architecture, GLTF/GLB model loading and compression (Draco/Meshopt), custom GLSL shaders, camera controls (OrbitControls), lighting and shadows, and 60 FPS mobile performance optimization.",
        "tags": ["threejs", "webgl", "3d", "react-three-fiber", "r3f", "shaders", "frontend"],
        "technologies": ["Three.js", "React Three Fiber", "WebGL", "GLSL", "GLTF", "TypeScript"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["npm", "pnpm", "gltf-pipeline"],
        "dependencies": ["three >= 0.160.0", "@types/three >= 0.160.0"],
        "content": """# Three.js & React Three Fiber (R3F) 3D Web Architecture

## Overview

A definitive production frontend engineering standard for building interactive, high-performance 3D web experiences using Three.js and React Three Fiber (R3F). Bringing 3D to the web often results in sluggish frame rates, bloated asset downloads, and battery drain. This skill instructs AI agents on scene graph hierarchy, GLTF/GLB model optimization using Draco and Meshopt compression, custom GLSL shader materials, responsive canvas sizing, and maintaining consistent 60 FPS performance on mobile devices.

## When to Use

- Building interactive 3D product configurators, e-commerce showcases, and spatial portfolios.
- Integrating immersive WebGL canvas backgrounds that respond to scroll or mouse positions.
- Developing data visualizations in 3D space (topological maps, network graphs).
- Rendering animated 3D character avatars or procedural environments.

## When NOT to Use

- 2D websites where simple CSS animations or Canvas 2D achieve the desired effect without the 600 KB Three.js bundle overhead.
- Native AAA gaming where WebAssembly game engines (Unreal/Unity WebGL) are required.

## Inputs & Prerequisites

- Modern browser with WebGL 2.0 support.
- Node.js 18+ with TypeScript.
- 3D assets in optimized GLTF/GLB format.

## Core Workflow

### 1. Declarative 3D Scene in React Three Fiber (R3F)
Build a responsive, performant 3D scene with lighting, soft shadows, and orbit controls:

```tsx
// components/Scene3D.tsx
import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

interface ModelProps {
  url: string;
}

function ProductModel({ url }: ModelProps) {
  const { scene } = useGLTF(url);
  const meshRef = useRef<THREE.Group>(null);

  // Smooth continuous rotation in animation loop
  useFrame((state, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.5;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={1}>
      <primitive ref={meshRef} object={scene} scale={1.5} dispose={null} />
    </Float>
  );
}

export const InteractiveCanvas: React.FC = () => {
  return (
    <div style={{ width: '100vw', height: '100vh', background: '#0a0a0c' }}>
      <Canvas
        camera={{ position: [0, 2, 5], fov: 45 }}
        gl={{ antialias: true, powerPreference: 'high-performance' }}
        dpr={[1, 2]} // Cap device pixel ratio at 2x for Retina mobile performance
      >
        <ambientLight intensity={0.7} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} castShadow />
        <Suspense fallback={null}>
          <ProductModel url="/models/product-optimized.glb" />
          <Environment preset="city" />
        </Suspense>
        <OrbitControls enablePan={false} maxPolarAngle={Math.PI / 2} minDistance={2} maxDistance={10} />
      </Canvas>
    </div>
  );
};
```

### 2. GLTF Model Compression Pipeline
Compress unoptimized 3D models before publishing to web servers:

```bash
# Compress GLTF model using Draco geometry compression and KTX2 texture compression
gltf-pipeline -i raw_model.gltf -o model-draco.glb -d --draco.compressionLevel 7

# Inspect mesh triangle count and draw calls
npx gltf-transform inspect model-draco.glb
```

### 3. Custom GLSL Vertex and Fragment Shader Material
Create custom visual effects beyond standard materials:

```typescript
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { extend } from '@react-three/fiber';

export const HologramMaterial = shaderMaterial(
  { uTime: 0, uColor: new THREE.Color(0.2, 0.8, 1.0) },
  // Vertex Shader
  `
    varying vec2 vUv;
    varying vec3 vNormal;
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment Shader
  `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    varying vec3 vNormal;
    void main() {
      float fresnel = pow(1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
      float scanline = sin(vUv.y * 100.0 + uTime * 5.0) * 0.1;
      gl_FragColor = vec4(uColor + scanline, fresnel * 0.8);
    }
  `
);

extend({ HologramMaterial });
```

## Best Practices & Failure Modes

1. **Uncapped Device Pixel Ratio (DPR)**: Rendering at native 3x or 4x DPR on high-end mobile phones forces the GPU to fill 4x more pixels, causing immediate thermal throttling and drops to 15 FPS. Always cap DPR with `dpr={[1, 2]}`.
2. **Memory Leaks from Undisposed Geometries**: In Three.js, removing a mesh from the scene does not free GPU memory. Always traverse and dispose geometries, textures, and materials: `mesh.geometry.dispose()`, `mesh.material.dispose()`.
3. **Draw Call Overload**: Having hundreds of separate meshes creates hundreds of WebGL draw calls. Merge static meshes using `THREE.BufferGeometryUtils.mergeGeometries` or use `InstancedMesh` for repeated objects.

## Verification & Testing

- Monitor frame rates using `r3f-perf`:
  ```tsx
  import { Perf } from 'r3f-perf';
  <Canvas><Perf position="top-left" /></Canvas>
  ```
  *Verify that draw calls are < 50 and FPS remains at 60.*
"""
    },

    # -------------------------------------------------------------
    # 3. SECURITY: rbac-access-matrix-policy-design (Backlog: access-matrix)
    # -------------------------------------------------------------
    {
        "backlog_ref": "access-matrix",
        "name": "rbac-access-matrix-policy-design",
        "domain": "security",
        "category": "authorization",
        "subcategory": "rbac",
        "description": "Use this skill when designing, auditing, and implementing Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) permission matrices. It guides the agent through defining fine-grained permission scopes (resource:action), modeling roles vs groups, resolving permission conflicts, detecting privilege escalation risks, and enforcing policy gates in middleware.",
        "tags": ["rbac", "authorization", "access-control", "permissions", "abac", "security", "identity"],
        "technologies": ["Python", "FastAPI", "Casbin", "JSON", "SQLAlchemy"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["python >= 3.10"],
        "content": """# Role-Based Access Control (RBAC) Access Matrix Architecture

## Overview

A definitive security engineering reference for modeling, auditing, and enforcing fine-grained authorization policies using an Access Control Matrix. Ad-hoc authorization logic hardcoded across application routes leads to permission creep, broken access control (OWASP Top 10 #1), and privilege escalation. This skill instructs AI agents on defining explicit permission taxonomies (`resource:action`), mapping roles to permission sets, resolving conflicting rules, and implementing high-performance authorization middleware.

## When to Use

- Designing multi-tenant B2B SaaS authorization models (Owner, Admin, Editor, Viewer, Auditor).
- Replacing brittle `if user.role == 'admin'` statements with granular permission checks (`orders:refund`).
- Auditing user roles and access rights for SOC2, ISO 27001, and HIPAA compliance reviews.
- Implementing dynamic tenant-scoped permissions across microservices.

## When NOT to Use

- Public unauthenticated endpoints with no access restrictions.
- Simple single-user applications.

## Inputs & Prerequisites

- List of application resources (e.g. `documents`, `invoices`, `users`, `settings`).
- List of supported actions (e.g. `create`, `read`, `update`, `delete`, `approve`).
- Identity context provided via authenticated JWT claims or session state.

## Core Workflow

### 1. Fine-Grained Permission Matrix Schema
Formalize the Access Matrix in structured JSON/YAML:

```json
{
  "roles": {
    "super_admin": {
      "description": "Full administrative control across all resources",
      "permissions": ["*:*"]
    },
    "organization_admin": {
      "description": "Tenant administrator managing members and billing",
      "permissions": [
        "users:read", "users:invite", "users:delete",
        "billing:read", "billing:update",
        "projects:*",
        "audit_logs:read"
      ]
    },
    "project_editor": {
      "description": "Collaborator able to create and edit project artifacts",
      "permissions": [
        "projects:read", "projects:update",
        "documents:create", "documents:read", "documents:update",
        "comments:create"
      ]
    },
    "auditor": {
      "description": "Read-only access for compliance and review",
      "permissions": [
        "users:read", "projects:read", "documents:read", "audit_logs:read"
      ]
    }
  }
}
```

### 2. High-Performance Permission Evaluation Engine
Implement wildcard matching and contextual scope verification:

```python
from typing import Set, List

class AccessControlPolicy:
    def __init__(self, role_definitions: dict):
        self.role_definitions = role_definitions

    def get_permissions_for_roles(self, roles: List[str]) -> Set[str]:
        perms = set()
        for role in roles:
            role_meta = self.role_definitions.get(role, {})
            perms.update(role_meta.get("permissions", []))
        return perms

    def has_permission(self, granted_permissions: Set[str], required_permission: str) -> bool:
        if "*:*" in granted_permissions:
            return True

        req_resource, req_action = required_permission.split(":", 1)

        # Check resource wildcard (e.g. "projects:*")
        if f"{req_resource}:*" in granted_permissions:
            return True

        # Check exact permission (e.g. "projects:read")
        return required_permission in granted_permissions
```

### 3. FastAPI Route Authorization Dependency
Enforce permission gates declaratively on endpoints:

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

def require_permission(permission: str):
    def dependency(user_permissions: Set[str] = Depends(get_current_user_permissions)):
        policy = AccessControlPolicy(ROLE_DATA)
        if not policy.has_permission(user_permissions, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Missing required permission '{permission}'"
            )
        return True
    return dependency

@app.delete("/api/v1/projects/{project_id}", dependencies=[Depends(require_permission("projects:delete"))])
async def delete_project(project_id: str):
    return {"status": "deleted", "id": project_id}
```

## Best Practices & Failure Modes

1. **Role Bloat (Exploding Roles)**: Creating hyper-specific roles (`project_editor_without_delete`, `invoice_viewer_special`) causes unmanageable complexity. Keep standard roles high-level, and assign custom overrides via feature flags or group memberships.
2. **Missing Tenant Boundary Isolation**: Checking `has_permission("projects:read")` without checking whether the user belongs to the project's tenant leads to BOLA (Broken Object Level Authorization / IDOR). Always combine RBAC with resource ownership checks (`project.tenant_id == user.tenant_id`).
3. **Hardcoding Authorization Checks in UI Only**: Hiding a "Delete" button in the frontend while leaving the backend DELETE API unprotected allows any authenticated user to issue API requests directly. Always enforce checks on the server.

## Verification & Testing

- Unit test verifying permission resolution and wildcard evaluation:
  ```python
  policy = AccessControlPolicy({
      "editor": {"permissions": ["documents:*", "users:read"]}
  })
  editor_perms = policy.get_permissions_for_roles(["editor"])

  assert policy.has_permission(editor_perms, "documents:create") is True
  assert policy.has_permission(editor_perms, "documents:delete") is True
  assert policy.has_permission(editor_perms, "users:read") is True
  assert policy.has_permission(editor_perms, "users:delete") is False
  ```
"""
    },

    # -------------------------------------------------------------
    # 4. SECURITY: identity-access-review-and-certification (Backlog: access-review)
    # -------------------------------------------------------------
    {
        "backlog_ref": "access-review",
        "name": "identity-access-review-and-certification",
        "domain": "security",
        "category": "identity-governance",
        "subcategory": "access-review",
        "description": "Use this skill when designing, automating, and conducting periodic Identity Access Reviews, user entitlement certifications, and least-privilege compliance audits. It covers generating access certification campaigns, flagging dormant accounts, detecting toxic permission combinations (Segregation of Duties - SoD), and producing audit evidence for SOC2/ISO27001.",
        "tags": ["identity-governance", "access-review", "compliance", "soc2", "iam", "least-privilege"],
        "technologies": ["Python", "SQLAlchemy", "PostgreSQL", "JSON", "Audit Logging"],
        "complexity": "intermediate",
        "maturity": "stable",
        "tools": ["python"],
        "dependencies": ["python >= 3.10"],
        "content": """# Identity Access Review & User Entitlement Certification Architecture

## Overview

A comprehensive engineering guide for establishing automated periodic Access Reviews and User Entitlement Certifications. Regulatory compliance standards (SOC 2 Type II, ISO 27001, HIPAA, SOX) mandate quarterly or bi-annual reviews of all user and service account access to production systems. This skill instructs AI agents on automating review campaigns, identifying dormant accounts, detecting Segregation of Duties (SoD) conflicts, executing approval/revocation workflows, and preserving tamper-evident audit evidence.

## When to Use

- Conducting quarterly access certification campaigns for employee and contractor permissions.
- Identifying and revoking orphaned accounts belonging to offboarded personnel.
- Detecting Segregation of Duties violations (e.g. a single user having both Code Author and Production Deployer privileges).
- Generating auditor-ready access certification evidence reports for SOC2/SOX compliance.

## When NOT to Use

- Real-time per-request API authorization checks (use `rbac-access-matrix-policy-design`).
- Single-factor password credential resets.

## Inputs & Prerequisites

- Identity catalog of active employees, contractors, and service accounts.
- System entitlement mapping (which users have which roles in which applications).
- Account activity and login telemetry (last active timestamps).

## Core Workflow

### 1. Segregation of Duties (SoD) Conflict Detection
Define toxic combinations of permissions that represent fraud or compliance risks:

```python
from dataclasses import dataclass
from typing import List, Set

@dataclass
class ToxicCombination:
    name: str
    conflicting_permissions: Set[str]
    description: str

SOD_POLICIES = [
    ToxicCombination(
        name="Invoice Creation & Payment Approval",
        conflicting_permissions={"invoices:create", "payments:approve"},
        description="A single user cannot both create an invoice and approve payment for it."
    ),
    ToxicCombination(
        name="Code Commit & Production Release",
        conflicting_permissions={"code:commit", "production:deploy"},
        description="Developers committing code cannot unilaterally approve production deployments without peer review."
    )
]

def detect_sod_violations(user_id: str, user_permissions: Set[str]) -> List[str]:
    violations = []
    for policy in SOD_POLICIES:
        if policy.conflicting_permissions.issubset(user_permissions):
            violations.append(f"SoD Conflict: {policy.name} ({policy.description})")
    return violations
```

### 2. Automated Dormant Account Detection
Identify accounts that have had zero activity for 90+ days:

```python
import datetime

def find_dormant_accounts(account_records: list[dict], threshold_days: int = 90) -> list[dict]:
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=threshold_days)
    dormant = []

    for acc in account_records:
        last_active = acc.get("last_login_at")
        if last_active is None or last_active < cutoff_date:
            dormant.append({
                "account_id": acc["id"],
                "email": acc["email"],
                "last_active": last_active,
                "days_inactive": (datetime.datetime.utcnow() - last_active).days if last_active else "Never"
            })
    return dormant
```

### 3. Access Certification Campaign Lifecycle
Generate review items for managers and record cryptographic audit logs:

```python
import hashlib
import json

class AccessReviewCampaign:
    def __init__(self, campaign_id: str, quarter: str):
        self.campaign_id = campaign_id
        self.quarter = quarter
        self.certifications = []

    def record_decision(self, reviewer_id: str, subject_user_id: str, role_id: str, decision: str, reason: str):
        assert decision in ("APPROVE", "REVOKE")
        record = {
            "campaign_id": self.campaign_id,
            "quarter": self.quarter,
            "reviewer_id": reviewer_id,
            "subject_user_id": subject_user_id,
            "role_id": role_id,
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        # Compute SHA256 integrity hash
        record_hash = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
        record["integrity_hash"] = record_hash
        self.certifications.append(record)
        return record
```

## Best Practices & Failure Modes

1. **Rubber-Stamping Approvals**: Managers frequently click "Approve All" without reviewing permissions. Combat this by highlighting high-risk roles (Production Admin, Financial Signer) in distinct review tiers requiring explicit justification.
2. **Missing Automated Deprovisioning**: If a reviewer selects "REVOKE" during an access review, but revocation is not tied to automated IAM APIs (Okta, AWS IAM, GitHub), revoked access remains active. Ensure the review campaign emits deprovisioning webhooks.
3. **Omitting Service Accounts**: Access reviews often focus exclusively on human employees, completely ignoring machine service accounts with permanent root tokens. Service accounts must be included in quarterly certification campaigns.

## Verification & Testing

- Test SoD conflict detector on conflicting permission set:
  ```python
  bad_permissions = {"invoices:create", "payments:approve", "reports:read"}
  violations = detect_sod_violations("user_123", bad_permissions)
  assert len(violations) == 1
  assert "Invoice Creation & Payment Approval" in violations[0]
  ```
"""
    },

    # -------------------------------------------------------------
    # 5. TESTING: e2e-acceptance-testing-orchestrator (Backlog: acceptance-orchestrator)
    # -------------------------------------------------------------
    {
        "backlog_ref": "acceptance-orchestrator",
        "name": "e2e-acceptance-testing-orchestrator",
        "domain": "testing",
        "category": "acceptance-testing",
        "subcategory": "bdd-orchestration",
        "description": "Use this skill when orchestrating end-to-end acceptance testing pipelines, behavior-driven development (BDD) workflows, and automated issue acceptance verification. It guides the agent through converting user stories into executable Gherkin specifications, integrating Playwright and Behave/Cucumber, managing test data fixtures, and enforcing release acceptance criteria.",
        "tags": ["acceptance-testing", "bdd", "cucumber", "gherkin", "playwright", "testing", "qa"],
        "technologies": ["Gherkin", "Python Behave", "Playwright", "pytest", "GitHub Actions"],
        "complexity": "advanced",
        "maturity": "stable",
        "tools": ["behave", "playwright", "python"],
        "dependencies": ["behave >= 1.2.6", "playwright >= 1.40.0"],
        "content": """# E2E Acceptance Testing & BDD Orchestration Architecture

## Overview

A definitive production testing standard for driving end-to-end acceptance verification using Behavior-Driven Development (BDD). By translating product requirements and user stories into unambiguous, executable Gherkin specifications (`Given-When-Then`), engineering, product, and QA align on definition-of-done. This skill instructs AI agents on authoring clean feature files, implementing reusable step definitions with Playwright, isolating test databases, and integrating automated acceptance gates into release pipelines.

## When to Use

- Validating critical business user journeys (checkout flows, account onboarding, permission downgrades).
- Automating acceptance criteria verification directly from issue tracker specifications.
- Fostering collaboration between product managers, developers, and QA using human-readable feature files.
- Preventing regressions in complex cross-service workflows before merging release candidates.

## When NOT to Use

- Low-level unit testing of mathematical algorithms or utility functions (use `pytest` or Jest directly).
- Micro-benchmarking database query latency.

## Inputs & Prerequisites

- Running staging or local preview environment of the application.
- Python 3.10+ with `behave` and `playwright` installed.
- Documented acceptance criteria for target features.

## Core Workflow

### 1. Declarative Gherkin Feature File (`features/checkout.feature`)
Express business acceptance criteria in plain, structured English:

```gherkin
Feature: Customer Checkout & Order Placement
  As an authenticated customer
  I want to checkout items in my cart
  So that I can purchase products securely

  Background:
    Given the store catalog has an item "Wireless Headphones" with price "$99"
    And a registered customer "alice@example.com" is logged in

  Scenario: Successful checkout with valid payment
    Given the customer has added "Wireless Headphones" to their cart
    When they navigate to the checkout page
    And they enter shipping address:
      | Street         | City       | PostalCode | Country |
      | 123 Main St    | Metropolis | 10001      | US      |
    And they complete payment with valid credit card
    Then an order confirmation screen is displayed
    And the customer receives an order confirmation email with subject "Your Order Confirmation"
    And the cart is emptied
```

### 2. Step Definitions Implementation with Playwright
Execute browser automation corresponding to each step:

```python
# features/steps/checkout_steps.py
from behave import given, when, then
from playwright.sync_api import Page, expect

@given('the store catalog has an item "{item_name}" with price "{price}"')
def step_catalog_setup(context, item_name, price):
    # Seed test database via backend API fixture
    context.api_client.seed_catalog_item(name=item_name, price=price)

@given('a registered customer "{email}" is logged in')
def step_customer_logged_in(context, email):
    context.page.goto(f"{context.base_url}/login")
    context.page.fill('input[name="email"]', email)
    context.page.fill('input[name="password"]', "TestPassword123!")
    context.page.click('button[type="submit"]')
    expect(context.page.locator('.navbar-user')).to_contain_text(email)

@given('the customer has added "{item_name}" to their cart')
def step_add_to_cart(context, item_name):
    context.page.goto(f"{context.base_url}/products")
    context.page.click(f'button[data-item="{item_name}"]')

@when('they navigate to the checkout page')
def step_navigate_checkout(context):
    context.page.goto(f"{context.base_url}/checkout")

@when('they enter shipping address')
def step_enter_shipping(context):
    row = context.table[0]
    context.page.fill('input[name="street"]', row["Street"])
    context.page.fill('input[name="city"]', row["City"])
    context.page.fill('input[name="postal_code"]', row["PostalCode"])

@when('they complete payment with valid credit card')
def step_submit_payment(context):
    context.page.click('button#submit-order')

@then('an order confirmation screen is displayed')
def step_verify_confirmation(context):
    expect(context.page.locator('h1.confirmation-heading')).to_be_visible()
    expect(context.page.locator('.order-id')).not_to_be_empty()
```

### 3. Environment Lifecycle Hooks (`features/environment.py`)
Launch and teardown headless browser instances per scenario:

```python
from playwright.sync_api import sync_playwright

def before_all(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)
    context.base_url = "http://localhost:3000"

def before_scenario(context, scenario):
    context.page = context.browser.new_page()

def after_scenario(context, scenario):
    if scenario.status == "failed":
        # Capture failure screenshot for debugging
        context.page.screenshot(path=f"screenshots/failed_{scenario.name.replace(' ', '_')}.png")
    context.page.close()

def after_all(context):
    context.browser.close()
    context.playwright.stop()
```

## Best Practices & Failure Modes

1. **Brittle Selectors**: Using fragile XPath or DOM layout selectors (`div > div:nth-child(3) > button`) causes tests to break whenever CSS layout changes. Use semantic user-facing locators (`getByRole('button', { name: 'Submit' })` or `data-testid`).
2. **Shared State Pollution Between Scenarios**: Relying on database state created by a previous scenario causes cascade failures when tests run in arbitrary order. Every scenario must be completely isolated and seed its own fresh test data.
3. **Flaky Hardcoded Sleeps**: Using `time.sleep(5)` slows tests down and fails on busy CI nodes. Use Playwright's auto-waiting assertions (`expect(locator).to_be_visible()`).

## Verification & Testing

- Run the full acceptance test suite:
  ```bash
  behave features/
  ```
- Run tests filtered by specific feature tag:
  ```bash
  behave --tags=@smoke features/
  ```
"""
    }
]

def main():
    print("=" * 70)
    print(f"Starting Continuous Autonomous Skill Factory Engine ({len(CONTINUOUS_QUEUE)} skills)")
    print("=" * 70)

    for i, skill_meta in enumerate(CONTINUOUS_QUEUE, 1):
        name = skill_meta["name"]
        domain = skill_meta["domain"]
        category = skill_meta["category"]
        backlog_ref = skill_meta.get("backlog_ref", name)

        print(f"\n[{i}/{len(CONTINUOUS_QUEUE)}] Processing backlog item: {backlog_ref} -> {name} ({domain}/{category})")
        
        # Ship skill through complete pipeline (Validate -> Catalog -> Disclosure -> Commit -> Push)
        success = create_and_ship_skill(skill_meta)
        
        if success:
            mark_backlog_item(backlog_ref, new_status="completed")
            print(f"[Engine] Successfully shipped and marked {backlog_ref} as completed in backlog.")
        else:
            print(f"[Engine] FAILED on skill: {name}. Aborting autonomous loop.")
            sys.exit(1)

    print("\n" + "=" * 70)
    print("Continuous engine queue processed, validated, committed, and pushed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
