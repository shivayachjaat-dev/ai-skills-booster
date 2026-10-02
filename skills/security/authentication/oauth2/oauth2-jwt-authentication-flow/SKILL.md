---
name: oauth2-jwt-authentication-flow
description: "Use this skill when designing, implementing, and securing OAuth 2.1 and OpenID Connect (OIDC) authentication flows with JSON Web Tokens (JWT). It enforces Authorization Code Flow with PKCE, asymmetric RS256 signature verification, refresh token rotation with reuse detection, claims validation, and centralized revocation blacklists."
domain: security
category: authentication
subcategory: oauth2
tags:
  - security
  - authentication
  - oauth2
  - jwt
  - oidc
  - auth
  - tokens
technologies:
  - OAuth 2.1
  - JWT
  - Node.js
  - Python
  - Redis
  - TypeScript
complexity: advanced
maturity: stable
tools:
  - python
  - node
  - curl
dependencies:
  - jsonwebtoken or pyjwt
  - cryptography
---
# OAuth2 and JWT Authentication Flow

## Overview

A defense-in-depth architectural standard for implementing modern, standards-compliant authentication and authorization using OAuth 2.1 and JSON Web Tokens (JWT). Eliminates common authentication vulnerabilities including CSRF token leakage, refresh token hijacking, signature bypass (alg: none), and privilege escalation.

## When to Use

- Implementing user login, signup, and session management for Single Page Applications (SPAs) or mobile apps.
- Securing backend microservice-to-microservice APIs using bearer token validation.
- Transitioning legacy session cookies to stateless JWT access tokens with stateful refresh tokens.
- Reviewing authentication middleware for security vulnerabilities prior to release.

## When NOT to Use

- Simple internal command-line tools requiring only a static secret API key.
- Monolithic web apps with server-rendered HTML where standard `HttpOnly`, `SameSite=Strict` cookies suffice without JWTs.

## Inputs & Prerequisites

- Identity Provider (IdP) service or internal authentication service.
- Asymmetric keypair (RSA 2048+ bit or ECDSA P-256) for token signing and public verification keys (`jwks.json`).
- Redis or distributed database for refresh token family tracking and revocation blacklists.

## Core Workflow

### 1. Flow Selection: Authorization Code Flow with PKCE
Never use the deprecated OAuth Implicit Flow or Resource Owner Password Credentials Flow:
- **SPAs and Mobile Apps**: Always use **Authorization Code Flow with PKCE (Proof Key for Code Exchange)**.
- Client generates high-entropy `code_verifier` and computes `code_challenge = base64url(sha256(code_verifier))`.
- Authorization server issues auth code, then trades code + `code_verifier` for tokens on back-channel.

### 2. Dual-Token Architecture
Separate ephemeral access credentials from persistent session renewal:
- **Access Token (JWT)**: Short-lived (5 to 15 minutes). Statelessly validated by resource servers using the public key.
- **Refresh Token (Opaque String)**: Longer-lived (7 to 30 days). Stored securely (in `HttpOnly`, `Secure`, `SameSite=Strict` cookies or OS keychain).

### 3. Refresh Token Rotation with Automatic Reuse Detection
To mitigate token theft, rotate the refresh token on every single refresh request:
1. When client exchanges `Refresh_Token_A`, issue a new `Access_Token_2` and a new `Refresh_Token_B`.
2. Invalidate `Refresh_Token_A`.
3. **Reuse Detection**: If `Refresh_Token_A` is ever presented again (indicating it was stolen and used by an attacker):
   - Immediately revoke the **entire token family** (all sessions for that user).
   - Force re-authentication and log an alert for anomalous session hijacking.

### 4. Asymmetric JWT Validation Invariants
Resource servers must validate tokens against these strict rules:
```typescript
import jwt from "jsonwebtoken";

export function verifyAccessToken(token: string, publicKeyPem: string) {
  return jwt.verify(token, publicKeyPem, {
    algorithms: ["RS256"],         // Disallow 'none' or symmetric 'HS256'
    issuer: "https://auth.company.com", // Verify iss
    audience: "https://api.company.com", // Verify aud
    clockTolerance: 10             // 10s leeway for clock skew
  });
}
```
- Reject any token specifying `alg: "none"`.
- Reject token if `exp` (expiration time) is in the past.
- Verify `nbf` (not before) and `iat` (issued at).

### 5. Instant Revocation via Distributed Blacklist
Stateless JWTs cannot be easily revoked before expiration. To handle immediate user bans, password changes, or logout:
- Maintain a Redis bloom filter or key-value store of revoked `jti` (JWT ID) claims:
  `SET blacklist:jti:<uuid> 1 EX <remaining_token_lifetime_seconds>`.
- In authentication middleware, check if `token.jti` exists in the blacklist before granting access.

## Decision Points & Edge Cases

| Scenario | Decision / Action |
|---|---|
| Frontend client is browser SPA | Store refresh token in `HttpOnly`, `Secure`, `SameSite=Strict` cookie. Store access token strictly in application memory (never `localStorage` due to XSS theft). |
| Clock drift across distributed servers | Configure standard 10 to 30-second clock tolerance in JWT verification options. |
| Key rotation on Identity Provider | Expose JWKS endpoint (`/.well-known/jwks.json`) with `kid` (Key ID) headers, caching public keys with TTL. |

## Validation & Acceptance Criteria

- [ ] PKCE challenge and verifier required on all client code exchanges.
- [ ] Access token lifespan does not exceed 15 minutes.
- [ ] JWT verification enforces RS256 algorithm, valid issuer, and audience.
- [ ] Refresh token rotation invalidates old tokens immediately.
- [ ] Reuse of spent refresh tokens revokes all sessions in the token family.

## Failure Handling & Recovery

- If Redis blacklist fails or is unreachable, default to fail-secure for high-risk operations (require fresh re-authentication).

## Expected Output & Artifacts

- OAuth 2.1 token exchange middleware.
- JWT verification helper module with JWKS support.
- Unit tests verifying token expiration and algorithm downgrade rejection.

## Related Skills

- `api-and-interface-design`
- `secret-leak-detection-and-remediation`
- `fastapi-async-api-design`
