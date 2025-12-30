# Missing API Dependencies

**Generated:** 2025-12-29 (Pacific Time)
**Purpose:** List external APIs that require keys/configuration not yet provided

---

## Summary

The API has **15+ external integrations**. Some are configured, some need API keys.

| Status | Count | Action Required |
|--------|-------|-----------------|
| ✅ Configured | 8 | None |
| ⚠️ Missing Key | 5 | Obtain and add to .env |
| ⏳ Optional | 3 | Only if feature needed |

---

## ✅ Already Configured

These APIs have keys in `/root/.claude/.env` and should work:

| Service | Env Variable | Used By |
|---------|--------------|---------|
| Supabase | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | Database, Vector Store |
| OpenAI | `OPENAI_API_KEY` | Embeddings |
| Anthropic | `ANTHROPIC_API_KEY` | AI Processing |
| ElevenLabs | `ELEVENLABS_API_KEY` | Voice synthesis |
| Perplexity | `PERPLEXITY_API_KEY` | Research agents |
| Google API | `GOOGLE_API_KEY` | Various Google services |
| ClickUp | `CLICKUP_API_KEY` | Task management |
| Gmail | `GMAIL_CREDENTIALS_PATH`, `GMAIL_APP_PASSWORD` | Email processing |

---

## ⚠️ Missing - Required for Full Functionality

### 1. Firebase (Authentication)
**Router:** All authenticated endpoints
**Missing:**
```bash
FIREBASE_PROJECT_ID=your-project-id
```
**How to get:**
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project (or create one)
3. Project Settings → General → Project ID
**Impact:** Without this, JWT authentication won't work. All protected endpoints will fail.

---

### 2. Hedra (Avatar Generation)
**Router:** `/api/hedra/*`
**Missing:**
```bash
HEDRA_API_KEY=your-hedra-api-key
```
**How to get:**
1. Go to [Hedra](https://www.hedra.com)
2. Sign up and access API dashboard
3. Generate API key
**Impact:** Avatar generation, lip-sync videos, realtime avatar sessions will return 503.

---

### 3. Nango (Unified OAuth for 500+ APIs)
**Router:** `/api/nango/*`
**Missing:**
```bash
NANGO_SECRET_KEY=your-nango-secret-key
NANGO_PUBLIC_KEY=your-nango-public-key
NANGO_CALLBACK_URL=https://your-domain.com/api/nango/callback
NANGO_WEBHOOK_SECRET=your-webhook-secret  # Optional
```
**How to get:**
1. Go to [Nango](https://nango.dev)
2. Sign up for account
3. Create environment → Get keys from Settings
**Impact:** OAuth connections to Slack, Notion, HubSpot, etc. won't work.

---

### 4. Neo4j (Knowledge Graph)
**Router:** `/api/graph/*`, `/api/health-dashboard/*`
**Status:** Partially configured - password may be missing
**Check if configured:**
```bash
NEO4J_URI=bolt://neo4j.leadingai.info:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```
**Impact:** Graph queries, entity relationships will fail.

---

### 5. Stripe (Billing - Production)
**Router:** `/api/billing/*`
**Status:** Test key configured, need production key
**Current:**
```bash
MCP_STRIPE_API_KEY=sk_test_...  # Test mode
```
**For Production:**
```bash
STRIPE_API_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
**Impact:** Test payments work, but production billing needs live keys.

---

## ⏳ Optional - Only If Feature Needed

### Mem0 (Persistent Memory)
**Router:** `/api/memory/*`
**Missing:**
```bash
MEM0_API_KEY=your-mem0-api-key
```
**Impact:** Falls back to in-memory storage (data lost on restart).

---

### Replicate (AI Models)
**Router:** Various AI features
**Missing:**
```bash
REPLICATE_API_TOKEN=your-replicate-token
```
**Impact:** Alternative AI models unavailable.

---

### Integration OAuth Clients
**Router:** `/api/integrations/*`
**For each integration, add:**
```bash
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
NOTION_CLIENT_ID=...
NOTION_CLIENT_SECRET=...
# etc.
```
**Impact:** Direct OAuth (without Nango) won't work for specific services.

---

## Environment File Template

Add these to `/root/.claude/.env`:

```bash
# === REQUIRED FOR FULL FUNCTIONALITY ===

# Firebase Authentication
FIREBASE_PROJECT_ID=

# Hedra Avatar Generation
HEDRA_API_KEY=

# Nango OAuth Manager
NANGO_SECRET_KEY=
NANGO_PUBLIC_KEY=
NANGO_CALLBACK_URL=http://localhost:8000/api/nango/callback

# Neo4j (verify password is set)
NEO4J_PASSWORD=

# === OPTIONAL ===

# Mem0 Persistent Memory
MEM0_API_KEY=

# Stripe Production (when ready)
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=

# Admin/Cron secrets (for protected endpoints)
ADMIN_SECRET=generate-a-secure-secret
CRON_SECRET=generate-another-secret
ENERGY_WEBHOOK_SECRET=generate-energy-secret
```

---

## Quick Check Command

Run this to see current configuration status:

```bash
cd /root/flourisha/00_AI_Brain/api && uv run uvicorn main:app --port 8000 &
sleep 3
curl -s http://localhost:8000/api/health | python3 -m json.tool
```

The startup logs will show which services are configured:
```
Configuration loaded: {
  'supabase': True,
  'neo4j': True,
  'firebase': False,  # <-- Needs FIREBASE_PROJECT_ID
  'openai': True,
  'anthropic': True,
  'clickup': True
}
```

---

## Priority Order for Configuration

1. **Firebase** - Required for any authenticated endpoint
2. **Neo4j Password** - Required for knowledge graph features
3. **Hedra** - Required for avatar features
4. **Nango** - Required for third-party OAuth integrations
5. **Stripe Live** - Required only for production billing
6. **Mem0** - Nice-to-have for persistent memory

---

*Report generated by Flourisha AI Agent*
