# Transcript Service

Robust YouTube transcript extraction with automatic failover.

## Location

`/root/flourisha/00_AI_Brain/services/transcript_service.py`

## Overview

The `TranscriptService` provides a two-tier approach to YouTube transcript extraction:

| Tier | Method | When Used |
|------|--------|-----------|
| **Tier 1** | YouTube Transcript API via Tor proxy | Primary - fast, free |
| **Tier 2** | yt-dlp audio download + Whisper | Fallback - when no transcript exists |

## Why Tor Proxy?

YouTube blocks transcript API requests from cloud provider IPs (AWS, GCP, Azure, Contabo, etc.). The Tor proxy routes requests through residential IPs to bypass this restriction.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    get_transcript(video_id)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: YouTube Transcript API via Tor                      │
│                                                              │
│  youtube-transcript-api + GenericProxyConfig                │
│  Proxy: socks5://127.0.0.1:9050                             │
│                                                              │
│  ✓ Fast (seconds)                                           │
│  ✓ Free                                                     │
│  ✓ Multiple language support                                │
│  ✗ Requires transcript to exist on YouTube                  │
└─────────────────────────────────────────────────────────────┘
                              │
                     (if failed)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: Audio Download + Whisper Transcription              │
│                                                              │
│  yt-dlp (via Tor) → faster-whisper (local)                  │
│                                                              │
│  ✓ Works for any video with audio                           │
│  ✓ High accuracy transcription                              │
│  ✗ Slower (minutes per video)                               │
│  ✗ Requires disk space for audio download                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    TranscriptResult                          │
│  - success: bool                                             │
│  - transcript: str                                           │
│  - source: YOUTUBE_API | WHISPER | FAILED                   │
│  - video_id: str                                             │
│  - language: str                                             │
│  - metadata: dict                                            │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Simple Usage

```python
from services.transcript_service import get_transcript

# Get transcript (uses Tor → Whisper fallback automatically)
result = get_transcript("63HbCXbc0gM")

if result.success:
    print(f"Transcript ({result.source.value}):")
    print(result.transcript[:500])
else:
    print(f"Failed: {result.error}")
```

### Full Control

```python
from services.transcript_service import TranscriptService

service = TranscriptService(whisper_model="base")

# Try with specific languages
result = service.get_transcript(
    video_id="63HbCXbc0gM",
    languages=["en", "en-US", "a.en"],
    skip_tier1=False
)

print(f"Source: {result.source.value}")
print(f"Language: {result.language}")
print(f"Metadata: {result.metadata}")
```

### Skip Tor (Whisper Only)

```python
# Force Whisper transcription (skip YouTube API)
result = get_transcript("VIDEO_ID", skip_tor=True)
```

### CLI Testing

```bash
# Test with video ID
python3 services/transcript_service.py "63HbCXbc0gM"

# Force Whisper only
python3 services/transcript_service.py "63HbCXbc0gM" --whisper-only
```

## TranscriptResult

```python
@dataclass
class TranscriptResult:
    success: bool              # True if transcript obtained
    transcript: Optional[str]  # Full transcript text
    source: TranscriptSource   # YOUTUBE_API, WHISPER, or FAILED
    video_id: str              # YouTube video ID
    language: str = "en"       # Detected language
    error: Optional[str]       # Error message if failed
    metadata: Optional[dict]   # Additional info (char_count, duration, etc.)
```

## Dependencies

### Required Packages

```bash
# Tor proxy support
pip install pysocks

# YouTube transcript API (already installed)
pip install youtube-transcript-api

# Audio processing
apt install ffmpeg
pip install faster-whisper

# Audio download
pip install yt-dlp
```

### System Services

```bash
# Tor must be running
systemctl status tor

# Verify Tor proxy port
ss -tlnp | grep 9050
```

## Configuration

### Tor Proxy

Default: `socks5://127.0.0.1:9050`

The service expects Tor to be running on localhost port 9050. See [TOR_PROXY_SETUP.md](../infrastructure/TOR_PROXY_SETUP.md) for installation.

### Whisper Model

Default: `base`

Available models:
| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39 MB | Fastest | Lower |
| base | 74 MB | Fast | Good |
| small | 244 MB | Medium | Better |
| medium | 769 MB | Slow | High |
| large-v3 | 1.5 GB | Slowest | Highest |

```python
service = TranscriptService(whisper_model="small")
```

### Language Preferences

Default: `['en', 'en-US', 'a.en']` (English, US English, auto-generated English)

```python
result = service.get_transcript(
    video_id="VIDEO_ID",
    languages=["es", "es-MX", "a.es"]  # Spanish preference
)
```

## Error Handling

```python
result = get_transcript(video_id)

if not result.success:
    if "IP" in result.error or "blocked" in result.error.lower():
        print("Tor proxy may need restart")
    elif "transcript" in result.error.lower():
        print("No transcript available, Whisper also failed")
    else:
        print(f"Unknown error: {result.error}")
```

## Performance

| Scenario | Time | Notes |
|----------|------|-------|
| Tier 1 success | 2-5 sec | Via Tor proxy |
| Tier 2 (short video) | 1-3 min | Download + transcribe |
| Tier 2 (long video) | 5-15 min | Depends on length |

## Troubleshooting

### "Missing dependencies for SOCKS support"

```bash
pip install pysocks
```

### "Tor proxy connection refused"

```bash
# Start Tor service
systemctl start tor

# Verify port 9050
ss -tlnp | grep 9050
```

### "Sign in to confirm you're not a bot" (yt-dlp)

YouTube is blocking yt-dlp. The service uses `--proxy socks5://127.0.0.1:9050` to route through Tor.

### "No transcript available"

The video has no captions. Tier 2 (Whisper) will handle this automatically.

### Whisper model download slow

Models are downloaded on first use. The `base` model is ~74MB.

```python
# Pre-download model
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cpu")
```

## Integration with Knowledge Ingestion

```python
from services.transcript_service import get_transcript
from services.knowledge_ingestion_service import ingest_document

# Get transcript
result = get_transcript("VIDEO_ID")

if result.success:
    # Save transcript to temp file
    with open("/tmp/transcript.txt", "w") as f:
        f.write(result.transcript)

    # Ingest into AI Brain
    await ingest_document(
        file_path="/tmp/transcript.txt",
        document_type="youtube_video",
        metadata={"video_id": result.video_id, "source": result.source.value}
    )
```

## Related Documentation

- [Tor Proxy Setup](../infrastructure/TOR_PROXY_SETUP.md) - Tor installation and configuration
- [Knowledge Ingestion](./KNOWLEDGE_INGESTION.md) - How documents are processed
- [YouTube Service](./youtube_service.py) - Legacy YouTube API integration

---

*Last updated: 2025-12-14*
