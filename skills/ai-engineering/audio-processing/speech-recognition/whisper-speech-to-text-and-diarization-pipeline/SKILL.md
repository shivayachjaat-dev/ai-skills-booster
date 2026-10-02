---
name: whisper-speech-to-text-and-diarization-pipeline
description: "Use this skill to build end-to-end automated speech recognition (ASR) and speaker diarization pipelines using OpenAI Whisper and PyAnnote. It covers CTranslate2 (faster-whisper) acceleration, Silero Voice Activity Detection (VAD) audio chunking, multi-speaker clustering, precise timestamp word alignment, and structured Markdown, SRT, and JSON transcript generation."
domain: ai-engineering
category: audio-processing
subcategory: speech-recognition
tags:
  - ai-engineering
  - audio-processing
  - speech-to-text
  - whisper
  - faster-whisper
  - speaker-diarization
  - pyannote
  - vad
technologies:
  - Whisper
  - faster-whisper
  - PyAnnote
  - Silero VAD
  - FFmpeg
  - Python
complexity: advanced
maturity: stable
tools:
  - python
  - ffmpeg
  - bash
dependencies:
  - faster-whisper@>=1.0.0
  - pyannote.audio@>=3.1.0
  - torch@>=2.1.0
---
# Whisper Speech-to-Text & Multi-Speaker Diarization Pipeline

## Overview

A production engineering standard for building high-accuracy, cost-effective automated speech recognition (ASR) pipelines with multi-speaker diarization. While vanilla Whisper models transcribe audio with remarkable linguistic precision, enterprise use cases (boardroom meetings, clinical consultations, podcast production, customer support triage) require knowing *who* spoke *when*, filtering non-speech background noise, and executing inference with high throughput. This skill guides AI engineers in integrating `faster-whisper` (CTranslate2 INT8/FP16 quantization), Silero Voice Activity Detection (VAD), and `pyannote.audio` speaker clustering to generate timestamped, speaker-labeled Markdown and subtitle outputs.

```
+------------------------------------------------------------------------+
|                 Speech Processing & Diarization Pipeline               |
|                                                                        |
|  [ Raw Audio / Video ] ---> [ FFmpeg Audio Normalization (16kHz Mono) ]|
|                                              |                         |
|                      +-----------------------+                         |
|                      |                                                 |
|                      v                                                 |
|          [ Silero VAD Pre-Filter ] (Remove dead silence & background)  |
|                      |                                                 |
|         +------------+------------+                                    |
|         v                         v                                    |
|  [ faster-whisper ]      [ pyannote.audio ]                            |
|  (CTranslate2 ASR)       (Speaker Embedding & Clustering)              |
|         |                         |                                    |
|         +------------+------------+                                    |
|                      v                                                 |
|      [ Timestamp Alignment & Speaker Fusion ]                          |
|                      |                                                 |
|                      v                                                 |
|  [ Formatted Output: Markdown Notes / SRT / JSON Transcript ]          |
+------------------------------------------------------------------------+
```

## When to Use

- Transcribing executive meetings, interviews, podcasts, or customer calls where distinguishing speaker identities is mandatory.
- Deploying private, on-premise, or cloud ASR pipelines that eliminate recurring third-party API costs.
- Generating synchronized subtitle files (`.srt`, `.vtt`) with precise word-level timing.
- Batch processing gigabytes of legacy audio recordings with GPU-accelerated INT8 quantization.

## When NOT to Use

- Real-time, ultra-low latency voice-to-voice streaming conversational agents (<200ms budget; use streaming WebRTC ASR like Whisper-live or Deepgram Nova-2).
- Non-speech audio classification (e.g., gunshot detection, musical pitch estimation).

## Inputs & Prerequisites

- Audio/video files in standard formats (`.wav`, `.mp3`, `.m4a`, `.mp4`, `.flac`).
- FFmpeg installed in the system PATH.
- Python 3.10+ with PyTorch (CUDA optional but recommended for speed).
- Hugging Face user access token for downloading PyAnnote diarization weights.

## Core Workflow

### Step 1: Audio Pre-Processing with FFmpeg
Convert incoming audio streams to 16kHz 16-bit mono PCM, the standard sample rate for Whisper and PyAnnote:

```bash
ffmpeg -i input_media.mp4 -vn -ar 16000 -ac 1 -c:a pcm_s16le normalized_audio.wav
```

### Step 2: Accelerated Transcription with faster-whisper
Use `faster-whisper` (CTranslate2) for 4x faster execution and 50% lower VRAM consumption:

```python
from faster_whisper import WhisperModel

# Use "large-v3" for maximum accuracy, or "distil-large-v3" for high speed
# Compute type: "float16" on GPU, "int8" on CPU
model = WhisperModel("large-v3", device="cuda", compute_type="float16")

segments, info = model.transcribe(
    "normalized_audio.wav",
    beam_size=5,
    vad_filter=True, # Built-in Silero VAD chunking
    vad_parameters=dict(min_silence_duration_ms=500),
    language="en",
    word_timestamps=True
)

transcription_segments = []
for segment in segments:
    transcription_segments.append({
        "start": segment.start,
        "end": segment.end,
        "text": segment.text.strip(),
        "words": [{"word": w.word, "start": w.start, "end": w.end, "prob": w.probability} for w in segment.words]
    })
```

### Step 3: Speaker Diarization with pyannote.audio
Extract speaker segmentation turns from the normalized audio:

```python
from pyannote.audio import Pipeline
import torch

def run_diarization(audio_path: str, hf_token: str):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        
    diarization = pipeline(audio_path)
    
    speaker_turns = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_turns.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return speaker_turns
```

### Step 4: Speaker-to-Text Temporal Fusion
Assign speaker labels to transcription segments by calculating maximum temporal intersection:

```python
def merge_speaker_and_text(transcripts, speaker_turns):
    merged = []
    
    for seg in transcripts:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_mid = (seg_start + seg_end) / 2.0
        
        # Find overlapping speaker
        matched_speaker = "Unknown"
        for turn in speaker_turns:
            if turn["start"] <= seg_mid <= turn["end"]:
                matched_speaker = turn["speaker"]
                break
                
        merged.append({
            "speaker": matched_speaker,
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"]
        })
        
    return merged
```

### Step 5: Structured Markdown Output Formatting
Group consecutive utterances by the same speaker into readable conversation blocks:

```python
def format_to_markdown(merged_entries) -> str:
    md_lines = ["# Meeting & Audio Transcription\n"]
    current_speaker = None
    
    for entry in merged_entries:
        speaker = entry["speaker"]
        timestamp = f"[{int(entry['start'] // 60):02d}:{int(entry['start'] % 60):02d}]"
        
        if speaker != current_speaker:
            current_speaker = speaker
            md_lines.append(f"\n### {speaker} {timestamp}\n")
            
        md_lines.append(f"{entry['text']} ")
        
    return "\n".join(md_lines)
```

## Best Practices & Failure Modes

- **Audio Clipping & Low SNR**: Poor microphone gain leads to hallucinated repetitive sentences in Whisper. Normalize audio gain using `-af loudnorm` in FFmpeg.
- **Cross-Talk & Overlapping Speakers**: When two speakers talk simultaneously, PyAnnote flags overlapping segments. Whisper might capture only the louder speaker. Handle overlapping intervals gracefully.
- **VAD Truncation**: Ensure `min_silence_duration_ms` is set to at least 400-500ms; overly aggressive silence pruning cuts off word endings and natural pauses.

## Verification & Testing

1. Test transcription accuracy against a standardized ground truth audio snippet (measure Word Error Rate / WER).
2. Verify speaker change transitions: Ensure no single speaker monologue artificially crosses distinct conversational turns.
3. Validate output formats: Generate valid SRT files and verify with subtitle players like VLC.
