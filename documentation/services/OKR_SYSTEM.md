# OKR System

Objectives and Key Results (OKR) tracking system for quarterly goal management with weekly measurement and daily progress integration.

## Overview

The Flourisha OKR System implements quarterly goal tracking using the OKR methodology popularized by Google and Intel. It provides structured goal setting, weekly measurement, and integration with the morning report system.

**Key Features:**
- Quarterly objective setting (4 objectives per quarter)
- Key results with quantifiable targets
- Weekly measurement schedule
- Daily progress tracking
- Morning report integration
- Risk and blocker identification

## OKR Structure

### Hierarchy

```
Quarter (Q1 2026)
  │
  ├─ Objective 1: Revenue System Foundation
  │   ├─ Key Result 1.1: Complete financial model (Target: 100%)
  │   ├─ Key Result 1.2: Identify 5 revenue streams (Target: 5)
  │   └─ Key Result 1.3: Build tracking dashboard (Target: 1)
  │
  ├─ Objective 2: Health Optimization
  │   ├─ Key Result 2.1: BP under 130/85 consistently (Target: 90% of readings)
  │   └─ Key Result 2.2: Exercise 4x/week (Target: 12 weeks at 4x)
  │
  ├─ Objective 3: AI Brain Implementation
  │   └─ Key Result 3.1: Deploy 4-department system (Target: 100%)
  │
  └─ Objective 4: Knowledge Systematization
      └─ Key Result 4.1: Process 50 YouTube videos (Target: 50)
```

### Component Definitions

**Objective**: Qualitative, ambitious, inspirational goal
- Should be memorable and motivating
- Typically 3-5 per quarter
- Aligned with long-term vision
- Example: "Build foundation for sustainable revenue generation"

**Key Result**: Quantifiable metric that measures objective success
- Must be measurable with clear target value
- Typically 2-5 per objective
- Aggressive but achievable
- Example: "Identify and validate 5 distinct revenue streams"

## Q1 2026 OKR Template

### Objective 1: Revenue System Foundation
**Why**: Establish systematic approach to revenue generation and tracking

| Key Result | Target | Measurement | Frequency |
|------------|--------|-------------|-----------|
| KR 1.1: Complete comprehensive financial model | 100% | Model completeness checklist | Weekly |
| KR 1.2: Identify 5 validated revenue streams | 5 streams | Number of validated streams | Weekly |
| KR 1.3: Build automated tracking dashboard | 1 dashboard | Dashboard functionality score | Weekly |

### Objective 2: Health Optimization
**Why**: Optimize physical health to support sustained high performance

| Key Result | Target | Measurement | Frequency |
|------------|--------|-------------|-----------|
| KR 2.1: Blood pressure under 130/85 | 90% of readings | BP reading percentage | Daily/Weekly rollup |
| KR 2.2: Exercise 4x per week | 12 weeks | Weekly exercise count | Weekly |
| KR 2.3: Sleep 7+ hours nightly | 85% of nights | Sleep tracking percentage | Daily/Weekly rollup |

### Objective 3: AI Brain Implementation
**Why**: Deploy comprehensive AI infrastructure for productivity and knowledge management

| Key Result | Target | Measurement | Frequency |
|------------|--------|-------------|-----------|
| KR 3.1: Deploy 4-department system | 100% | Implementation checklist | Weekly |
| KR 3.2: Process 100 knowledge items | 100 items | Processed content count | Weekly |
| KR 3.3: Achieve 90% morning report delivery | 90% | Delivery success rate | Weekly |

### Objective 4: Knowledge Systematization
**Why**: Build comprehensive, searchable knowledge base from all learning sources

| Key Result | Target | Measurement | Frequency |
|------------|--------|-------------|-----------|
| KR 4.1: Process 50 YouTube videos | 50 videos | Processed video count | Weekly |
| KR 4.2: Create personality profiles for 20 contacts | 20 profiles | Profile completion count | Weekly |
| KR 4.3: Execute 10 knowledge synthesis sessions | 10 sessions | Session completion count | Weekly |

## Measurement Methodology

### Weekly Measurement Schedule

**When**: Every Monday at 8:00 AM Pacific
**Duration**: 30 minutes
**Process**:
1. Review previous week's progress
2. Update current values for all key results
3. Calculate progress percentage
4. Identify blockers or risks
5. Adjust tactics if needed
6. Update OKR tracking database

### Progress Calculation

```python
def calculate_kr_progress(current_value: float, target_value: float, kr_type: str) -> float:
    """
    Calculate key result progress percentage.

    Args:
        current_value: Current measured value
        target_value: Target value for quarter end
        kr_type: 'percentage', 'count', 'binary', or 'average'

    Returns:
        Progress as percentage (0-100)
    """
    if kr_type == 'percentage':
        # For percentage-based KRs (e.g., 90% of readings)
        return (current_value / target_value) * 100

    elif kr_type == 'count':
        # For count-based KRs (e.g., 5 revenue streams)
        return (current_value / target_value) * 100

    elif kr_type == 'binary':
        # For completion-based KRs (e.g., dashboard built)
        return 100 if current_value >= target_value else 0

    elif kr_type == 'average':
        # For average-based KRs (e.g., BP readings)
        # Requires rolling calculation
        return calculate_rolling_average_progress(current_value, target_value)

def calculate_objective_progress(key_results: list) -> float:
    """
    Calculate overall objective progress from key results.

    Args:
        key_results: List of key result progress percentages

    Returns:
        Weighted average progress
    """
    if not key_results:
        return 0

    # Equal weighting for all KRs by default
    weights = [1.0 / len(key_results)] * len(key_results)

    return sum(kr * weight for kr, weight in zip(key_results, weights))
```

### Status Indicators

| Status | Criteria | Action |
|--------|----------|--------|
| ON TRACK | >= 70% progress at week 8 of 12 | Continue current approach |
| NEEDS ATTENTION | 50-69% progress | Review tactics, increase effort |
| AT RISK | < 50% progress | Major intervention needed |
| BLOCKED | 0% progress for 2+ weeks | Remove blocker or reassess |
| COMPLETED | 100% progress | Celebrate and document learnings |

## Visibility Model (New in Migration 004)

OKRs support personal and workspace visibility, enabling users to track OKRs across different contexts.

### Visibility Levels

| Visibility | Description | Use Case |
|------------|-------------|----------|
| `personal` | Only owner sees, spans all workspaces | Life goals, personal development |
| `workspace` | All workspace members see | Team/company OKRs |

### User's "Life View"

Personal OKRs give users a unified view across all their contexts:

```
┌─────────────────────────────────────────────────────┐
│              GREG'S LIFE VIEW                       │
│                                                     │
│  Personal OKRs (visibility='personal')              │
│  ├─ Health: BP under 130/85                         │
│  ├─ Career: Deploy 5 agents                         │
│  └─ Learning: Process 50 videos                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐    ┌─────────────┐                │
│  │ Workspace A │    │ Workspace B │                │
│  │ (Flourisha) │    │ (Consulting)│                │
│  │             │    │             │                │
│  │ Team OKRs   │    │ Client OKRs │                │
│  └─────────────┘    └─────────────┘                │
└─────────────────────────────────────────────────────┘
```

### Future: Groups

Groups will enable cross-workspace OKR sharing when implemented (Phase 3).

---

## Database Schema

### okr_tracking Table

```sql
-- Base table (from migration 002)
CREATE TABLE okr_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),

    -- OKR Structure
    quarter TEXT NOT NULL,  -- e.g., 'Q1_2026'
    objective_id TEXT NOT NULL,
    objective_title TEXT NOT NULL,
    objective_description TEXT,
    owner TEXT,
    target_completion_date DATE,

    -- Key Result
    key_result_id TEXT NOT NULL,
    key_result_title TEXT NOT NULL,
    key_result_target NUMERIC NOT NULL,
    key_result_current NUMERIC DEFAULT 0,
    key_result_unit TEXT,

    -- Status
    status TEXT DEFAULT 'not_started',

    -- Visibility (migration 004)
    user_id UUID,                    -- Owner for personal OKRs
    visibility VARCHAR(20) DEFAULT 'personal',  -- 'personal' | 'workspace'
    workspace_id UUID,               -- For workspace-scoped OKRs
    priority INTEGER DEFAULT 0,
    department VARCHAR(100),

    UNIQUE(tenant_id, quarter, objective_id, key_result_id)
);

-- Enable RLS
ALTER TABLE okr_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their tenant's OKRs
CREATE POLICY "tenant_okr_access"
ON okr_tracking
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_okr_quarter ON okr_tracking(quarter);
CREATE INDEX idx_okr_tenant ON okr_tracking(tenant_id);
CREATE INDEX idx_okr_status ON okr_tracking(status);
CREATE UNIQUE INDEX idx_okr_unique ON okr_tracking(tenant_id, quarter, key_result_number);
```

### okr_measurements Table

```sql
CREATE TABLE okr_measurements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    okr_id UUID NOT NULL REFERENCES okr_tracking(id) ON DELETE CASCADE,
    measured_at TIMESTAMPTZ DEFAULT NOW(),

    -- Measurement Data
    measured_value NUMERIC NOT NULL,
    measurement_type VARCHAR(20),  -- 'daily', 'weekly', 'monthly', 'manual'
    measured_by TEXT,

    -- Context
    notes TEXT,
    data_source VARCHAR(100),  -- e.g., 'energy_tracking', 'manual_entry', 'automated'

    -- RLS
    CONSTRAINT measurement_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE okr_measurements ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "tenant_measurement_access"
ON okr_measurements
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_measurement_okr ON okr_measurements(okr_id);
CREATE INDEX idx_measurement_date ON okr_measurements(measured_at DESC);
```

## Python Service Functions

### Core OKR Service

Location: `/root/flourisha/00_AI_Brain/services/okr_service.py`

```python
from datetime import datetime, timedelta
from typing import List, Dict
import asyncpg

class OKRService:
    """Service for managing OKR tracking and measurement."""

    async def create_okr(
        self,
        tenant_id: str,
        quarter: str,
        objective_number: int,
        objective: str,
        key_result_number: str,
        key_result: str,
        kr_type: str,
        target_value: float
    ) -> str:
        """Create new OKR entry."""

    async def update_kr_progress(
        self,
        okr_id: str,
        current_value: float,
        notes: str = None
    ) -> bool:
        """Update key result progress."""

    async def record_measurement(
        self,
        okr_id: str,
        value: float,
        measurement_type: str = 'manual',
        data_source: str = None
    ) -> str:
        """Record a measurement for a key result."""

    async def get_quarter_okrs(
        self,
        tenant_id: str,
        quarter: str
    ) -> List[Dict]:
        """Fetch all OKRs for a quarter."""

    async def calculate_okr_status(
        self,
        okr_id: str,
        current_week: int,
        total_weeks: int = 12
    ) -> str:
        """
        Calculate OKR status based on progress and timeline.

        Returns: 'ON TRACK', 'NEEDS ATTENTION', 'AT RISK', or 'BLOCKED'
        """
        progress = await self.get_current_progress(okr_id)
        expected_progress = (current_week / total_weeks) * 100

        if progress >= expected_progress * 0.9:
            return 'ON TRACK'
        elif progress >= expected_progress * 0.7:
            return 'NEEDS ATTENTION'
        elif progress > 0:
            return 'AT RISK'
        else:
            return 'BLOCKED'

    async def get_weekly_velocity(
        self,
        okr_id: str,
        weeks: int = 4
    ) -> float:
        """Calculate average weekly progress velocity."""
        measurements = await self.get_recent_measurements(okr_id, weeks)
        if len(measurements) < 2:
            return 0

        # Calculate week-over-week progress
        velocities = []
        for i in range(1, len(measurements)):
            delta = measurements[i]['value'] - measurements[i-1]['value']
            velocities.append(delta)

        return sum(velocities) / len(velocities)

    async def forecast_completion(
        self,
        okr_id: str
    ) -> datetime:
        """Forecast completion date based on current velocity."""
        current = await self.get_current_progress(okr_id)
        velocity = await self.get_weekly_velocity(okr_id)
        target = await self.get_target_value(okr_id)

        if velocity <= 0:
            return None

        weeks_remaining = (target - current) / velocity
        return datetime.now() + timedelta(weeks=weeks_remaining)
```

## Integration with Morning Report

The OKR system integrates with the morning report to provide daily progress visibility:

```python
# In morning_report_service.py
async def get_okr_section(self, date: datetime) -> dict:
    """Generate OKR progress section for morning report."""
    quarter = self._get_current_quarter(date)
    okrs = await self.okr_service.get_quarter_okrs(self.tenant_id, quarter)

    okr_summary = {
        'quarter': quarter,
        'objectives': []
    }

    for objective_num in range(1, 5):  # 4 objectives
        obj_okrs = [okr for okr in okrs if okr['objective_number'] == objective_num]
        if not obj_okrs:
            continue

        obj_progress = sum(okr['progress_percentage'] for okr in obj_okrs) / len(obj_okrs)
        obj_status = await self._determine_objective_status(obj_okrs)

        okr_summary['objectives'].append({
            'number': objective_num,
            'title': obj_okrs[0]['objective'],
            'progress': obj_progress,
            'status': obj_status,
            'key_results': obj_okrs
        })

    return okr_summary
```

## Best Practices

### Setting OKRs
1. **Ambitious but achievable**: Aim for 70-80% completion rate
2. **Measurable**: Every KR must have a clear numeric target
3. **Aligned**: Connect to long-term vision and strategy
4. **Focused**: Limit to 3-5 objectives per quarter
5. **Balanced**: Mix business, personal, and health goals

### Measurement Discipline
1. **Weekly reviews**: Non-negotiable Monday measurement
2. **Honest assessment**: Don't inflate progress
3. **Document blockers**: Capture risks immediately
4. **Adjust tactics**: If off-track, change approach quickly
5. **Celebrate wins**: Acknowledge progress and completions

### Common Pitfalls
- Setting too many objectives (> 5)
- Vague key results without clear metrics
- Infrequent measurement (< weekly)
- Sandbagging targets (too easy)
- Abandoning OKRs mid-quarter without review

## Related Documentation

- [MORNING_REPORT.md](./MORNING_REPORT.md) - Daily OKR integration
- [SYSTEM_SPEC.md](../SYSTEM_SPEC.md) - Canonical system reference
- [DATABASE_SCHEMA.md](../database/DATABASE_SCHEMA.md) - OKR table schemas

---

*Part of Pillar 3: THINK (Strategic Command) in the Flourisha Five Pillars Architecture*
