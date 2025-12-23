# Morning Report System

Automated 7 AM daily report delivered via HTML email to provide comprehensive daily intelligence.

## Overview

The Morning Report system generates a comprehensive daily intelligence briefing delivered at 7:00 AM Pacific Time. It synthesizes data from multiple sources across the Flourisha AI Brain to provide actionable insights for the day ahead.

**Key Features:**
- Automated daily delivery at 7:00 AM Pacific
- HTML-formatted email to gwasmuth@gmail.com
- Integrates OKR tracking, energy forecasting, knowledge insights, and PARA updates
- THE ONE THING recommendation using priority scoring algorithm
- Yesterday recap with completed tasks and energy patterns
- Today's plan with time-blocked schedule

## System Architecture

### Triggering Mechanism
The morning report is triggered via cron job on the AI Brain server:

```bash
# /etc/crontab or systemd timer
0 7 * * * /root/flourisha/00_AI_Brain/scripts/morning_report.sh
```

### Data Sources

The morning report aggregates data from:

1. **Supabase Database**
   - `energy_tracking` - Yesterday's energy/focus data
   - `okr_tracking` - Current OKR progress
   - `processed_content` - Recent knowledge ingestion
   - `projects` - Active project status

2. **Neo4j Knowledge Graph**
   - Context relationships
   - Personality profiles (Phase 3)
   - Connection patterns

3. **Calendar Integration**
   - Today's scheduled events
   - Time availability blocks

4. **Task Management**
   - Open tasks by priority
   - Overdue items
   - Today's planned work

## Report Sections

### 1. THE ONE THING

**Purpose**: Identify the single most important task for the day using multi-factor priority scoring.

**Algorithm**:
```python
def calculate_the_one_thing(tasks, okrs, energy_forecast):
    """
    Priority Score =
        (OKR_Impact × 0.4) +
        (Urgency × 0.3) +
        (Energy_Match × 0.2) +
        (Dependencies_Cleared × 0.1)
    """
    scored_tasks = []
    for task in tasks:
        okr_impact = calculate_okr_contribution(task, okrs)
        urgency = get_urgency_score(task.due_date, task.priority)
        energy_match = match_task_to_energy_forecast(task, energy_forecast)
        dependencies = check_dependencies_cleared(task)

        score = (
            okr_impact * 0.4 +
            urgency * 0.3 +
            energy_match * 0.2 +
            dependencies * 0.1
        )
        scored_tasks.append((task, score))

    return max(scored_tasks, key=lambda x: x[1])[0]
```

**Output Format**:
```
THE ONE THING for [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task: Complete Q1 revenue forecast model
Why: 95% contribution to OKR 1 (Revenue System), due tomorrow
Estimated Time: 2.5 hours
Best Window: 9:00 AM - 11:30 AM (high energy forecast)
```

### 2. Yesterday Recap

**Data Sources**:
- Completed tasks from task management system
- Energy tracking data (90-minute intervals)
- Meeting summaries

**Components**:
- Tasks completed count
- Energy pattern visualization
- Average focus quality (Deep/Shallow/Distracted)
- Notable accomplishments
- Meeting summary

**Example Output**:
```
YESTERDAY RECAP - [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 7 tasks completed
✓ 3 meetings (2h 15m total)

Energy Pattern:
Morning   [████████░░] 8/10 avg - Deep focus
Afternoon [██████░░░░] 6/10 avg - Shallow focus
Evening   [████░░░░░░] 4/10 avg - Distracted

Top Accomplishments:
1. Completed 4-department architecture documentation
2. Implemented energy tracking Chrome extension
3. Refined OKR measurement methodology
```

### 3. Today's Plan

**Data Sources**:
- Calendar events
- Scheduled tasks
- Energy forecast

**Components**:
- Time-blocked schedule
- Task assignments with duration estimates
- Meeting preparation requirements
- Buffer time allocations

**Example Output**:
```
TODAY'S PLAN - [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7:00 AM - 9:00 AM  Morning routine + report review
9:00 AM - 11:30 AM ⭐ THE ONE THING: Revenue forecast
11:30 AM - 12:00 PM Buffer / Transition
12:00 PM - 1:00 PM Lunch
1:00 PM - 2:00 PM  Meeting: Team sync
2:00 PM - 4:00 PM  Task: Personality profile schema design
4:00 PM - 5:00 PM  Admin + Email processing
5:00 PM - 6:00 PM  Buffer / Wrap-up

Energy Forecast: Strong morning (8-9/10), moderate afternoon (6-7/10)
```

### 4. OKR Progress

**Data Source**: `okr_tracking` table in Supabase

**Components**:
- Quarterly objective status
- Key results with current vs. target
- Weekly velocity
- Blockers or risks

**Example Output**:
```
Q1 2026 OKR PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Objective 1: Revenue System Foundation
Progress: 67% (2 of 3 KRs on track)
  ✓ KR1: Complete financial model → 100%
  ⚠ KR2: Identify 5 revenue streams → 60% (3 of 5)
  ✓ KR3: Build tracking dashboard → 85%
Status: ON TRACK

Objective 2: Health Optimization
Progress: 45%
  → KR1: BP under 130/85 consistently → 55%
  → KR2: Exercise 4x/week → 75% (3 of 4 weeks)
Status: NEEDS ATTENTION
```

See [OKR_SYSTEM.md](./OKR_SYSTEM.md) for detailed tracking methodology.

### 5. PARA Updates

**Data Source**: Project and task management system

**Components**:
- Active projects with status
- Areas requiring attention
- Resources recently added
- Archive suggestions

**Example Output**:
```
PARA SYSTEM UPDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECTS (Active)
  • AI Brain Implementation → Week 2 of 8
  • Q1 Revenue Planning → Final week
  • Client Onboarding System → Design phase

AREAS (Attention Required)
  ⚠ Health: BP readings trending high
  ✓ Finance: On track
  → Learning: 2 new courses started

RESOURCES (Recently Added)
  • 3 YouTube videos processed
  • 1 meeting transcript ingested
  • 2 research papers saved
```

### 6. Energy Forecast

**Data Sources**:
- Historical energy tracking data
- Today's schedule density
- Sleep quality (if available)
- Day of week patterns

**Algorithm**:
```python
def forecast_daily_energy():
    """
    Forecast energy levels using:
    1. Historical day-of-week patterns
    2. Recent 7-day trend
    3. Schedule density impact
    """
    day_pattern = get_historical_pattern(day_of_week)
    recent_trend = calculate_trend(last_7_days_energy)
    schedule_impact = estimate_schedule_drain(todays_calendar)

    forecast = (
        day_pattern * 0.5 +
        recent_trend * 0.3 +
        schedule_impact * 0.2
    )
    return forecast
```

See [ENERGY_TRACKING.md](./ENERGY_TRACKING.md) for tracking methodology.

### 7. Knowledge Insights

**Data Sources**:
- Recently processed content (last 24 hours)
- Knowledge graph connections
- Emerging patterns

**Components**:
- New knowledge added
- Unexpected connections discovered
- Topics requiring deeper research
- Relevant past insights surfaced

**Example Output**:
```
KNOWLEDGE INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Knowledge (Last 24h):
  • Processed: "Daron Vener 5-Department Model" video
  • Added: 3 connections to existing AI architecture notes
  • Tagged: #ai-systems #architecture #productivity

Connections Discovered:
  → Energy tracking correlates with task completion rate
  → Morning deep focus windows align with complex coding tasks

Suggested Exploration:
  • Research: Temporal agent lifecycle management
  • Review: Past notes on multi-agent coordination
```

## Email Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #2563eb; }
        .highlight { background: #fef3c7; padding: 2px 6px; }
        .progress-bar { height: 8px; background: #e5e7eb; border-radius: 4px; }
        .progress-fill { height: 100%; background: #10b981; border-radius: 4px; }
        h1 { color: #1e40af; }
        h2 { color: #3b82f6; border-bottom: 2px solid #dbeafe; padding-bottom: 8px; }
    </style>
</head>
<body>
    <h1>🌅 Morning Report - {date}</h1>

    <div class="section">
        <h2>⭐ THE ONE THING</h2>
        <!-- THE ONE THING content -->
    </div>

    <!-- Additional sections -->

    <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 14px;">
            Generated by Flourisha AI Brain v1.0 | Pillar 3: THINK (Strategic Command)
        </p>
    </footer>
</body>
</html>
```

## Configuration Options

Configuration stored in `/root/flourisha/00_AI_Brain/config/morning_report.json`:

```json
{
  "delivery": {
    "enabled": true,
    "time": "07:00",
    "timezone": "America/Los_Angeles",
    "recipients": ["gwasmuth@gmail.com"],
    "format": "html"
  },
  "sections": {
    "the_one_thing": { "enabled": true, "priority_weights": {"okr": 0.4, "urgency": 0.3, "energy": 0.2, "dependencies": 0.1} },
    "yesterday_recap": { "enabled": true, "include_energy_graph": true },
    "todays_plan": { "enabled": true, "time_blocking": true },
    "okr_progress": { "enabled": true, "show_all": false, "only_at_risk": false },
    "para_updates": { "enabled": true },
    "energy_forecast": { "enabled": true, "lookback_days": 7 },
    "knowledge_insights": { "enabled": true, "max_items": 5 }
  },
  "data_sources": {
    "supabase": { "enabled": true },
    "neo4j": { "enabled": true },
    "calendar": { "enabled": true, "provider": "google" },
    "tasks": { "enabled": true, "provider": "internal" }
  }
}
```

## Dependencies

### Python Packages
```python
# requirements.txt
supabase>=1.0.0
neo4j>=5.0.0
jinja2>=3.0.0  # Email templating
mailgun>=0.1.1  # Email delivery
python-dotenv>=1.0.0
```

### Environment Variables
```bash
# .env
MORNING_REPORT_ENABLED=true
MORNING_REPORT_TIME=07:00
MORNING_REPORT_TZ=America/Los_Angeles
MORNING_REPORT_EMAIL=gwasmuth@gmail.com
MAILGUN_API_KEY=your_key_here
MAILGUN_DOMAIN=your_domain_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Service Dependencies
- Supabase (database queries)
- Neo4j (knowledge graph)
- Mailgun (email delivery)
- Google Calendar API (optional)
- Task management system

## Service Implementation

Core service location: `/root/flourisha/00_AI_Brain/services/morning_report_service.py`

```python
class MorningReportService:
    async def generate_report(self, date: datetime) -> str:
        """Generate complete morning report."""

    async def get_the_one_thing(self) -> Task:
        """Calculate THE ONE THING for today."""

    async def get_yesterday_recap(self) -> dict:
        """Generate yesterday summary."""

    async def get_todays_plan(self) -> dict:
        """Build today's schedule."""

    async def get_okr_progress(self) -> dict:
        """Fetch current OKR status."""

    async def forecast_energy(self) -> dict:
        """Predict today's energy levels."""

    async def send_report(self, html_content: str) -> bool:
        """Deliver report via email."""
```

## Testing

```bash
# Manual trigger for testing
python -m services.morning_report_service --test

# Dry run (generate but don't send)
python -m services.morning_report_service --dry-run

# Send to alternate email
python -m services.morning_report_service --email test@example.com
```

---

## Evening Hook (6 PM Wrap-up)

**Purpose:** End-of-day wrap-up and tomorrow preparation, complementing the morning report.

**Delivery Time:** 6:00 PM Pacific (configurable)

**Trigger:** Cron job or Claude Code hook

### Evening Hook Sections

#### 1. Day Recap
- Tasks completed vs. planned
- Energy pattern summary
- Unfinished items with carry-forward recommendations
- Meetings attended with key outcomes

#### 2. Tomorrow Prep
- Pre-populate tomorrow's THE ONE THING candidates
- Surface upcoming deadlines (next 48 hours)
- Calendar preview for tomorrow
- Energy forecast based on tomorrow's schedule density

#### 3. Reflection Prompts
- "What worked well today?"
- "What got in the way?"
- "What should tomorrow's focus be?"

### Evening Hook Configuration

```json
{
  "evening_hook": {
    "enabled": true,
    "time": "18:00",
    "timezone": "America/Los_Angeles",
    "delivery_method": "claude_hook",
    "sections": {
      "day_recap": true,
      "tomorrow_prep": true,
      "reflection_prompts": true
    }
  }
}
```

### Integration with Morning Report

The evening hook feeds into the next morning's report:
- Reflection responses inform THE ONE THING calculation
- Carry-forward tasks appear in Today's Plan
- Energy patterns update forecasting models

---

## Related Documentation

- [OKR_SYSTEM.md](./OKR_SYSTEM.md) - OKR tracking methodology
- [ENERGY_TRACKING.md](./ENERGY_TRACKING.md) - Energy/focus tracking
- [FLOURISHA_AI_ARCHITECTURE.md](../FLOURISHA_AI_ARCHITECTURE.md) - System overview
- [DATABASE_SCHEMA.md](../database/DATABASE_SCHEMA.md) - Data sources

---

*Part of Pillar 3: THINK (Strategic Command) in the Flourisha Five Pillars Architecture*
