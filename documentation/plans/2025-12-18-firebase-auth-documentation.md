# Plan: Update SYSTEM_SPEC.md with Firebase Auth Documentation

## Problem Statement

SYSTEM_SPEC.md currently documents `Supabase Auth` for authentication, but the actual implementation uses **Firebase Authentication** with Supabase as the database only. This discrepancy could confuse future development.

## User Decisions (Confirmed)

- **UI Library:** Chakra UI (SYSTEM_SPEC is correct)
- **Doc Structure:** Link only to FRONTEND_ARCHITECTURE.md (keep separate)
- **Firebase Scope:** Auth only (no other Firebase services)

## Key Files to Modify

1. `/root/flourisha/00_AI_Brain/documentation/SYSTEM_SPEC.md` - Primary changes

## Key Files to Reference

1. `/root/flourisha/00_AI_Brain/auth/firebase_auth.py` - Actual auth implementation
2. `/root/flourisha/01f_Flourisha_Projects/flourisha-app/FRONTEND_ARCHITECTURE.md` - Frontend design (link to this)
3. `/root/flourisha/00_AI_Brain/documentation/security/OAUTH_CREDENTIALS.md` - Firebase credentials

---

## Changes to Make

### Change 1: Fix Technology Stack (Frontend Development section ~line 1095)

**Current:**
```markdown
| **Auth** | Supabase Auth | OAuth, session management |
```

**Change to:**
```markdown
| **Auth** | Firebase Auth | OAuth (Google), Email/Password, JWT tokens |
```

---

### Change 2: Add Authentication Architecture Section

Add new section after "Technology Stack" section:

```markdown
## Authentication Architecture

> **Key Design Decision:** Firebase handles user authentication (identity), Supabase handles data storage (PostgreSQL). This separation provides flexibility and leverages each platform's strengths.

### Authentication Flow

```
User Login → Firebase Auth → JWT Token → Backend validates JWT → Supabase RLS enforces access
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **User Authentication** | Firebase Auth | Email/Password, Google OAuth |
| **JWT Verification** | Firebase Public Keys | Backend validates tokens without service account |
| **Database** | Supabase PostgreSQL | All application data with RLS policies |
| **Authorization** | Supabase RLS | Row-level security validates JWT claims |

### Firebase Configuration

| Setting | Value |
|---------|-------|
| **Project ID** | `flourisha-d959a` |
| **Auth Methods** | Email/Password, Google OAuth |
| **Custom Claims** | `tenant_id`, `groups`, `role` |
| **JWT Verification** | Public key validation (no service account needed) |

### Key Auth Files

- `00_AI_Brain/auth/firebase_auth.py` - JWT verification implementation
- `00_AI_Brain/documentation/security/OAUTH_CREDENTIALS.md` - Credential management
```

---

### Change 3: Add Firebase to Infrastructure/Core Services table

Add row to Core Services table:

```markdown
| Firebase Auth | `flourisha-d959a` project | User authentication, JWT issuance |
```

---

### Change 4: Add Link to FRONTEND_ARCHITECTURE.md in Quick Navigation

Add to Quick Navigation table:

```markdown
| **Understand frontend design** | [FRONTEND_ARCHITECTURE.md](../01f_Flourisha_Projects/flourisha-app/FRONTEND_ARCHITECTURE.md) |
```

---

### Change 5: Update FRONTEND_ARCHITECTURE.md (optional follow-up)

Note: FRONTEND_ARCHITECTURE.md says `shadcn/ui` but user confirmed **Chakra UI** is correct. Consider updating that doc later to match.

---

## Implementation Steps

1. [ ] Update Technology Stack table: `Supabase Auth` → `Firebase Auth`
2. [ ] Add "Authentication Architecture" section after Technology Stack
3. [ ] Add Firebase Auth row to Infrastructure/Core Services table
4. [ ] Add FRONTEND_ARCHITECTURE.md link to Quick Navigation table
5. [ ] Update "Last Updated" timestamp

---

## Risk Assessment

- **Low risk** - Documentation-only changes
- **No code changes** required
- **Improves accuracy** for future development work
