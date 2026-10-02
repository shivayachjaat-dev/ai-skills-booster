---
name: ansible-idempotent-configuration-management
description: "Use this skill when designing, authoring, and executing automated server configuration management playbooks and roles using Ansible. It guides the agent through enforcing strict task idempotency, structuring reusable Ansible roles, managing encrypted secrets with Ansible Vault, organizing inventory variables, and testing with Molecule."
domain: devops
category: infrastructure-as-code
subcategory: ansible
tags:
  - ansible
  - configuration-management
  - devops
  - automation
  - infrastructure-as-code
  - linux
technologies:
  - Ansible 2.15+
  - YAML
  - Linux
  - Ansible Vault
  - Molecule
complexity: intermediate
maturity: stable
tools:
  - ansible-playbook
  - ansible-vault
  - molecule
dependencies:
  - ansible-core >= 2.15.0
---
# Ansible Idempotent Configuration Management Architecture

## Overview

A comprehensive engineering guide for automating server provisioning and operating systems configuration using Ansible. This skill instructs AI agents on authoring strictly idempotent tasks (tasks that make zero changes when run repeatedly against desired state), structuring modular Ansible Roles, securing sensitive variables via Ansible Vault, implementing event-driven handlers, and executing automated testing using Molecule.

## When to Use

- Provisioning and configuring Linux virtual machines, bare-metal servers, and edge nodes consistently.
- Applying OS security baselines (hardening SSH, configuring UFW/iptables firewalls, installing security patches).
- Deploying configuration files (NGINX, PostgreSQL, systemd service units) with automatic service reload handlers.
- Automating multi-node rolling updates with serial batch execution.

## When NOT to Use

- Deploying immutable container images to Kubernetes clusters (use Helm or Kustomize).
- Provisioning dynamic cloud infrastructure resources like VPCs, subnets, and RDS databases (use Terraform).

## Inputs & Prerequisites

- Ansible 2.15+ installed on control node.
- Target hosts reachable via SSH with sudo privileges.
- Inventory file defining host groups (`hosts.ini` or `inventory.yaml`).

## Core Workflow

### 1. Reusable Modular Role Directory Structure
Follow the standard Ansible role structure:
```text
roles/webserver/
├── defaults/main.yaml      # Low-priority default variables
├── vars/main.yaml          # High-priority immutable role variables
├── tasks/main.yaml         # Main list of idempotent tasks
├── handlers/main.yaml      # Service reload handlers notified by tasks
├── templates/              # Jinja2 template files (.j2)
└── meta/main.yaml          # Role dependencies and author info
```

### 2. Idempotent Tasks & Handlers (`tasks/main.yaml`)
Avoid raw `command` or `shell` modules. Always use declarative modules with `changed_when` safeguards:

```yaml
---
# roles/webserver/tasks/main.yaml
- name: Ensure NGINX and TLS packages are installed
  ansible.builtin.apt:
    name:
      - nginx
      - ssl-cert
    state: present
    update_cache: yes
    cache_valid_time: 3600

- name: Deploy hardened NGINX configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: Reload NGINX service

- name: Ensure NGINX service is enabled and active
  ansible.builtin.systemd:
    name: nginx
    state: started
    enabled: yes

- name: Audit open listening ports idempotently
  ansible.builtin.command: ss -tulpn
  register: port_audit_output
  changed_when: false # Read-only command; never reports changed: true
```

```yaml
---
# roles/webserver/handlers/main.yaml
- name: Reload NGINX service
  ansible.builtin.systemd:
    name: nginx
    state: reloaded
```

### 3. Encrypted Secrets with Ansible Vault
Encrypt sensitive database credentials and private keys:

```bash
# Encrypt sensitive variables file
ansible-vault encrypt group_vars/production/vault.yaml

# Run playbook with vault password prompt or password file
ansible-playbook -i inventory.yaml site.yaml --vault-password-file .vault_pass
```

### 4. Zero-Downtime Rolling Update Playbook
Execute rolling updates across web nodes sequentially:

```yaml
---
# site.yaml
- name: Rolling update web servers
  hosts: webservers
  serial: 1 # Update one server at a time
  max_fail_percentage: 0
  roles:
    - role: webserver
```

## Best Practices & Failure Modes

1. **Non-Idempotent `shell` Tasks**: Using `ansible.builtin.shell: "echo 'config' >> /etc/app.conf"` appends the text repeatedly every time the playbook runs, corrupting the file. Use `ansible.builtin.lineinfile` or `template`.
2. **Missing `validate` on Config Templates**: If a templating bug generates invalid syntax in `/etc/nginx/nginx.conf` and the service reloads, the webserver crashes immediately. Always include `validate: 'nginx -t -c %s'` on templates.
3. **Flaky Handlers on Task Failures**: Handlers are notified during task execution but only run at the very end of the play. If an intermediate task fails before handlers execute, notifications are lost. Use `meta: flush_handlers` where immediate execution is required.

## Verification & Testing

- Dry-run playbook with syntax and diff check:
  ```bash
  ansible-playbook -i inventory.yaml site.yaml --syntax-check
  ansible-playbook -i inventory.yaml site.yaml --check --diff
  ```
- Verify zero changes on second consecutive run (idempotency proof):
  ```bash
  ansible-playbook -i inventory.yaml site.yaml
  # Output must show: changed=0 failed=0
  ```
