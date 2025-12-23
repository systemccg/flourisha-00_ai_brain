#!/usr/bin/env python3
"""
YouTube Learning Processor
Processes liked YouTube videos to create summaries and extract Flourisha improvements.

Usage:
    python3 process_likes.py                    # Process all new liked videos
    python3 process_likes.py --auth             # Authenticate with YouTube
    python3 process_likes.py --dry-run          # Preview without processing
    python3 process_likes.py --video-url URL    # Process specific video
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import re

# Third-party imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("Error: Required packages not installed.")
    print("Run: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client youtube-transcript-api")
    sys.exit(1)

# Configuration
CONFIG_DIR = Path.home() / '.config' / 'youtube-processor'
AI_BRAIN_CREDS = Path('/root/flourisha/00_AI_Brain/credentials')
CREDENTIALS_FILE = AI_BRAIN_CREDS / 'youtube_oauth.json'
TOKEN_FILE = AI_BRAIN_CREDS / 'youtube_token.json'
STATE_FILE = CONFIG_DIR / 'processed_videos.json'
CONFIG_FILE = CONFIG_DIR / 'config.json'

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Default configuration
DEFAULT_CONFIG = {
    "storage": {
        "project_root": "/root/flourisha/01f_Flourisha_Projects/flourisha-enhancements",
        "learnings_dir": "youtube-learnings",
        "ideas_dir": "improvement-ideas"
    },
    "processing": {
        "relevance_threshold": 6,
        "auto_categorize": True,
        "create_improvement_proposals": True,
        "min_video_length": 300
    },
    "categories": {
        "flourisha-improvements": {"keywords": ["ai agent", "automation", "workflow", "infrastructure", "context", "memory"]},
        "ai-tech-learning": {"keywords": ["ai", "machine learning", "llm", "neural", "model"]},
        "business-strategy": {"keywords": ["business", "strategy", "growth", "revenue", "operations"]},
        "productivity": {"keywords": ["productivity", "workflow", "efficiency", "time management"]},
        "development": {"keywords": ["programming", "code", "software", "development", "engineering"]},
        "other": {"keywords": []}
    }
}


class YouTubeLearningProcessor:
    """Process YouTube liked videos into organized learnings."""

    def __init__(self, config_path=None, dry_run=False):
        """Initialize processor with configuration."""
        self.dry_run = dry_run
        self.config = self._load_config(config_path)
        self.state = self._load_state()
        self.youtube = None

        # Set up paths
        self.project_root = Path(self.config['storage']['project_root'])
        self.learnings_dir = self.project_root / self.config['storage']['learnings_dir']
        self.ideas_dir = self.project_root / self.config['storage']['ideas_dir']

        # Ensure directories exist
        if not self.dry_run:
            self.learnings_dir.mkdir(parents=True, exist_ok=True)
            self.ideas_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path=None):
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        elif CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            # Create default config
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            return DEFAULT_CONFIG

    def _load_state(self):
        """Load processing state."""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {"last_processed": None, "videos": {}}

    def _save_state(self):
        """Save processing state."""
        if not self.dry_run:
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)

    def authenticate(self, force_reauth=False):
        """Authenticate with YouTube API."""
        creds = None

        if TOKEN_FILE.exists() and not force_reauth:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
                    print("\nSetup Instructions:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Enable YouTube Data API v3")
                    print("3. Create OAuth 2.0 credentials")
                    print("4. Download client_secret.json")
                    print(f"5. Save to {CREDENTIALS_FILE}")
                    sys.exit(1)

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            if not self.dry_run:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())

        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✓ Authenticated with YouTube API")

    def get_liked_videos(self, max_results=50):
        """Fetch liked videos from YouTube."""
        if not self.youtube:
            self.authenticate()

        print(f"\n📺 Fetching liked videos (max {max_results})...")

        liked_videos = []
        request = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            myRating='like',
            maxResults=max_results
        )

        while request and len(liked_videos) < max_results:
            response = request.execute()
            liked_videos.extend(response.get('items', []))
            request = self.youtube.videos().list_next(request, response)

        print(f"✓ Found {len(liked_videos)} liked videos")
        return liked_videos

    def get_video_by_url(self, url):
        """Get video details by URL."""
        if not self.youtube:
            self.authenticate()

        # Extract video ID from URL
        video_id = self._extract_video_id(url)
        if not video_id:
            print(f"Error: Could not extract video ID from URL: {url}")
            return None

        request = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        response = request.execute()

        items = response.get('items', [])
        return items[0] if items else None

    def _extract_video_id(self, url):
        """Extract video ID from YouTube URL."""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_transcript(self, video_id):
        """Get video transcript."""
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            return ' '.join([entry['text'] for entry in transcript_list])
        except Exception as e:
            print(f"  ⚠️  Transcript not available: {e}")
            return None

    def summarize_with_ai(self, video_data, transcript):
        """Generate AI summary using Claude."""
        # This would call Claude API - for now, return structured template
        title = video_data['snippet']['title']
        channel = video_data['snippet']['channelTitle']
        description = video_data['snippet'].get('description', '')

        # Build prompt for Claude
        prompt = f"""Analyze this YouTube video and provide a structured summary:

Title: {title}
Channel: {channel}
Description: {description[:500]}
Transcript: {transcript[:3000] if transcript else 'Not available'}

Provide:
1. Summary (2-3 paragraphs)
2. Key Points (5-7 bullet points)
3. Main Concepts (frameworks, tools, techniques)
4. Category (flourisha-improvements, ai-tech-learning, business-strategy, productivity, development, other)
5. Flourisha Relevance Score (0-10): How applicable is this to improving Flourisha AI infrastructure?
6. Actionable Insights (specific things that could be implemented)

Format as JSON with keys: summary, key_points, concepts, category, relevance_score, insights"""

        # For now, return a mock response - you'll integrate with Claude API
        # This is where you'd call: anthropic.messages.create(...)

        return self._mock_ai_response(title, channel, transcript)

    def _mock_ai_response(self, title, channel, transcript):
        """Mock AI response for testing - replace with actual Claude API call."""
        # Categorize based on keywords
        category = self._categorize_content(title, transcript or "")

        # Score relevance based on category and keywords
        relevance = self._score_relevance(title, transcript or "", category)

        return {
            "summary": f"This video from {channel} discusses {title}. [AI would generate 2-3 paragraph summary here]",
            "key_points": [
                "First key point extracted from content",
                "Second key point about the main topic",
                "Third important insight",
                "Fourth actionable item",
                "Fifth technical detail"
            ],
            "concepts": {
                "Framework 1": "Description of framework or concept",
                "Tool/Technique": "How it's used or applied"
            },
            "category": category,
            "relevance_score": relevance,
            "insights": [
                "Actionable insight 1",
                "Actionable insight 2",
                "Implementation idea 3"
            ]
        }

    def _categorize_content(self, title, content):
        """Categorize content based on keywords."""
        text = (title + " " + content).lower()

        # Check each category's keywords
        category_scores = {}
        for cat, data in self.config['categories'].items():
            if cat == 'other':
                continue
            score = sum(1 for keyword in data['keywords'] if keyword.lower() in text)
            category_scores[cat] = score

        # Return category with highest score, or 'other' if none match
        if category_scores and max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        return 'other'

    def _score_relevance(self, title, content, category):
        """Score Flourisha relevance (0-10)."""
        if category == 'flourisha-improvements':
            return 9
        elif category in ['ai-tech-learning', 'productivity']:
            return 6
        elif category in ['development', 'business-strategy']:
            return 4
        else:
            return 2

    def create_summary_file(self, video_data, ai_summary):
        """Create markdown summary file."""
        video_id = video_data['id']
        title = video_data['snippet']['title']
        channel = video_data['snippet']['channelTitle']
        published = video_data['snippet']['publishedAt'][:10]

        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-')[:50]
        filename = f"{datetime.now().strftime('%Y-%m-%d')}_{safe_title}.md"
        filepath = self.learnings_dir / filename

        # Build frontmatter
        frontmatter = f"""---
title: {title}
channel: {channel}
url: https://youtube.com/watch?v={video_id}
date_published: {published}
date_processed: {datetime.now().strftime('%Y-%m-%d')}
category: {ai_summary['category']}
flourisha_relevance: {ai_summary['relevance_score']}
---

# {title}

**Channel:** {channel}
**Published:** {published}
**Link:** [Watch on YouTube](https://youtube.com/watch?v={video_id})

---

## Summary

{ai_summary['summary']}

---

## Key Points

{chr(10).join(f"- {point}" for point in ai_summary['key_points'])}

---

## Main Concepts

{chr(10).join(f"- **{concept}:** {desc}" for concept, desc in ai_summary.get('concepts', {}).items())}

---

## Actionable Insights

{chr(10).join(f"{i+1}. {insight}" for i, insight in enumerate(ai_summary.get('insights', [])))}

---

## Flourisha Improvements

> **Relevance Score:** {ai_summary['relevance_score']}/10

{self._generate_improvement_note(ai_summary)}

---

**Processed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by youtube-learning-processor
"""

        if not self.dry_run:
            with open(filepath, 'w') as f:
                f.write(frontmatter)
            print(f"  ✓ Created summary: {filename}")
        else:
            print(f"  [DRY RUN] Would create: {filename}")

        return str(filepath)

    def _generate_improvement_note(self, ai_summary):
        """Generate improvement section based on relevance."""
        score = ai_summary['relevance_score']

        if score >= 8:
            return f"""This video is highly relevant to Flourisha improvements.

See detailed improvement proposal: [To be created in improvement-ideas/]"""
        elif score >= 6:
            return "This video contains some applicable concepts for Flourisha infrastructure."
        else:
            return "General learning content - not specific to Flourisha improvements."

    def create_improvement_proposal(self, video_data, ai_summary, summary_file):
        """Create improvement proposal if relevant enough."""
        if ai_summary['relevance_score'] < self.config['processing']['relevance_threshold']:
            return None

        # Get next improvement ID
        existing_ideas = list(self.ideas_dir.glob('*.md'))
        if existing_ideas:
            ids = [int(f.stem.split('-')[0]) for f in existing_ideas if f.stem[0].isdigit()]
            next_id = max(ids) + 1 if ids else 1
        else:
            next_id = 1

        title = video_data['snippet']['title']
        video_id = video_data['id']
        safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-')[:30]
        filename = f"{next_id:03d}-{safe_title}.md"
        filepath = self.ideas_dir / filename

        proposal = f"""---
title: Improvement from {title}
source_video: https://youtube.com/watch?v={video_id}
source_summary: {summary_file}
category: {ai_summary['category']}
priority: {'high' if ai_summary['relevance_score'] >= 8 else 'medium'}
status: proposed
date_created: {datetime.now().strftime('%Y-%m-%d')}
---

# Improvement: [To be refined based on video content]

**Source:** [{title}]({summary_file})
**Priority:** {'High' if ai_summary['relevance_score'] >= 8 else 'Medium'}
**Status:** Proposed

---

## Overview

[High-level description of the improvement idea]

---

## Current State

[What's the current limitation or gap?]

---

## Proposed Solution

**High-Level Approach:**

{chr(10).join(f"{i+1}. {insight}" for i, insight in enumerate(ai_summary.get('insights', [])))}

---

## Affected Systems

[Which parts of Flourisha would be impacted?]

---

## Implementation Considerations

**Benefits:**
- [Benefit 1]
- [Benefit 2]

**Challenges:**
- [Challenge 1]
- [Challenge 2]

**Estimated Complexity:** Medium

---

## Next Steps

1. Review video in detail
2. Research implementation options
3. Design solution architecture
4. Create implementation plan

---

**Created:** {datetime.now().strftime('%Y-%m-%d')} by youtube-learning-processor
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""

        if not self.dry_run:
            with open(filepath, 'w') as f:
                f.write(proposal)
            print(f"  ✓ Created improvement proposal: {filename}")
        else:
            print(f"  [DRY RUN] Would create improvement: {filename}")

        return str(filepath)

    def process_video(self, video_data):
        """Process a single video."""
        video_id = video_data['id']
        title = video_data['snippet']['title']

        # Check if already processed
        if video_id in self.state['videos']:
            print(f"\n⏭️  Skipping (already processed): {title}")
            return False

        print(f"\n📹 Processing: {title}")

        # Get transcript
        print("  Fetching transcript...")
        transcript = self.get_transcript(video_id)

        if not transcript:
            print("  ⚠️  No transcript available - will use title/description only")

        # Generate AI summary
        print("  Generating AI summary...")
        ai_summary = self.summarize_with_ai(video_data, transcript)

        print(f"  Category: {ai_summary['category']}")
        print(f"  Relevance: {ai_summary['relevance_score']}/10")

        # Create summary file
        summary_file = self.create_summary_file(video_data, ai_summary)

        # Create improvement proposal if relevant
        improvement_file = None
        if self.config['processing']['create_improvement_proposals']:
            if ai_summary['relevance_score'] >= self.config['processing']['relevance_threshold']:
                improvement_file = self.create_improvement_proposal(
                    video_data, ai_summary, summary_file
                )

        # Update state
        if not self.dry_run:
            self.state['videos'][video_id] = {
                'processed_date': datetime.now().isoformat(),
                'title': title,
                'category': ai_summary['category'],
                'relevance_score': ai_summary['relevance_score'],
                'summary_file': summary_file,
                'improvement_file': improvement_file
            }
            self.state['last_processed'] = datetime.now().isoformat()
            self._save_state()

        return True

    def process_all_likes(self, max_results=50):
        """Process all liked videos."""
        videos = self.get_liked_videos(max_results)

        processed = 0
        skipped = 0

        for video in videos:
            if self.process_video(video):
                processed += 1
            else:
                skipped += 1

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}📊 Summary:")
        print(f"  Processed: {processed}")
        print(f"  Skipped: {skipped}")
        print(f"  Total: {len(videos)}")

        if not self.dry_run:
            print(f"\n✓ Results saved to:")
            print(f"  Summaries: {self.learnings_dir}")
            print(f"  Improvements: {self.ideas_dir}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Process YouTube liked videos')
    parser.add_argument('--auth', action='store_true', help='Authenticate with YouTube')
    parser.add_argument('--dry-run', action='store_true', help='Preview without processing')
    parser.add_argument('--video-url', help='Process specific video by URL')
    parser.add_argument('--max-results', type=int, default=50, help='Max videos to fetch')
    parser.add_argument('--config', help='Path to custom config file')

    args = parser.parse_args()

    # Initialize processor
    processor = YouTubeLearningProcessor(config_path=args.config, dry_run=args.dry_run)

    # Handle authentication-only mode
    if args.auth:
        processor.authenticate(force_reauth=True)
        print("✓ Authentication complete")
        return

    # Authenticate
    processor.authenticate()

    # Process specific video or all likes
    if args.video_url:
        video = processor.get_video_by_url(args.video_url)
        if video:
            processor.process_video(video)
        else:
            print("Error: Video not found")
    else:
        processor.process_all_likes(max_results=args.max_results)


if __name__ == '__main__':
    main()
