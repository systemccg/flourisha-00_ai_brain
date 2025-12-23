# Flourisha App - Setup and Testing Guide

**Last Updated:** 2025-11-22
**Status:** ✅ Operational on Contabo with Tailscale

---

## Quick Start

### Access the Application

```bash
# Frontend (with Tailscale connected)
http://100.66.28.67:5173

# Backend API
http://100.66.28.67:8001

# API Documentation
http://100.66.28.67:8001/docs
```

### Check Service Status

```bash
# Run comprehensive tests
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app
source backend/venv/bin/activate
python3 test_all_features.py

# Check processes
ps aux | grep "vite\|uvicorn" | grep -v grep

# Check logs
tail -f /tmp/backend.log
tail -f /tmp/vite-dev.log
```

---

## Initial Setup Completed

### ✅ Network Configuration
- Frontend: Vite dev server on `0.0.0.0:5173` (accessible via Tailscale)
- Backend: FastAPI on `0.0.0.0:8001` (accessible via Tailscale)
- CORS: Configured to allow `http://100.66.28.67:5173`
- Tailscale IP: `100.66.28.67`
- DNS: `leadingai004.tail8b1922.ts.net`

**Files:**
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/web/.env.local` - Frontend config
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/web/vite.config.ts` - Vite config
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/main.py` - CORS config

### ✅ Authentication (Firebase)
- Service: Firebase Authentication
- Methods: Email/Password, Google OAuth
- JWT Verification: Working (x509 certificate parsing implemented)
- Auto-tenant: Users without custom claims → `tenant_id: mk3029839`
- Authorized Domain: `100.66.28.67` added to Firebase

**Files:**
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/auth/firebase_auth.py` - JWT verification
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/auth/middleware.py` - Auth middleware + auto-tenant
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/web/src/lib/firebase.ts` - Frontend Firebase config

### ✅ Database (Supabase/PostgreSQL)
- Service: Supabase via local-ai-packaged stack
- URL: `https://db.leadingai.info`
- Tables: projects, processed_content, youtube_subscriptions, input_sources, processing_queue
- PostgREST: Schema cache loaded (114 relations)
- RLS: Row-Level Security policies in place

**Files:**
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/database/01_content_intelligence_schema.sql` - Schema definition
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/services/supabase_client.py` - Database client

### ✅ Knowledge Graph (Neo4j)
- Service: Neo4j via graphiti integration
- Integration: KnowledgeGraphService initialized
- Backend: Knowledge graph operations ready

**Files:**
- `/root/flourisha/01f_Flourisha_Projects/flourisha-app/backend/services/knowledge_graph.py` - Neo4j integration

---

## Google Cloud APIs Setup

### ⚠️ YouTube Data API v3 (REQUIRED)

**Status:** Needs to be enabled manually

The YouTube video processing feature requires the YouTube Data API v3 to be enabled in your Google Cloud project.

**Enable Now:**
1. Go to: https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=544000491438
2. Click **"Enable API"**
3. Wait 1-2 minutes for changes to propagate

**Error if Not Enabled:**
```
HttpError 403: YouTube Data API v3 has not been used in project 544000491438
before or it is disabled. Enable it by visiting https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=544000491438
```

**After Enabling:**
- YouTube video processing will work
- YouTube playlists/channel subscriptions will work
- Video transcript fetching will work

**Environment Variable:**
```bash
# Already configured in /root/.claude/.env
GOOGLE_API_KEY="AIzaSyA0NkM2ppRrM4FnMNT5G9JyVBsrk5skHR4"
```

---

## Feature Testing

### 1. Authentication Testing

**Sign Up:**
```bash
# In browser: http://100.66.28.67:5173/signup
# Enter email/password or use Google Sign-In
```

**What Happens:**
1. Firebase creates user account
2. Backend auto-assigns `tenant_id: mk3029839` if not set
3. User gets JWT token
4. Token stored in localStorage
5. All API requests use: `Authorization: Bearer <token>`

**Test from Browser Console:**
```javascript
// After signing up/logging in
const token = localStorage.getItem('firebase-token');
console.log('Token:', token);

// Test authenticated request
fetch('http://100.66.28.67:8001/api/v1/projects', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
}).then(r => r.json()).then(console.log);
```

### 2. Projects CRUD Testing

**Create Project:**
```bash
# From frontend: http://100.66.28.67:5173/projects
# Click "New Project"
# Enter name, description, tech stack
```

**API Test (with auth token):**
```bash
# Get your Firebase token from browser localStorage first
TOKEN="<your-firebase-jwt-token>"

# Create project
curl -X POST http://100.66.28.67:8001/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Testing project creation",
    "tech_stack": ["Python", "FastAPI"],
    "context_replacements": {},
    "default_visibility": "private"
  }'

# List projects
curl http://100.66.28.67:8001/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Content Upload Testing

**Upload Content:**
```bash
# From frontend: http://100.66.28.67:5173/content
# Click "Upload Content"
# Select file or paste text
```

**What Gets Processed:**
1. Content stored in Supabase
2. AI processing with Anthropic Claude
3. Embeddings generated for vector search
4. Knowledge graph nodes/edges created in Neo4j
5. Metadata indexed

### 4. YouTube Processing Testing

**⚠️ Requires YouTube API to be enabled first!**

**Process Single Video:**
```bash
# From frontend: http://100.66.28.67:5173/youtube
# Paste YouTube URL
# Click "Process Video"
```

**What Happens:**
1. Extract video ID from URL (e.g., `7B2HJr0Y68g` from `https://youtube.com/watch?v=7B2HJr0Y68g`)
2. Fetch video metadata via YouTube Data API
3. Get transcript via youtube-transcript-api
4. AI processing with Claude (summary, insights, tags)
5. Store in database with full metadata
6. Create knowledge graph nodes
7. Generate embeddings for vector search

**API Test:**
```bash
TOKEN="<your-firebase-jwt-token>"
VIDEO_ID="7B2HJr0Y68g"  # Example video

curl -X POST "http://100.66.28.67:8001/api/v1/youtube/process/$VIDEO_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Subscribe to Playlist:**
```bash
TOKEN="<your-firebase-jwt-token>"
PROJECT_ID="<project-uuid>"

curl -X POST http://100.66.28.67:8001/api/v1/youtube/playlists/subscribe \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "playlist_id": "PLxxxxxxxxxxxxxx",
    "playlist_name": "My Learning Playlist",
    "project_id": "'"$PROJECT_ID"'",
    "auto_process": true
  }'
```

### 5. API Documentation Testing

**Interactive API Docs:**
```bash
# Open in browser
http://100.66.28.67:8001/docs

# This provides:
# - All available endpoints
# - Request/response schemas
# - Try it out interface
# - Authentication testing
```

---

## Common Issues & Solutions

### Issue: "site can't be reached"
**Cause:** Vite not listening on network interfaces
**Solution:** Already fixed in `vite.config.ts` with `host: '0.0.0.0'`

### Issue: CORS errors in browser console
**Cause:** Backend not allowing frontend origin
**Solution:** Already fixed - `http://100.66.28.67:5173` added to CORS origins in `main.py`

### Issue: TypeScript "module does not provide export" error
**Cause:** Importing types as runtime values
**Solution:** Already fixed - using `import type { User }` syntax

### Issue: "tenant_id not found in user claims"
**Cause:** Firebase user doesn't have custom claims
**Solution:** Already fixed - auto-assignment in `middleware.py` assigns default tenant

### Issue: YouTube API 403 error
**Cause:** YouTube Data API v3 not enabled
**Solution:** Enable at https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=544000491438

### Issue: Database "table not found in schema cache"
**Cause:** PostgREST schema cache not refreshed
**Solution:**
```bash
docker restart supabase-rest
```

### Issue: Backend not responding
**Check:**
```bash
# Is it running?
ps aux | grep uvicorn | grep -v grep

# Check logs
tail -50 /tmp/backend.log

# Restart if needed
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app/backend
pkill -f "uvicorn main:app"
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
```

### Issue: Frontend not responding
**Check:**
```bash
# Is it running?
ps aux | grep vite | grep -v grep

# Check logs
tail -50 /tmp/vite-dev.log

# Restart if needed
cd /root/flourisha/01f_Flourisha_Projects/flourisha-app/web
pkill -f "vite"
npm run dev > /tmp/vite-dev.log 2>&1 &
```

---

## Environment Variables

### Backend (.env at /root/.claude/.env)
```bash
# Supabase
SUPABASE_URL="https://db.leadingai.info"
SUPABASE_ANON_KEY="<anon-key>"
SUPABASE_SERVICE_KEY="<service-role-key>"

# Firebase
FIREBASE_PROJECT_ID="flourisha-d959a"
FIREBASE_PRIVATE_KEY="<private-key>"
FIREBASE_CLIENT_EMAIL="<service-account-email>"

# Google APIs
GOOGLE_API_KEY="AIzaSyA0NkM2ppRrM4FnMNT5G9JyVBsrk5skHR4"
GOOGLE_CLIENT_ID="<client-id>"
GOOGLE_CLIENT_SECRET="<client-secret>"

# Anthropic
ANTHROPIC_API_KEY="<api-key>"

# Neo4j
NEO4J_URI="bolt://localhost:7687"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="<password>"
```

### Frontend (.env.local)
```bash
# API Configuration
VITE_API_URL=http://100.66.28.67:8001  # Tailscale IP (NOT localhost)

# Firebase
VITE_FIREBASE_API_KEY="<web-api-key>"
VITE_FIREBASE_AUTH_DOMAIN="flourisha-d959a.firebaseapp.com"
VITE_FIREBASE_PROJECT_ID="flourisha-d959a"
VITE_FIREBASE_STORAGE_BUCKET="flourisha-d959a.appspot.com"
VITE_FIREBASE_MESSAGING_SENDER_ID="<sender-id>"
VITE_FIREBASE_APP_ID="<app-id>"
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Tailscale Connected)                │
│                                                               │
│  Browser: http://100.66.28.67:5173                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend (React + Vite + Firebase)              │
│                                                               │
│  - Authentication UI (Firebase Auth)                         │
│  - Project Management                                        │
│  - Content Upload                                            │
│  - YouTube Processing                                        │
│  - Port: 5173, Host: 0.0.0.0                                │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP + JWT
                            ▼
┌─────────────────────────────────────────────────────────────┐
│             Backend (FastAPI + Python)                       │
│                                                               │
│  - JWT Verification (Firebase Admin SDK)                    │
│  - Auto-tenant Assignment                                    │
│  - CORS: http://100.66.28.67:5173                           │
│  - Port: 8001, Host: 0.0.0.0                                │
└─────┬──────────┬──────────┬──────────┬────────────┬─────────┘
      │          │          │          │            │
      ▼          ▼          ▼          ▼            ▼
┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────┐ ┌────────────┐
│ Supabase │ │ Neo4j  │ │Firebase │ │Claude│ │  YouTube   │
│   DB     │ │  KG    │ │  Auth   │ │  AI  │ │ Data API   │
│          │ │        │ │         │ │      │ │            │
│ Tables:  │ │ Nodes  │ │ Users   │ │Process│ │ Metadata  │
│ projects │ │ Edges  │ │ JWT     │ │Content│ │Transcripts│
│ content  │ │ Props  │ │ Claims  │ │      │ │ Playlists │
│ youtube  │ │        │ │         │ │      │ │           │
└──────────┘ └────────┘ └─────────┘ └──────┘ └───────────┘
```

---

## Deployment Checklist

### ✅ Completed
- [x] Network configuration (Tailscale)
- [x] Frontend Vite config (`host: 0.0.0.0`)
- [x] Backend CORS config
- [x] Firebase JWT verification
- [x] Auto-tenant assignment
- [x] Database schema applied
- [x] PostgREST schema cache refreshed
- [x] All TypeScript type imports fixed
- [x] Environment variables configured
- [x] Services running and accessible
- [x] Comprehensive test suite created

### ⚠️ TODO
- [ ] Enable YouTube Data API v3 in Google Cloud Console
- [ ] Test YouTube video processing end-to-end
- [ ] Test YouTube playlist subscriptions
- [ ] Configure content processing workers
- [ ] Set up monitoring/logging (optional)
- [ ] Production deployment (optional)

---

## Next Steps

1. **Enable YouTube API:**
   - Visit: https://console.cloud.google.com/apis/library/youtube.googleapis.com?project=544000491438
   - Click "Enable API"
   - Wait 1-2 minutes

2. **Test YouTube Processing:**
   ```bash
   # In browser: http://100.66.28.67:5173/youtube
   # Paste any YouTube video URL
   # Click "Process"
   ```

3. **Create First Project:**
   ```bash
   # In browser: http://100.66.28.67:5173/projects
   # Click "New Project"
   # Fill out details
   ```

4. **Start Processing Content:**
   - Upload documents
   - Process YouTube videos
   - Subscribe to YouTube playlists
   - Build knowledge graph

---

## Support & Documentation

**Project Location:**
```
/root/flourisha/01f_Flourisha_Projects/flourisha-app/
├── backend/          # FastAPI backend
├── web/             # React frontend
├── docs/            # Additional documentation
├── test_all_features.py    # Comprehensive tests
└── SETUP_AND_TESTING.md    # This file
```

**Related Documentation:**
- Network Topology: `/root/flourisha/00_AI_Brain/documentation/infrastructure/network-topology.md`
- Architecture: `/root/flourisha/01f_Flourisha_Projects/flourisha-app/docs/ARCHITECTURE.md`
- API Reference: `/root/flourisha/01f_Flourisha_Projects/flourisha-app/docs/API_REFERENCE.md`

**Test & Verify:**
```bash
# Run all tests
python3 test_all_features.py

# Expected: 7/7 tests passed
```

---

**Status:** 🟢 Fully Operational (except YouTube API - needs manual enable)
**Last Tested:** 2025-11-22
**Maintainer:** Flourisha AI System
