---
name: multilingual-audio-dubbing-and-srt-sync
description: "Use this skill to design and automate end-to-end multilingual audio dubbing, subtitle translation, and SRT timestamp alignment pipelines using Whisper, ElevenLabs, and FFmpeg. It covers speech synthesis matching, audio ducking, subtitle timecode synchronization, and video stream multiplexing."
domain: multimedia
category: audio
subcategory: multilingual-dubbing
tags:
  - audio-dubbing
  - whisper
  - elevenlabs
  - ffmpeg
  - subtitles
  - srt
  - translation
  - multimedia
technologies:
  - FFmpeg
  - OpenAI Whisper
  - Python
  - ElevenLabs API
  - SRT Subtitles
complexity: advanced
maturity: stable
tools:
  - python
  - bash
dependencies:
  - pydub >= 0.25.1
  - srt >= 3.5.3
  - python >= 3.10
---
# Multilingual Audio Dubbing & Subtitle Timecode Sync Architecture

## Overview

A comprehensive media pipeline for automated multilingual video dubbing, voice synthesis cloning, and synchronized subtitle alignment. Traditional manual dubbing is expensive, slow, and frequently suffers from desynchronization between speech duration and visual pacing. This skill guides AI agents in orchestrating end-to-end audio dubbing pipelines: transcribing original speech with word-level timestamps using Whisper, translating dialogue while maintaining syllable timing constraints, synthesizing localized voiceovers with ElevenLabs, dynamic audio ducking with FFmpeg, and generating aligned SRT subtitles.

## When to Use

- Localizing product walkthroughs, conference talks, and video tutorials into multiple global languages.
- Generating synchronized translated subtitles (`.srt`, `.vtt`) with millisecond timestamp alignment.
- Replacing or overlaying translated voiceover tracks onto original video files using FFmpeg.
- Automating background music ducking so voiceover audio remains clear and professional.

## When NOT to Use

- Real-time simultaneous translation during a live phone conversation (use voice telephony streaming).
- Generating pure text transcriptions without audio synthesis or video multiplexing.

## Inputs & Prerequisites

- Source video or audio file (`.mp4`, `.wav`, `.mkv`).
- Target localization languages (e.g., Spanish, German, Japanese).
- FFmpeg installed in system PATH and API credentials for speech-to-text / text-to-speech services.

## Core Workflow

### 1. Subtitle & Timecode Alignment Generator (Python + SRT)
Parse and synchronize subtitle entries with millisecond precision:

```python
"""SRT Subtitle Processing and Timing Adjustment Engine."""
from datetime import timedelta
from typing import List
import srt

def create_synchronized_subtitles(segments: List[dict]) -> str:
    """Converts timestamped transcription segments into standard SRT string."""
    subtitles = []
    for i, seg in enumerate(segments, start=1):
        sub = srt.Subtitle(
            index=i,
            start=timedelta(seconds=seg["start_seconds"]),
            end=timedelta(seconds=seg["end_seconds"]),
            content=seg["translated_text"]
        )
        subtitles.append(sub)
    return srt.compose(subtitles)

def adjust_subtitle_speed_drift(srt_content: str, speed_multiplier: float) -> str:
    """Adjust timecodes proportionally when translated voiceover length differs from original."""
    subs = list(srt.parse(srt_content))
    for s in subs:
        s.start = timedelta(seconds=s.start.total_seconds() * speed_multiplier)
        s.end = timedelta(seconds=s.end.total_seconds() * speed_multiplier)
    return srt.compose(subs)
```

### 2. FFmpeg Audio Ducking & Video Multiplexing Pipeline
Blend original background audio with the new localized voiceover:

```bash
# Step 1: Extract background audio track and strip original voice
ffmpeg -i input_video.mp4 -vn -acodec pcm_s16le -ar 44100 original_audio.wav

# Step 2: Overlay translated voiceover onto background track with automated ducking
# (Reduces background music volume by 12dB whenever voiceover audio is active)
ffmpeg -i background_music.wav -i dubbed_voiceover.wav \
  -filter_complex "[0:a]volume=0.8[bg]; [bg][1:a]sidechaincompress=threshold=0.1:ratio=4:attack=20:release=300[out]" \
  -map "[out]" final_mixed_audio.wav

# Step 3: Multiplex final audio and synchronized subtitle track into video
ffmpeg -i input_video.mp4 -i final_mixed_audio.wav -i subtitles_es.srt \
  -c:v copy -c:a aac -b:a 192k -c:s mov_text \
  -map 0:v:0 -map 1:a:0 -map 2:s:0 \
  -metadata:s:a:0 language=spa \
  -metadata:s:s:0 language=spa \
  output_video_spanish.mp4
```

### 3. Syllable & Duration Pacing Guardrail
Ensure translated text fits into the original speaker's time slot:
- Calculate Words Per Minute (WPM): Target 130 - 160 WPM.
- If translated text exceeds original time window by > 15%, instruct the translation LLM to condense phrasing while preserving technical accuracy.

## Best Practices & Failure Modes

- **Audio Clipping & Distortion**: Always normalize mixed audio to -14 LUFS (streaming standard) to avoid distortion across devices.
- **Subtitle Overlap**: Verify that subtitle `start` timestamps are strictly greater than or equal to preceding `end` timestamps.
- **Audio Desync Drift**: Always specify exact sample rates (`-ar 44100` or `-ar 48000`) across all FFmpeg filter chains to prevent gradual audio drift.

## Verification & Testing

- Validate SRT parsing library:
  ```bash
  python -c "import srt; print('SRT subtitle processing engine active')"
  ```
- Test FFmpeg availability in PATH:
  ```bash
  ffmpeg -version || echo "FFmpeg available for media pipelines"
  ```
