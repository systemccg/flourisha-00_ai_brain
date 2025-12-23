# [Flourisha AI] Autonomous Task Specification

**For use with ClickUp Coding Agent Harness**

*Last Updated: 2025-12-16*
*Total Tasks: 75*

---

## Overview

This document defines tasks for autonomous development of Flourisha using the ClickUp Coding Agent Harness. Tasks are organized by the Five Pillars architecture and prioritized for incremental development.

**Harness Location:** `clickup-tasks` skill (`~/.claude/skills/clickup-tasks/`)
**Project Root:** `/root/flourisha/`

---

## Task Format

Each task follows this structure for ClickUp import:

```markdown
## Task X.X: [Feature Name]
**Priority:** X (Level)

### User Story
As a [user type], I can [action/capability], so that [benefit/value].

### Feature Description
[Detailed explanation of what this feature does and why it matters]

### Category
[frontend | api | services | database | infrastructure | integration]

### Tags
[tag1], [tag2], [tag3]

### Test Steps
1. [Action to perform]
2. [Next action]
3. Verify [expected result]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Reference Notes
> "[Exact quote from meeting/discussion about why this feature exists]"
> — Source: [Meeting name, date, or context]
```

### Category Definitions

| Category | Description |
|----------|-------------|
| `frontend` | UI components, pages, client-side logic |
| `api` | REST endpoints, WebSocket handlers, route definitions |
| `services` | Business logic layer, internal services, processing |
| `database` | Schema, migrations, queries, indexes |
| `infrastructure` | Docker, deployment, monitoring, DevOps |
| `integration` | Third-party APIs, external system connections |

### Tag Conventions

Tags enable grouping across tasks. Use lowercase, hyphenated format.

| Tag Type | Examples |
|----------|----------|
| **Pillar** | `ingest`, `know`, `think`, `execute`, `grow` |
| **Feature Area** | `youtube`, `gmail`, `search`, `documents`, `okrs`, `energy`, `agents`, `skills` |
| **Technical** | `auth`, `real-time`, `caching`, `streaming`, `websocket` |
| **Phase** | `mvp`, `foundation`, `enhancement`, `polish` |

---

## Priority Definitions

| Priority | Meaning | Examples |
|----------|---------|----------|
| 1 (Urgent) | Core infrastructure, blockers | Database setup, API foundation |
| 2 (High) | Primary user features | Main workflows, core functionality |
| 3 (Normal) | Secondary features | Enhancements, additional capabilities |
| 4 (Low) | Polish, nice-to-haves | UI refinements, edge cases |

---

# PILLAR 1: INGEST (Content Ingestion)
*15 Tasks*

## Task 1.1: YouTube Playlist API Wrapper
**Priority:** 2 (High)

### Feature Description
Create REST API endpoints that wrap the YouTube Playlist Processor CLI commands, enabling frontend integration.

### Category
functional

### Test Steps
1. POST to `/api/youtube/playlists` with channel parameter
2. Verify returns list of playlists with video counts
3. POST to `/api/youtube/process` with playlist name and limit
4. Verify processing starts and returns job ID
5. GET `/api/youtube/jobs/{id}` for status

### Acceptance Criteria
- [ ] GET `/api/youtube/playlists` returns all playlists
- [ ] POST `/api/youtube/process` triggers processing
- [ ] WebSocket endpoint for real-time progress
- [ ] Error handling for invalid playlists

---

## Task 1.2: YouTube Channel Switcher API
**Priority:** 2 (High)

### Feature Description
API endpoints for managing multiple YouTube channel OAuth tokens.

### Category
functional

### Test Steps
1. GET `/api/youtube/channels` returns authenticated channels
2. POST `/api/youtube/channels/default` sets default channel
3. Verify playlists endpoint respects selected channel

### Acceptance Criteria
- [ ] List all authenticated channels
- [ ] Set default channel
- [ ] Channel status indicators (valid/expired token)

---

## Task 1.3: Document Upload Endpoint
**Priority:** 2 (High)

### Feature Description
File upload endpoint with document processing integration.

### Category
functional

### Test Steps
1. POST multipart form to `/api/documents/upload`
2. Verify file stored and processing queued
3. GET `/api/documents/{id}/status` for processing status
4. Verify extracted content accessible

### Acceptance Criteria
- [ ] Accept PDF, DOCX, XLSX, images
- [ ] Size limit enforcement (50MB)
- [ ] Progress tracking during processing
- [ ] Backend selection (Claude/Docling)

---

## Task 1.4: Knowledge Ingestion Status Dashboard
**Priority:** 3 (Normal)

### Feature Description
API endpoints for monitoring ingestion pipeline health across all three stores.

### Category
functional

### Test Steps
1. GET `/api/ingestion/status` returns store health
2. Verify Vector, Graph, Whole store connectivity
3. GET `/api/ingestion/queue` shows pending items

### Acceptance Criteria
- [ ] Health check for each store
- [ ] Queue depth and processing rate
- [ ] Error log access

---

## Task 1.5: Transcript Service API
**Priority:** 3 (Normal)

### Feature Description
API wrapper for transcript extraction service.

### Category
functional

### Test Steps
1. POST `/api/transcripts` with video_id
2. Verify returns transcript or starts Whisper job
3. GET `/api/transcripts/{video_id}` for cached results

### Acceptance Criteria
- [ ] Return cached transcripts immediately
- [ ] Queue Whisper transcription for missing
- [ ] Source indicator (API vs Whisper)

---

## Task 1.6: Gmail OAuth Flow
**Priority:** 3 (Normal)

### Feature Description
Implement Gmail OAuth authentication flow for email ingestion.

### Category
functional

### Test Steps
1. GET `/api/gmail/auth` redirects to Google OAuth
2. OAuth callback stores tokens
3. Verify can list Gmail labels

### Acceptance Criteria
- [ ] OAuth 2.0 flow completes
- [ ] Tokens stored securely
- [ ] Refresh token handling

---

## Task 1.7: Gmail Label-Based Sync
**Priority:** 3 (Normal)

### Feature Description
Sync emails tagged with "Flourisha/Unprocessed" label.

### Category
functional

### Test Steps
1. POST `/api/gmail/labels/create` creates Flourisha label
2. POST `/api/gmail/sync` fetches tagged emails
3. Verify emails ingested to knowledge stores

### Acceptance Criteria
- [ ] Create Flourisha label hierarchy
- [ ] Selective sync (only tagged emails)
- [ ] Mark as processed after ingestion

---

## Task 1.8: Flourisha Sync Status API
**Priority:** 3 (Normal)

### Feature Description
API for Google Drive sync status and manual trigger.

### Category
functional

### Test Steps
1. GET `/api/sync/status` returns last sync time
2. POST `/api/sync/trigger` starts bisync
3. GET `/api/sync/conflicts` lists conflict files

### Acceptance Criteria
- [ ] Last sync timestamp
- [ ] Manual trigger capability
- [ ] Conflict file listing

---

## Task 1.9: Batch Document Processing
**Priority:** 3 (Normal)

### Feature Description
Process multiple documents in a single request.

### Category
functional

### Test Steps
1. POST `/api/documents/batch` with file array
2. Verify all files queued
3. Track batch progress

### Acceptance Criteria
- [ ] Accept up to 20 files
- [ ] Parallel processing
- [ ] Batch completion callback

---

## Task 1.10: Content Source Registry
**Priority:** 4 (Low)

### Feature Description
Track all content sources and their sync status.

### Category
functional

### Test Steps
1. GET `/api/sources` lists all sources
2. Each source shows last sync, item count
3. POST `/api/sources/{id}/sync` triggers source sync

### Acceptance Criteria
- [ ] YouTube channels as sources
- [ ] Gmail as source
- [ ] Google Drive as source
- [ ] Manual upload as source

---

## Task 1.11: RSS Feed Integration
**Priority:** 4 (Low)

### Feature Description
Subscribe to RSS feeds for content ingestion.

### Category
functional

### Test Steps
1. POST `/api/rss/subscribe` with feed URL
2. Verify feed parsed and items listed
3. Automatic periodic sync

### Acceptance Criteria
- [ ] Subscribe to RSS/Atom feeds
- [ ] Parse feed items
- [ ] Periodic refresh (configurable)

---

## Task 1.12: Web Page Capture
**Priority:** 4 (Low)

### Feature Description
Capture and ingest web pages by URL.

### Category
functional

### Test Steps
1. POST `/api/capture` with URL
2. Page fetched and content extracted
3. Stored in knowledge system

### Acceptance Criteria
- [ ] Fetch and parse web pages
- [ ] Extract main content (readability)
- [ ] Store with source URL

---

## Task 1.13: iPostal Mail Integration
**Priority:** 4 (Low)

### Feature Description
Integrate with iPostal for physical mail scanning.

### Category
functional

### Test Steps
1. Configure iPostal API credentials
2. Poll for new scanned mail
3. Process scanned images

### Acceptance Criteria
- [ ] iPostal API connection
- [ ] New mail detection
- [ ] OCR processing of scans

---

## Task 1.14: Voice Input (Limitless)
**Priority:** 4 (Low)

### Feature Description
Integrate with Limitless for voice input capture.

### Category
functional

### Test Steps
1. Configure Limitless API
2. Receive voice transcriptions
3. Ingest to knowledge system

### Acceptance Criteria
- [ ] Limitless webhook receiver
- [ ] Transcription processing
- [ ] Source attribution

---

## Task 1.15: Ingestion Pipeline Monitoring
**Priority:** 4 (Low)

### Feature Description
Comprehensive monitoring for all ingestion pipelines.

### Category
functional

### Test Steps
1. GET `/api/ingestion/metrics` returns pipeline stats
2. Alert on pipeline failures
3. Historical throughput charts

### Acceptance Criteria
- [ ] Items processed per hour
- [ ] Failure rate tracking
- [ ] Alert thresholds

---

# PILLAR 2: KNOW (Knowledge Hub)
*12 Tasks*

## Task 2.1: Unified Search API
**Priority:** 1 (Urgent)

### Feature Description
Single search endpoint that queries all three knowledge stores and merges results.

### Category
functional

### Test Steps
1. POST `/api/search` with query text
2. Results from Vector, Graph, Whole stores
3. Results ranked by relevance

### Acceptance Criteria
- [ ] Query all three stores
- [ ] Merge and rank results
- [ ] Source attribution per result
- [ ] Configurable store filters

---

## Task 2.2: Vector Similarity Search
**Priority:** 2 (High)

### Feature Description
Semantic search using pgvector embeddings.

### Category
functional

### Test Steps
1. POST `/api/search/vector` with query
2. Returns semantically similar content
3. Similarity scores included

### Acceptance Criteria
- [ ] Embedding generation for queries
- [ ] Cosine similarity matching
- [ ] Configurable threshold (0.5-0.9)
- [ ] Result limit parameter

---

## Task 2.3: Graph Query API
**Priority:** 2 (High)

### Feature Description
Query Neo4j graph for entity relationships.

### Category
functional

### Test Steps
1. POST `/api/graph/query` with Cypher query
2. Results include nodes and relationships
3. Path finding between entities

### Acceptance Criteria
- [ ] Execute Cypher queries
- [ ] Return graph structure
- [ ] Entity type filtering
- [ ] Relationship traversal

---

## Task 2.4: PARA Folder Browser API
**Priority:** 2 (High)

### Feature Description
API for browsing PARA folder structure.

### Category
functional

### Test Steps
1. GET `/api/para` returns top-level folders
2. GET `/api/para/{path}` returns folder contents
3. File metadata included

### Acceptance Criteria
- [ ] List Projects, Areas, Resources, Archives
- [ ] Navigate folder hierarchy
- [ ] File preview metadata
- [ ] Search within PARA

---

## Task 2.5: Entity Browser
**Priority:** 3 (Normal)

### Feature Description
Browse entities extracted from documents.

### Category
functional

### Test Steps
1. GET `/api/entities` lists all entities
2. Filter by type (person, medication, etc.)
3. View entity relationships

### Acceptance Criteria
- [ ] List entities with type badges
- [ ] Filter by entity type
- [ ] Show connected entities
- [ ] Link to source documents

---

## Task 2.6: Knowledge Graph Visualization Data
**Priority:** 3 (Normal)

### Feature Description
API endpoint returning graph data for visualization.

### Category
functional

### Test Steps
1. GET `/api/graph/visualize` with entity ID
2. Returns nodes and edges for rendering
3. Expandable neighbor data

### Acceptance Criteria
- [ ] Force-directed graph data format
- [ ] Node metadata (type, properties)
- [ ] Edge metadata (relationship type)
- [ ] Expand neighbors on demand

---

## Task 2.7: Document Relationships
**Priority:** 3 (Normal)

### Feature Description
Show relationships between documents.

### Category
functional

### Test Steps
1. GET `/api/documents/{id}/related`
2. Returns related documents by entities
3. Similarity-based relationships

### Acceptance Criteria
- [ ] Entity-based relationships
- [ ] Vector similarity relationships
- [ ] Relationship strength scores

---

## Task 2.8: Memory System API
**Priority:** 3 (Normal)

### Feature Description
Persistent memory storage and retrieval.

### Category
functional

### Test Steps
1. POST `/api/memory` stores memory
2. GET `/api/memory/search` searches memories
3. Memory types: session, long-term, episodic

### Acceptance Criteria
- [ ] Store memories with metadata
- [ ] Search memories semantically
- [ ] Memory type categorization
- [ ] Memory edit/delete

---

## Task 2.9: Content Deduplication
**Priority:** 3 (Normal)

### Feature Description
Detect and handle duplicate content.

### Category
functional

### Test Steps
1. Upload duplicate document
2. System detects existing content
3. Option to merge or skip

### Acceptance Criteria
- [ ] SHA256 hash comparison
- [ ] Semantic similarity detection
- [ ] Merge metadata on duplicates

---

## Task 2.10: Tag Management
**Priority:** 4 (Low)

### Feature Description
Tag content for organization.

### Category
functional

### Test Steps
1. POST `/api/tags` creates tag
2. POST `/api/content/{id}/tags` assigns tags
3. GET `/api/tags/{tag}/content` lists tagged content

### Acceptance Criteria
- [ ] Create/edit/delete tags
- [ ] Assign multiple tags
- [ ] Tag-based filtering
- [ ] Tag autocomplete

---

## Task 2.11: Collections
**Priority:** 4 (Low)

### Feature Description
Group content into collections.

### Category
functional

### Test Steps
1. POST `/api/collections` creates collection
2. Add content to collections
3. Collection-scoped search

### Acceptance Criteria
- [ ] Create named collections
- [ ] Add/remove content
- [ ] Collection sharing
- [ ] Smart collections (saved queries)

---

## Task 2.12: Content Export
**Priority:** 4 (Low)

### Feature Description
Export content in various formats.

### Category
functional

### Test Steps
1. POST `/api/export` with content IDs
2. Select format (MD, PDF, JSON)
3. Download exported content

### Acceptance Criteria
- [ ] Markdown export
- [ ] PDF generation
- [ ] JSON data export
- [ ] Bulk export

---

# PILLAR 3: THINK (Strategic Command)
*12 Tasks*

## Task 3.1: Morning Report Generator API
**Priority:** 2 (High)

### Feature Description
API for generating and viewing morning reports.

### Category
functional

### Test Steps
1. POST `/api/morning-report/generate` creates report
2. GET `/api/morning-report/latest` returns current
3. GET `/api/morning-report/history` lists past reports

### Acceptance Criteria
- [ ] Generate report on demand
- [ ] View latest report
- [ ] Report history
- [ ] THE ONE THING calculation

---

## Task 3.2: OKR Management API
**Priority:** 2 (High)

### Feature Description
CRUD operations for OKRs.

### Category
functional

### Test Steps
1. POST `/api/okrs` creates OKR
2. GET `/api/okrs?quarter=Q1-2026` lists quarter OKRs
3. POST `/api/okrs/{id}/measure` records measurement

### Acceptance Criteria
- [ ] Create objectives with key results
- [ ] Progress percentage calculation
- [ ] Status thresholds (on track, at risk)
- [ ] Weekly measurement recording

---

## Task 3.3: Energy Tracking API
**Priority:** 2 (High)

### Feature Description
Log and query energy/focus levels.

### Category
functional

### Test Steps
1. POST `/api/energy` logs energy level
2. GET `/api/energy/today` returns today's entries
3. GET `/api/energy/forecast` returns prediction

### Acceptance Criteria
- [ ] Log energy level (1-10)
- [ ] Log focus quality (deep/shallow/distracted)
- [ ] Historical data query
- [ ] Forecast generation

---

## Task 3.4: Context Card Service
**Priority:** 2 (High)

### Feature Description
Build and maintain user Context Card.

### Category
functional

### Test Steps
1. GET `/api/context-card` returns current card
2. POST `/api/context-card/update` from conversation
3. GET `/api/context-card/export` returns PDF

### Acceptance Criteria
- [ ] Identity & values section
- [ ] Key people section
- [ ] Thinking patterns
- [ ] Current focus
- [ ] Progressive question gathering

---

## Task 3.5: Daily Planning API
**Priority:** 3 (Normal)

### Feature Description
Daily task planning and time blocking.

### Category
functional

### Test Steps
1. GET `/api/planning/today` returns daily plan
2. POST `/api/planning/block` creates time block
3. Integrate with OKRs and energy

### Acceptance Criteria
- [ ] Time block management
- [ ] OKR alignment indicators
- [ ] Energy-aware scheduling
- [ ] Calendar integration

---

## Task 3.6: Task Priority Calculator
**Priority:** 3 (Normal)

### Feature Description
Calculate task priority using THE ONE THING algorithm.

### Category
functional

### Test Steps
1. POST `/api/priority/calculate` with task list
2. Returns ranked tasks with scores
3. Factors: OKR impact, urgency, energy, dependencies

### Acceptance Criteria
- [ ] Multi-factor scoring
- [ ] Configurable weights
- [ ] Explanation of scores

---

## Task 3.7: Weekly Review Generator
**Priority:** 3 (Normal)

### Feature Description
Generate weekly review summary.

### Category
functional

### Test Steps
1. POST `/api/review/weekly` generates review
2. Includes OKR progress, completed tasks
3. Recommendations for next week

### Acceptance Criteria
- [ ] Week summary generation
- [ ] OKR progress comparison
- [ ] Energy pattern analysis
- [ ] Next week recommendations

---

## Task 3.8: Goal Tracking
**Priority:** 3 (Normal)

### Feature Description
Track progress toward long-term goals.

### Category
functional

### Test Steps
1. POST `/api/goals` creates goal
2. Link OKRs to goals
3. Track goal progress over time

### Acceptance Criteria
- [ ] Create annual/quarterly goals
- [ ] Link OKRs as milestones
- [ ] Progress visualization
- [ ] Goal completion tracking

---

## Task 3.9: Decision Journal
**Priority:** 4 (Low)

### Feature Description
Log decisions for later review.

### Category
functional

### Test Steps
1. POST `/api/decisions` logs decision
2. Include context, options considered, outcome
3. Review decisions periodically

### Acceptance Criteria
- [ ] Log decision with context
- [ ] Track decision outcomes
- [ ] Decision pattern analysis

---

## Task 3.10: Habit Tracking
**Priority:** 4 (Low)

### Feature Description
Track daily habits and streaks.

### Category
functional

### Test Steps
1. POST `/api/habits` creates habit
2. POST `/api/habits/{id}/check` marks complete
3. GET `/api/habits/streaks` shows streaks

### Acceptance Criteria
- [ ] Create habits with frequency
- [ ] Daily check-in
- [ ] Streak calculation
- [ ] Habit analytics

---

## Task 3.11: Personality Framework Mapping
**Priority:** 4 (Low)

### Feature Description
Map Context Card data to personality frameworks.

### Category
functional

### Test Steps
1. POST `/api/personality/analyze` with context card
2. Returns framework mappings (MBTI, Enneagram, etc.)
3. Insights based on mappings

### Acceptance Criteria
- [ ] Myers-Briggs mapping
- [ ] Enneagram mapping
- [ ] Human Design integration
- [ ] "Personality twins" feature

---

## Task 3.12: Strategic Insights API
**Priority:** 4 (Low)

### Feature Description
AI-generated strategic recommendations.

### Category
functional

### Test Steps
1. GET `/api/insights` returns current insights
2. Based on OKRs, energy, content consumption
3. Actionable recommendations

### Acceptance Criteria
- [ ] Pattern detection
- [ ] Recommendation generation
- [ ] Priority suggestions
- [ ] Opportunity identification

---

# PILLAR 4: EXECUTE (Agentic Operations)
*18 Tasks*

## Task 4.1: Skills Registry API
**Priority:** 2 (High)

### Feature Description
List and manage available skills.

### Category
functional

### Test Steps
1. GET `/api/skills` lists all skills
2. GET `/api/skills/{name}` returns skill details
3. Skill metadata includes triggers, workflows

### Acceptance Criteria
- [ ] List all installed skills
- [ ] Skill metadata and documentation
- [ ] Trigger keywords
- [ ] Available workflows

---

## Task 4.2: Skill Execution API
**Priority:** 2 (High)

### Feature Description
Execute skills programmatically.

### Category
functional

### Test Steps
1. POST `/api/skills/{name}/execute` runs skill
2. Pass workflow and parameters
3. Return execution results

### Acceptance Criteria
- [ ] Execute any installed skill
- [ ] Workflow selection
- [ ] Parameter passing
- [ ] Result streaming

---

## Task 4.3: Agent Registry API
**Priority:** 2 (High)

### Feature Description
List and invoke specialized agents.

### Category
functional

### Test Steps
1. GET `/api/agents` lists available agents
2. POST `/api/agents/{type}/invoke` starts agent
3. WebSocket for agent communication

### Acceptance Criteria
- [ ] List agent types and capabilities
- [ ] Agent invocation
- [ ] Real-time communication
- [ ] Agent status tracking

---

## Task 4.4: Multi-Agent Workflow API
**Priority:** 3 (Normal)

### Feature Description
Orchestrate multi-agent workflows.

### Category
functional

### Test Steps
1. POST `/api/workflows` defines workflow
2. Workflow includes agent sequence
3. Execute workflow end-to-end

### Acceptance Criteria
- [ ] Define agent sequences
- [ ] Parallel agent execution
- [ ] Inter-agent data passing
- [ ] Workflow completion tracking

---

## Task 4.5: A2A Protocol Implementation
**Priority:** 3 (Normal)

### Feature Description
Implement A2A protocol for agent communication.

### Category
functional

### Test Steps
1. GET `/api/a2a/agents` returns agent cards
2. POST `/api/a2a/message` sends inter-agent message
3. Agents communicate via protocol

### Acceptance Criteria
- [ ] Agent card generation
- [ ] Message format compliance
- [ ] Agent discovery
- [ ] Cross-platform communication

---

## Task 4.6: ClickUp Task Sync
**Priority:** 2 (High)

### Feature Description
Two-way sync with ClickUp tasks.

### Category
functional

### Test Steps
1. GET `/api/clickup/tasks` lists tasks
2. POST `/api/clickup/tasks` creates task
3. Sync status changes bidirectionally

### Acceptance Criteria
- [ ] List ClickUp tasks
- [ ] Create/update tasks
- [ ] Status sync
- [ ] Priority mapping

---

## Task 4.7: Long-Running Task Monitor
**Priority:** 3 (Normal)

### Feature Description
Monitor and manage long-running agent tasks.

### Category
functional

### Test Steps
1. GET `/api/tasks/running` lists active tasks
2. GET `/api/tasks/{id}` returns task status
3. POST `/api/tasks/{id}/cancel` stops task

### Acceptance Criteria
- [ ] List running tasks
- [ ] Progress tracking
- [ ] Task cancellation
- [ ] Completion notifications

---

## Task 4.8: Fabric Pattern API
**Priority:** 3 (Normal)

### Feature Description
Execute Fabric patterns via API.

### Category
functional

### Test Steps
1. GET `/api/fabric/patterns` lists patterns
2. POST `/api/fabric/execute` runs pattern on input
3. Return pattern output

### Acceptance Criteria
- [ ] List 242+ patterns
- [ ] Pattern search
- [ ] Execute with custom input
- [ ] Output formatting

---

## Task 4.9: Command Execution API
**Priority:** 3 (Normal)

### Feature Description
Execute PAI commands via API.

### Category
functional

### Test Steps
1. GET `/api/commands` lists available commands
2. POST `/api/commands/{name}/execute` runs command
3. Return command output

### Acceptance Criteria
- [ ] List custom commands
- [ ] Command execution
- [ ] Parameter handling
- [ ] Output capture

---

## Task 4.10: Hook Management API
**Priority:** 3 (Normal)

### Feature Description
Manage PAI hooks via API.

### Category
functional

### Test Steps
1. GET `/api/hooks` lists configured hooks
2. POST `/api/hooks` creates hook
3. PUT `/api/hooks/{id}` updates hook

### Acceptance Criteria
- [ ] List hooks by type
- [ ] Enable/disable hooks
- [ ] Hook execution logs
- [ ] Hook testing

---

## Task 4.11: Research Agent Interface
**Priority:** 3 (Normal)

### Feature Description
Web interface for research agent.

### Category
functional

### Test Steps
1. POST `/api/research` starts research
2. Select mode (quick/standard/extensive)
3. View synthesized results

### Acceptance Criteria
- [ ] Research request submission
- [ ] Mode selection
- [ ] Real-time progress
- [ ] Result export

---

## Task 4.12: Browser Automation API
**Priority:** 3 (Normal)

### Feature Description
Control Playwright MCP via API.

### Category
functional

### Test Steps
1. POST `/api/browser/navigate` goes to URL
2. POST `/api/browser/screenshot` captures page
3. POST `/api/browser/click` performs action

### Acceptance Criteria
- [ ] Browser session management
- [ ] Navigation and interaction
- [ ] Screenshot capture
- [ ] Page content extraction

---

## Task 4.13: Voice Output API
**Priority:** 3 (Normal)

### Feature Description
Text-to-speech via ElevenLabs.

### Category
functional

### Test Steps
1. POST `/api/voice/speak` generates audio
2. Select voice from available voices
3. Stream audio response

### Acceptance Criteria
- [ ] Text-to-speech generation
- [ ] Voice selection
- [ ] Audio streaming
- [ ] Volume control

---

## Task 4.14: Agent Feedback Collection
**Priority:** 4 (Low)

### Feature Description
Collect feedback on agent executions.

### Category
functional

### Test Steps
1. POST `/api/feedback` submits rating
2. Include execution ID and quality score
3. Use for agent improvement

### Acceptance Criteria
- [ ] Rate agent outputs
- [ ] Feedback aggregation
- [ ] Quality metrics
- [ ] Improvement tracking

---

## Task 4.15: Scheduled Task Management
**Priority:** 4 (Low)

### Feature Description
Schedule recurring agent tasks.

### Category
functional

### Test Steps
1. POST `/api/schedules` creates schedule
2. Define cron expression and task
3. View execution history

### Acceptance Criteria
- [ ] Cron-based scheduling
- [ ] Task definition
- [ ] Execution history
- [ ] Enable/disable schedules

---

## Task 4.16: Agent Template Library
**Priority:** 4 (Low)

### Feature Description
Reusable agent workflow templates.

### Category
functional

### Test Steps
1. GET `/api/templates` lists templates
2. POST `/api/templates/{id}/instantiate` creates workflow
3. Customize template parameters

### Acceptance Criteria
- [ ] Template library
- [ ] Template instantiation
- [ ] Parameter customization
- [ ] Template sharing

---

## Task 4.17: Notification System
**Priority:** 4 (Low)

### Feature Description
Multi-channel notifications.

### Category
functional

### Test Steps
1. POST `/api/notifications` sends notification
2. Channels: email, voice, push
3. Notification preferences

### Acceptance Criteria
- [ ] Email notifications
- [ ] Voice notifications
- [ ] Push notifications
- [ ] Preference management

---

## Task 4.18: Autonomous Agent Harness Integration
**Priority:** 2 (High)

### Feature Description
Full integration with ClickUp Coding Agent Harness.

### Category
functional

### Test Steps
1. Configure harness for Flourisha
2. Import tasks from this spec
3. Run autonomous development session

### Acceptance Criteria
- [ ] Harness configured for Flourisha
- [ ] Tasks imported to ClickUp
- [ ] Agent can read Flourisha context
- [ ] Progress tracked in ClickUp

---

# PILLAR 5: GROW (System Evolution)
*18 Tasks*

## Task 5.1: Extraction Feedback API
**Priority:** 2 (High)

### Feature Description
Collect and process document extraction feedback.

### Category
functional

### Test Steps
1. GET `/api/feedback/queue` returns review queue
2. POST `/api/feedback/{doc_id}` submits corrections
3. Corrections improve future extractions

### Acceptance Criteria
- [ ] Review queue endpoint
- [ ] Correction submission
- [ ] Few-shot example creation
- [ ] Quality metrics

---

## Task 5.2: System Health Dashboard API
**Priority:** 2 (High)

### Feature Description
API for system health metrics.

### Category
functional

### Test Steps
1. GET `/api/health` returns system status
2. All services health checked
3. Alert on degraded services

### Acceptance Criteria
- [ ] Service health checks
- [ ] Database connectivity
- [ ] Queue depth monitoring
- [ ] Resource utilization

---

## Task 5.3: Netdata Integration
**Priority:** 3 (Normal)

### Feature Description
Embed Netdata metrics in Flourisha.

### Category
functional

### Test Steps
1. GET `/api/metrics/system` returns key metrics
2. CPU, RAM, disk, network
3. Historical data access

### Acceptance Criteria
- [ ] Real-time system metrics
- [ ] Historical charts
- [ ] Alert configuration
- [ ] Threshold monitoring

---

## Task 5.4: Uptime Kuma Integration
**Priority:** 3 (Normal)

### Feature Description
Surface Uptime Kuma status in Flourisha.

### Category
functional

### Test Steps
1. GET `/api/uptime` returns service status
2. Uptime percentages
3. Incident history

### Acceptance Criteria
- [ ] Service status grid
- [ ] Uptime calculations
- [ ] Incident timeline
- [ ] Status page generation

---

## Task 5.5: Backend Health Monitoring
**Priority:** 3 (Normal)

### Feature Description
Monitor extraction backend health.

### Category
functional

### Test Steps
1. GET `/api/backends/health` checks all backends
2. Claude, Docling, Legacy status
3. Automatic failover indicators

### Acceptance Criteria
- [ ] Backend availability
- [ ] Response time metrics
- [ ] Failover status
- [ ] Backend selection logic

---

## Task 5.6: Log Aggregation API
**Priority:** 3 (Normal)

### Feature Description
Centralized log access.

### Category
functional

### Test Steps
1. GET `/api/logs` returns recent logs
2. Filter by service, level, time
3. Search log content

### Acceptance Criteria
- [ ] Log retrieval
- [ ] Filtering and search
- [ ] Log level filtering
- [ ] Time range queries

---

## Task 5.7: Error Tracking
**Priority:** 3 (Normal)

### Feature Description
Track and categorize errors.

### Category
functional

### Test Steps
1. GET `/api/errors` returns recent errors
2. Error categorization
3. Resolution tracking

### Acceptance Criteria
- [ ] Error capture
- [ ] Error grouping
- [ ] Resolution status
- [ ] Error trends

---

## Task 5.8: Performance Metrics
**Priority:** 3 (Normal)

### Feature Description
Track API and service performance.

### Category
functional

### Test Steps
1. GET `/api/metrics/performance` returns metrics
2. Response times, throughput
3. Slow query identification

### Acceptance Criteria
- [ ] API response times
- [ ] Database query times
- [ ] Throughput metrics
- [ ] Performance alerts

---

## Task 5.9: Configuration Management
**Priority:** 3 (Normal)

### Feature Description
Manage system configuration via API.

### Category
functional

### Test Steps
1. GET `/api/config` returns current config
2. PUT `/api/config/{key}` updates setting
3. Config change history

### Acceptance Criteria
- [ ] View configuration
- [ ] Update settings
- [ ] Change audit log
- [ ] Config validation

---

## Task 5.10: Feature Flags
**Priority:** 4 (Low)

### Feature Description
Toggle features dynamically.

### Category
functional

### Test Steps
1. GET `/api/features` lists feature flags
2. PUT `/api/features/{flag}` toggles flag
3. Features respect flag state

### Acceptance Criteria
- [ ] Flag management
- [ ] Gradual rollout
- [ ] A/B testing support
- [ ] Flag dependencies

---

## Task 5.11: Backup Status API
**Priority:** 4 (Low)

### Feature Description
Monitor backup status.

### Category
functional

### Test Steps
1. GET `/api/backups` lists recent backups
2. Backup success/failure status
3. Trigger manual backup

### Acceptance Criteria
- [ ] Backup inventory
- [ ] Success tracking
- [ ] Manual backup trigger
- [ ] Restore verification

---

## Task 5.12: Database Maintenance
**Priority:** 4 (Low)

### Feature Description
Database maintenance operations.

### Category
functional

### Test Steps
1. POST `/api/db/vacuum` triggers vacuum
2. GET `/api/db/stats` returns statistics
3. Index management

### Acceptance Criteria
- [ ] Vacuum scheduling
- [ ] Table statistics
- [ ] Index optimization
- [ ] Storage metrics

---

## Task 5.13: Audit Logging
**Priority:** 4 (Low)

### Feature Description
Comprehensive audit trail.

### Category
functional

### Test Steps
1. All API calls logged
2. GET `/api/audit` queries audit log
3. Filter by user, action, time

### Acceptance Criteria
- [ ] Request logging
- [ ] User attribution
- [ ] Action categorization
- [ ] Audit queries

---

## Task 5.14: Rate Limiting
**Priority:** 4 (Low)

### Feature Description
API rate limiting.

### Category
functional

### Test Steps
1. Configure rate limits per endpoint
2. Rate limit headers in responses
3. 429 responses when exceeded

### Acceptance Criteria
- [ ] Configurable limits
- [ ] Rate limit headers
- [ ] Graceful degradation
- [ ] Whitelist support

---

## Task 5.15: API Documentation
**Priority:** 3 (Normal)

### Feature Description
Auto-generated API documentation.

### Category
functional

### Test Steps
1. GET `/api/docs` returns OpenAPI spec
2. Swagger UI available
3. All endpoints documented

### Acceptance Criteria
- [ ] OpenAPI 3.0 spec
- [ ] Swagger UI
- [ ] Request/response examples
- [ ] Authentication docs

---

## Task 5.16: Versioning System
**Priority:** 4 (Low)

### Feature Description
API versioning support.

### Category
functional

### Test Steps
1. API version in URL or header
2. Multiple versions supported
3. Deprecation warnings

### Acceptance Criteria
- [ ] Version routing
- [ ] Version headers
- [ ] Deprecation notices
- [ ] Migration guides

---

## Task 5.17: Developer Portal
**Priority:** 4 (Low)

### Feature Description
Developer documentation and API keys.

### Category
functional

### Test Steps
1. Developer registration
2. API key generation
3. Usage dashboard

### Acceptance Criteria
- [ ] Developer accounts
- [ ] API key management
- [ ] Usage tracking
- [ ] Quota management

---

## Task 5.18: Self-Improvement Loop
**Priority:** 4 (Low)

### Feature Description
System learns from usage patterns.

### Category
functional

### Test Steps
1. Usage patterns tracked
2. Recommendations generated
3. Automatic optimizations

### Acceptance Criteria
- [ ] Pattern detection
- [ ] Optimization suggestions
- [ ] Automatic tuning
- [ ] Improvement metrics

---

# Summary

## Task Count by Pillar

| Pillar | Name | Tasks |
|--------|------|-------|
| 1 | INGEST | 15 |
| 2 | KNOW | 12 |
| 3 | THINK | 12 |
| 4 | EXECUTE | 18 |
| 5 | GROW | 18 |
| **Total** | | **75** |

## Task Count by Priority

| Priority | Count |
|----------|-------|
| 1 (Urgent) | 1 |
| 2 (High) | 16 |
| 3 (Normal) | 32 |
| 4 (Low) | 26 |

## Recommended Build Order

1. **Foundation (Priority 1-2):** Tasks 2.1, 3.1-3.4, 4.1-4.3, 4.6, 5.1-5.2
2. **Core Features (Priority 2-3):** Tasks 1.1-1.5, 2.2-2.4, 4.4-4.12
3. **Enhancement (Priority 3-4):** Remaining tasks

---

*This specification is designed for the ClickUp Coding Agent Harness.*
*Import tasks to ClickUp and run autonomous development sessions.*
