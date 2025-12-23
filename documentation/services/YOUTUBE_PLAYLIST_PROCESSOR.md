# YouTube Playlist Processor

Playlist-aware video processing with category-specific templates.

## Quick Start

```bash
# Navigate to AI Brain
cd /root/flourisha/00_AI_Brain

# List available templates
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_playlist_processor.py templates

# Preview a playlist (shows which template will be used)
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_playlist_processor.py preview "flourisha-enhancements"

# Process videos (dry run)
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_playlist_processor.py process "flourisha-enhancements" --limit 2 --dry-run

# Process videos for real
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_playlist_processor.py process "flourisha-enhancements" --limit 5
```

## Multi-Channel Support

```bash
# List authenticated YouTube channels
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_channel_manager.py list

# Show playlists for specific channel
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_channel_manager.py playlists "CoCreators Group"
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_channel_manager.py playlists "Wazzy"

# Set default channel
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_channel_manager.py default "CoCreators Group"

# Authenticate new channel (opens OAuth Playground flow)
/root/flourisha/00_AI_Brain/venv/bin/python3 services/youtube_channel_manager.py auth
```

## Authenticated Channels

| Channel | ID | Playlists |
|---------|----|-----------|
| CoCreators Group | UCtPFDR0Xz9g2gYQhDplLG7w | 30 (default) |
| Wazzy | UC-gudwsLXW326OwoHa7Yu3A | 83 |

## Templates

| Template | Playlists | Output Location |
|----------|-----------|-----------------|
| flourisha_enhancement | flourisha-enhancements, Automation, AI future, No-code app dev | `01f_Flourisha_Projects/flourisha-enhancements/youtube-ideas/` |
| health | HLT-*, HLTH-*, Mindfulness, PE Recovery | `02f_Flourisha_Areas/health/youtube-insights/` |
| business | BIZ-*, Marketing, Strategy | `02f_Flourisha_Areas/business/youtube-insights/` |
| finance | FIN-* | `02f_Flourisha_Areas/finance/youtube-insights/` |
| personal_development | Personal Growth, Productivity | `02f_Flourisha_Areas/personal-growth/youtube-insights/` |
| music_production | Music production, Music Prod-* | `03f_Flourisha_Resources/music-production/youtube-notes/` |
| skip | ASOT, Haven Chill, Christian Trance, etc. | No output |
| default | Unmapped playlists | `03f_Flourisha_Resources/youtube-learnings/` |

## Configuration

**Config file:** `/root/flourisha/00_AI_Brain/config/youtube_playlist_templates.json`

**Current settings:**
- Model: `claude-opus-4-20250514`
- Transcript max length: Unlimited (0)
- Fallback to description: Yes

## Dependencies

- **TranscriptService**: Uses Tor proxy for YouTube transcript API
- **Tor**: Must be running on port 9050 (`systemctl status tor`)
- **Anthropic API**: For Claude summaries

## Credentials

**OAuth credentials:** `/root/flourisha/00_AI_Brain/credentials/youtube_oauth.json`
**Channel tokens:** `/root/flourisha/00_AI_Brain/credentials/youtube_tokens/`
**Channel registry:** `/root/flourisha/00_AI_Brain/credentials/youtube_channels.json`

## Output Format

Each processed video creates a markdown file with:
- Frontmatter (title, video_id, channel, dates)
- Summary table (channel, video date, link)
- AI-generated analysis based on template

## Troubleshooting

### Transcript fails
```bash
# Check Tor is running
systemctl status tor
ss -tlnp | grep 9050

# Test transcript service directly
cd /root/flourisha/00_AI_Brain
python3 services/transcript_service.py "VIDEO_ID"
```

### Token expired
YouTube OAuth refresh tokens expire after 7 days if the Google Cloud project is in "Testing" mode. Re-authenticate:
```bash
python3 services/youtube_channel_manager.py auth
```

---

*Last updated: 2025-12-15*
