---
name: cors-csrf-web-security-hardening
description: "Use this skill when designing, implementing, and auditing Cross-Origin Resource Sharing (CORS) and Cross-Site Request Forgery (CSRF) defenses for web APIs and single-page applications. It guides the agent through strict origin allowlists, preflight OPTION request caching, SameSite cookie strategies, double-submit cookie patterns, and Sec-Fetch-* metadata header verification."
domain: security
category: application-security
subcategory: cors-csrf
tags:
  - security
  - cors
  - csrf
  - web-security
  - cookies
  - headers
  - owasp
technologies:
  - HTTP
  - FastAPI
  - Express.js
  - Django
  - OWASP
complexity: intermediate
maturity: stable
tools:
  - curl
  - python
dependencies:
  - python >= 3.10
---
# CORS & CSRF Web Security Hardening

## Overview

A definitive security engineering reference for eliminating Cross-Origin Resource Sharing (CORS) misconfigurations and Cross-Site Request Forgery (CSRF) vulnerabilities. This skill provides concrete middleware configurations, cookie flag hardening (`SameSite=Strict/Lax`, `Secure`, `HttpOnly`), anti-CSRF token verification, and defense-in-depth origin inspection using modern `Sec-Fetch-*` headers.

## When to Use

- Exposing secure REST/GraphQL APIs consumed by browser-based Single Page Applications (SPAs).
- Resolving CORS errors (`No 'Access-Control-Allow-Origin' header is present`) securely without wildcarding `*`.
- Protecting authenticated state-changing endpoints (e.g. `/api/transfer-funds`, `/api/update-password`) from CSRF attacks.
- Setting up cross-domain session cookies across micro-frontends or multi-domain architectures.

## When NOT to Use

- Pure machine-to-machine APIs (m2m) authenticated exclusively via Bearer tokens in `Authorization` headers with no cookies, where browsers never send ambient credentials automatically.
- Internal RPC services communicating over private VPC networks.

## Inputs & Prerequisites

- Web server framework (FastAPI, Express, Flask, Go Gin, or Next.js).
- Clear inventory of trusted origins (e.g., `https://app.example.com`, `https://admin.example.com`).

## Core Workflow

### 1. Hardened CORS Configuration in FastAPI
Never reflect the incoming `Origin` header dynamically or use `allow_origins=["*"]` with `allow_credentials=True`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Explicitly declare allowed origins (No wildcards in production)
ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True, # Allows credentials (cookies, authorization headers)
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Requested-With",
    ],
    expose_headers=["Content-Length", "X-Request-ID"],
    max_age=86400, # Cache preflight OPTIONS responses for 24 hours
)
```

### 2. Double-Submit Cookie Anti-CSRF Pattern
For cookie-authenticated web apps, implement the cryptographically verified double-submit cookie pattern:

```python
import hmac
import hashlib
import secrets
from fastapi import Request, HTTPException, status, Response

CSRF_SECRET_KEY = b"your-super-secret-hmac-key-32bytes"

def generate_csrf_token(session_id: str) -> str:
    random_entropy = secrets.token_hex(16)
    signature = hmac.new(
        CSRF_SECRET_KEY,
        f"{session_id}:{random_entropy}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{random_entropy}.{signature}"

def verify_csrf_token(session_id: str, token: str) -> bool:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return False
        random_entropy, signature = parts
        expected = hmac.new(
            CSRF_SECRET_KEY,
            f"{session_id}:{random_entropy}".encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False

async def csrf_protect_middleware(request: Request, call_next):
    # Safe methods do not mutate state
    if request.method in ("GET", "HEAD", "OPTIONS", "TRACE"):
        return await call_next(request)

    # State-changing method (POST, PUT, DELETE, PATCH)
    session_id = request.cookies.get("session_id")
    if not session_id:
        # If no session cookie exists, request cannot exploit ambient credentials
        return await call_next(request)

    # Extract token from custom header
    submitted_token = request.headers.get("X-CSRF-Token")
    if not submitted_token or not verify_csrf_token(session_id, submitted_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF validation failed: Invalid or missing token."
        )

    return await call_next(request)
```

### 3. Cookie Security Attributes
Set cookies with maximum browser isolation:

```python
def set_auth_cookies(response: Response, session_id: str, csrf_token: str):
    # Session cookie: HttpOnly, Strict, Secure
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,          # Only sent over HTTPS
        samesite="Strict",    # Not sent on cross-site navigations
        max_age=3600 * 8,     # 8 hours
        path="/"
    )
    
    # CSRF cookie: Accessible by JavaScript to read and set in X-CSRF-Token header
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,       # Frontend JavaScript must read this
        secure=True,
        samesite="Strict",
        max_age=3600 * 8,
        path="/"
    )
```

### 4. Defense-in-Depth: Sec-Fetch Metadata Inspection
Inspect browser-provided metadata headers that cannot be forged by client scripts:

```python
def verify_sec_fetch_headers(request: Request):
    sec_fetch_site = request.headers.get("sec-fetch-site") # same-origin, same-site, cross-site, none
    sec_fetch_mode = request.headers.get("sec-fetch-mode") # cors, navigate, no-cors
    
    # Block state-changing cross-site requests
    if request.method in ("POST", "PUT", "DELETE", "PATCH"):
        if sec_fetch_site == "cross-site":
            raise HTTPException(status_code=403, detail="Cross-site mutation rejected by Sec-Fetch policy.")
```

## Best Practices & Failure Modes

1. **The `null` Origin Vulnerability**: Sandboxed `<iframe>` tags or local HTML files send `Origin: null`. Never configure `Access-Control-Allow-Origin: null`.
2. **Subdomain Wildcard Exploits**: Using regex like `r".*\.example\.com"` matches `malicious-example.com` or attacker domains if the dot is unescaped. Always parse and match exact hostnames.
3. **SameSite=Lax Top-Level Navigation**: `SameSite=Lax` sends cookies on top-level GET requests initiated from external sites. If state-changing operations are mapped to GET endpoints (e.g. `/api/delete?id=123`), CSRF is still possible. State changes must strictly require POST/PUT/DELETE.

## Verification & Testing

- Test preflight CORS OPTIONS request:
  ```bash
  curl -i -X OPTIONS https://api.example.com/api/orders     -H "Origin: https://app.example.com"     -H "Access-Control-Request-Method: POST"     -H "Access-Control-Request-Headers: Authorization,X-CSRF-Token"
  ```
  Verify `Access-Control-Allow-Origin: https://app.example.com` is returned.
- Test untrusted origin rejection:
  ```bash
  curl -i -X OPTIONS https://api.example.com/api/orders     -H "Origin: https://evil-attacker.com"     -H "Access-Control-Request-Method: POST"
  ```
  Verify no `Access-Control-Allow-Origin` header is returned.
