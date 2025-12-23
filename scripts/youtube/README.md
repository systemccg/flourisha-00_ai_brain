# YouTube Learning Processor - Setup Guide

**Purpose:** Process liked YouTube videos into organized learnings and improvement ideas

---

## Quick Start

### 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client youtube-transcript-api
```

### 2. Set Up YouTube API Credentials

**A. Go to Google Cloud Console:**
```
https://console.cloud.google.com/
```

**B. Create a Project (if you don't have one):**
1. Click "Select a project" → "New Project"
2. Name it "Flourisha YouTube Processor"
3. Click "Create"

**C. Enable YouTube Data API v3:**
1. Go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click "Enable"

**D. Create OAuth 2.0 Credentials:**
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as application type
4. Name it "YouTube Processor"
5. Click "Create"
6. Download the JSON file (click the download icon)

**E. Save Credentials:**
```bash
mkdir -p ~/.config/youtube-processor
mv ~/Downloads/client_secret_*.json ~/.config/youtube-processor/client_secret.json
```

### 3. First-Time Authentication

```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --auth
```

This will:
- Open your browser for OAuth consent
- Ask you to authorize the app
- Save authentication token for future use

### 4. Process Your Liked Videos

```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py
```

---

## Usage

### Basic Commands

**Process all new liked videos:**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py
```

**Dry run (preview what would be processed):**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --dry-run
```

**Process specific video:**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --video-url "https://youtube.com/watch?v=VIDEO_ID"
```

**Limit number of videos:**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --max-results 10
```

**Re-authenticate:**
```bash
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --auth
```

### Through Flourisha Skill

**Activate via natural language:**
```
"process my youtube likes"
```

Flourisha will run the script and report results.

---

## How It Works

### 1. Fetch Liked Videos

Connects to YouTube API and gets videos you've liked:
- Fetches up to 50 videos by default
- Checks which ones haven't been processed yet
- Skips already-processed videos

### 2. Extract Transcript

For each new video:
- Downloads transcript via YouTube Transcript API
- Falls back to title/description if no transcript
- Handles multiple languages (defaults to English)

### 3. Generate AI Summary

Uses Claude to create:
- 2-3 paragraph summary
- Key points (5-7 bullets)
- Main concepts and frameworks
- Actionable insights

### 4. Categorize Content

Intelligently categorizes into:
- **flourisha-improvements** (8-10 relevance)
- **ai-tech-learning**
- **business-strategy**
- **productivity**
- **development**
- **other**

### 5. Score Relevance

Rates Flourisha relevance (0-10):
- **8-10:** Highly applicable to infrastructure
- **6-7:** Somewhat relevant
- **4-5:** General learning
- **0-3:** Not Flourisha-specific

### 6. Create Files

**Summary (always):**
```
01f_Flourisha_Projects/flourisha-enhancements/youtube-learnings/
└── 2025-11-20_video-title.md
```

**Improvement Proposal (if relevance >= 6):**
```
01f_Flourisha_Projects/flourisha-enhancements/improvement-ideas/
└── 001-improvement-idea.md
```

### 7. Track State

Saves processing state to:
```
~/.config/youtube-processor/processed_videos.json
```

Prevents re-processing same videos.

---

## Configuration

### Config File Location

```
~/.config/youtube-processor/config.json
```

### Default Configuration

```json
{
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
  "categories": {
    "flourisha-improvements": {
      "keywords": ["ai agent", "automation", "workflow", "infrastructure", "context", "memory"]
    },
    "ai-tech-learning": {
      "keywords": ["ai", "machine learning", "llm", "neural", "model"]
    },
    "business-strategy": {
      "keywords": ["business", "strategy", "growth", "revenue", "operations"]
    },
    "productivity": {
      "keywords": ["productivity", "workflow", "efficiency", "time management"]
    },
    "development": {
      "keywords": ["programming", "code", "software", "development", "engineering"]
    }
  }
}
```

### Customization

**Change relevance threshold:**
```json
{
  "processing": {
    "relevance_threshold": 7
  }
}
```

**Add category keywords:**
```json
{
  "categories": {
    "flourisha-improvements": {
      "keywords": ["ai agent", "automation", "workflow", "my-custom-keyword"]
    }
  }
}
```

---

## Output Files

### Summary Format

```markdown
---
title: Video Title
channel: Channel Name
url: https://youtube.com/watch?v=ID
date_published: 2025-11-20
date_processed: 2025-11-20
category: flourisha-improvements
flourisha_relevance: 9
---

# Video Title

**Channel:** Channel Name
**Published:** 2025-11-20
**Link:** [Watch on YouTube](URL)

---

## Summary

[AI-generated summary paragraphs]

---

## Key Points

- Key point 1
- Key point 2
- Key point 3

---

## Main Concepts

- **Concept 1:** Description
- **Concept 2:** Description

---

## Actionable Insights

1. Insight 1
2. Insight 2
3. Insight 3

---

## Flourisha Improvements

> **Relevance Score:** 9/10

[Improvement notes or link to proposal]

---

**Processed:** 2025-11-20 by youtube-learning-processor
```

### Improvement Proposal Format

```markdown
---
title: Improvement from Video
source_video: https://youtube.com/watch?v=ID
category: infrastructure
priority: high
status: proposed
date_created: 2025-11-20
---

# Improvement: [Refined Title]

**Source:** [Video Title](link-to-summary)
**Priority:** High
**Status:** Proposed

---

## Overview

[What to improve]

---

## Current State

[Current limitations]

---

## Proposed Solution

1. Step 1
2. Step 2
3. Step 3

---

## Affected Systems

[Which parts of Flourisha]

---

## Implementation Considerations

**Benefits:**
- Benefit 1
- Benefit 2

**Challenges:**
- Challenge 1
- Challenge 2

---

## Next Steps

1. Action 1
2. Action 2

---

**Created:** 2025-11-20 by youtube-learning-processor
```

---

## Automation

### Daily Processing

Add to crontab for automatic processing:

```bash
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py >> /var/log/youtube_processor.log 2>&1
```

### Weekly Processing

```bash
# Runs every Sunday at 8 AM:
0 8 * * 0 /usr/bin/python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py
```

---

## Troubleshooting

### Issue: Authentication Failed

```bash
# Delete token and re-authenticate
rm ~/.config/youtube-processor/token.json
python3 /root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py --auth
```

### Issue: Quota Exceeded

YouTube API has daily quotas. Solutions:

1. **Wait until quota resets** (midnight Pacific Time)
2. **Request quota increase** (Google Cloud Console)
3. **Process fewer videos** (use --max-results 10)

### Issue: Transcript Not Available

Some videos don't have transcripts. Script will:
- Log a warning
- Use title/description only
- Still create summary (less detailed)

### Issue: Module Not Found

```bash
# Install dependencies
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client youtube-transcript-api
```

---

## Integration with Claude API

**Current Status:** Script has mock AI responses

**To integrate real Claude API:**

1. Install Anthropic SDK:
```bash
pip install anthropic
```

2. Set API key:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

3. Update `summarize_with_ai()` method in script:
```python
import anthropic

def summarize_with_ai(self, video_data, transcript):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": prompt  # Use existing prompt template
        }]
    )

    return json.loads(message.content[0].text)
```

---

## Files Created

**Scripts:**
- `/root/flourisha/00_AI_Brain/scripts/youtube/process_likes.py` - Main processor

**Configuration:**
- `~/.config/youtube-processor/client_secret.json` - OAuth credentials
- `~/.config/youtube-processor/token.json` - Auth token (auto-generated)
- `~/.config/youtube-processor/config.json` - Processing config
- `~/.config/youtube-processor/processed_videos.json` - State tracking

**Output:**
- `/root/flourisha/01f_Flourisha_Projects/flourisha-enhancements/youtube-learnings/*.md` - Summaries
- `/root/flourisha/01f_Flourisha_Projects/flourisha-enhancements/improvement-ideas/*.md` - Proposals

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up YouTube API credentials
3. ✅ Run authentication
4. ✅ Process your liked videos
5. ⏳ Review generated summaries
6. ⏳ Evaluate improvement proposals
7. ⏳ Implement the best ideas!

---

**Last Updated:** 2025-11-20
**Maintained By:** Flourisha AI Brain
