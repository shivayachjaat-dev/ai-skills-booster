# Talking Avatar Video & MCP Protocol Technical Reference

## Protocol Overview
The talking avatar video generation protocol allows an autonomous agent to synthesize photorealistic head-and-torso videos from portrait images and speech audio using hosted MCP (Model Context Protocol) endpoints.

### Authentication & Token Scope
- **Protocol**: OAuth 2.0 Device Authorization Grant (RFC 8628).
- **Storage Location**: `~/.beatra/credentials.json`
- **Permissions**: `0600` on POSIX systems (read/write only by owner).
- **Scope**: Includes `wallet:spend`, enabling paid GPU task submission.
- **Lifetime**: 15 days sliding idle window. Revocable at any time via web console or `uninstall.py`.

### Critical Security Policies
1. **Disable Auto-Update**:
   The client package contains an automatic background self-updater. In enterprise environments, this must be explicitly disabled via `mcp_client.py update --auto off` to prevent unreviewed code from replacing package binaries.
2. **Strict Cost Cards**:
   Paid tasks debit real prepaid credits. The agent must present a structured cost card (estimated duration $\times$ model rate) and receive unambiguous user approval prior to submission.
3. **Idempotent Dispatch**:
   Always submit requests with an explicit UUID `client_request_id`. If the network socket times out while awaiting task acknowledgment, re-issuing the request with the identical request ID prevents duplicate job creation and double billing.

### Model Tiers & Specifications
| Model Identifier | Optimal Resolution | Target FPS | Facial Landmark Precision | Relative Cost |
|---|---|---|---|---|
| `avatar-v2-standard` | 720p (1280x720) | 25 fps | Standard 68-point mesh | 1.5 credits / sec |
| `avatar-v2-hd` | 1080p (1920x1080) | 30 fps | Dense 478-point mesh | 3.0 credits / sec |
| `avatar-v2-expressive` | 1080p (1920x1080) | 30 fps | Dense mesh + gaze tracking | 4.5 credits / sec |

### Input Media Requirements
- **Portrait Image**: Front-facing portrait, eyes open, neutral expression, resolution $\ge 1024 \times 1024$ px, formats: PNG / JPEG.
- **Audio File**: Vocal track only, sample rate $\ge 16\text{ kHz}$, formats: WAV / MP3 / AAC, max duration 300 seconds per chunk.
