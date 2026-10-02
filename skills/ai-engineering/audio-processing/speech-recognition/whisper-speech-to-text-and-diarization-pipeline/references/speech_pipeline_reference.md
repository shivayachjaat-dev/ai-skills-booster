# Whisper & Diarization Optimization Reference

## Whisper Model Comparison
| Model Size | Parameters | VRAM (FP16) | Relative Speed | Typical WER (English) |
|---|---|---|---|---|
| tiny | 39 M | ~1 GB | 32x | ~8-10% |
| base | 74 M | ~1 GB | 16x | ~6-8% |
| small | 244 M | ~2 GB | 6x | ~4-5% |
| medium | 769 M | ~5 GB | 2x | ~3-4% |
| large-v3 | 1550 M | ~10 GB | 1x | ~2-3% |
| distil-large-v3 | 756 M | ~4 GB | 6x | ~2.5-3.5% |

## FFmpeg Commands for Audio Normalization
```bash
# Normalize loudness to EBU R128 standard
ffmpeg -i raw_input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 16000 -ac 1 clean_mono.wav
```
