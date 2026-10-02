---
name: ai-agent-voice-telephony-and-sms-integration
description: "Use this skill to design, orchestrate, and deploy voice-enabled AI agents and SMS notification pipelines using Twilio, WebRTC, and real-time audio streaming. It covers inbound call IVR trees, WebSocket audio streaming, latency optimization, conversational interruption handling, and SMS delivery receipts."
domain: ai-engineering
category: communication
subcategory: voice-telephony
tags:
  - voice-agents
  - telephony
  - twilio
  - sms
  - webrtc
  - speech-to-text
  - audio-streaming
technologies:
  - Twilio API
  - Python
  - WebSockets
  - FastAPI
  - TwiML
complexity: advanced
maturity: stable
tools:
  - python
dependencies:
  - twilio >= 8.10.0
  - fastapi >= 0.100.0
  - python >= 3.10
---
# AI Voice Telephony & SMS Agent Integration Architecture

## Overview

A real-time telecommunications engineering specification for connecting autonomous AI agents to phone networks, SMS gateways, and audio streaming WebSockets. Voice agents present unique technical hurdles compared to text chatbots: sub-500ms audio turnaround latency requirements, background noise suppression, speech-to-text (STT) streaming, turn-taking pauses, and handling caller interruptions gracefully. This skill provides AI agents with standard Twilio Media Streams integration, TwiML generation, bi-directional audio WebSocket pipelines, and resilient SMS dispatch.

## When to Use

- Building real-time interactive voice agents that answer telephone calls or conduct outbound voice surveys.
- Streaming real-time caller audio over WebSockets to low-latency LLMs and TTS models.
- Handling conversational interruptions (barge-in) when the user speaks while the agent is talking.
- Sending two-factor authentication (2FA) SMS codes, dispatch alerts, and SMS conversation workflows.

## When NOT to Use

- Asynchronous batch audio transcription of archived MP3 recordings (use Whisper batch processing).
- Pure text-only chatbots without telephony or cellular voice requirements.

## Inputs & Prerequisites

- Telephony provider account (Twilio, Vonage, or Telnyx) with provisioned phone numbers.
- Publicly accessible HTTPS/WSS endpoint (via domain or tunneling).
- Ultra-low latency Speech-to-Text (STT) and Text-to-Speech (TTS) engine credentials.

## Core Workflow

### 1. Inbound Call Handler & WebSocket Stream TwiML (FastAPI)
Direct incoming voice calls to a bi-directional audio WebSocket stream:

```python
"""FastAPI Telephony Ingress and TwiML Response Generator."""
from fastapi import FastAPI, Response, Request
from twilio.twiml.voice_response import VoiceResponse, Connect

app = FastAPI(title="Voice Agent Telephony Gateway")

@app.post("/telephony/inbound-call")
async def handle_inbound_voice_call(request: Request):
    """Respond to Twilio webhook with instruction to stream caller audio to our WebSocket."""
    form = await request.form()
    caller_number = form.get("From", "Unknown")
    call_sid = form.get("CallSid", "")
    print(f"[Telephony] Inbound voice call received from: {caller_number} (CallSid: {call_sid})")

    vr = VoiceResponse()
    # Initial greeting while stream connects
    vr.say("Connecting you to the AI support assistant. Please speak clearly after the tone.", voice="Polly.Amy")
    
    # Establish bi-directional media stream over WebSocket
    connect = Connect()
    host = request.headers.get("host", "example.com")
    connect.stream(url=f"wss://{host}/telephony/media-stream/{call_sid}")
    vr.append(connect)

    return Response(content=str(vr), media_type="application/xml")
```

### 2. Bi-Directional Audio Streaming & Barge-In Detection
Handle 8kHz mulaw audio chunks and detect conversational interruptions:

```python
"""WebSocket Media Stream Audio Processing."""
import json
import base64
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/telephony/media-stream/{call_sid}")
async def media_stream_endpoint(websocket: WebSocket, call_sid: str):
    await websocket.accept()
    print(f"[WebSocket] Connected audio stream for Call: {call_sid}")
    stream_sid = None

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                print(f"[Audio Stream] Initialized StreamSid: {stream_sid}")
            elif event == "media":
                # Incoming audio chunk in base64 (8000Hz mulaw)
                payload_b64 = data["media"]["payload"]
                audio_bytes = base64.b64decode(payload_b64)
                # Dispatch chunk to streaming STT engine...
            elif event == "stop":
                print(f"[Audio Stream] Terminated for Call: {call_sid}")
                break
    except WebSocketDisconnect:
        print(f"[WebSocket] Disconnected for Call: {call_sid}")
```

### 3. Outbound SMS Notification with Delivery Tracking
Send programmatic SMS alerts with status callbacks:

```python
"""Outbound SMS Dispatcher."""
from twilio.rest import Client
import os

def dispatch_sms_alert(to_number: str, message_body: str) -> str:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "AC_dummy_sid")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "dummy_auth_token")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER", "+15551234567")

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_body,
        from_=from_number,
        to=to_number,
        status_callback="https://api.example.com/telephony/sms-status"
    )
    return message.sid
```

## Best Practices & Failure Modes

- **Turnaround Latency Target**: Keep Total Response Latency (Caller stops speaking -> Agent audio plays) strictly under 600ms to avoid unnatural awkward pauses.
- **Barge-In Interruption**: When user speech is detected while the agent is speaking, immediately send a `clear` event to flush Twilio's audio buffer and silence the playback.
- **Toll Fraud & Geo-Fencing**: Configure Twilio geo-permissions to allow voice calls only to designated target regions to prevent international toll fraud.

## Verification & Testing

- Validate Twilio SDK and FastAPI:
  ```bash
  python -c "import twilio, fastapi; print('Telephony libraries verified')"
  ```
- Test TwiML XML serialization:
  ```bash
  python -c "from twilio.twiml.voice_response import VoiceResponse; vr = VoiceResponse(); vr.say('Hello'); print('TwiML generated:', len(str(vr)))"
  ```
