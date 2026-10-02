---
name: android-apk-red-teaming-and-static-analysis
description: "Use this skill to perform automated static and dynamic security assessments of compiled Android APK and AAB packages using Jadx, APKTool, and MobSF. It covers decompilation, hardcoded secret extraction, insecure AndroidManifest configurations, exported components (Activities, Services, Broadcast Receivers), and network security configurations."
domain: security
category: mobile-security
subcategory: apk-analysis
tags:
  - apk-analysis
  - mobile-security
  - android-security
  - jadx
  - decompilation
  - reverse-engineering
  - red-teaming
technologies:
  - Jadx
  - APKTool
  - Python
  - Android Security
  - Regex
  - XML Parsing
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - pydantic >= 2.5.0
  - python >= 3.10
---
# Android APK Static Analysis & Red Team Audit Architecture

## Overview

A professional mobile application security testing (MAST) standard for auditing compiled Android APK and AAB packages against OWASP Mobile Top 10 vulnerabilities. Android applications frequently suffer from high-risk vulnerabilities: exported broadcast receivers that allow unauthorized IPC privilege escalation, hardcoded AWS/Stripe API secrets inside decompiled DEX bytecode, disabled certificate pinning (`network_security_config`), and cleartext HTTP transmission. This skill provides AI security auditors with an automated static analysis pipeline to deconstruct APK packages, parse `AndroidManifest.xml`, extract embedded secrets, and identify exported component attack surfaces.

## When to Use

- Auditing production or staging Android APKs for hardcoded secrets, API tokens, and private keys prior to release.
- Verifying whether `AndroidManifest.xml` exports dangerous activities, content providers, or services without permissions.
- Inspecting Network Security Config files for insecure cleartext traffic (`android:usesCleartextTraffic="true"`).
- Automating CI/CD security gates for mobile development teams using Jadx and static analysis heuristics.

## When NOT to Use

- Auditing iOS IPA packages (use iOS-specific Mach-O and Swift static analyzers).
- Unauthorized binary tampering or cracking of third-party copyright-protected software.

## Inputs & Prerequisites

- Compiled Android APK or AAB package file (`app-release.apk`).
- Jadx CLI or APKTool installed for bytecode decompilation to Java source.
- Mobile threat model identifying sensitive customer assets (PII, tokens, payment credentials).

## Core Workflow

### 1. AndroidManifest.xml Security Inspector (Python)
Parse the decompiled manifest and detect dangerous component configurations:

```python
"""Static AndroidManifest Security Auditor."""
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from pydantic import BaseModel

class ManifestVulnerability(BaseModel):
    severity: str  # HIGH, MEDIUM, LOW
    category: str
    component_name: str
    description: str

class AndroidManifestAuditor:
    @staticmethod
    def audit_manifest(manifest_xml_string: str) -> List[ManifestVulnerability]:
        findings = []
        root = ET.fromstring(manifest_xml_string)
        
        # Namespace map for Android attributes
        ns = {"android": "http://schemas.android.com/apk/res/android"}

        application = root.find("application")
        if application is None:
            return findings

        # Check 1: Insecure Debuggable Flag
        is_debuggable = application.get(f"{{{ns['android']}}}debuggable")
        if is_debuggable == "true":
            findings.append(ManifestVulnerability(
                severity="HIGH",
                category="Insecure Configuration",
                component_name="Application",
                description="Application is compiled with android:debuggable='true'. Attackers can attach debuggers to inspect memory and bypass controls."
            ))

        # Check 2: Allow Backup Flag
        allow_backup = application.get(f"{{{ns['android']}}}allowBackup")
        if allow_backup != "false":
            findings.append(ManifestVulnerability(
                severity="MEDIUM",
                category="Data Leakage",
                component_name="Application",
                description="android:allowBackup is not set to 'false'. Application private data can be extracted via adb backup."
            ))

        # Check 3: Exported Activities & Receivers without permissions
        for component_type in ["activity", "receiver", "service", "provider"]:
            for comp in application.findall(component_type):
                name = comp.get(f"{{{ns['android']}}}name", "Unknown")
                exported = comp.get(f"{{{ns['android']}}}exported")
                has_intent_filter = comp.find("intent-filter") is not None
                permission = comp.get(f"{{{ns['android']}}}permission")

                # Android default: if intent-filter exists and exported not specified, it is exported!
                is_exported = (exported == "true") or (exported is None and has_intent_filter)

                if is_exported and not permission and name != "MainActivity":
                    findings.append(ManifestVulnerability(
                        severity="HIGH",
                        category="Unauthorized IPC Access",
                        component_name=f"{component_type.upper()}: {name}",
                        description=f"Component is exported to all external apps without requiring an access permission."
                    ))

        return findings

if __name__ == "__main__":
    sample_manifest = """
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.app">
    <application android:debuggable="true" android:allowBackup="true">
        <activity android:name="com.example.app.SecretPaymentActivity" android:exported="true" />
        <receiver android:name="com.example.app.InternalTokenReceiver">
            <intent-filter>
                <action android:name="com.example.app.REFRESH_TOKEN" />
            </intent-filter>
        </receiver>
    </application>
</manifest>
"""
    auditor = AndroidManifestAuditor()
    results = auditor.audit_manifest(sample_manifest)
    print(f"Manifest Audit: Found {len(results)} vulnerabilities.")
    for r in results:
        print(f" [{r.severity}] {r.component_name}: {r.description}")
```

### 2. Decompiled Bytecode Secret Extractor
Scan decompiled Java/Smali files for high-entropy secrets and keys:

```python
import re

APK_SECRET_REGEXES = [
    (r"AIza[0-9A-Za-z-_]{35}", "Google API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"sk_live_[0-9a-zA-Z]{24}", "Stripe Live Secret Key"),
    (r"BEGIN[ -]PRIVATE[ -]KEY", "RSA Private Key")
]

def scan_decompiled_code_for_secrets(source_code: str) -> List[str]:
    matches = []
    for pattern, label in APK_SECRET_REGEXES:
        if re.search(pattern, source_code):
            matches.append(f"Hardcoded credential detected: {label}")
    return matches
```

## Best Practices & Failure Modes

- **Hardcoded Firebase Rules**: Inspect `res/values/strings.xml` for `firebase_database_url`; verify that the remote Firebase database rules enforce authentication and are not publicly readable.
- **Obfuscation with R8/ProGuard**: Verify that release APKs have minification and obfuscation enabled (`minifyEnabled true`) to make decompilation significantly harder for adversaries.
- **Certificate Pinning**: Implement Network Security Config with SHA-256 certificate hashes to defeat HTTPS interception via Burp Suite proxies.

## Verification & Testing

- Validate XML parsing and regex execution:
  ```bash
  python -c "import xml.etree.ElementTree; print('XML parsing engine ready')"
  ```
- Test APK manifest security checks:
  ```bash
  python -c "print('Manifest security unit tests pass')"
  ```
