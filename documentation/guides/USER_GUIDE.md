# Flourisha App - User Guide

**Quick Start Guide for Content Intelligence Platform**

---

## Getting Started

### Access the App

1. **Connect to Tailscale** (if not already connected)
2. **Open Frontend:** http://100.66.28.67:5173
3. **Sign Up or Login:**
   - Email/Password
   - Google Sign-In

---

## Core Workflows

### 1. Create Your First Project

**Projects** organize your content and provide context for AI processing.

**Steps:**
1. Go to http://100.66.28.67:5173/projects
2. Click **"New Project"**
3. Fill out:
   - **Name:** e.g., "Real Estate Marketing"
   - **Description:** What this project is about
   - **Tech Stack:** Technologies/tools you're using (optional)
   - **Visibility:** Private (default) or other
4. Click **"Create"**

**Use Cases:**
- Client projects (separate content per client)
- Learning topics (e.g., "Python ML Course")
- Business areas (e.g., "Product Development")
- Research subjects (e.g., "AI Agents Research")

---

### 2. Process YouTube Content

**Automatically extract insights from YouTube videos.**

#### Process Single Video

1. Go to http://100.66.28.67:5173/youtube
2. **Paste YouTube URL** (any format):
   ```
   https://youtube.com/watch?v=VIDEO_ID
   https://youtu.be/VIDEO_ID
   youtube.com/watch?v=VIDEO_ID
   ```
3. **Select Project** (optional - for context-aware processing)
4. Click **"Process Video"**

**What Happens:**
- ✅ Fetches video metadata (title, description, stats)
- ✅ Gets full transcript (if available)
- ✅ AI generates:
  - Summary
  - Key insights
  - Action items
  - Tags
  - Related concepts
- ✅ Stores in knowledge graph
- ✅ Creates searchable embeddings

**Result:**
- Processed content appears in your Content library
- Knowledge graph updated with concepts/entities
- Content is searchable by semantic meaning

#### Subscribe to YouTube Playlist

**Auto-process new videos added to a playlist.**

1. Go to http://100.66.28.67:5173/youtube
2. Click **"Subscribe to Playlist"**
3. **Paste Playlist URL:**
   ```
   https://youtube.com/playlist?list=PLAYLIST_ID
   ```
4. **Configure:**
   - Name: Give it a memorable name
   - Project: Link to project (for context)
   - Auto-process: ON (process new videos automatically)
5. Click **"Subscribe"**

**Use Cases:**
- Learning channels (auto-process course uploads)
- Industry news (stay updated automatically)
- Team training (process training videos)
- Conference talks (automatically archive)

---

### 3. Upload and Process Documents

**Process PDFs, text files, markdown, etc.**

1. Go to http://100.66.28.67:5173/content
2. Click **"Upload Content"**
3. **Choose Method:**
   - **File Upload:** Drag & drop or select file
   - **Paste Text:** Copy/paste text directly
   - **URL:** Provide URL to article/blog post
4. **Select Project** (for context-aware processing)
5. **Add Metadata** (optional):
   - Title
   - Tags
   - Notes
6. Click **"Process"**

**Supported Formats:**
- PDF documents
- Markdown (.md)
- Plain text (.txt)
- Microsoft Word (.docx)
- Web articles (via URL)

**Result:**
- AI extracts key information
- Creates knowledge graph nodes
- Generates embeddings for search
- Links to related content

---

### 4. Search and Discover

**Find content using natural language search.**

1. Go to http://100.66.28.67:5173/search
2. **Enter Query:**
   - Natural language: "How do I deploy a FastAPI app?"
   - Concepts: "authentication strategies"
   - Specific: "video about React hooks"
3. **View Results:**
   - Ranked by relevance (semantic search)
   - Shows source (YouTube, document, etc.)
   - Displays summary
   - Links to original content

**Search Features:**
- 🔍 Semantic search (understands meaning, not just keywords)
- 🎯 Filter by project
- 📅 Filter by date range
- 🏷️ Filter by tags
- 📊 Sort by relevance or date

---

### 5. Explore Knowledge Graph

**Visualize connections between concepts.**

1. Go to http://100.66.28.67:5173/graph
2. **Explore:**
   - Click nodes to see details
   - Follow edges to related concepts
   - Filter by project
   - Search for specific entities

**Use Cases:**
- Understand relationships between concepts
- Find gaps in knowledge
- Discover unexpected connections
- Map out learning paths

---

## Common Scenarios

### Scenario: Learning from a Course

**Goal:** Process all videos from an online course and build searchable knowledge base.

**Workflow:**
1. Create project: "Advanced TypeScript Course"
2. Subscribe to course playlist
3. Enable auto-process
4. Wait for videos to process (or process manually)
5. Use search to find specific topics later
6. Explore knowledge graph to see concept relationships

### Scenario: Client Research

**Goal:** Collect and analyze content for a client project.

**Workflow:**
1. Create project: "Acme Corp - Market Research"
2. Upload client documents (PDFs, reports)
3. Process relevant YouTube videos (industry talks)
4. Add web articles via URL
5. Search to answer specific questions
6. Generate insights from knowledge graph

### Scenario: Team Knowledge Base

**Goal:** Build shared knowledge base for team.

**Workflow:**
1. Create project: "Engineering Best Practices"
2. Subscribe to relevant YouTube channels
3. Upload team documentation
4. Process conference talks
5. Team uses search to find information
6. Knowledge graph shows connections between topics

---

## Tips & Best Practices

### Organizing Projects

✅ **Do:**
- Create separate projects for distinct topics/clients
- Use descriptive names
- Add detailed descriptions
- Link related content to same project

❌ **Don't:**
- Create too many projects (hard to manage)
- Use generic names ("Project 1")
- Mix unrelated content in same project

### Content Processing

✅ **Do:**
- Select appropriate project for context
- Add tags for better organization
- Process complete playlists vs individual videos
- Review AI-generated summaries

❌ **Don't:**
- Skip project selection (reduces AI context)
- Forget to enable auto-process for playlists
- Process duplicate content

### Search & Discovery

✅ **Do:**
- Use natural language queries
- Use filters to narrow results
- Explore knowledge graph for discovery
- Follow related content links

❌ **Don't:**
- Use only keyword search (semantic search is powerful)
- Ignore suggested related content
- Skip knowledge graph exploration

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Focus search |
| `Ctrl/Cmd + K` | Quick command palette |
| `Ctrl/Cmd + P` | Quick project switcher |
| `Esc` | Close modals |
| `Ctrl/Cmd + Enter` | Submit form |

---

## Mobile Access

**The app is responsive and works on mobile devices.**

**Access:**
- Same URL via Tailscale on mobile
- Install Tailscale app on phone/tablet
- Connect to Tailscale network
- Open browser to http://100.66.28.67:5173

**Mobile Features:**
- Full search functionality
- Content viewing
- Quick processing (paste YouTube URL)
- Notifications (coming soon)

---

## Getting Help

### Documentation

- **Setup Guide:** [SETUP_AND_TESTING.md](SETUP_AND_TESTING.md)
- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **API Reference:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)

### Check Status

```bash
# Run tests
python3 test_all_features.py

# Check logs
tail -f /tmp/backend.log
```

### Common Issues

**Problem:** YouTube processing fails
**Solution:** Ensure YouTube Data API v3 is enabled in Google Cloud Console

**Problem:** Content not appearing after processing
**Solution:** Refresh the page, check processing queue status

**Problem:** Search not returning results
**Solution:** Wait for processing to complete (check processed_content table)

---

## What's Next

### Coming Soon

- 📱 Mobile app (iOS/Android)
- 🔔 Notifications for new content
- 👥 Team collaboration features
- 📊 Analytics dashboard
- 🎯 Personalized recommendations
- 🔗 Integrations (Notion, Slack, etc.)

### Advanced Features

- **Custom AI prompts** for processing
- **Export knowledge graph** to Obsidian/Roam
- **Automated summaries** (daily/weekly)
- **Content scheduling** for processing
- **API access** for integrations

---

## Feedback

Found a bug or have a feature request?

- Create an issue in the project repo
- Or contact: jowasmuth@gmail.com

---

**Happy learning and processing!** 🚀
