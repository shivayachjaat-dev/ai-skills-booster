---
name: webauthn-fido2-passkey-authentication
description: "Use this skill when designing, implementing, and securing passwordless authentication and multi-factor authentication (MFA) using WebAuthn, FIDO2, and Passkeys. It covers registration and authentication ceremony state machines, cryptographic challenge verification, public key credential storage, authenticator attestation, and signature counter verification."
domain: security
category: zero-trust
subcategory: mfa-webauthn
tags:
  - webauthn
  - fido2
  - passkeys
  - authentication
  - security
  - mfa
  - cryptography
technologies:
  - WebAuthn
  - FIDO2
  - SimpleWebAuthn
  - TypeScript
  - Python py_webauthn
complexity: advanced
maturity: stable
tools:
  - browser
  - python
  - npm
dependencies:
  - @simplewebauthn/server >= 9.0.0
  - @simplewebauthn/browser >= 9.0.0
---
# WebAuthn & FIDO2 Passkey Authentication Architecture

## Overview

A definitive production security reference for implementing phishing-resistant, passwordless authentication using WebAuthn and FIDO2 Passkeys. This skill instructs AI agents on managing registration and authentication ceremonies, generating and validating cryptographically random challenges, parsing and verifying client data JSON and authenticator data, storing public key credentials, and enforcing clone detection via signature counters.

## When to Use

- Implementing modern passwordless logins using biometric authenticators (TouchID, FaceID, Windows Hello, YubiKeys).
- Providing phishing-resistant Multi-Factor Authentication (MFA) to satisfy compliance (NIST SP 800-63B AAL3).
- Enabling synchronized Passkeys (Apple Keychain, Google Password Manager, 1Password) across user devices.
- Eliminating credential stuffing and database password breaches permanently.

## When NOT to Use

- Legacy CLI tools or embedded headless devices lacking browser WebAuthn API support (use SPIFFE or mutual TLS).
- Server-to-server machine authentication (use OAuth2 Client Credentials or mutual TLS).

## Inputs & Prerequisites

- Web application running on HTTPS or `localhost`.
- Relying Party (RP) configuration: RP ID (e.g. `example.com`), RP Name.
- User session store (Redis or database) to persist transient ceremony challenges.

## Core Workflow

### 1. Registration Ceremony (Passkey Creation)
Generate registration options on the server and verify the client's credential response:

```typescript
// server/registration.ts
import {
  generateRegistrationOptions,
  verifyRegistrationResponse,
} from '@simplewebauthn/server';

const rpName = 'Acme Corp';
const rpID = 'example.com';
const origin = `https://${rpID}`;

// Step 1: Generate Registration Options
export async function getRegistrationOptions(user: { id: string; email: string }) {
  const options = await generateRegistrationOptions({
    rpName,
    rpID,
    userID: user.id,
    userName: user.email,
    attestationType: 'none',
    authenticatorSelection: {
      residentKey: 'preferred',
      userVerification: 'preferred',
    },
  });

  // CRITICAL: Save options.challenge in user session with 2-minute TTL
  // await session.set("reg_challenge", options.challenge);
  return options;
}

// Step 2: Verify Registration Response
export async function completeRegistration(userSession: any, clientResponse: any) {
  const expectedChallenge = userSession.reg_challenge;

  const verification = await verifyRegistrationResponse({
    response: clientResponse,
    expectedChallenge,
    expectedOrigin: origin,
    expectedRPID: rpID,
    requireUserVerification: false,
  });

  if (!verification.verified || !verification.registrationInfo) {
    throw new Error('Registration verification failed');
  }

  const { credentialID, credentialPublicKey, counter } = verification.registrationInfo;

  // Persist passkey to database
  // await db.passkey.create({ credentialID, credentialPublicKey, counter, userId: userSession.userId });
  return { success: true };
}
```

### 2. Authentication Ceremony (Passkey Login)
Authenticate user without passwords:

```typescript
// server/authentication.ts
import {
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} from '@simplewebauthn/server';

export async function getAuthOptions() {
  const options = await generateAuthenticationOptions({
    rpID: 'example.com',
    userVerification: 'preferred',
  });
  // Save options.challenge in session
  return options;
}

export async function completeAuthentication(userPasskey: any, expectedChallenge: string, response: any) {
  const verification = await verifyAuthenticationResponse({
    response,
    expectedChallenge,
    expectedOrigin: 'https://example.com',
    expectedRPID: 'example.com',
    authenticator: {
      credentialID: userPasskey.credentialID,
      credentialPublicKey: userPasskey.credentialPublicKey,
      counter: userPasskey.counter,
    },
  });

  if (!verification.verified) {
    throw new Error('Authentication failed');
  }

  // Update signature counter in DB to detect cloned authenticators
  // await db.passkey.updateCounter(userPasskey.id, verification.authenticationInfo.newCounter);
  return { success: true };
}
```

## Best Practices & Failure Modes

1. **Origin & RP ID Mismatches**: `rpID` must be the effective domain or a registrable suffix of the origin (e.g. `rpID: "example.com"` is valid for `https://app.example.com`, but `rpID: "other.com"` will be rejected by the browser).
2. **Replay Attacks via Static Challenges**: Challenges must be cryptographically random and strictly single-use. Delete the challenge from session storage immediately upon first verification attempt.
3. **Counter Rollback (Cloned Authenticator)**: If the incoming signature counter is less than or equal to the stored counter (for hardware security keys), the key may have been duplicated or cloned. Log an immediate security alert and flag the session. Note that multi-device synced passkeys may report counter = 0.

## Verification & Testing

- Test browser registration ceremony:
  ```typescript
  import { startRegistration } from '@simplewebauthn/browser';
  const options = await fetch('/api/auth/register-options').then(r => r.json());
  const regResponse = await startRegistration(options);
  await fetch('/api/auth/register-complete', { method: 'POST', body: JSON.stringify(regResponse) });
  ```
- Verify authentication ceremony in browser:
  ```typescript
  import { startAuthentication } from '@simplewebauthn/browser';
  const options = await fetch('/api/auth/login-options').then(r => r.json());
  const authResponse = await startAuthentication(options);
  await fetch('/api/auth/login-complete', { method: 'POST', body: JSON.stringify(authResponse) });
  ```
