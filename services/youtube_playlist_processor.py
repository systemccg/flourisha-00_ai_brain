#!/usr/bin/env python3
"""
YouTube Playlist-Aware Processor
Processes videos from playlists using category-specific templates.

Usage:
    python youtube_playlist_processor.py process <playlist_name> [--limit N]
    python youtube_playlist_processor.py preview <playlist_name>
    python youtube_playlist_processor.py templates
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from youtube_channel_manager import YouTubeChannelManager

try:
    from transcript_service import get_transcript as get_transcript_service, TranscriptSource
    TRANSCRIPT_SERVICE_AVAILABLE = True
except ImportError:
    TRANSCRIPT_SERVICE_AVAILABLE = False
    print("Warning: transcript_service not available - using fallback")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not installed - AI summaries unavailable")


class PlaylistProcessor:
    """Process YouTube playlists with category-aware templates."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        channel_name: Optional[str] = None
    ):
        """Initialize processor."""
        self.config_path = config_path or Path('/root/flourisha/00_AI_Brain/config/youtube_playlist_templates.json')
        self.config = self._load_config()
        self.channel_manager = YouTubeChannelManager()
        self.channel_name = channel_name
        self.output_base = Path('/root/flourisha')

        # Initialize Anthropic client if available
        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    def _load_config(self) -> Dict[str, Any]:
        """Load template configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        raise FileNotFoundError(f"Config not found: {self.config_path}")

    def get_template_for_playlist(self, playlist_name: str) -> Dict[str, Any]:
        """Get the appropriate template for a playlist."""
        mappings = self.config.get('playlist_mappings', {})
        template_key = mappings.get(playlist_name, self.config['settings']['default_template'])
        return self.config['templates'].get(template_key, self.config['templates']['default'])

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates."""
        templates = []
        for key, template in self.config['templates'].items():
            templates.append({
                'key': key,
                'name': template.get('name', key),
                'description': template.get('description', ''),
                'output_dir': template.get('output_dir', 'N/A')
            })
        return templates

    def preview_playlist(self, playlist_name: str) -> Dict[str, Any]:
        """Preview what would happen if we processed a playlist."""
        # Find playlist
        playlists = self.channel_manager.get_playlists(self.channel_name)
        playlist = next((p for p in playlists if p['title'] == playlist_name), None)

        if not playlist:
            return {'error': f"Playlist '{playlist_name}' not found"}

        template = self.get_template_for_playlist(playlist_name)

        if template.get('action') == 'skip':
            return {
                'playlist': playlist_name,
                'action': 'SKIP',
                'reason': template.get('reason', 'Configured to skip')
            }

        # Get videos
        videos = self.channel_manager.get_playlist_videos(
            playlist['id'],
            channel_name=self.channel_name,
            max_results=10
        )

        return {
            'playlist': playlist_name,
            'video_count': playlist['video_count'],
            'template': template['name'],
            'output_dir': template.get('output_dir'),
            'sample_videos': [v['title'] for v in videos[:5]],
            'prompt_preview': template.get('prompt', '')[:200] + '...'
        }

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text[:50].strip('-')

    def _get_transcript(self, video_id: str) -> Optional[str]:
        """Get transcript using the TranscriptService (Tor + Whisper fallback)."""

        # Use the robust TranscriptService with Tor proxy and Whisper fallback
        if TRANSCRIPT_SERVICE_AVAILABLE:
            try:
                result = get_transcript_service(video_id)

                if result.success:
                    source_name = result.source.value if hasattr(result.source, 'value') else str(result.source)
                    print(f"    Got transcript via {source_name}")

                    transcript = result.transcript

                    # Truncate only if max_length > 0
                    max_length = self.config['settings'].get('transcript_max_length', 0)
                    if max_length > 0 and len(transcript) > max_length:
                        transcript = transcript[:max_length] + '... [truncated]'

                    return transcript
                else:
                    print(f"    TranscriptService failed: {result.error}")
                    return None

            except Exception as e:
                print(f"    TranscriptService error: {str(e)[:100]}")
                return None
        else:
            print(f"    TranscriptService not available")
            return None

    def _generate_summary(self, prompt: str) -> Optional[str]:
        """Generate AI summary using Claude (model from config)."""
        if not self.anthropic_client:
            return None

        model = self.config.get('settings', {}).get('model', 'claude-opus-4-20250514')

        try:
            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"    AI summary error: {e}")
            return None

    def process_video(
        self,
        video: Dict[str, Any],
        template: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Process a single video with a template."""
        video_id = video['video_id']
        title = video['title']
        channel = video.get('channel_title', 'Unknown')
        description = video.get('description', '')

        result = {
            'video_id': video_id,
            'title': title,
            'status': 'pending'
        }

        # Skip template
        if template.get('action') == 'skip':
            result['status'] = 'skipped'
            result['reason'] = template.get('reason')
            return result

        # Get transcript
        print(f"    Fetching transcript...")
        transcript = self._get_transcript(video_id)

        if not transcript:
            if self.config['settings'].get('fallback_to_description') and description:
                print(f"    No transcript, using description")
                transcript = f"[Video Description]\n{description}"
            elif self.config['settings'].get('require_transcript'):
                result['status'] = 'skipped'
                result['reason'] = 'No transcript available'
                return result
            else:
                transcript = f"[No transcript available]\nTitle: {title}\nDescription: {description}"

        # Build prompt (include description for context)
        prompt_template = template.get('prompt', '')
        prompt = prompt_template.format(
            title=title,
            channel=channel,
            description=description or 'No description available',
            transcript=transcript
        )

        # Generate summary
        print(f"    Generating summary...")
        summary = self._generate_summary(prompt)

        if not summary:
            result['status'] = 'error'
            result['reason'] = 'Failed to generate summary'
            return result

        # Build output
        date_str = datetime.now().strftime('%Y-%m-%d')
        title_slug = self._slugify(title)
        filename = template.get('filename_pattern', '{date}_{title_slug}.md').format(
            date=date_str,
            title_slug=title_slug
        )

        output_dir = self.output_base / template.get('output_dir', 'youtube-output')
        output_path = output_dir / filename

        # Get video publish date
        video_date = video.get('published_at', '')[:10] if video.get('published_at') else 'Unknown'

        # Build frontmatter
        frontmatter = template.get('frontmatter', {}).copy()
        frontmatter['title'] = title
        frontmatter['video_id'] = video_id
        frontmatter['video_url'] = f"https://youtube.com/watch?v={video_id}"
        frontmatter['channel'] = channel
        frontmatter['video_date'] = video_date
        frontmatter['processed_date'] = date_str

        # Build markdown content
        fm_yaml = '\n'.join([f"{k}: {v}" for k, v in frontmatter.items()])
        content = f"""---
{fm_yaml}
---

# {title}

| | |
|---|---|
| **Channel** | {channel} |
| **Video Date** | {video_date} |
| **Link** | [Watch on YouTube](https://youtube.com/watch?v={video_id}) |

---

{summary}

---

*Processed: {datetime.now().isoformat()} by youtube-playlist-processor*
"""

        if dry_run:
            result['status'] = 'dry_run'
            result['would_create'] = str(output_path)
            result['summary_preview'] = summary[:300] + '...'
        else:
            # Create output directory and file
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(content)
            result['status'] = 'success'
            result['output_path'] = str(output_path)

        return result

    def process_playlist(
        self,
        playlist_name: str,
        limit: int = 10,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Process videos from a playlist."""
        # Find playlist
        playlists = self.channel_manager.get_playlists(self.channel_name)
        playlist = next((p for p in playlists if p['title'] == playlist_name), None)

        if not playlist:
            return {'error': f"Playlist '{playlist_name}' not found"}

        template = self.get_template_for_playlist(playlist_name)

        if template.get('action') == 'skip':
            return {
                'playlist': playlist_name,
                'status': 'skipped',
                'reason': template.get('reason')
            }

        print(f"\n Processing playlist: {playlist_name}")
        print(f"   Template: {template['name']}")
        print(f"   Output: {template.get('output_dir')}")

        # Get videos
        videos = self.channel_manager.get_playlist_videos(
            playlist['id'],
            channel_name=self.channel_name,
            max_results=limit
        )

        results = {
            'playlist': playlist_name,
            'template': template['name'],
            'videos_found': len(videos),
            'processed': [],
            'skipped': [],
            'errors': []
        }

        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] {video['title'][:50]}...")

            result = self.process_video(video, template, dry_run)

            if result['status'] == 'success' or result['status'] == 'dry_run':
                results['processed'].append(result)
            elif result['status'] == 'skipped':
                results['skipped'].append(result)
            else:
                results['errors'].append(result)

        return results


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(
        description='YouTube Playlist-Aware Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Templates command
    subparsers.add_parser('templates', help='List available templates')

    # Preview command
    preview_parser = subparsers.add_parser('preview', help='Preview playlist processing')
    preview_parser.add_argument('playlist', help='Playlist name')
    preview_parser.add_argument('--channel', '-c', help='Channel name')

    # Process command
    process_parser = subparsers.add_parser('process', help='Process a playlist')
    process_parser.add_argument('playlist', help='Playlist name')
    process_parser.add_argument('--limit', '-l', type=int, default=5, help='Max videos to process')
    process_parser.add_argument('--channel', '-c', help='Channel name')
    process_parser.add_argument('--dry-run', '-n', action='store_true', help='Preview without saving')

    args = parser.parse_args()

    # Load environment
    from dotenv import load_dotenv
    load_dotenv('/root/.claude/.env')

    processor = PlaylistProcessor(
        channel_name=getattr(args, 'channel', None)
    )

    if args.command == 'templates':
        templates = processor.list_templates()
        print(f"\n{'Template':<25} {'Name':<25} {'Output Directory'}")
        print("-" * 80)
        for t in templates:
            print(f"{t['key']:<25} {t['name']:<25} {t['output_dir']}")

    elif args.command == 'preview':
        result = processor.preview_playlist(args.playlist)
        print(json.dumps(result, indent=2))

    elif args.command == 'process':
        result = processor.process_playlist(
            args.playlist,
            limit=args.limit,
            dry_run=args.dry_run
        )

        print(f"\n{'='*60}")
        print(f"Summary for: {result.get('playlist')}")
        print(f"{'='*60}")
        print(f"  Processed: {len(result.get('processed', []))}")
        print(f"  Skipped:   {len(result.get('skipped', []))}")
        print(f"  Errors:    {len(result.get('errors', []))}")

        if result.get('processed'):
            print(f"\nProcessed videos:")
            for v in result['processed']:
                path = v.get('output_path') or v.get('would_create')
                print(f"  - {v['title'][:40]}...")
                print(f"    -> {path}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
