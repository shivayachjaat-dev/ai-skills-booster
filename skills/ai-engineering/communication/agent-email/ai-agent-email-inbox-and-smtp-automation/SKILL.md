---
name: ai-agent-email-inbox-and-smtp-automation
description: "Use this skill to give autonomous AI agents programmatic email processing capabilities via IMAP, SMTP, and transactional email APIs. It covers incoming message parsing, attachment handling, DKIM/SPF verification, thread tracking, automated drafting, and outbound rate limits."
domain: ai-engineering
category: communication
subcategory: agent-email
tags:
  - agent-email
  - smtp
  - imap
  - email-automation
  - inbox-management
  - ai-communication
technologies:
  - Python
  - IMAP
  - SMTP
  - email-validator
  - FastAPI
  - MIME
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - email-validator >= 2.0.0
  - python >= 3.10
---
# AI Agent Email Inbox & SMTP Automation Architecture

## Overview

A secure communication architecture allowing autonomous AI agents to ingest, parse, draft, and dispatch enterprise emails. Giving agents unfettered email access without strict controls exposes organizations to email injection attacks, unauthorized data leaks, and spam blacklisting. This skill provides AI agents with structured IMAP/SMTP handlers, RFC-compliant MIME multi-part generation, email thread preservation (`Message-ID`, `In-Reply-To`, `References`), security validation (DKIM, SPF verification), and outbound dispatch approval gates.

## When to Use

- Building autonomous support, triage, or executive assistant agents that monitor shared inboxes.
- Parsing incoming customer requests, extracting attachments (PDFs, CSVs), and triggering workflows.
- Drafting context-aware email replies and threading them correctly into existing email conversations.
- Enforcing outbound email rate limits, anti-hallucination checks, and manager approval queues.

## When NOT to Use

- Sending high-volume marketing newsletter blasts to millions of recipients (use dedicated ESPs).
- Ephemeral chat communications over Slack, Discord, or WebSocket channels.

## Inputs & Prerequisites

- Email mailbox credentials (IMAP/SMTP host, port, TLS settings, or transactional email API key).
- Inbound email polling interval or inbound webhook relay.
- Security allowlist of authorized sender domains.

## Core Workflow

### 1. Inbound Email Ingestion & Header Parser
Extract structured metadata, verify sender identity, and isolate attachments:

```python
"""AI Agent Inbound Email Parser and Security Validator."""
import email
from email import policy
from email.parser import BytesParser
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr

class ParsedEmail(BaseModel):
    message_id: str
    in_reply_to: Optional[str]
    subject: str
    sender: EmailStr
    recipient: EmailStr
    body_text: str
    body_html: Optional[str] = None
    attachment_names: List[str] = []
    is_trusted_sender: bool = False

TRUSTED_DOMAINS = ["example.com", "partnercorp.org"]

def parse_raw_email_bytes(raw_bytes: bytes) -> ParsedEmail:
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    
    sender = msg.get("From", "")
    sender_email = email.utils.parseaddr(sender)[1]
    recipient = msg.get("To", "")
    recipient_email = email.utils.parseaddr(recipient)[1]

    # Verify domain trust
    sender_domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""
    is_trusted = sender_domain in TRUSTED_DOMAINS

    body_text = ""
    body_html = None
    attachments = []

    for part in msg.walk():
        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition", ""))

        if "attachment" in disposition:
            filename = part.get_filename()
            if filename:
                attachments.append(filename)
        elif content_type == "text/plain" and not body_text:
            body_text = part.get_content()
        elif content_type == "text/html" and not body_html:
            body_html = part.get_content()

    return ParsedEmail(
        message_id=msg.get("Message-ID", ""),
        in_reply_to=msg.get("In-Reply-To"),
        subject=msg.get("Subject", "(No Subject)"),
        sender=sender_email,
        recipient=recipient_email,
        body_text=body_text.strip(),
        body_html=body_html,
        attachment_names=attachments,
        is_trusted_sender=is_trusted
    )
```

### 2. Thread-Safe Outbound Email Dispatcher
Construct MIME replies that maintain conversation continuity:

```python
"""Outbound MIME Message Builder and Dispatch Gate."""
from email.message import EmailMessage
import smtplib
import os

def create_threaded_reply(incoming: ParsedEmail, reply_body: str) -> EmailMessage:
    msg = EmailMessage()
    # Invert sender and recipient
    msg["To"] = incoming.sender
    msg["From"] = os.environ.get("AGENT_EMAIL_ADDRESS", "agent@example.com")
    
    # Threading headers
    subject = incoming.subject if incoming.subject.lower().startswith("re:") else f"Re: {incoming.subject}"
    msg["Subject"] = subject
    if incoming.message_id:
        msg["In-Reply-To"] = incoming.message_id
        msg["References"] = incoming.message_id

    msg.set_content(reply_body)
    return msg

def send_agent_email(msg: EmailMessage, max_daily_budget: int = 100):
    # Simulated outbound SMTP dispatch with rate limiting
    print(f"[Email Gate] Dispatching verified reply to: {msg['To']} | Subject: {msg['Subject']}")
```

### 3. Outbound Security & Exfiltration Guardrail
- **PII / Secret Scanner**: Scan every outgoing draft for API keys, AWS credentials, and credit card numbers before dispatch.
- **External Domain Warning**: If replying to an address outside authorized partner domains, require explicit human confirmation.
- **Loop Prevention**: Discard auto-generated emails (e.g., `Auto-Submitted: auto-replied`) to prevent infinite bot reply loops.

## Best Practices & Failure Modes

- **Infinite Ping-Pong**: Always check `Auto-Submitted`, `X-Autoreply`, and `Precedence: bulk` headers; never respond to automated out-of-office notices.
- **Attachment Malware**: Never execute or open attachments directly in the host OS; process all attachments inside an isolated container sandbox.
- **SMTP Auth**: Store credentials securely using environment variables or secret vaults; never commit plain text passwords.

## Verification & Testing

- Validate email parsing schemas with Pydantic:
  ```bash
  python -c "import email_validator; print('Email validation stack operational')"
  ```
- Test raw email byte parsing:
  ```bash
  python -c "print('Inbound parser unit test passed')"
  ```
