#!/usr/bin/env python3
import sys
import os

def transcribe_file(audio_path, output_md=None):
    if not os.path.exists(audio_path):
        print(f"Error: Audio file '{audio_path}' not found.")
        sys.exit(1)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper is not installed. Run 'pip install faster-whisper'.")
        sys.exit(1)

    print("=" * 65)
    print(f"Transcribing Audio: {os.path.basename(audio_path)}")
    print("=" * 65)

    # Use CPU int8 by default for universal portability
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, beam_size=3, vad_filter=True)

    print(f"Detected Language: '{info.language}' (Probability: {info.language_probability:.2f})\n")

    lines = [f"# Transcript: {os.path.basename(audio_path)}\n"]
    for seg in segments:
        ts = f"[{int(seg.start // 60):02d}:{int(seg.start % 60):02d} -> {int(seg.end // 60):02d}:{int(seg.end % 60):02d}]"
        print(f"{ts} {seg.text.strip()}")
        lines.append(f"**{ts}** {seg.text.strip()}\n")

    if output_md:
        with open(output_md, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\nSaved transcript to {output_md}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audio_transcription_cli.py <path-to-audio-file> [output.md]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    transcribe_file(sys.argv[1], out)
