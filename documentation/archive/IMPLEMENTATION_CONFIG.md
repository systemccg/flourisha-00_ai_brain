# 4-Department AI Brain - Implementation Configuration

**Date:** 2025-12-06
**Status:** Configuration Finalized - Ready for Phase 1 Implementation

---

## User Configuration Decisions

### 1. Email Configuration ✅ FINALIZED

**Email Address:** `gwasmuth@gmail.com`
**SMTP Server:** Gmail (already configured for daily security reminder)
**Format:** HTML
**Usage:** 7 AM morning report + Sunday evening weekly review + 1st of month review
**Delivery:** Automated cron jobs (no manual intervention)

**Implementation:**
- Service: `/root/flourisha/00_AI_Brain/utils/email_sender.py`
- Uses existing Gmail SMTP configuration
- HTML template for morning report with structured sections
- Include "THE ONE THING" prominently at top
- Daily digest format: Summary → Recap → Plan → OKR → PARA → Energy → Insights

---

### 2. SMS Integration ✅ FINALIZED

**Status:** Twilio account creation required
**Phone Number:** 6195123137
**Operating Hours:** 8 AM - 6 PM Pacific Time
**Trigger:** Every 90 minutes during work hours
**Content:** Energy level (1-10) + Focus quality (Deep/Shallow/Distracted) + Optional notes

**Configuration:**
```python
SMS_CONFIG = {
    'phone': '+16195123137',
    'timezone': 'America/Los_Angeles',
    'start_hour': 8,
    'end_hour': 18,
    'interval_minutes': 90,
    'enable_weekend_suppression': True,
    'weekend_message': 'Tracking paused. Have a great weekend! Reply RESUME to continue.'
}
```

**Twilio Setup Required:**
1. Create account at twilio.com
2. Get API key and phone number
3. Store in environment variables: `TWILIO_API_KEY`, `TWILIO_PHONE`, `TWILIO_AUTH_TOKEN`
4. Create `/root/flourisha/00_AI_Brain/services/sms_tracker.py` to handle:
   - 90-minute timer during 8 AM - 6 PM
   - SMS prompt: "Energy? (1-10) | Focus? (D/S/X Deep/Shallow/Distracted)"
   - Response parsing and storage
   - Weekend suppression with manual override

**Database Table:** `energy_tracking` with source='sms'

---

### 3. OKR Configuration ✅ FINALIZED

**Approach:** Template-based (start with templates, customize as needed)
**Objectives per Quarter:** 4
**Measurement:** Weekly → Monthly → Quarterly
**Q1 2026 Template:**

```yaml
Q1_2026:
  objectives:
    - title: "Build Production-Ready AI Brain"
      description: "Complete migration and deployment with full automation"
      owner: "Greg"
      target_completion: "2026-03-31"
      key_results:
        - title: "Migrate all N8N patterns to AI Brain"
          target: 100
          unit: "%"
        - title: "Achieve 95% uptime for background workers"
          target: 95
          unit: "%"
        - title: "Process 1000+ documents through knowledge graph"
          target: 1000
          unit: "documents"

    - title: "Establish Automated Operating Rhythm"
      description: "Zero-click daily/weekly/monthly planning with full automation"
      owner: "Greg"
      target_completion: "2026-03-31"
      key_results:
        - title: "Maintain 90%+ daily roadmap usage"
          target: 90
          unit: "%"
        - title: "Average productivity score ≥ 7.5/10"
          target: 7.5
          unit: "/10"
        - title: "Complete OKR reviews 95% of weeks"
          target: 95
          unit: "%"

    - title: "Expand Knowledge Intelligence System"
      description: "Deep personality profiling and email context integration"
      owner: "Greg"
      target_completion: "2026-03-31"
      key_results:
        - title: "Profile 100% of email contacts"
          target: 100
          unit: "%"
        - title: "Email response agent assists 80% of replies"
          target: 80
          unit: "%"
        - title: "Relationship pattern detection in 50+ connections"
          target: 50
          unit: "relationships"

    - title: "Establish Temporal Agent Factory"
      description: "AI agents for specific projects with continuous improvement"
      owner: "Greg"
      target_completion: "2026-03-31"
      key_results:
        - title: "Deploy 10+ temporal agents"
          target: 10
          unit: "agents"
        - title: "2+ agents auto-promoted to permanent status"
          target: 2
          unit: "permanent agents"
        - title: "Capture learnings from 50+ agent executions"
          target: 50
          unit: "learning captures"
```

**Storage:** `/root/flourisha/00_AI_Brain/okr/Q1_2026.yaml` (template)
**Tracking:** Weekly measurement via cron job on Monday 7 AM
**Update:** Monthly review on Sunday before month-end
**Display:** Include in morning report with progress bars

---

### 4. Chrome Extension ✅ FINALIZED

**Approval:** YES - Build in `/root/flourisha/00_AI_Brain/chrome-extension/`
**Tracking Interval:** 90 minutes (flexible, configurable)
**Weekend Handling:** Suppression mode available with option to switch to "Personal Life Goals" tracking
**Features:**

1. **Popup Window (Every 90 minutes)**
   - Energy level: 1-10 slider
   - Focus quality: D (Deep Work) | S (Shallow Work) | X (Distracted)
   - Optional notes field
   - "Skip" button to dismiss
   - "Snooze" to extend interval

2. **Settings Panel**
   - Toggle weekend suppression
   - Toggle personal goals mode (weekends)
   - Change tracking interval (60/90/120 minutes)
   - View weekly energy/focus summary
   - Export data as CSV

3. **Data Storage**
   - Local: IndexedDB for offline storage
   - Cloud: Sync to Supabase `energy_tracking` table
   - Source: 'chrome_extension'
   - Timestamp: Automatic

4. **Weekday vs Weekend**
   - **Weekday (Mon-Fri, 8 AM - 6 PM):** Professional energy tracking
   - **Weekend:** Ask "What personal goals are you tracking today?" → track differently
   - **Manual Override:** Button to resume work tracking anytime

**Implementation File:** `/root/flourisha/00_AI_Brain/chrome-extension/manifest.json`

---

### 5. Personality Profiles ✅ FINALIZED

**Email Analysis Scope:** ALL emails analyzed and labeled
**Personality Profile Scope:** Only contacts saved in address book
**Current Implementation:** Label all, analyze saved contacts
**Future Enhancement:** Social handle lookup across platforms

**Labeling System:**
- AUTO: System-categorized labels (spam, promotional, personal, professional, vendor, etc.)
- ACTION_REQUIRED: Needs response (not spam/advertising)
- SAVED_CONTACT: Has personality profile
- RELATIONSHIP_TYPE: colleague, client, vendor, friend, family

**Personality Profile Fields:**
```sql
CREATE TABLE personality_profiles (
    id UUID PRIMARY KEY,
    entity_id UUID,
    entity_name TEXT,
    entity_type TEXT,
    communication_style TEXT,      -- direct, diplomatic, analytical, emotional
    decision_making TEXT,          -- data-driven, intuitive, collaborative, authoritative
    behavioral_patterns JSONB,
    relationship_type TEXT,        -- colleague, client, vendor, friend, family
    interaction_history JSONB,
    email_count INTEGER,
    last_email_date TIMESTAMPTZ,
    typical_response_time INTERVAL,
    preferred_communication_channel TEXT,
    personality_flags TEXT[],      -- e.g., 'micromanager', 'narcissist', 'conflict-avoidant'
    communication_preferences TEXT[],
    ai_generated_summary TEXT,
    confidence_score FLOAT,
    tenant_id TEXT NOT NULL
);
```

**Human Review:**
- No pre-approval required for flags (auto-assigned)
- Allow human review/update anytime
- Admin interface to edit flags manually
- "Update Profile" button on email context sidebar

**Email Context Integration:**
When user reads email from saved contact:
- Show personality flags in sidebar
- Suggest tone/approach for reply
- Show recent interaction history
- Highlight red flags (micromanager, etc.)

**Future Phase (Not Phase 1):**
- Query LinkedIn, Twitter, Instagram for relationship depth
- Auto-update profiles from social activity
- Cross-platform communication pattern detection

---

### 6. Agent Factory ✅ FINALIZED

**Naming Convention:** `agent_Purpose_YYYYMMDD`
- Example: `agent_ContentAnalysis_20251206`
- Example: `agent_SalesProspecting_20251208`

**Lifetime Management:**
- **Default Retention:** 30 days
- **Auto-Promotion:** After 2 uses → "permanent" status
- **Permanent Agent:** Moved to `/root/flourisha/00_AI_Brain/agents/permanent/`
- **Archival:** After 30 days, move to `/root/flourisha/00_AI_Brain/agents/archived/`

**Lifecycle:**
```
Create (Purpose Specific)
    ↓
Execute (Task 1)
    ↓
Collect Feedback
    ↓
Execute (Task 2)
    ↓
[IF 2+ uses] → Promote to Permanent
[ELSE] → Continue as Temporal
    ↓
[After 30 days] → Archive with learnings
    ↓
Update Registry (Permanent agents available for future)
```

**Agent Registry:**
- Location: `/root/flourisha/00_AI_Brain/a2a/registry/agents.json`
- Includes: name, purpose, capabilities, system_prompt, created_date, use_count, promotion_date (if permanent)
- Updated on: creation, execution, promotion, archival

**A2A Protocol Integration:**
- Agents register themselves via A2A on creation
- Capabilities advertised to other agents
- Auto-discovery for agent delegation

---

## Implementation Sequence (Updated with Configuration)

### Phase 1: Core Infrastructure (Week 1)

**Priority 1: Documentation** (Create docs in correct locations)
- [ ] `/root/flourisha/00_AI_Brain/documentation/services/MORNING_REPORT.md`
- [ ] `/root/flourisha/00_AI_Brain/documentation/services/OKR_SYSTEM.md`
- [ ] `/root/flourisha/00_AI_Brain/documentation/services/ENERGY_TRACKING.md`
- [ ] `/root/flourisha/00_AI_Brain/documentation/FOUR_DEPARTMENT_SYSTEM.md`
- [ ] Update `/root/flourisha/00_AI_Brain/documentation/database/DATABASE_SCHEMA.md`

**Priority 2: Scripts & Services**
- [ ] `scripts/morning-report-generator.py` (400 LOC)
- [ ] `hooks/evening-productivity-analysis.ts` (300 LOC)
- [ ] `scripts/para-analyzer.py` (350 LOC)
- [ ] `services/okr_tracker.py` (500 LOC)
- [ ] `services/project_priority_manager.py` (250 LOC)
- [ ] `services/productivity_analyzer.py` (300 LOC)
- [ ] `utils/email_sender.py` (150 LOC) - Uses existing Gmail config
- [ ] `okr/Q1_2026.yaml` (Template OKRs)

**Priority 3: Database**
- [ ] Migration: `database/migrations/create_energy_tracking.sql`
- [ ] Migration: `database/migrations/create_okr_tracking.sql`
- [ ] Apply migrations via Supabase

**Priority 4: Integration**
- [ ] Register evening hook in Claude Code settings.json
- [ ] Create cron job: `0 7 * * * morning-report-generator.py` (7 AM daily)
- [ ] Create cron job: `0 */4 * * * para-analyzer.py` (every 4 hours)
- [ ] Test morning report delivery to gwasmuth@gmail.com

### Phase 2: Energy/Focus Tracking (Week 2)

**Priority 1: Twilio Setup**
- [ ] Create Twilio account
- [ ] Get API credentials
- [ ] Store in environment variables

**Priority 2: SMS Service**
- [ ] `services/sms_tracker.py` (200 LOC)
- [ ] SMS prompt template
- [ ] Response parsing logic
- [ ] Weekend suppression handler
- [ ] Database storage to `energy_tracking` table

**Priority 3: Chrome Extension**
- [ ] `chrome-extension/manifest.json` (Manifest v3)
- [ ] `chrome-extension/popup/popup.html` (UI)
- [ ] `chrome-extension/popup/popup.js` (90-min timer logic)
- [ ] `chrome-extension/background.js` (Supabase sync)
- [ ] `chrome-extension/settings/settings.html` (Configuration)
- [ ] Load unpacked extension in Chrome for testing

**Priority 4: Integration**
- [ ] Create cron job: SMS tracker (every 90 minutes 8 AM - 6 PM)
- [ ] Test SMS prompt to 6195123137
- [ ] Test Chrome extension popup
- [ ] Verify data syncs to Supabase

### Phase 3: Knowledge Graph Enhancements (Week 3)

**Priority 1: Personality Profiles**
- [ ] `services/personality_analyzer.py` (450 LOC)
- [ ] Create `personality_profiles` table in Neo4j
- [ ] Email labeling service
- [ ] Claude-powered personality analysis

**Priority 2: Email Context**
- [ ] `services/context_enrichment.py` (350 LOC)
- [ ] Query personality profiles for email context
- [ ] Generate reply suggestions based on communication style

**Priority 3: Email Response Agent**
- [ ] `agents/email-responder/AGENT.md`
- [ ] Integration with Gmail API
- [ ] Context-aware draft generation

### Phase 4: System Evolution (Week 4)

**Priority 1: Agent Factory**
- [ ] `services/agent_factory.py` (600 LOC)
- [ ] Temporal agent creation with naming convention
- [ ] Agent lifecycle management (30-day retention)
- [ ] Auto-promotion after 2 uses

**Priority 2: Continuous Improvement**
- [ ] `services/system_evolution.py` (400 LOC)
- [ ] Agent performance monitoring
- [ ] Feedback collection
- [ ] Registry updates

**Priority 3: Agent Templates**
- [ ] Purpose → System Prompt generator
- [ ] Capability mapping
- [ ] Common agent templates

### Phase 5: Weekly/Monthly Cadence (Week 5)

**Priority 1: Weekly Summary**
- [ ] `scripts/weekly-summary-generator.py` (300 LOC)
- [ ] Cron: Sunday 6 PM
- [ ] 7-day productivity aggregate
- [ ] OKR weekly check-in

**Priority 2: Monthly Review**
- [ ] `scripts/monthly-review-generator.py` (300 LOC)
- [ ] Cron: 1st of month 6 PM
- [ ] 30-day retrospective
- [ ] Goal progress analysis

---

## Email Templates

### Morning Report HTML

```html
<h2>Good morning, Greg! ☀️</h2>

<h3 style="color: #d63031;">THE ONE THING</h3>
<p><strong>{one_thing_task}</strong></p>
<p style="font-size: 0.9em; color: #636e72;">Why: {okr_linkage}</p>

<h3>Yesterday Recap</h3>
<ul>
  <li>Productivity: {score}/10</li>
  <li>Deep Work: {deep_work_hours}h | Shallow: {shallow_work_hours}h</li>
  <li>Top Accomplishments:</li>
  <ul>
    {accomplishments}
  </ul>
  <li>Energy Pattern: Peak at {peak_time}, Dip at {dip_time}</li>
</ul>

<h3>Today's Strategic Plan</h3>
<h4>Tier 1 (Must Complete)</h4>
<ul>{tier1_tasks}</ul>
<h4>Tier 2 (Should Complete)</h4>
<ul>{tier2_tasks}</ul>
<h4>Tier 3 (Could Do)</h4>
<ul>{tier3_tasks}</ul>

<h3>OKR Progress Check - Q1 2026</h3>
{okr_progress_table}

<h3>PARA Updates Since Yesterday</h3>
<ul>{para_changes}</ul>

<h3>Energy Forecast</h3>
<p>{energy_forecast}</p>

<h3>Knowledge Insights</h3>
<p>{relevant_learnings}</p>
```

---

## Success Criteria (Configuration-Aligned)

### Week 1 (Phase 1)
- [ ] 7 AM morning report arrives in gwasmuth@gmail.com daily
- [ ] Productivity score calculated and displayed
- [ ] "THE ONE THING" clearly identified with OKR linkage
- [ ] PARA analyzer detects file changes every 4 hours
- [ ] OKR progress calculated with 4-objective template
- [ ] Evening hook captures productivity analysis on SessionEnd

### Week 2 (Phase 2)
- [ ] Twilio SMS prompts arrive at 6195123137 every 90 minutes (8 AM - 6 PM)
- [ ] Chrome extension popup appears every 90 minutes
- [ ] Energy data syncs to Supabase `energy_tracking` table
- [ ] Weekend suppression working (no SMS/popups Sat-Sun)
- [ ] Energy forecast in morning report is accurate

### Week 3 (Phase 3)
- [ ] All email contacts labeled (spam, professional, etc.)
- [ ] Saved contacts have personality profiles
- [ ] Email context sidebar shows personality flags
- [ ] Email response agent drafts with tone suggestions

### Week 4 (Phase 4)
- [ ] Temporal agents created with naming: `agent_Purpose_YYYYMMDD`
- [ ] Auto-promotion to permanent after 2 uses working
- [ ] Agent registry updated on creation/promotion/archival
- [ ] 30-day auto-archival functional

### Week 5 (Phase 5)
- [ ] Sunday evening weekly summary email
- [ ] Monthly review email on 1st of month
- [ ] OKR progress correctly measured and reported

---

## Environment Variables Required

```bash
# Gmail SMTP (already configured)
GMAIL_USER=gwasmuth@gmail.com
GMAIL_APP_PASSWORD=[existing]

# Twilio (to be created)
TWILIO_API_KEY=[create in account]
TWILIO_PHONE=+16195123137
TWILIO_AUTH_TOKEN=[create in account]

# OpenAI (existing)
OPENAI_API_KEY=[existing]

# Supabase (existing)
SUPABASE_URL=[existing]
SUPABASE_KEY=[existing]

# Neo4j (existing)
NEO4J_URI=[existing]
NEO4J_USER=[existing]
NEO4J_PASSWORD=[existing]
```

---

## Next Immediate Steps

1. **Twilio Account Creation** (User action)
   - Create account at twilio.com
   - Purchase phone number (or use existing)
   - Get API credentials
   - Store in environment variables

2. **Documentation Creation** (Claude action)
   - Create service documentation files
   - Document FOUR_DEPARTMENT_SYSTEM architecture
   - Update DATABASE_SCHEMA.md with new tables

3. **Phase 1 Implementation** (Claude action)
   - Create morning report generator
   - Create evening analysis hook
   - Create PARA analyzer
   - Create OKR tracker service
   - Create productivity analyzer
   - Create email sender utility
   - Create database migrations
   - Set up cron jobs

---

**Status:** ✅ All configuration finalized. Ready for Phase 1 implementation.

