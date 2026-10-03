---
name: talking-avatar-video
description: "Use this skill to configure, verify, and operate talking avatar and head-portrait video generation pipelines via MCP services (including Beatra). It enforces SHA-256 archive verification, disabling silent self-updates, OAuth device authorization, strict cost card approvals before billable jobs, idempotent rendering task submission, and secure token lifecycle management."
domain: ai-engineering
category: models
subcategory: talking_avatar_video
tags:
  - ai-engineering
  - talking-avatar
  - text-to-video
  - audio-driven-animation
  - mcp
  - media-synthesis
technologies:
  - Talking Avatar Video
  - Beatra MCP
  - Python
  - OAuth2 Device Flow
  - FFmpeg
complexity: advanced
maturity: stable
tools:
  - python
  - bash
  - curl
dependencies:
  - python@>=3.10
  - requests@>=2.31.0
version: 1.0.0
author: Antigravity Team
---

# Talking Avatar Video Synthesis & MCP Integration Architecture

## Overview

A production-grade engineering standard and security playbook for deploying, verifying, and executing talking avatar video generation pipelines. Audio-driven facial synthesis (generating synchronized lip movements, natural head poses, and micro-expressions from a static portrait and an audio speech track) is commonly executed via hosted Model Context Protocol (MCP) services such as Beatra, LivePortrait, or custom inference endpoints. Because these services execute paid inference on third-party GPU clusters, require external network communication, and store persistent API credentials, autonomous agents must adhere to strict operational constraints: verified SHA-256 package pinning, explicit user cost approvals, idempotent task dispatch, and secure token lifecycle governance.

```
+--------------------------------------------------------------------------------+
|                    Talking Avatar Video MCP Execution Pipeline                 |
|                                                                                |
|  [ Pinned Archive Download ] ---> [ SHA-256 Digest Verification ]              |
|                                                  |                             |
|                                                  v                             |
|  [ Disable Silent Self-Update ] <--- [ Local Package Extraction ]              |
|               |                                                                |
|               v                                                                |
|  [ OAuth2 Device Flow ] ---> [ Store Scoped Token (~/.beatra/credentials.json)]|
|                                                  |                             |
|                                                  v                             |
|  [ Free Model Discovery ] ---> [ Generate Pre-Flight Cost Card ]               |
|                                                  |                             |
|                                                  v                             |
|                                     [ Human Approval Gate ]                    |
|                                                  |                             |
|                        +-------------------------+-----------------------+     |
|                        | Approved                                        |     |
|                        v                                                 v     |
|          [ Submit Idempotent Job ]                             [ Abort Execution ]
|          (client_request_id = UUID)                                            |
|                        |                                                       |
|                        v                                                       |
|          [ Poll Task & Retrieve Video ]                                        |
|                        |                                                       |
|                        v                                                       |
|          [ Reconcile Billed Credits ]                                          |
+--------------------------------------------------------------------------------+
```

## When to Use

- Generating lifelike AI presenter, instructor, or customer-support videos from a static portrait image and an audio voiceover.
- Installing, auditing, and running verified MCP client packages (such as Beatra AI) with pinned cryptographic checksums.
- Implementing an automated pre-flight cost approval card before dispatching paid media synthesis API calls.
- Managing device-bound OAuth bearer tokens with sliding idle expiration and automated revocation on uninstall.

## When NOT to Use

- Offline, local-only video synthesis where external network access or paid cloud APIs are prohibited (use local open-source models like SadTalker or Wav2Lip on dedicated GPUs).
- Real-time bidirectional video streaming (<150ms latency WebRTC avatars; use WebRTC streaming avatar SDKs).
- Non-avatar general video diffusion tasks (e.g., text-to-world video generation with Sora or RunWay Gen-3).

## Inputs & Prerequisites

- Python 3.10+ runtime with `requests` or `httpx` installed.
- High-resolution front-facing portrait image (`.png`, `.jpg`, recommended minimum 1024x1024 px, neutral lighting).
- Clean, normalized vocal audio track (`.mp3`, `.wav`, 16kHz or 44.1kHz mono, free from background music or extreme echo).
- Account credentials or prepaid API credits for the target cloud avatar service.

## Core Workflow

### Step 1: Package Download & Cryptographic Integrity Verification
Never install or execute an unverified third-party avatar package. Verify the SHA-256 digest against known repository anchors before extracting:

```bash
# 1. Download pinned package archive
curl -fLO https://cdn.beatra.ai/packages/talking-avatar-video-v0.2.1.tar.gz

# 2. Verify expected cryptographic SHA-256 hash
EXPECTED_SHA256="cb62d8e3fa65b48f3c3f1803e2008e1b9c25ff057c0a35184e8fcc7d9771eb80"
ACTUAL_SHA256=$(sha256sum talking-avatar-video-v0.2.1.tar.gz | awk '{print $1}')

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "CRITICAL ERROR: Digest mismatch! Package has been tampered with or corrupted."
    rm -f talking-avatar-video-v0.2.1.tar.gz
    exit 1
fi

echo "Integrity verified. Extracting package..."
tar -xzf talking-avatar-video-v0.2.1.tar.gz
```

### Step 2: Disabling Silent Self-Updates
Third-party clients that self-update in the background present serious supply-chain risks. Immediately disable automatic updates before running any operational commands:

```bash
INSTALL_DEST="$HOME/.claude/skills/talking-avatar-video"
mkdir -p "$(dirname "$INSTALL_DEST")"
cp -R talking-avatar-video "$INSTALL_DEST"

# Explicitly disable silent self-update
python3 "$INSTALL_DEST/scripts/mcp_client.py" update --auto off
```
*Expected Output:* `Automatic Beatra package updates are disabled.`

### Step 3: Authorization via OAuth Device Flow
Authorize the agent session using an interactive device authorization flow. The resulting token must be locked to restrictive POSIX permissions (`0600`):

```bash
# Initiates browser sign-in; stores bearer token in ~/.beatra/credentials.json
python3 "$INSTALL_DEST/scripts/authorize.py"
```

### Step 4: Non-Billable Pre-Flight Check & Cost Estimation
Query available model configurations and compute the credit estimate without incurring charges:

```python
import json
import subprocess

def get_cost_estimate(install_path: str, model_name: str, audio_duration_sec: float) -> dict:
    """Queries free discovery endpoint to generate a pre-flight cost card."""
    cmd = [
        "python3", f"{install_path}/scripts/mcp_client.py", 
        "tools", "estimate", 
        "--model", model_name, 
        "--duration", str(audio_duration_sec)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    estimate_data = json.loads(res.stdout)
    
    print("=" * 60)
    print("PRE-FLIGHT COST APPROVAL CARD")
    print("=" * 60)
    print(f"Target Model:       {model_name}")
    print(f"Audio Duration:     {audio_duration_sec:.1f} seconds")
    print(f"Estimated Credits:  {estimate_data.get('estimated_credits')} credits")
    print(f"Current Balance:    {estimate_data.get('wallet_balance')} credits")
    print("Files to Upload:    [portrait.png, voiceover.wav]")
    print("=" * 60)
    return estimate_data
```

### Step 5: Human Approval Gate & Idempotent Submission
Only dispatch paid synthesis once explicit human consent is granted. Use a persistent UUID for `client_request_id` to prevent duplicate charges upon network timeouts:

```python
import uuid
import sys

def submit_avatar_render(install_path: str, image_path: str, audio_path: str, model_name: str):
    # Idempotency key: prevents duplicate billing if HTTP socket drops
    client_request_id = str(uuid.uuid4())
    
    cmd = [
        "python3", f"{install_path}/scripts/mcp_client.py", "call", "avatar.render",
        "--request-id", client_request_id,
        "--model", model_name,
        "--image", image_path,
        "--audio", audio_path
    ]
    
    print(f"Submitting render job with request ID: {client_request_id}...")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    job_result = json.loads(proc.stdout)
    
    task_id = job_result["task_id"]
    print(f"Task dispatched: {task_id}. Polling for completion...")
    return task_id
```

### Step 6: Task Reconciliation & Cleanup
Monitor the asynchronous rendering task to terminal state, report actual net credits debited, and retrieve the rendered MP4 file. When uninstallation is requested, revoke the token and wipe credentials:

```bash
# Check uninstall status and revoke tokens
python3 "$INSTALL_DEST/scripts/uninstall.py"
```

## Best Practices & Failure Modes

- **Strict Cost Card Approval**: Never proceed with synthesis based on implied user consent or general instructions like "build the video". Always output the estimated cost in credits and wait for explicit confirmation.
- **Idempotent Retry Protocol**: If a connection drops during task submission, retry *only* with the identical `client_request_id`. Never generate a new request ID for an ongoing task, or the user will be double-billed.
- **Credential Storage Safety**: Never export `~/.beatra/credentials.json` into command-line arguments, environment variables, or commit logs. Ensure the file has `0600` file permissions (`chmod 600 ~/.beatra/credentials.json`).
- **Facial Landmark Occlusion**: Avoid portraits where hands, microphones, or heavy shadows obscure the chin or jawline. Synthetic lip sync will produce unnatural warping if face detection confidence falls below 0.85.

## Verification & Testing

1. Validate file hashes: Run `python scripts/talking-avatar-video_helper.py --verify-hash` to ensure the installation archive matches the expected digest.
2. Verify update isolation: Confirm that `~/.beatra/updates/<id>/state.json` contains `"auto_update": false`.
3. Test non-billable discovery: Run `mcp_client.py verify` to verify API connectivity without spending credits.
4. Execute test rendering: Perform a 3-second test synthesis with a sample portrait and audio track to confirm AV sync and credit deduction accuracy.
