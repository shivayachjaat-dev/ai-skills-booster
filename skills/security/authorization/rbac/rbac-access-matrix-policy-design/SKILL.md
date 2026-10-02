---
name: rbac-access-matrix-policy-design
description: "Use this skill when designing, auditing, and implementing Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) permission matrices. It guides the agent through defining fine-grained permission scopes (resource:action), modeling roles vs groups, resolving permission conflicts, detecting privilege escalation risks, and enforcing policy gates in middleware."
domain: security
category: authorization
subcategory: rbac
tags:
  - rbac
  - authorization
  - access-control
  - permissions
  - abac
  - security
  - identity
technologies:
  - Python
  - FastAPI
  - Casbin
  - JSON
  - SQLAlchemy
complexity: intermediate
maturity: stable
tools:
  - python
dependencies:
  - python >= 3.10
---
# Role-Based Access Control (RBAC) Access Matrix Architecture

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
