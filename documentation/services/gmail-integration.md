# Gmail Integration - Implementation Guide

**Service Type:** Email ingestion and sync
**Integration Point:** Existing RAG system (KnowledgeIngestionService)
**Status:** Planning phase
**Priority:** HIGH

## Executive Summary

Gmail Integration enables selective email ingestion into the Flourisha AI Brain knowledge base using a privacy-first, label-based approach. Only emails explicitly labeled with `Flourisha/Unprocessed` are synced, ensuring user control and GDPR compliance.

**Key Features:**
- OAuth 2.0 authentication (no passwords)
- Selective ingestion via Gmail labels
- Integration with three-store RAG (Vector + Graph + Whole)
- Automatic email-to-knowledge-base pipeline

---

## System Architecture

### Three-Store RAG Integration

```
Gmail Labeled Email
        ↓
Email Fetching Service
        ↓
Email Parser (extract text, metadata)
        ↓
KnowledgeIngestionService.ingest_document()
    ├→ Vector Store (pgvector): Semantic search via embeddings
    ├→ Graph Store (Neo4j/Graphiti): Entities (people, topics, relationships)
    └→ Whole Store (Supabase): Raw email content for source retrieval
```

### Component Architecture

**1. OAuth Service**
- Generates authorization URLs
- Handles OAuth callbacks
- Encrypts/stores tokens (AES-256)
- Automatic token refresh

**2. Label Manager**
- Creates `Flourisha/Unprocessed` label if not exists
- Verifies label permissions
- Stores label ID for efficient querying

**3. Email Scanner**
- Queries Gmail for labeled messages
- Extracts metadata (from, subject, date)
- Handles pagination for large result sets
- Respects Gmail API rate limits

**4. Email Parser**
- Extracts plain text from HTML
- Preserves email structure
- Parses sender/recipient information
- Handles attachments (metadata only initially)

**5. Ingestion Pipeline**
- Queues emails for processing
- Calls KnowledgeIngestionService
- Tracks sync status and progress
- Error handling and retry logic

---

## Architecture Decision Records (ADRs)

### ADR-001: Selective Ingestion via Gmail Labels

**Context:** Privacy and compliance concerns with blind inbox mirroring

**Decision:** Use Gmail labels as consent boundary - only emails with `Flourisha/Unprocessed` label are ingested

**Rationale:**
- User explicitly controls what's stored
- GDPR data minimization compliance
- Reduced storage costs (curated content only)
- Clear opt-in mechanism visible in Gmail UI

**Consequences:**
- ✅ Enhanced privacy and user control
- ✅ Lower storage and compute costs
- ✅ Better quality knowledge base (curated)
- ❌ Requires active user participation
- ❌ Won't auto-capture all emails

**Alternatives Considered:**
- Blind inbox sync → Rejected (privacy/liability)
- Sender whitelist → Rejected (less flexible)

---

### ADR-002: Integration with Existing RAG System

**Context:** Flourisha has working three-store RAG infrastructure

**Decision:** Reuse KnowledgeIngestionService instead of building new storage layer

**Rationale:**
- Avoid code duplication
- Unified knowledge base (emails + documents)
- Consistent query interface
- Faster implementation

**Consequences:**
- ✅ Faster development
- ✅ Unified search across all content types
- ✅ Shared infrastructure costs
- ❌ Tightly coupled to existing RAG system
- ❌ Changes to RAG affect email pipeline

---

### ADR-003: OAuth 2.0 for Authorization

**Context:** Need secure Gmail access without passwords

**Decision:** Use Google OAuth 2.0 with authorization code flow

**Rationale:**
- Industry standard for Google APIs
- No password storage (tokens only)
- User consent screen shows permissions
- Revokable access

**Consequences:**
- ✅ Secure, transparent permissions
- ✅ Users can revoke from Google settings
- ❌ Requires Google verification for production
- ❌ OAuth flow complexity

**Required Scopes:**
- `gmail.labels` - Create and manage labels
- `gmail.modify` - Apply labels to messages

---

### ADR-004: Token Encryption and Secure Storage

**Context:** OAuth tokens must be stored securely

**Decision:** AES-256 encryption before storing in Supabase

**Rationale:**
- Defense in depth (encrypted at rest)
- GDPR compliance
- Key rotation capability
- Standard practice

**Consequences:**
- ✅ Tokens protected if database breached
- ✅ Compliance with security standards
- ❌ Performance overhead (minimal)
- ❌ Key management complexity

---

## Data Flow: Email to Knowledge Base

### Step 1: User Labels Email in Gmail
```
User opens email in Gmail
User applies "Flourisha/Unprocessed" label
Gmail updates email metadata
```

### Step 2: Sync Job Triggered
```typescript
// Periodic sync (every 1 hour) or manual trigger
async function syncLabeledEmails(userId: string) {
  const labelId = await getLabelId(userId, 'Flourisha/Unprocessed');
  const messages = await gmail.users.messages.list({
    userId: 'me',
    labelIds: [labelId],
    q: `after:${lastSyncDate}`
  });

  for (const message of messages) {
    await processEmail(message.id);
  }
}
```

### Step 3: Email Fetched and Parsed
```typescript
async function processEmail(messageId: string) {
  const email = await gmail.users.messages.get({
    id: messageId,
    format: 'full'
  });

  const parsed = {
    subject: extractHeader(email, 'Subject'),
    from: extractHeader(email, 'From'),
    to: extractHeader(email, 'To'),
    date: new Date(parseInt(email.internalDate)),
    body: extractBody(email), // HTML → plain text
    metadata: {
      threadId: email.threadId,
      labels: email.labelIds,
      messageId: email.id
    }
  };

  return parsed;
}
```

### Step 4: Ingested to RAG System
```typescript
async function ingestEmailToRAG(email: ParsedEmail) {
  const document = {
    id: generateId(),
    source: 'gmail',
    sourceId: email.metadata.messageId,
    title: `Email: ${email.subject}`,
    content: email.body,
    metadata: {
      sender: email.from,
      recipients: [email.to],
      sentAt: email.date.toISOString(),
      threadId: email.metadata.threadId,
      docType: 'email'
    }
  };

  // Reuse existing ingestion service
  const result = await knowledgeIngestionService.ingest_document({
    ...document,
    extraction_backend: 'claude' // Use Claude for entity extraction
  });

  return result;
}
```

### Step 5: Stored in Three Stores

**Whole Store (Supabase):**
```sql
INSERT INTO documents (id, source, source_id, title, content, metadata)
VALUES (
  'doc_123',
  'gmail',
  'msg_abc',
  'Email: Project Update',
  'Full email body text...',
  '{"sender": "alice@example.com", "sentAt": "2025-12-13", ...}'
);
```

**Vector Store (pgvector):**
```sql
-- Email chunked and embedded
INSERT INTO document_chunks (document_id, content, embedding)
VALUES (
  'doc_123',
  'Project Update - We completed Phase 1...',
  '[0.234, -0.456, ...]::vector' -- 1536-dimensional embedding
);
```

**Graph Store (Neo4j):**
```cypher
CREATE (email:Document {id: "doc_123", type: "email", subject: "Project Update"})
CREATE (person:Person {name: "Alice", email: "alice@example.com"})
CREATE (project:Project {name: "Phase 1"})
CREATE (email)-[:SENT_BY]->(person)
CREATE (email)-[:ABOUT]->(project)
```

---

## Database Schema

### New Tables Required

```sql
-- OAuth credentials (encrypted)
CREATE TABLE gmail_credentials (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL, -- AES-256 encrypted
    refresh_token TEXT NOT NULL, -- AES-256 encrypted
    token_expires_at TIMESTAMPTZ NOT NULL,
    scope TEXT NOT NULL,
    gmail_address TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- Sync state tracking
CREATE TABLE gmail_sync_state (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    label_id TEXT NOT NULL,
    last_sync_timestamp TIMESTAMPTZ,
    history_id TEXT, -- Gmail history checkpoint
    sync_status TEXT DEFAULT 'idle', -- idle, syncing, error
    last_error TEXT,
    error_count INTEGER DEFAULT 0,
    messages_synced INTEGER DEFAULT 0,
    last_checked_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sync job tracking
CREATE TABLE sync_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'queued', -- queued, processing, completed, failed
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    messages_processed INTEGER DEFAULT 0,
    messages_ingested INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_log JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_gmail_credentials_user ON gmail_credentials(user_id);
CREATE INDEX idx_gmail_sync_state_user ON gmail_sync_state(user_id);
CREATE INDEX idx_sync_jobs_user_created ON sync_jobs(user_id, created_at DESC);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
```

---

## API Endpoints

### POST /api/gmail/auth
Initiate OAuth 2.0 flow

**Response:** Redirect to Google OAuth consent screen

---

### GET /api/gmail/callback
Handle OAuth callback from Google

**Query Params:**
- `code`: Authorization code
- `state`: CSRF token

**Response:**
```json
{
  "success": true,
  "message": "Gmail connected successfully",
  "user_id": "uuid",
  "email": "user@gmail.com"
}
```

---

### POST /api/gmail/labels/create
Create or verify Flourisha/Unprocessed label

**Response:**
```json
{
  "success": true,
  "label_id": "Label_123",
  "created": false
}
```

---

### POST /api/gmail/sync
Trigger email sync job

**Request:**
```json
{
  "force_full_sync": false,
  "limit": 100
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "sync_job_789",
  "status": "queued"
}
```

---

## Security Considerations

### Token Encryption
```typescript
import crypto from 'crypto';

const ALGORITHM = 'aes-256-gcm';
const KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'base64');

function encryptToken(token: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(ALGORITHM, KEY, iv);
  const encrypted = Buffer.concat([
    cipher.update(token, 'utf8'),
    cipher.final()
  ]);
  const authTag = cipher.getAuthTag();

  return Buffer.concat([iv, authTag, encrypted]).toString('base64');
}

function decryptToken(encryptedToken: string): string {
  const data = Buffer.from(encryptedToken, 'base64');
  const iv = data.slice(0, 16);
  const authTag = data.slice(16, 32);
  const encrypted = data.slice(32);

  const decipher = crypto.createDecipheriv(ALGORITHM, KEY, iv);
  decipher.setAuthTag(authTag);

  return Buffer.concat([
    decipher.update(encrypted),
    decipher.final()
  ]).toString('utf8');
}
```

### CSRF Protection
```typescript
// Generate state parameter for OAuth
const state = crypto.randomBytes(32).toString('hex');
await redis.setex(`oauth:state:${userId}`, 600, state); // 10 min TTL

// Verify on callback
const storedState = await redis.get(`oauth:state:${userId}`);
if (state !== storedState) {
  throw new Error('CSRF validation failed');
}
```

---

## Testing Strategy

### Unit Tests
- Token encryption/decryption
- Email parsing (HTML → text)
- Label creation logic
- Rate limiter calculations

### Integration Tests
- OAuth flow (mocked Gmail API)
- Label application
- Email fetching with pagination
- RAG ingestion (mocked KnowledgeIngestionService)

### E2E Tests
- Complete flow: OAuth → Label → Sync → Query
- Test with real Gmail account (development)
- Verify emails appear in search results

### Security Tests
- Token encryption verified
- CSRF protection working
- Scope validation
- Unauthorized access prevented

---

## Implementation Timeline

**Week 1:** Google Cloud setup, OAuth implementation
**Week 2:** Label management, email fetching
**Week 3:** RAG integration, testing
**Week 4+:** Google verification, production deployment

---

## Related Documentation

- **RAG System Overview:** `/root/flourisha/00_AI_Brain/documentation/knowledge-stores/OVERVIEW.md`
- **KnowledgeIngestionService:** `/root/flourisha/00_AI_Brain/documentation/services/KNOWLEDGE_INGESTION.md`
- **Database Schema:** `/root/flourisha/00_AI_Brain/documentation/database/DATABASE_SCHEMA.md`
- **Vector Store:** `/root/flourisha/00_AI_Brain/documentation/database/VECTOR_STORE.md`

---

**Created:** 2025-12-13
**Last Updated:** 2025-12-13
