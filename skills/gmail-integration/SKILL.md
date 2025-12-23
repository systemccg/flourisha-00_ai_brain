---
name: gmail-integration
description: Gmail API integration with selective label-based ingestion into AI Brain RAG system. USE WHEN user says "sync gmail", "connect gmail", "check email", "search emails", OR "gmail setup". Implements OAuth 2.0, label management, and email-to-RAG pipeline.
---

# Gmail Integration Skill

**Auto-loads:** No (invoked on-demand)
**Priority:** HIGH
**Status:** Working (service implemented)
**Tech Stack:** Python, Gmail API, OAuth 2.0
**Service Location:** `/root/flourisha/00_AI_Brain/services/gmail_service.py`

## Overview

Selective email ingestion system that:
- Uses OAuth 2.0 for secure Gmail access (no passwords)
- Implements label-based filtering (`Flourisha/Unprocessed` label)
- Feeds emails into three-store RAG system (Vector + Graph + Whole)
- Respects privacy through explicit user control

## Workflow Triggers

| User Says | Action |
|-----------|--------|
| "sync gmail" | Trigger email sync from labeled messages |
| "connect gmail" | Initiate OAuth 2.0 flow |
| "gmail setup" | Guide through Google Cloud Console setup |
| "search emails for X" | Query RAG system for email content |
| "check gmail status" | Show sync status and connection health |

## Architecture

### Key Components
1. **OAuth Service** - Google authentication and token management
2. **Label Manager** - Create/manage Flourisha/Unprocessed label in Gmail
3. **Email Scanner** - Identify emails to sync based on labels
4. **Ingestion Pipeline** - Parse emails and feed to RAG system
5. **Rate Limiter** - Respect Gmail API quotas

### Data Flow
```
User labels email in Gmail
  ↓
Sync job fetches labeled emails only
  ↓
Email parsed (subject, body, metadata)
  ↓
KnowledgeIngestionService.ingest_document()
  ├→ Vector Store (pgvector embeddings)
  ├→ Graph Store (entities: people, topics)
  └→ Whole Store (raw email content)
```

## Architecture Decisions

### ADR-001: Selective Ingestion via Labels
**Why:** Privacy-first approach - user explicitly chooses what's stored
**Benefit:** GDPR compliance, reduced storage costs, user control
**Tradeoff:** Requires active user participation

### ADR-002: Integration with Existing RAG
**Why:** Reuse KnowledgeIngestionService instead of building new infrastructure
**Benefit:** Unified knowledge base, faster implementation
**Tradeoff:** Tightly coupled to existing RAG system

### ADR-003: OAuth 2.0 (No Passwords)
**Why:** Industry standard, Google-recommended approach
**Benefit:** Secure, revokable, transparent permissions
**Tradeoff:** Requires Google verification for production

## Implementation Checklist

### Phase 1: Setup (Week 1)
- [ ] Create Google Cloud project
- [ ] Enable Gmail API
- [ ] Configure OAuth 2.0 credentials
- [ ] Set up development environment

### Phase 2: OAuth Flow (Week 1-2)
- [ ] Implement authorization URL generation
- [ ] Build OAuth callback handler
- [ ] Token encryption and storage (AES-256)
- [ ] Token refresh mechanism

### Phase 3: Label Management (Week 2)
- [ ] Create Flourisha/Unprocessed label in user's Gmail
- [ ] Label application service
- [ ] Batch label operations

### Phase 4: Email Sync (Week 3)
- [ ] Fetch labeled emails from Gmail API
- [ ] Parse email content and metadata
- [ ] Handle attachments (metadata only initially)
- [ ] Queue for RAG ingestion

### Phase 5: RAG Integration (Week 3)
- [ ] Integrate with KnowledgeIngestionService
- [ ] Verify vector embeddings created
- [ ] Verify graph entities extracted
- [ ] Test email search in knowledge base

### Phase 6: Production (Week 4+)
- [ ] Complete Google verification
- [ ] Deploy to production
- [ ] Monitor Gmail API quotas
- [ ] User testing and refinement

## Required Scopes

- `https://www.googleapis.com/auth/gmail.labels` - Create/manage labels
- `https://www.googleapis.com/auth/gmail.modify` - Apply labels to messages

## Database Schema

### New Tables Needed
```sql
CREATE TABLE gmail_credentials (
    user_id UUID PRIMARY KEY,
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT NOT NULL,
    token_expires_at TIMESTAMPTZ NOT NULL,
    gmail_address TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE gmail_sync_state (
    user_id UUID PRIMARY KEY,
    label_id TEXT NOT NULL,
    last_sync_timestamp TIMESTAMPTZ,
    history_id TEXT,
    sync_status TEXT DEFAULT 'idle',
    messages_synced INTEGER DEFAULT 0
);
```

## Security Considerations

- Tokens encrypted with AES-256 before database storage
- HTTPS only for all OAuth flows
- No password storage (OAuth tokens only)
- User can revoke access from Google Account settings
- Least privilege: Only request needed scopes

## Testing Strategy

- **Unit:** OAuth token exchange, label creation, email parsing
- **Integration:** Gmail API (mocked), RAG ingestion
- **E2E:** Full flow from OAuth → Label → Sync → Query
- **Security:** Token encryption, CSRF protection, scope validation

## Next Steps

1. Read detailed implementation guide: `/root/flourisha/00_AI_Brain/documentation/services/gmail-integration.md`
2. Set up Google Cloud Console (see docs/gmail-api-setup.md)
3. Implement OAuth service
4. Test with development Gmail account

## Related Documentation

- **Implementation Details:** `/root/flourisha/00_AI_Brain/documentation/services/gmail-integration.md`
- **RAG System:** `/root/flourisha/00_AI_Brain/documentation/knowledge-stores/OVERVIEW.md`
- **Database Schema:** `/root/flourisha/00_AI_Brain/documentation/database/DATABASE_SCHEMA.md`
- **Supabase Integration:** `/root/flourisha/00_AI_Brain/documentation/database/VECTOR_STORE.md`

---

**Created:** 2025-12-13
**Last Updated:** 2025-12-13
