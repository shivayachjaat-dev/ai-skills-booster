---
name: http-security-headers-hardening
description: "Use this skill when auditing, configuring, and hardening HTTP security headers for web applications and APIs. It guides the agent through Content-Security-Policy (CSP) with dynamic cryptographic nonces, Strict-Transport-Security (HSTS), X-Content-Type-Options, Permissions-Policy, Referrer-Policy, and Cross-Origin Resource isolation headers (COOP, COEP, CORP)."
domain: security
category: application-security
subcategory: security-headers
tags:
  - security-headers
  - csp
  - hsts
  - web-security
  - owasp
  - infosec
  - http
technologies:
  - HTTP
  - FastAPI
  - Express.js
  - NGINX
  - OWASP Secure Headers Project
complexity: intermediate
maturity: stable
tools:
  - curl
  - python
dependencies:
  - python >= 3.10
---
# HTTP Security Headers & Content Security Policy (CSP) Hardening

## Overview

A definitive security engineering reference for eliminating browser-based attacks through hardened HTTP response headers. Misconfigured or missing headers expose web applications to Cross-Site Scripting (XSS), clickjacking, MIME sniffing, SSL stripping, and cross-origin data theft. This skill instructs AI agents on implementing a strict Content-Security-Policy (CSP) using cryptographic nonces, enforcing HSTS with preloading, configuring granular Permissions-Policy, and isolating origins via COOP, COEP, and CORP.

## When to Use

- Hardening public web applications and APIs before production deployment.
- Satisfying OWASP ASVS (Application Security Verification Standard) Level 2 & 3 header requirements.
- Preventing DOM-based and stored XSS execution via strict script source whitelisting.
- Securing modern browser features (SharedArrayBuffer, WebAssembly threads) via Cross-Origin Isolation.

## When NOT to Use

- Pure machine-to-machine internal backend APIs where response bodies are consumed exclusively by non-browser HTTP clients (though adding security headers is harmless).

## Inputs & Prerequisites

- Web server (NGINX, Caddy) or backend application framework (FastAPI, Express, Next.js).
- Inventory of required external CDN resources (fonts, analytics, payment iframes).

## Core Workflow

### 1. Production Security Middleware (FastAPI / Starlette)
Generate per-request cryptographic nonces and set defense-in-depth headers:

```python
import secrets
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Generate unique 128-bit cryptographically secure nonce for this request
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        response: Response = await call_next(request)

        # 2. Strict Content Security Policy (CSP) with Nonce
        csp_directives = [
            "default-src 'self'",
            f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'",
            "style-src 'self' 'unsafe-inline'", # unsafe-inline for styles is often necessary for CSS-in-JS
            "img-src 'self' data: https:",
            "font-src 'self' https://fonts.gstatic.com",
            "frame-src 'self' https://js.stripe.com",
            "connect-src 'self' https://api.stripe.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'", # Prevents clickjacking (replaces X-Frame-Options)
            "upgrade-insecure-requests"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 3. HTTP Strict Transport Security (HSTS): 2 years + subdomains + preload
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"

        # 4. Prevent MIME Sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 5. Referrer Policy: Send full URL only to same origin; origin only to HTTPS
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Granular Device Permissions Policy
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(self 'https://js.stripe.com')"

        # 7. Cross-Origin Isolation (COOP & COEP)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        return response
```

### 2. NGINX Hardened Headers Configuration
Enforce security headers directly at reverse proxy gateway:

```nginx
# /etc/nginx/conf.d/security_headers.conf
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header X-Frame-Options "DENY" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

## Best Practices & Failure Modes

1. **The `'unsafe-inline'` Script Trap**: Adding `'unsafe-inline'` to `script-src` without `'nonce-...'` completely defeats CSP, allowing injected `<script>` tags to execute freely. Use cryptographic nonces with `'strict-dynamic'`.
2. **Missing `includeSubDomains` on HSTS**: Without `includeSubDomains`, attackers can spoof insecure HTTP subdomains (`http://staging.example.com`) and hijack cookies via man-in-the-middle attacks.
3. **Breaking Third-Party Embeds**: Enabling strict `Cross-Origin-Embedder-Policy: require-corp` blocks external images or iframes that lack `Cross-Origin-Resource-Policy` headers. Audit external assets before enabling COEP.

## Verification & Testing

- Inspect response headers using curl:
  ```bash
  curl -I https://app.example.com
  ```
- Test headers against Mozilla Observatory security scanner:
  ```bash
  curl -s -X POST https://http-observatory.security.mozilla.org/api/v1/analyze?host=app.example.com
  ```
