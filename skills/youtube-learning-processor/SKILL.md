---
name: youtube-learning-processor
description: |
  Automatically processes YouTube videos you've liked to create intelligent summaries,
  categorize content, and extract actionable Flourisha improvement ideas.

  Fetches liked videos, extracts transcripts, generates AI summaries, intelligently
  categorizes into PARA structure, and creates actionable implementation plans for
  infrastructure improvements.

  USE WHEN:
  - "process my youtube likes"
  - "summarize youtube videos"
  - "extract youtube learnings"
  - After watching educational content worth capturing
  - To review improvement ideas from videos

version: 1.0.0
tags: [learning, youtube, automation, knowledge-capture, flourisha-improvements]
---

# YouTube Learning Processor

**Purpose:** Transform YouTube likes into organized knowledge and actionable Flourisha improvements

---

## When to Activate This Skill

**Manual Triggers:**
- "process my youtube likes"
- "summarize youtube videos I liked"
- "extract learnings from youtube"
- "check youtube for flourisha improvements"
- "sync youtube knowledge"

**Automatic Triggers:**
- Can be scheduled (daily/weekly) via cron
- After watching multiple educational videos
- When accumulating improvement ideas

---

## What This Skill Does

### 1. Fetches Your Liked Videos
- Connects to YouTube API
- Gets videos you've thumbs-up'd
- Filters for new/unprocessed videos
- Tracks processing state

### 2. Extracts Content
- Downloads video transcripts (YouTube API)
- Falls back to audio → transcript if needed
- Extracts video metadata (title, description, tags)
- Captures channel information

### 3. Generates Intelligent Summaries
- AI-powered summarization of content
- Key points extraction
- Concepts and frameworks identified
- Actionable insights highlighted

### 4. Categorizes Intelligently
- **Flourisha Improvements** - Ideas to enhance your AI infrastructure
- **AI/Tech Learning** - General AI and technology knowledge
- **Business/Strategy** - Business operations and strategy
- **Productivity** - Productivity and workflow optimization
- **Development** - Software development practices
- **Other** - Miscellaneous valuable content

### 5. Creates Actionable Plans
For videos categorized as "Flourisha Improvements":
- Extracts specific improvement ideas
- Creates high-level implementation overview
- Identifies affected systems/components
- Suggests priority level
- Links to original video

### 6. Organizes in PARA Structure
**Storage Location:** `/root/flourisha/01f_Flourisha_Projects/flourisha-enhancements/`

```
01f_Flourisha_Projects/flourisha-enhancements/
├── README.md                           # Project overview
├── youtube-learnings/                  # All processed videos
│   ├── 2025-11-20_video-title.md      # Individual summaries
│   └── index.md                        # Learning index
├── improvement-ideas/                  # Actionable improvements
│   ├── 001-idea-name.md               # Improvement proposals
│   ├── 002-another-idea.md
│   └── index.md                        # Ideas index
└── implementation-queue/               # Ready to implement
    ├── high-priority/
    ├── medium-priority/
    └── low-priority/
```

---

## Prerequisites

### YouTube API Setup

**1. Get YouTube API Credentials:**
```bash
# Navigate to Google Cloud Console
# https://console.cloud.google.com/

# Enable YouTube Data API v3
# Create OAuth 2.0 credentials
# Download client_secret.json
```

**2. Store Credentials:**
```bash
mkdir -p ~/.config/youtube-processor
mv ~/Downloads/client_secret.json ~/.config/youtube-processor/
```

**3. First-time Authentication:**
```bash
# Run processor first time - will open browser for OAuth
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --auth
```

### Dependencies

```bash
# Install required packages
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client youtube-transcript-api
```

---

## Usage

### Manual Processing

**Process all new liked videos:**
```bash
# Activate skill
"process my youtube likes"

# Or run script directly
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py
```

**Process specific video:**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --video-url "https://youtube.com/watch?v=VIDEO_ID"
```

**Dry run (preview what would be processed):**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --dry-run
```

### Automatic Scheduling

**Daily processing (recommended):**
```bash
# Add to crontab
crontab -e

# Process at 2 AM daily
0 2 * * * /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py >> /var/log/youtube_processor.log 2>&1
```

**Weekly processing:**
```bash
# Process every Sunday at 8 AM
0 8 * * 0 /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py
```

---

## Workflow

### Step 1: Fetch Liked Videos

```python
# Connect to YouTube API
youtube = get_authenticated_service()

# Get liked videos playlist
liked_videos = youtube.playlistItems().list(
    part='snippet',
    playlistId='LL',  # Liked videos playlist
    maxResults=50
).execute()
```

### Step 2: Check Processing State

```bash
# Track processed videos in state file
~/.config/youtube-processor/processed_videos.json

# Skip already processed videos
# Process only new likes since last run
```

### Step 3: Extract Transcript

```python
from youtube_transcript_api import YouTubeTranscriptApi

# Try to get transcript
transcript = YouTubeTranscriptApi.get_transcript(video_id)

# Combine transcript segments
full_text = ' '.join([entry['text'] for entry in transcript])
```

### Step 4: Generate Summary with AI

```python
# Use Claude to summarize
prompt = f"""
Analyze this YouTube video and provide:

1. **Summary** (2-3 paragraphs)
2. **Key Points** (bullet list)
3. **Main Concepts** (frameworks, tools, techniques mentioned)
4. **Category** (Flourisha Improvements, AI/Tech Learning, Business/Strategy, etc.)
5. **Actionable Insights** (what can be implemented)
6. **Flourisha Relevance** (if applicable - how this could improve Flourisha infrastructure)

Video Title: {title}
Channel: {channel}
Transcript:
{transcript}
"""

summary = claude_api.summarize(prompt)
```

### Step 5: Categorize Content

**AI-powered categorization:**
- Analyzes content themes
- Identifies primary category
- Can assign multiple tags
- Determines Flourisha relevance score (0-10)

**Categories:**
- `flourisha-improvements` - Score 8-10 on relevance
- `ai-tech-learning` - AI/ML content
- `business-strategy` - Business operations
- `productivity` - Workflow optimization
- `development` - Software development
- `other` - General learning

### Step 6: Create Summary Note

**File:** `01f_Flourisha_Projects/flourisha-enhancements/youtube-learnings/2025-11-20_video-title.md`

```markdown
---
title: Video Title Here
channel: Channel Name
url: https://youtube.com/watch?v=VIDEO_ID
date_liked: 2025-11-20
date_processed: 2025-11-20
category: flourisha-improvements
tags: [ai, automation, infrastructure]
flourisha_relevance: 9
---

# Video Title Here

**Channel:** Channel Name
**Duration:** 15:32
**Link:** [Watch on YouTube](https://youtube.com/watch?v=VIDEO_ID)

---

## Summary

[AI-generated 2-3 paragraph summary]

---

## Key Points

- First key point
- Second key point
- Third key point

---

## Main Concepts

- **Concept 1:** Description
- **Concept 2:** Description
- **Framework:** Name and application

---

## Actionable Insights

1. Insight that can be implemented
2. Another actionable item
3. Tool or technique to try

---

## Flourisha Improvements Identified

> **Relevance Score:** 9/10

This video suggests improvements to:
- AI agent orchestration
- Context management
- Workflow automation

See detailed improvement proposal: [001-improvement-name.md](../improvement-ideas/001-improvement-name.md)

---

**Processed:** 2025-11-20 by youtube-learning-processor
```

### Step 7: Create Improvement Proposal (if relevant)

**File:** `01f_Flourisha_Projects/flourisha-enhancements/improvement-ideas/001-agent-memory-system.md`

```markdown
---
title: Implement Agent Memory System
source_video: https://youtube.com/watch?v=VIDEO_ID
category: infrastructure
priority: high
status: proposed
date_created: 2025-11-20
affected_systems: [agents, context-management]
---

# Improvement: Implement Agent Memory System

**Source:** [Video Title](../youtube-learnings/2025-11-20_video-title.md)
**Priority:** High
**Status:** Proposed

---

## Overview

Implement persistent memory system for agents to retain context across sessions,
improving continuity and reducing context loading overhead.

---

## Current State

- Agents load full context each session
- No memory of previous interactions
- Context window limitations
- Repeated explanations needed

---

## Proposed Solution

**High-Level Approach:**

1. **Vector Database Integration**
   - Store conversation summaries in vector DB
   - Index by topic, date, entities
   - Enable semantic search

2. **Memory Types**
   - Short-term: Current session context
   - Long-term: Important facts, preferences, decisions
   - Episodic: Specific event memories

3. **Retrieval Strategy**
   - Auto-retrieve relevant memories at session start
   - Context-aware memory injection
   - Importance-based filtering

---

## Affected Systems

- **Agent Context Loading** (`/root/.claude/hooks/load-core-context.ts`)
- **Session Management** (SessionStart hooks)
- **Database** (Neo4j or new vector DB)
- **Skills System** (memory-aware skills)

---

## Implementation Considerations

**Benefits:**
- Improved context continuity
- Reduced token usage
- Better long-term assistance
- Personalized responses

**Challenges:**
- Storage and indexing infrastructure
- Privacy and security
- Memory relevance scoring
- Retrieval performance

**Estimated Complexity:** Medium-High

---

## Next Steps

1. Research vector DB options (Chroma, Pinecone, Weaviate)
2. Design memory schema
3. Implement basic storage layer
4. Create retrieval mechanism
5. Test with sample conversations
6. Integrate into agent workflows

---

## Related Videos

- [Video Title](../youtube-learnings/2025-11-20_video-title.md)

---

**Created:** 2025-11-20 by youtube-learning-processor
**Last Updated:** 2025-11-20
```

---

## Output Structure

### Summary Notes

**Location:** `youtube-learnings/`
**Format:** One file per video
**Naming:** `YYYY-MM-DD_sanitized-video-title.md`

**Contents:**
- Video metadata
- AI summary
- Key points
- Concepts/frameworks
- Actionable insights
- Flourisha relevance (if applicable)

### Improvement Ideas

**Location:** `improvement-ideas/`
**Format:** Numbered proposals
**Naming:** `NNN-improvement-slug.md`

**Contents:**
- Overview of improvement
- Current state analysis
- Proposed solution (high-level)
- Affected systems
- Implementation considerations
- Next steps

### Index Files

**youtube-learnings/index.md:**
- Chronological list of all processed videos
- Grouped by category
- Filterable by tags

**improvement-ideas/index.md:**
- All improvement proposals
- Sorted by priority
- Status tracking (proposed, in-progress, completed, archived)

---

## Configuration

### Config File

**Location:** `~/.config/youtube-processor/config.json`

```json
{
  "youtube_api": {
    "credentials_path": "/root/flourisha/00_AI_Brain/credentials/youtube_oauth.json",
    "token_path": "/root/flourisha/00_AI_Brain/credentials/youtube_token.json"
  },
  "storage": {
    "project_root": "/root/flourisha/01f_Flourisha_Projects/flourisha-enhancements",
    "learnings_dir": "youtube-learnings",
    "ideas_dir": "improvement-ideas"
  },
  "processing": {
    "relevance_threshold": 6,
    "auto_categorize": true,
    "create_improvement_proposals": true,
    "min_video_length": 300
  },
  "ai": {
    "model": "claude-sonnet-4",
    "summarization_prompt": "custom_prompt.txt"
  }
}
```

### State Tracking

**Location:** `~/.config/youtube-processor/processed_videos.json`

```json
{
  "last_processed": "2025-11-20T10:30:00Z",
  "videos": {
    "VIDEO_ID_1": {
      "processed_date": "2025-11-20",
      "category": "flourisha-improvements",
      "relevance_score": 9,
      "summary_file": "2025-11-20_video-title.md",
      "improvement_created": true
    }
  }
}
```

---

## Examples

### Example 1: AI Infrastructure Video

**Input:** Liked video about "Building AI Agent Memory Systems"

**Output:**
1. Summary: `youtube-learnings/2025-11-20_building-ai-agent-memory.md`
2. Category: `flourisha-improvements`
3. Relevance: 9/10
4. Improvement: `improvement-ideas/001-agent-memory-system.md`

### Example 2: General Learning

**Input:** Liked video about "Python Best Practices"

**Output:**
1. Summary: `youtube-learnings/2025-11-20_python-best-practices.md`
2. Category: `development`
3. Relevance: 4/10 (general, not Flourisha-specific)
4. No improvement proposal created

---

## Troubleshooting

### Issue: YouTube API Quota Exceeded

```bash
# Quota resets daily (midnight Pacific Time)
# Check quota usage: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas

# Solutions:
# 1. Process fewer videos per run
# 2. Increase API quota (paid)
# 3. Use multiple projects/keys
```

### Issue: Transcript Not Available

```bash
# Some videos don't have transcripts
# Fallback options:

# 1. Use whisper for audio transcription
pip install openai-whisper
whisper audio.mp3 --model base

# 2. Skip and log
echo "Video VIDEO_ID: No transcript available" >> ~/.config/youtube-processor/skipped.log
```

### Issue: Authentication Failed

```bash
# Re-authenticate
rm ~/.config/youtube-processor/token.json
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --auth
```

---

## Integration with Flourisha

### With update-flourisha-brain

After processing videos:
```bash
# Update brain with new learnings
"update the brain with youtube learnings"

# Flourisha will:
# - Check for new improvement ideas
# - Update relevant documentation
# - Sync to Google Drive
```

### With Task Management

Improvement ideas can be promoted to tasks:
```bash
# Convert improvement to task/project
# Move from improvement-ideas/ to active project
# Add to task tracker
```

### With Research Skill

Videos can trigger deeper research:
```bash
# If video mentions interesting topic
"research [topic] in depth"

# Use research skill to gather more info
```

---

## Maintenance

### Weekly Review

```bash
# Review new learnings
cd /root/flourisha/01f_Flourisha_Projects/flourisha-enhancements

# Check what was processed
cat youtube-learnings/index.md

# Review improvement ideas
cat improvement-ideas/index.md

# Decide what to implement
```

### Monthly Cleanup

```bash
# Archive old learnings
mv youtube-learnings/2025-10-*.md archived-learnings/2025-10/

# Update indexes
# Consolidate similar improvement ideas
# Close completed improvements
```

---

## Privacy & Security

**Data Stored:**
- Video metadata (public information)
- Your likes (private to you)
- Generated summaries (local only)
- OAuth tokens (encrypted, local)

**Best Practices:**
- Keep credentials secure in `~/.config/youtube-processor/`
- Don't commit `client_secret.json` to git
- Review summaries before sharing
- API tokens stored locally only

---

## Future Enhancements

**Planned Features:**
- [ ] Audio transcription fallback (Whisper)
- [ ] Multi-language support
- [ ] Video timestamp extraction (jump to key moments)
- [ ] Integration with Obsidian tags
- [ ] Automatic implementation scheduling
- [ ] Similar video recommendations
- [ ] Learning path generation
- [ ] Knowledge graph integration

---

## Related Skills

- **update-flourisha-brain** - Update docs with learnings
- **research** - Deep dive on video topics
- **create-skill** - Implement improvements as skills

---

## Supplementary Resources

**Scripts:**
- `/root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py`
- `/root/flourisha/00_AI_Brain/scripts/youtube/categorize.py`
- `/root/flourisha/00_AI_Brain/scripts/youtube/generate_summary.py`

**Workflows:**
- `workflows/youtube-processing-flow.md`
- `workflows/improvement-extraction.md`

**Examples:**
- `examples/sample-summary.md`
- `examples/sample-improvement.md`

---

**Last Updated:** 2025-11-20
**Version:** 1.0.0
**Maintainer:** Flourisha AI Brain
