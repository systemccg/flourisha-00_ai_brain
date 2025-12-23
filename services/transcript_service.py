"""
Robust YouTube Transcript Service
Tier 1: YouTube Transcript API via Tor Proxy
Tier 2: Audio download + Whisper transcription (failover)
"""
import os
import tempfile
import subprocess
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranscriptSource(Enum):
    """Source of the transcript"""
    YOUTUBE_API = "youtube_api"
    WHISPER = "whisper"
    FAILED = "failed"


@dataclass
class TranscriptResult:
    """Result from transcript extraction"""
    success: bool
    transcript: Optional[str]
    source: TranscriptSource
    video_id: str
    language: str = "en"
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TranscriptService:
    """
    Robust transcript extraction with automatic failover.

    Tier 1: YouTube Transcript API via Tor SOCKS proxy
    Tier 2: yt-dlp audio download + faster-whisper transcription
    """

    # Tor SOCKS5 proxy configuration
    TOR_PROXY = {
        "https": "socks5://127.0.0.1:9050",
        "http": "socks5://127.0.0.1:9050"
    }

    # Whisper model size (tiny, base, small, medium, large-v3)
    # Using 'base' as good balance of speed/accuracy
    WHISPER_MODEL = "base"

    def __init__(self, whisper_model: str = None):
        """Initialize transcript service"""
        self.whisper_model = whisper_model or self.WHISPER_MODEL
        self._whisper_instance = None

    def _get_whisper_model(self):
        """Lazy-load Whisper model"""
        if self._whisper_instance is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Whisper model: {self.whisper_model}")
            # Use CPU by default, switch to cuda if available
            self._whisper_instance = WhisperModel(
                self.whisper_model,
                device="cpu",
                compute_type="int8"
            )
        return self._whisper_instance

    def _try_youtube_api(self, video_id: str, languages: list = None) -> TranscriptResult:
        """
        Tier 1: Try to get transcript via YouTube API through Tor proxy
        """
        languages = languages or ['en', 'en-US', 'a.en']

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            from youtube_transcript_api.proxies import GenericProxyConfig

            # Configure Tor proxy
            proxy_config = GenericProxyConfig(
                http_url="socks5://127.0.0.1:9050",
                https_url="socks5://127.0.0.1:9050"
            )

            ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

            # First try to list available transcripts
            logger.info(f"Attempting to fetch transcript for {video_id} via Tor proxy")
            transcript_list = ytt_api.list(video_id)

            # Find the best transcript
            transcript = None
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except:
                    continue

            if transcript is None:
                # Try auto-generated
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    pass

            if transcript is None:
                return TranscriptResult(
                    success=False,
                    transcript=None,
                    source=TranscriptSource.YOUTUBE_API,
                    video_id=video_id,
                    error="No transcript available for this video"
                )

            # Fetch the transcript content
            fetched = transcript.fetch()
            full_text = " ".join([snippet.text for snippet in fetched.snippets])

            logger.info(f"Successfully fetched transcript via YouTube API ({len(full_text)} chars)")

            return TranscriptResult(
                success=True,
                transcript=full_text,
                source=TranscriptSource.YOUTUBE_API,
                video_id=video_id,
                language=transcript.language_code,
                metadata={"char_count": len(full_text)}
            )

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"YouTube API transcript failed: {error_msg}")

            return TranscriptResult(
                success=False,
                transcript=None,
                source=TranscriptSource.YOUTUBE_API,
                video_id=video_id,
                error=error_msg
            )

    def _try_whisper_fallback(self, video_id: str) -> TranscriptResult:
        """
        Tier 2: Download audio with yt-dlp and transcribe with Whisper
        """
        logger.info(f"Initiating Whisper fallback for {video_id}")

        # Create temp directory for audio file
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, f"{video_id}.mp3")

            try:
                # Step 1: Download audio with yt-dlp
                logger.info(f"Downloading audio for {video_id}")

                video_url = f"https://www.youtube.com/watch?v={video_id}"

                cmd = [
                    "yt-dlp",
                    "-x",  # Extract audio
                    "--audio-format", "mp3",
                    "--audio-quality", "5",  # Medium quality (0=best, 10=worst)
                    "-o", audio_path,
                    "--no-playlist",
                    "--quiet",
                    "--proxy", "socks5://127.0.0.1:9050",  # Use Tor proxy
                    "--extractor-args", "youtube:player_client=web",
                    video_url
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                if result.returncode != 0:
                    raise Exception(f"yt-dlp failed: {result.stderr}")

                if not os.path.exists(audio_path):
                    raise Exception("Audio file not created")

                file_size = os.path.getsize(audio_path)
                logger.info(f"Audio downloaded: {file_size / 1024 / 1024:.1f} MB")

                # Step 2: Transcribe with Whisper
                logger.info("Transcribing with Whisper...")

                model = self._get_whisper_model()
                segments, info = model.transcribe(
                    audio_path,
                    language="en",
                    beam_size=5,
                    vad_filter=True  # Voice activity detection
                )

                # Combine all segments
                full_text = " ".join([segment.text.strip() for segment in segments])

                logger.info(f"Whisper transcription complete ({len(full_text)} chars)")

                return TranscriptResult(
                    success=True,
                    transcript=full_text,
                    source=TranscriptSource.WHISPER,
                    video_id=video_id,
                    language=info.language,
                    metadata={
                        "char_count": len(full_text),
                        "duration": info.duration,
                        "audio_size_mb": file_size / 1024 / 1024
                    }
                )

            except subprocess.TimeoutExpired:
                return TranscriptResult(
                    success=False,
                    transcript=None,
                    source=TranscriptSource.WHISPER,
                    video_id=video_id,
                    error="Audio download timed out"
                )
            except Exception as e:
                logger.error(f"Whisper fallback failed: {e}")
                return TranscriptResult(
                    success=False,
                    transcript=None,
                    source=TranscriptSource.WHISPER,
                    video_id=video_id,
                    error=str(e)
                )

    def get_transcript(
        self,
        video_id: str,
        languages: list = None,
        skip_tier1: bool = False
    ) -> TranscriptResult:
        """
        Get transcript with automatic failover.

        Args:
            video_id: YouTube video ID
            languages: Preferred languages for transcript
            skip_tier1: Skip YouTube API and go straight to Whisper

        Returns:
            TranscriptResult with transcript or error details
        """
        # Clean video ID (remove any URL parts)
        if "youtube.com" in video_id or "youtu.be" in video_id:
            video_id = self._extract_video_id(video_id)

        logger.info(f"Getting transcript for video: {video_id}")

        # Tier 1: Try YouTube API via Tor
        if not skip_tier1:
            result = self._try_youtube_api(video_id, languages)
            if result.success:
                return result

            logger.info(f"Tier 1 failed: {result.error}")

        # Tier 2: Whisper fallback
        logger.info("Falling back to Whisper transcription...")
        result = self._try_whisper_fallback(video_id)

        if not result.success:
            logger.error(f"All transcript methods failed for {video_id}")

        return result

    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats"""
        import re

        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11})(?:[&?]|$)',
            r'(?:embed/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return url  # Return as-is if no pattern matches


# Convenience function
def get_transcript(video_id: str, skip_tor: bool = False) -> TranscriptResult:
    """
    Quick function to get a transcript.

    Args:
        video_id: YouTube video ID or URL
        skip_tor: Skip Tor proxy and go straight to Whisper

    Returns:
        TranscriptResult with transcript text
    """
    service = TranscriptService()
    return service.get_transcript(video_id, skip_tier1=skip_tor)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcript_service.py <video_id_or_url> [--whisper-only]")
        sys.exit(1)

    video_id = sys.argv[1]
    skip_tor = "--whisper-only" in sys.argv

    print(f"\n{'='*60}")
    print(f"Getting transcript for: {video_id}")
    print(f"Skip Tor: {skip_tor}")
    print(f"{'='*60}\n")

    result = get_transcript(video_id, skip_tor=skip_tor)

    print(f"\n{'='*60}")
    print(f"SUCCESS: {result.success}")
    print(f"SOURCE: {result.source.value}")
    print(f"LANGUAGE: {result.language}")

    if result.success:
        print(f"LENGTH: {len(result.transcript)} characters")
        print(f"\nFIRST 500 CHARS:\n{result.transcript[:500]}...")
    else:
        print(f"ERROR: {result.error}")

    print(f"{'='*60}\n")
