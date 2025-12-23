#!/usr/bin/env python3
"""
Claude API Integration for YouTube Learning Processor
Provides AI summarization using Claude API.

Usage:
    from claude_integration import ClaudeSummarizer

    summarizer = ClaudeSummarizer()
    summary = summarizer.summarize(video_data, transcript)
"""

import os
import json
from typing import Dict, Any, Optional

try:
    import anthropic
except ImportError:
    print("Warning: anthropic package not installed. Install with: pip install anthropic")
    anthropic = None


class ClaudeSummarizer:
    """Summarize YouTube videos using Claude API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4"):
        """Initialize Claude client."""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None

        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def summarize(self, video_data: Dict[str, Any], transcript: Optional[str]) -> Dict[str, Any]:
        """
        Generate AI summary of video content.

        Args:
            video_data: Video metadata from YouTube API
            transcript: Video transcript text (or None)

        Returns:
            Dict with summary, key_points, concepts, category, relevance_score, insights
        """
        if not self.client:
            print("Warning: Claude API not configured. Using mock responses.")
            return self._mock_response(video_data, transcript)

        # Build prompt
        prompt = self._build_prompt(video_data, transcript)

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text

            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If not JSON, parse text format
                return self._parse_text_response(response_text)

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return self._mock_response(video_data, transcript)

    def _build_prompt(self, video_data: Dict[str, Any], transcript: Optional[str]) -> str:
        """Build Claude prompt for video summarization."""
        title = video_data['snippet']['title']
        channel = video_data['snippet']['channelTitle']
        description = video_data['snippet'].get('description', '')[:500]

        prompt = f"""Analyze this YouTube video and provide a structured summary.

**Video Information:**
- Title: {title}
- Channel: {channel}
- Description: {description}

{"**Transcript:**" + transcript[:3000] if transcript else "**Note:** No transcript available - analyze based on title and description"}

**Required Output (JSON format):**

Provide your analysis as a JSON object with these exact keys:

{{
  "summary": "2-3 paragraph summary of the video content and main message",
  "key_points": [
    "First key point or insight",
    "Second key point or insight",
    "Third key point or insight",
    "Fourth key point or insight",
    "Fifth key point or insight"
  ],
  "concepts": {{
    "Concept/Framework Name": "Brief description of the concept or how it's applied",
    "Tool/Technique": "Description of the tool or technique discussed"
  }},
  "category": "One of: flourisha-improvements, ai-tech-learning, business-strategy, productivity, development, other",
  "relevance_score": 0-10,
  "insights": [
    "First actionable insight or implementation idea",
    "Second actionable insight",
    "Third actionable insight"
  ]
}}

**Category Guidelines:**
- **flourisha-improvements** (8-10 relevance): AI infrastructure, agent systems, automation, context management, workflow optimization specific to AI assistants
- **ai-tech-learning** (5-7 relevance): General AI/ML concepts, models, techniques
- **business-strategy** (3-5 relevance): Business operations, strategy, growth
- **productivity** (4-6 relevance): Personal productivity, time management, workflows
- **development** (3-5 relevance): Software development, programming practices
- **other** (0-3 relevance): General content not fitting above

**Relevance Score (for Flourisha AI infrastructure):**
- 9-10: Directly applicable to improving Flourisha (agent memory, context optimization, automation)
- 7-8: Very relevant AI concepts applicable to infrastructure
- 5-6: Somewhat relevant (general AI/productivity concepts)
- 3-4: Tangentially related
- 0-2: Not relevant to AI infrastructure

Return ONLY the JSON object, no additional text."""

        return prompt

    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text-format response if JSON parsing fails."""
        # Extract sections from text
        # This is a fallback - ideally Claude returns JSON

        lines = response.split('\n')
        result = {
            "summary": "",
            "key_points": [],
            "concepts": {},
            "category": "other",
            "relevance_score": 5,
            "insights": []
        }

        current_section = None

        for line in lines:
            line = line.strip()

            if 'summary:' in line.lower():
                current_section = 'summary'
            elif 'key points:' in line.lower() or 'key point' in line.lower():
                current_section = 'key_points'
            elif 'concepts:' in line.lower() or 'concept' in line.lower():
                current_section = 'concepts'
            elif 'category:' in line.lower():
                current_section = 'category'
            elif 'relevance' in line.lower() and 'score' in line.lower():
                current_section = 'relevance_score'
            elif 'insights:' in line.lower() or 'actionable' in line.lower():
                current_section = 'insights'
            elif line and current_section:
                if current_section == 'summary':
                    result['summary'] += line + ' '
                elif current_section == 'key_points' and line.startswith('-'):
                    result['key_points'].append(line[1:].strip())
                elif current_section == 'insights' and (line.startswith('-') or line[0].isdigit()):
                    result['insights'].append(line.lstrip('-').lstrip('0123456789.').strip())

        return result

    def _mock_response(self, video_data: Dict[str, Any], transcript: Optional[str]) -> Dict[str, Any]:
        """Generate mock response when Claude API not available."""
        title = video_data['snippet']['title']
        channel = video_data['snippet']['channelTitle']

        return {
            "summary": f"This video from {channel} titled '{title}' discusses [AI-generated summary would appear here]. The content covers key concepts and provides actionable insights for implementation.",
            "key_points": [
                "Key insight extracted from video content",
                "Important technique or framework discussed",
                "Practical application or use case",
                "Technical detail or specification",
                "Best practice or recommendation"
            ],
            "concepts": {
                "Main Framework": "Description of the framework or concept presented",
                "Tool/Technique": "How the tool or technique is used"
            },
            "category": self._guess_category(title, transcript or ""),
            "relevance_score": 5,
            "insights": [
                "Actionable insight that could be implemented",
                "Another practical application",
                "Improvement idea for existing systems"
            ]
        }

    def _guess_category(self, title: str, content: str) -> str:
        """Guess category based on keywords."""
        text = (title + " " + content).lower()

        categories = {
            'flourisha-improvements': ['ai agent', 'automation', 'workflow', 'infrastructure', 'context', 'memory'],
            'ai-tech-learning': ['ai', 'machine learning', 'llm', 'neural', 'model', 'gpt'],
            'business-strategy': ['business', 'strategy', 'growth', 'revenue', 'operations'],
            'productivity': ['productivity', 'workflow', 'efficiency', 'time management'],
            'development': ['programming', 'code', 'software', 'development', 'engineering']
        }

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category

        return 'other'


# Example usage
if __name__ == '__main__':
    summarizer = ClaudeSummarizer()

    # Mock video data
    mock_video = {
        'snippet': {
            'title': 'Building AI Agents with Memory',
            'channelTitle': 'AI Explained',
            'description': 'Learn how to build AI agents with persistent memory using vector databases'
        }
    }

    mock_transcript = """
    Today we're going to discuss how to build AI agents with memory capabilities.
    Vector databases like ChromaDB enable semantic search across past conversations.
    This allows agents to remember context and provide more personalized responses.
    """

    result = summarizer.summarize(mock_video, mock_transcript)
    print(json.dumps(result, indent=2))
