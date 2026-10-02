---
name: incident-response-and-triage
description: "Use this skill when triaging, containing, and investigating active production security incidents and data breaches. It guides the agent through the PICERL framework (Preparation, Identification, Containment, Eradication, Recovery, Lessons Learned), evidence preservation without anti-forensic contamination, forensic log isolation, and root-cause analysis."
domain: security
category: incident-response
subcategory: triage
tags:
  - security
  - incident-response
  - forensics
  - triage
  - devsecops
  - threat-containment
technologies:
  - Linux
  - Git
  - Syslog
  - Auditd
  - Memory Forensics
complexity: expert
maturity: stable
tools:
  - python
  - curl
dependencies:
  - python >= 3.9
---
# Incident Response and Triage

## Overview

A structured incident management framework for triaging, containing, investigating, and recovering from active security breaches and system compromises. Adhering to the NIST SP 800-61 and PICERL methodologies, this skill instructs AI agents on rapid threat containment without destroying volatile forensic evidence.

## When to Use

- Alert received indicating active unauthorized access, credential stuffing, or anomalous egress traffic.
- Suspicious web shell, reverse shell, or unauthorized root process detected on cloud workloads.
- Exposed database dump or customer credential breach reported publicly.
- Executing post-incident root cause forensics and drafting executive post-mortem reports.

## When NOT to Use

- Routine software bugs or benign application crashes (use `debugging-and-error-recovery`).
- Planned pre-commit secret linting (use `secret-leak-detection-and-remediation`).

## Inputs & Prerequisites

- Incident declaration: affected hostnames, IP addresses, service names, and initial alert timestamps.
- Read-only forensic access to system logs, cloud audit trails (CloudTrail, auditd), and network flow logs.
- Incident Commander (IC) assignment and established secure out-of-band communication channel (Signal, dedicated Slack).

## Core Workflow

### 1. Phase 1: Identification & Scoping (Within 15 Minutes)
Establish the blast radius and timeline:
- **Determine Incident Severity**: P1 (Critical customer data breach / active remote code execution) vs P2 (Isolated compromised dev credential).
- **Establish Scope**: List compromised hostnames, container IDs, user accounts, and leaked tokens.
- **Timeline Creation**: Record initial access timestamp, detection timestamp, and ongoing activities in an append-only timeline.

### 2. Phase 2: Containment (Preserving Volatile Evidence)
> NEVER immediately reboot, format, or delete an actively compromised server. Rebooting permanently destroys volatile memory (RAM), active network socket state, and running malware binaries.

Execute surgical containment:
1. **Network Isolation**: Quarantine the host using security groups or firewall rules to block internet egress while preserving connection to the forensic bastion:
   ```bash
   # Block all egress except forensic network
   iptables -A OUTPUT -d 10.0.0.0/8 -j ACCEPT
   iptables -A OUTPUT -j DROP
   ```
2. **Volatile Artifact Capture**: Dump running process tree and open network sockets before taking an EC2/disk snapshot:
   ```bash
   netstat -tlpn > /forensics/sockets.txt
   ps auxf > /forensics/processes.txt
   ```
3. **Session Termination**: Invalidate active sessions, revoke compromised IAM access keys, and force password resets for affected user accounts.

### 3. Phase 3: Eradication
Locate and neutralize all attacker persistence mechanisms:
- Scan for backdoor accounts added to `/etc/passwd` or `~/.ssh/authorized_keys`.
- Inspect scheduled cron jobs (`/etc/cron*`, `/var/spool/cron/*`) and systemd service units.
- Identify and remove unauthorized binaries, modified libraries, and web shells.

### 4. Phase 4: Recovery & Validation
- Rebuild compromised systems from known-good baseline immutable images (AMI / Docker image) rather than attempting to "clean" a tampered host.
- Re-deploy patched application code resolving the initial entry point vulnerability.
- Monitor host for 72 hours under heightened telemetry for signs of reinfection.

### 5. Phase 5: Post-Mortem & Lessons Learned
Author an blameless post-mortem report documenting:
- Root cause breakdown (e.g. unpatched dependency, leaked token).
- Mean Time to Detect (MTTD) and Mean Time to Remediate (MTTR).
- Action items with explicit owners and completion deadlines to prevent recurrence.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Attacker actively exfiltrating database | Sever database egress immediately regardless of forensic convenience; data protection takes priority over evidence preservation. |
| Suspected compromise of root credentials | Rotate cloud organization root credentials out-of-band; assume all internal systems may be observed. |
| Legal / Law Enforcement involvement | Maintain strict chain of custody hashes (SHA-256) on disk images and memory dumps. |

## Validation & Acceptance Criteria

- [ ] Compromised credentials fully revoked and rotated.
- [ ] Network containment verified; zero rogue outbound connections.
- [ ] Disk and memory forensics preserved with SHA-256 integrity hashes.
- [ ] Root cause definitively isolated and patched.
- [ ] Comprehensive incident timeline and post-mortem published.

## Failure Handling & Recovery

- If containment fails and attacker moves laterally, isolate the entire subnet and failover to a clean disaster recovery region.

## Expected Output & Artifacts

- Incident chronology and timeline document.
- Forensic artifact checklist and SHA-256 checksum register.
- Executive post-mortem report with corrective action items.

## Related Skills

- `secret-leak-detection-and-remediation`
- `zero-trust-network-architecture`
- `github-pr-security-review`
