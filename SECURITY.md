# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

Security is paramount for Agent Skills. Because skills provide operational workflows, scripts, and commands that AI coding agents execute on developer machines and in CI/CD pipelines, we strictly enforce defensive, non-harmful security standards across all skills.

If you discover a security vulnerability, an unsafe execution pattern, an unintended privilege escalation, or a prompt injection risk in any skill:

1. **Do not open a public issue.**
2. Send an email to `shivayachjaat@gmail.com` with:
   - The skill name and path
   - A description of the vulnerability or unsafe pattern
   - Steps to reproduce or proof-of-concept
   - Suggested remediation
3. You will receive an acknowledgment within 24 hours.

## Safety Standards for Skills

Every skill in AI Skills Booster adheres to these strict rules:
- **Defense-only**: No offensive attack payloads, exploit delivery, or credential theft patterns.
- **No hardcoded secrets**: No API keys, credentials, tokens, or personal identifiers.
- **Defensive execution**: Scripts must validate inputs, avoid arbitrary shell command injection, and gracefully fail on unexpected states.
- **Auditability**: Every command executed by a skill must be explicit, transparent, and non-destructive without explicit user confirmation.
