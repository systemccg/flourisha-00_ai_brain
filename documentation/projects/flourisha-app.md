# Flourisha App - Content Intelligence Platform

**Location:** `/root/flourisha/01f_Flourisha_Projects/flourisha-app/`
**Status:** 🟢 Operational (Production-ready on Contabo)
**Last Updated:** 2025-11-22

---

## Overview

Full-stack content intelligence platform with AI-powered processing, knowledge graph, and semantic search.

**Tech Stack:**
- **Frontend:** React + TypeScript + Vite
- **Backend:** Python + FastAPI
- **Database:** Supabase (PostgreSQL)
- **Auth:** Firebase Authentication
- **AI:** Anthropic Claude (Sonnet 4.5)
- **Knowledge Graph:** Neo4j (via Graphiti)
- **Vector Search:** Embeddings + Supabase pgvector

---

## Quick Access

### URLs (via Tailscale)

```bash
# Frontend
http://100.66.28.67:5173

# Backend API
http://100.66.28.67:8001

# API Documentation
http://100.66.28.67:8001/docs

# OpenAPI Schema
http://100.66.28.67:8001/openapi.json
```

### Key Files

```bash
# Project root
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app

# Documentation
cat SETUP_AND_TESTING.md    # Complete setup guide
cat USER_GUIDE.md            # User workflows
cat docs/ARCHITECTURE.md     # Architecture details

# Run tests
python3 test_all_features.py

# Logs
tail -f /tmp/backend.log
tail -f /tmp/vite-dev.log
```

---

## Architecture Summary

### Components

1. **Frontend (React + Vite)**
   - Location: `web/`
   - Port: 5173
   - Config: `.env.local`, `vite.config.ts`
   - Features: Authentication, Projects, Content, YouTube, Search

2. **Backend (FastAPI)**
   - Location: `backend/`
   - Port: 8001
   - Config: `/root/.claude/.env`
   - API: RESTful with JWT auth

3. **Database (Supabase)**
   - Service: local-ai-packaged stack
   - URL: https://db.leadingai.info
   - Tables: projects, processed_content, youtube_subscriptions, input_sources, processing_queue

4. **Authentication (Firebase)**
   - Service: Firebase Auth
   - Methods: Email/Password, Google OAuth
   - Auto-tenant: `mk3029839` (CoCreators)

5. **Knowledge Graph (Neo4j)**
   - Integration: Graphiti
   - Purpose: Concept relationships, entity linking

### Data Flow

```
User → Frontend → Backend → Firebase (verify JWT)
                         → Supabase (store data)
                         → Neo4j (knowledge graph)
                         → Claude AI (process content)
                         → YouTube API (fetch videos)
```

---

## Deployment Status

### ✅ Completed Setup

- [x] Network configuration (Tailscale IP: 100.66.28.67)
- [x] Frontend: Vite dev server listening on 0.0.0.0:5173
- [x] Backend: FastAPI on 0.0.0.0:8001
- [x] CORS: Configured for Tailscale IP
- [x] Firebase JWT verification (x509 certificate parsing)
- [x] Auto-tenant assignment for new users
- [x] Database schema applied
- [x] PostgREST schema cache refreshed
- [x] All TypeScript type imports fixed
- [x] Comprehensive test suite created
- [x] Documentation: Setup, Testing, User Guide

### ⚠️ Manual Setup Required

- [ ] **YouTube Data API v3:** Must be enabled in Google Cloud Console
  - URL: https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=544000491438
  - Action: Click "Enable API"
  - Required for: YouTube video processing, playlist subscriptions

### Future Enhancements

- [ ] Content processing workers (background jobs)
- [ ] Mobile app (iOS/Android)
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] Integrations (Notion, Slack, etc.)

---

## Common Operations

### Start/Stop Services

```bash
# Start Frontend
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app/web
npm run dev > /tmp/vite-dev.log 2>&1 &

# Start Backend
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &

# Check Status
ps aux | grep "vite\|uvicorn" | grep -v grep

# Stop Services
pkill -f "vite"
pkill -f "uvicorn main:app"
```

### Run Tests

```bash
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app
source backend/venv/bin/activate
python3 test_all_features.py

# Expected: 7/7 tests passed
```

### Database Operations

```bash
# Connect to Supabase DB
docker exec -it supabase-db psql -U postgres -d postgres

# Check tables
\dt public.*

# Query projects
SELECT * FROM public.projects LIMIT 5;

# Restart PostgREST (if schema cache issues)
docker restart supabase-rest
```

### Check Logs

```bash
# Backend logs
tail -f /tmp/backend.log

# Frontend logs
tail -f /tmp/vite-dev.log

# Supabase PostgREST
docker logs supabase-rest --tail 50

# Supabase DB
docker logs supabase-db --tail 50
```

---

## Environment Variables

### Backend (`/root/.claude/.env`)

```bash
# Supabase
SUPABASE_URL="https://db.leadingai.info"
SUPABASE_ANON_KEY="<key>"
SUPABASE_SERVICE_KEY="<key>"

# Firebase
FIREBASE_PROJECT_ID="flourisha-d959a"
FIREBASE_PRIVATE_KEY="<key>"
FIREBASE_CLIENT_EMAIL="<email>"

# Google
GOOGLE_API_KEY="AIzaSyA0NkM2ppRrM4FnMNT5G9JyVBsrk5skHR4"

# Anthropic
ANTHROPIC_API_KEY="<key>"

# Neo4j
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="<password>"
```

### Frontend (`web/.env.local`)

```bash
# API
VITE_API_URL=http://100.66.28.67:8001

# Firebase
VITE_FIREBASE_API_KEY="<key>"
VITE_FIREBASE_AUTH_DOMAIN="flourisha-d959a.firebaseapp.com"
VITE_FIREBASE_PROJECT_ID="flourisha-d959a"
VITE_FIREBASE_STORAGE_BUCKET="flourisha-d959a.appspot.com"
VITE_FIREBASE_MESSAGING_SENDER_ID="<id>"
VITE_FIREBASE_APP_ID="<id>"
```

---

## Troubleshooting

### Issue: YouTube processing fails with 403 error

**Error:**
```
HttpError 403: YouTube Data API v3 has not been used in project 544000491438
```

**Solution:**
Enable YouTube Data API v3 in Google Cloud Console:
https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=544000491438

### Issue: CORS errors in browser

**Symptoms:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
1. Check backend CORS config in `backend/main.py`
2. Verify Tailscale IP is in `allow_origins` list
3. Restart backend after changes

### Issue: Authentication fails

**Symptoms:** `Token verification failed`

**Solutions:**
1. Check Firebase config in backend
2. Verify `FIREBASE_PRIVATE_KEY` is set correctly
3. Check that `100.66.28.67` is in Firebase authorized domains
4. Review `backend/auth/firebase_auth.py` logs

### Issue: Database connection fails

**Symptoms:** `Could not find the table 'public.projects' in the schema cache`

**Solutions:**
1. Restart PostgREST: `docker restart supabase-rest`
2. Verify schema applied: `docker exec -it supabase-db psql -U postgres -d postgres -c "\dt public.*"`
3. Re-apply schema if needed: `docker exec -i supabase-db psql -U postgres -d postgres < backend/database/01_content_intelligence_schema.sql`

### Issue: Frontend not accessible

**Symptoms:** "site can't be reached" at http://100.66.28.67:5173

**Solutions:**
1. Check Vite is running: `ps aux | grep vite`
2. Verify `vite.config.ts` has `host: '0.0.0.0'`
3. Check logs: `tail -f /tmp/vite-dev.log`
4. Restart: `pkill -f vite && cd web && npm run dev > /tmp/vite-dev.log 2>&1 &`

---

## Integration with PAI System

### Documentation Sync

This project's documentation is part of the Flourisha Google Drive:

```bash
# Local
/root/flourisha/01f_Flourisha_Projects/flourisha-app/

# Google Drive
Flourisha_gDrive/01f_Flourisha_Projects/flourisha-app/

# Sync
flourisha-bisync
```

### AI Brain Reference

This documentation is indexed in AI Brain:
- `/root/flourisha/00_AI_Brain/documentation/projects/flourisha-app.md` (this file)
- Linked from `/root/flourisha/00_AI_Brain/documentation/README.md`

---

## Development Notes

### Tech Stack Decisions

**Why React + Vite?**
- Fast HMR during development
- Modern build tooling
- TypeScript support out of box

**Why FastAPI?**
- Python ecosystem (AI/ML libraries)
- Async support (critical for AI operations)
- Auto-generated OpenAPI docs
- Type safety with Pydantic

**Why Supabase?**
- PostgreSQL + REST API
- Row-Level Security
- Real-time subscriptions
- Vector search (pgvector)

**Why Firebase Auth?**
- Simple OAuth integration
- JWT tokens
- Client SDKs
- Custom claims for multi-tenancy

**Why Neo4j?**
- Graph database for relationships
- Cypher query language
- Perfect for knowledge graphs
- Graphiti integration

### Multi-Tenancy

**Tenant Structure:**
- `tenant_id`: Organization/workspace identifier
- `tenant_user_id`: User ID within tenant
- Default tenant: `mk3029839` (CoCreators)

**RLS Policies:**
- All tables have `tenant_id` column
- Row-Level Security enforced in Supabase
- Users can only access data in their tenant

### AI Processing Pipeline

1. **Content Ingestion:**
   - YouTube: video_id → metadata + transcript
   - Documents: file → text extraction
   - URLs: web page → content extraction

2. **AI Processing:**
   - Claude API with custom prompts
   - Project context for context-aware processing
   - Structured output (JSON schema)

3. **Storage:**
   - Supabase: Structured data + metadata
   - Neo4j: Concepts, entities, relationships
   - Vector DB: Embeddings for semantic search

4. **Retrieval:**
   - Semantic search via embeddings
   - Knowledge graph traversal
   - Metadata filtering

---

## API Endpoints

### Authentication
- `POST /api/v1/signup` - Create account
- `POST /api/v1/login` - Login
- `GET /api/v1/me` - Get current user

### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Content
- `GET /api/v1/content` - List content
- `POST /api/v1/content` - Upload content
- `GET /api/v1/content/{id}` - Get content
- `PUT /api/v1/content/{id}` - Update content
- `DELETE /api/v1/content/{id}` - Delete content

### YouTube
- `POST /api/v1/youtube/process/{video_id}` - Process video
- `POST /api/v1/youtube/playlists/subscribe` - Subscribe to playlist
- `POST /api/v1/youtube/channels/subscribe` - Subscribe to channel
- `GET /api/v1/youtube/subscriptions` - List subscriptions
- `DELETE /api/v1/youtube/subscriptions/{id}` - Unsubscribe

**Full API Docs:** http://100.66.28.67:8001/docs

---

## Related Documentation

- **Setup Guide:** [/root/flourisha/01f_Flourisha_Projects/flourisha-app/SETUP_AND_TESTING.md](../../../../01f_Flourisha_Projects/flourisha-app/SETUP_AND_TESTING.md)
- **User Guide:** [/root/flourisha/01f_Flourisha_Projects/flourisha-app/USER_GUIDE.md](../../../../01f_Flourisha_Projects/flourisha-app/USER_GUIDE.md)
- **Architecture:** [/root/flourisha/01f_Flourisha_Projects/flourisha-app/docs/ARCHITECTURE.md](../../../../01f_Flourisha_Projects/flourisha-app/docs/ARCHITECTURE.md)
- **Network Topology:** [../infrastructure/network-topology.md](../infrastructure/network-topology.md)

---

**Maintained by:** Flourisha AI System
**Contact:** jowasmuth@gmail.com
