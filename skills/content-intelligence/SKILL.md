---
name: content-intelligence
description: Access Flourisha AI Brain for content search, processing, and knowledge graph queries. USE WHEN user wants to search their knowledge base OR process YouTube videos OR upload documents OR query what they've learned. Provides conversational interface to all content intelligence features.
---

# Content Intelligence Skill

Access to Flourisha AI Brain - your unified personal knowledge management system combining YouTube processing, document ingestion, email attachment scanning, and knowledge graph exploration.

## What AI Brain Contains

- **YouTube Videos** - Transcripts, summaries, AI-extracted insights (auto-processed from playlists/channels)
- **Documents** - PDFs, Word docs, text files, spreadsheets (manual upload or email attachment)
- **Email Attachments** - Auto-scanned and processed from Gmail (AI Brain/Inbox label)
- **Knowledge Graph** - Entities, relationships, and episodic memory (Neo4j + Graphiti)
- **Project-Organized Content** - Everything organized by projects and areas (PARA methodology)

## Quick Start

### Search Everything
```
"Search my knowledge base for discussions about machine learning"
"Find all content related to Python async programming"
"What have I learned about system design?"
```

### Process YouTube Videos
```
"Add this YouTube video to my AI Brain: https://youtube.com/watch?v=dQw4w9WgXcQ"
"Process YouTube video with ID: dQw4w9WgXcQ"
```

### Upload Documents
```
"Upload this PDF to my AI Brain: /path/to/document.pdf"
"Process this Word document and add to my knowledge base"
```

### Query Knowledge Graph
```
"What entities are related to 'machine learning' in my knowledge?"
"Explore connections around the topic of distributed systems"
```

## Core Commands

All commands work through the Agent SDK MCP server, which provides a conversational interface.

### 1. Search Content

**What:** Vector similarity search across all AI Brain content

**How to use:**
```
Search my AI Brain for: "Your query here"
Find content about: "Topic you're interested in"
What do I know about: "Concept or question"
```

**Parameters:**
- `query` (required): Natural language search query
- `limit` (optional): Max results to return (default: 10)
- `threshold` (optional): Minimum similarity (0.0-1.0, default: 0.6)

**Returns:**
- Matching documents with relevance scores
- Source (YouTube, email, manual upload, etc.)
- Excerpts and metadata

**Example:**
```
User: "Search my brain for how to implement vector databases"
→ AI Brain searches 1,536-dimensional embeddings
→ Returns top 10 results with similarity scores
→ Shows sources: 3 YouTube videos, 4 PDFs, 2 email attachments
```

### 2. Process YouTube Videos

**What:** Extract transcript, generate summary, AI analysis, store searchable chunks

**How to use:**
```
Process YouTube video: https://youtube.com/watch?v=VIDEO_ID
Add to my brain: youtube.com/watch?v=VIDEO_ID
```

**Parameters:**
- `video_id` (required): YouTube video ID (e.g., dQw4w9WgXcQ)

**Processing Pipeline:**
1. Fetch video metadata (title, description, duration)
2. Extract transcript using **TranscriptService** (two-tier approach):
   - **Tier 1:** YouTube Transcript API via Tor proxy (socks5://127.0.0.1:9050)
   - **Tier 2:** Fallback to yt-dlp audio download + faster-whisper transcription
3. AI analysis with Claude (summary, key insights, tags)
4. Agentic chunking (400-1000 character semantic chunks)
5. Generate embeddings (OpenAI text-embedding-3-small, 1536 dimensions)
6. Store in PostgreSQL + pgvector
7. Add to Neo4j knowledge graph
8. Create PARA markdown file in Google Drive

**Why Tor Proxy?**
YouTube blocks transcript API requests from cloud provider IPs. The Tor proxy routes requests through residential exit nodes to bypass this restriction. If no transcript exists on YouTube, the system automatically falls back to Whisper transcription.

**Example:**
```
User: "Process this YouTube video for me: https://youtube.com/watch?v=abc123"
→ AI Brain extracts 8,000-word transcript
→ Claude generates 200-word summary + 5 key insights
→ Splits into 12 semantic chunks
→ Creates embeddings for each chunk
→ Stores in database with full-text search capability
→ Result: Now searchable with any related query
```

### 3. Upload Documents

**What:** Process local files (PDF, DOCX, TXT, CSV, Excel) into AI Brain

**How to use:**
```
Upload document: /path/to/file.pdf
Process this file: /path/to/document.docx
Add to my brain: /path/to/research.txt
```

**Supported Formats:**
- **PDF** - Text extraction with table detection
- **DOCX/DOC** - Paragraph and table extraction
- **TXT/MD** - Plain text with encoding detection
- **CSV/Excel** - Tabular data with sheet parsing

**Parameters:**
- `file_path` (required): Local path to document
- `title` (optional): Custom title for document
- `project_id` (optional): Assign to specific project

**Processing Pipeline:**
1. Validate file (exists, size check <100MB)
2. Extract text based on format
3. Calculate content hash (SHA-256 for deduplication)
4. Check if already processed (version control)
5. AI analysis (summary, classification, entity extraction)
6. Agentic chunking (semantic 400-1000 char chunks)
7. Embeddings generation
8. Store in 6-layer architecture:
   - PostgreSQL (metadata, version control)
   - pgvector (embeddings with similarity search)
   - Neo4j (knowledge graph relationships)
   - PARA files (markdown in Google Drive)
   - processed_content (full-document embedding)
   - Optional: Backward compatibility layer

**Example:**
```
User: "Upload this research paper: /root/downloads/ml_survey.pdf"
→ AI Brain extracts 25 pages of text
→ Generates summary + topics + authors
→ Creates 45 semantic chunks
→ Embeds each chunk for search
→ Stores in database with version control
→ Creates markdown file in Resources folder
→ Result: Citable and searchable
```

### 4. Query Knowledge Graph

**What:** Explore entities, relationships, and episodic memory in Neo4j

**How to use:**
```
Show me connections to: "machine learning"
Explore the entity: "Python"
What relationships exist around: "distributed systems"
```

**Parameters:**
- `entity` (optional): Specific entity to explore
- `query` (optional): Natural language semantic query

**Returns:**
- Related entities and their relationships
- Connection strength/confidence
- Source documents
- Timeline of mentions

**Example:**
```
User: "Show connections to 'React'"
→ AI Brain queries Neo4j knowledge graph
→ Returns:
  - Related: "JavaScript", "frontend", "state management"
  - Connected documents: 12 video transcripts, 4 PDFs
  - Relationships: "uses", "builds_with", "compared_to"
  - Last mentioned: 3 days ago
```

## Background Processing

AI Brain runs two background workers that process content automatically:

### Content Queue Worker
- **Purpose:** Process queued items (videos, documents)
- **Interval:** 10-second polling
- **Service:** `flourisha-content-worker`
- **Check status:** `systemctl status flourisha-content-worker`

### Gmail Monitor Worker
- **Purpose:** Scan Gmail for attachments and process them
- **Interval:** 5-minute polling
- **Label monitored:** `AI Brain/Inbox` (configurable)
- **Service:** `flourisha-gmail-worker`
- **Check status:** `systemctl status flourisha-gmail-worker`

### Manual Monitoring

```bash
# Check worker status
systemctl status flourisha-content-worker
systemctl status flourisha-gmail-worker

# View logs
journalctl -u flourisha-content-worker -f
journalctl -u flourisha-gmail-worker -f

# Restart if needed
systemctl restart flourisha-content-worker
systemctl restart flourisha-gmail-worker
```

## Architecture Overview

### Data Flow

```
Input Sources
├── YouTube (playlists, channels, direct video URLs)
├── Email (Gmail attachments from AI Brain/Inbox)
├── Manual Upload (local files via Agent SDK)
└── Browser (bookmarks, web content)
    ↓
Processing Pipeline
├── 1. Content Extraction (text, metadata)
├── 2. AI Analysis (Claude for understanding)
├── 3. Agentic Chunking (semantic 400-1000 char)
├── 4. Embeddings (OpenAI 1536-dim vectors)
└── 5. Storage (6-layer architecture)
    ↓
Storage Layers
├── PostgreSQL (structured data, version control)
├── pgvector (similarity search capability)
├── Neo4j (knowledge graph, relationships)
├── PARA Files (markdown in Google Drive)
├── processed_content (full-doc embedding)
└── Backward Compatibility
    ↓
Access Interface
├── Agent SDK (conversational, MCP)
├── Claude Code (via this skill)
├── Skills (content-intelligence)
├── FastAPI (direct HTTP if MCP unavailable)
└── Google Drive (PARA files)
```

### N8N RAG Pattern (3-Table Architecture)

**document_metadata**
- `id`: Document identifier
- `content_hash`: SHA-256 for deduplication
- `version_number`: Version control
- `is_current`: Track latest version
- `is_deleted`: Soft delete support
- `source_type`: 'youtube', 'email_attachment', 'manual_upload'
- `source_metadata`: JSON with original details
- `created_by`: User or worker that processed it
- `tenant_id`: Multi-tenant isolation

**documents_pg** (with pgvector)
- `file_id`: Reference to document_metadata
- `chunk_index`: Position in document
- `content`: 400-1000 character chunk
- `embedding`: 1536-dimensional vector (for similarity search)
- `metadata`: Additional chunk-level data

**document_rows** (for tabular data)
- Unused for YouTube/documents currently
- Future: For spreadsheet/table processing

## Privacy & Security

- **Multi-tenant isolation:** RLS (Row Level Security) policies in Supabase
- **Version control:** Every change tracked with soft deletes
- **Deduplication:** Content hash prevents duplicate storage
- **Access control:** Firebase JWT authentication with custom claims
- **Local sync:** PARA files sync to Google Drive (your copy)

## Troubleshooting

### Document Not Showing Up

1. Check background worker status:
   ```bash
   systemctl status flourisha-content-worker
   journalctl -u flourisha-content-worker -f
   ```

2. Verify file was processed:
   ```bash
   # Check recent entries in database
   ```

3. Restart worker if needed:
   ```bash
   systemctl restart flourisha-content-worker
   ```

### Gmail Not Processing Attachments

1. Check Gmail monitor worker:
   ```bash
   systemctl status flourisha-gmail-worker
   journalctl -u flourisha-gmail-worker -f
   ```

2. Verify label exists and has messages:
   - Check Gmail for "AI Brain/Inbox" label
   - Ensure messages have attachments

3. Authenticate Gmail (if not authenticated):
   ```bash
   python3 /root/flourisha/00_AI_Brain/services/gmail_service.py
   ```

### Search Not Finding Content

1. Verify content was processed:
   - Check database for documents
   - Check PARA files in Google Drive

2. Try broader search terms:
   - Exact matches are case-sensitive
   - Use natural language queries for semantic search

3. Check similarity threshold:
   - Default is 0.6 (60% similarity)
   - Increase for stricter results

### Vector Similarity Search Not Working

1. Check embeddings service:
   ```bash
   # Verify OpenAI API key is set
   echo $OPENAI_API_KEY
   ```

2. Verify pgvector extension:
   ```bash
   # Connect to Supabase and check
   ```

## Integration with Claude Code

This skill is automatically available in Claude Code. Use it by:

1. **Directly in conversation:**
   ```
   "Search my AI Brain for discussions about React"
   "Upload this PDF: /path/to/file.pdf"
   "What entities are related to 'machine learning'?"
   ```

2. **In custom skills:**
   ```bash
   skill: "content-intelligence"
   ```

3. **Invoking MCP tools:**
   ```
   mcp://flourisha-ai-brain/search_content?query="your query"
   ```

## Configuration

### Environment Variables

```bash
# Gmail
GMAIL_MONITOR_LABEL=AI Brain/Inbox
GMAIL_PROCESSED_LABEL=AI Brain/Processed
GMAIL_POLL_INTERVAL=300  # 5 minutes
GMAIL_BATCH_SIZE=10

# Processing
FLOURISHA_TENANT_ID=default
FLOURISHA_USER_ID=agent-sdk

# Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_KEY=...
NEO4J_URI=bolt://...
NEO4J_USER=neo4j
NEO4J_PASSWORD=...
```

## Advanced Usage

### Batch Processing

To process multiple documents at once:
```
Upload these documents to my AI Brain:
1. /path/to/doc1.pdf
2. /path/to/doc2.docx
3. /path/to/doc3.txt
```

### Project Organization

Associate uploads with projects:
```
Upload /path/to/paper.pdf to project: "machine-learning-research"
```

### Gmail Label Setup

Create a Gmail label for AI Brain ingestion:
```
1. In Gmail, create label: AI Brain/Inbox
2. Set filter to auto-apply if desired
3. Attach documents and send to self
4. Gmail monitor will process every 5 minutes
```

## Performance Characteristics

- **Search:** <1 second for vector similarity (pgvector index)
- **Chunking:** ~100 chunks/minute (agentic, semantic-aware)
- **Embeddings:** ~1000 chunks/minute (batch processing)
- **Gmail polling:** 1-5 minutes (configurable)
- **Video processing:** 5-10 minutes per video (transcript + analysis + chunking)

## Support

For issues or feature requests:
- Check logs: `journalctl -u flourisha-*-worker -f`
- Review system status: `systemctl status flourisha-*`
- Inspect database: Direct Supabase query
- Check knowledge graph: Neo4j browser at `http://localhost:7687`

---

**Version:** 2.0 (Content Intelligence Integration)
**Last Updated:** 2025-12-14
**Maintenance:** Flourisha AI Brain System
