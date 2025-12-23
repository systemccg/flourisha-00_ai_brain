# Energy Tracking System

Comprehensive energy and focus tracking using Chrome extension and SMS integration for real-time productivity optimization.

## Overview

The Energy Tracking System captures energy levels and focus quality at 90-minute intervals throughout the workday. It combines Chrome extension popups with SMS fallback to ensure consistent data collection for energy forecasting and task scheduling optimization.

**Key Features:**
- Chrome extension with 90-minute interval popups
- SMS integration via Telnyx for mobile tracking
- 1-10 energy scale with focus quality indicators (Deep/Shallow/Distracted)
- Weekend suppression (optional tracking)
- Real-time database storage in Supabase
- Integration with morning report energy forecasting

## System Architecture

### Data Collection Methods

```
┌─────────────────────────────────────────────────────────────┐
│                    Energy Tracking System                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRIMARY: Chrome Extension                                  │
│  ┌────────────────────────────────────────┐                │
│  │  • 90-minute interval popups           │                │
│  │  • Energy scale: 1-10                  │                │
│  │  • Focus quality: D/S/X                │                │
│  │  • Active hours: 8 AM - 6 PM Pacific   │                │
│  │  • Weekend mode: Suppressed            │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  FALLBACK: SMS (Telnyx)                                     │
│  ┌────────────────────────────────────────┐                │
│  │  • Same 90-minute intervals            │                │
│  │  • Reply format: "8 D" or "6 S"        │                │
│  │  • Active when Chrome not responding   │                │
│  └────────────────────────────────────────┘                │
│                                                             │
│  STORAGE: Supabase (energy_tracking table)                  │
│  USAGE: Morning report, task scheduling, pattern analysis   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Chrome Extension

### Features

**Popup Interface:**
- Appears every 90 minutes during active hours (8 AM - 6 PM Pacific)
- Energy slider: 1 (exhausted) to 10 (peak energy)
- Focus quality buttons: Deep / Shallow / Distracted
- Current task field (optional)
- Quick submit (< 10 seconds)
- Non-intrusive notification if popup missed

**Active Hours:**
- Monday - Friday: 8:00 AM - 6:00 PM Pacific
- Weekends: Suppressed (optional tracking via manual entry)
- Holidays: Configurable suppression

**Data Capture:**
```javascript
{
  "timestamp": "2026-01-15T14:30:00-08:00",
  "energy_level": 7,
  "focus_quality": "deep",
  "current_task": "Writing documentation",
  "source": "chrome_extension"
}
```

### Extension Architecture

**Manifest (manifest.json):**
```json
{
  "manifest_version": 3,
  "name": "Flourisha Energy Tracker",
  "version": "1.0.0",
  "permissions": [
    "alarms",
    "notifications",
    "storage"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  }
}
```

**Background Service (background.js):**
```javascript
// Set 90-minute alarm
chrome.alarms.create('energyCheck', {
  periodInMinutes: 90,
  when: Date.now() + (90 * 60 * 1000)
});

// Handle alarm trigger
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'energyCheck') {
    const now = new Date();
    const hour = now.getHours();
    const day = now.getDay();

    // Check if within active hours
    if (isActiveHour(hour, day)) {
      chrome.action.openPopup();
      chrome.notifications.create({
        type: 'basic',
        title: 'Energy Check',
        message: 'Time to log your energy level',
        priority: 2
      });
    }
  }
});

function isActiveHour(hour, day) {
  // Skip weekends (0 = Sunday, 6 = Saturday)
  if (day === 0 || day === 6) return false;

  // Active hours: 8 AM - 6 PM Pacific
  return hour >= 8 && hour < 18;
}
```

**Popup Interface (popup.html):**
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 320px; padding: 20px; font-family: system-ui; }
    .slider-container { margin: 20px 0; }
    .focus-buttons { display: flex; gap: 10px; margin: 20px 0; }
    .focus-btn { flex: 1; padding: 12px; border: 2px solid #ddd; cursor: pointer; }
    .focus-btn.active { border-color: #2563eb; background: #dbeafe; }
    .submit-btn { width: 100%; padding: 12px; background: #2563eb; color: white; }
  </style>
</head>
<body>
  <h2>Energy Check</h2>

  <div class="slider-container">
    <label>Energy Level: <span id="energyValue">5</span></label>
    <input type="range" id="energySlider" min="1" max="10" value="5" />
  </div>

  <div class="focus-buttons">
    <button class="focus-btn" data-focus="deep">Deep</button>
    <button class="focus-btn" data-focus="shallow">Shallow</button>
    <button class="focus-btn" data-focus="distracted">Distracted</button>
  </div>

  <input type="text" id="currentTask" placeholder="Current task (optional)" />

  <button class="submit-btn" id="submitBtn">Submit</button>

  <script src="popup.js"></script>
</body>
</html>
```

**Popup Logic (popup.js):**
```javascript
let selectedFocus = null;

// Energy slider
document.getElementById('energySlider').addEventListener('input', (e) => {
  document.getElementById('energyValue').textContent = e.target.value;
});

// Focus quality buttons
document.querySelectorAll('.focus-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    document.querySelectorAll('.focus-btn').forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');
    selectedFocus = e.target.dataset.focus;
  });
});

// Submit
document.getElementById('submitBtn').addEventListener('click', async () => {
  const energy = document.getElementById('energySlider').value;
  const task = document.getElementById('currentTask').value;

  if (!selectedFocus) {
    alert('Please select focus quality');
    return;
  }

  const data = {
    timestamp: new Date().toISOString(),
    energy_level: parseInt(energy),
    focus_quality: selectedFocus,
    current_task: task || null,
    source: 'chrome_extension'
  };

  // Send to Supabase
  await sendToSupabase(data);

  // Close popup
  window.close();
});

async function sendToSupabase(data) {
  const response = await fetch('https://your-project.supabase.co/rest/v1/energy_tracking', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': 'YOUR_SUPABASE_ANON_KEY',
      'Authorization': 'Bearer YOUR_SUPABASE_ANON_KEY'
    },
    body: JSON.stringify({
      ...data,
      tenant_id: 'default',
      user_id: 'gwasmuth@gmail.com'
    })
  });

  if (!response.ok) {
    console.error('Failed to submit energy tracking');
  }
}
```

## SMS Integration

### Telnyx Configuration

**Active Hours:** Same as Chrome extension (8 AM - 6 PM Pacific, weekdays only)

**SMS Format:**
```
Prompt: "Energy check! Reply with: [energy 1-10] [focus: D/S/X]"
Example reply: "8 D" (energy: 8, focus: deep)
Example reply: "6 S" (energy: 6, focus: shallow)
Example reply: "3 X" (energy: 3, focus: distracted)
```

**Telnyx Webhook Handler:**
```python
# /root/flourisha/00_AI_Brain/webhooks/telnyx_energy.py
from fastapi import FastAPI, Form
from datetime import datetime
import re

app = FastAPI()

@app.post("/webhooks/telnyx/energy")
async def handle_energy_sms(
    From: str = Form(...),
    Body: str = Form(...)
):
    """
    Handle incoming SMS energy tracking responses.

    Expected format: "8 D" or "6 S" or "3 X"
    """
    # Parse response
    match = re.match(r'(\d+)\s*([DSX])', Body.upper())

    if not match:
        return {
            "message": "Invalid format. Reply: [energy 1-10] [focus: D/S/X]"
        }

    energy = int(match.group(1))
    focus_code = match.group(2)

    # Validate energy range
    if energy < 1 or energy > 10:
        return {
            "message": "Energy must be 1-10"
        }

    # Map focus code
    focus_map = {
        'D': 'deep',
        'S': 'shallow',
        'X': 'distracted'
    }

    # Store in database
    await store_energy_tracking(
        user_id='gwasmuth@gmail.com',
        energy_level=energy,
        focus_quality=focus_map[focus_code],
        source='sms'
    )

    return {
        "message": f"Logged: Energy {energy}, Focus {focus_map[focus_code]}"
    }

async def store_energy_tracking(user_id: str, energy_level: int,
                                focus_quality: str, source: str):
    """Store energy tracking in Supabase."""
    from services.database_service import get_supabase_client

    client = get_supabase_client()
    await client.table('energy_tracking').insert({
        'tenant_id': 'default',
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'energy_level': energy_level,
        'focus_quality': focus_quality,
        'source': source
    }).execute()
```

**Scheduled SMS Prompts:**
```python
# /root/flourisha/00_AI_Brain/services/sms_scheduler.py
import schedule
from twilio.rest import Client
from datetime import datetime

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_energy_prompt():
    """Send SMS energy tracking prompt."""
    now = datetime.now()

    # Check if weekday and active hours
    if now.weekday() >= 5:  # Weekend
        return

    if now.hour < 8 or now.hour >= 18:
        return

    client.messages.create(
        to='+1234567890',
        from_=TWILIO_PHONE_NUMBER,
        body='Energy check! Reply with: [energy 1-10] [focus: D/S/X]\nExample: "8 D"'
    )

# Schedule every 90 minutes during active hours
schedule.every(90).minutes.do(send_energy_prompt)
```

## Database Schema

### energy_tracking Table

```sql
CREATE TABLE energy_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Tracking Data
    timestamp TIMESTAMPTZ NOT NULL,
    energy_level INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    focus_quality VARCHAR(20) NOT NULL CHECK (focus_quality IN ('deep', 'shallow', 'distracted')),

    -- Context
    current_task TEXT,
    source VARCHAR(20) NOT NULL CHECK (source IN ('chrome_extension', 'sms', 'manual')),

    -- Optional metadata
    location VARCHAR(100),
    notes TEXT,

    -- RLS
    CONSTRAINT energy_tenant CHECK (tenant_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE energy_tracking ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their tenant's data
CREATE POLICY "tenant_energy_access"
ON energy_tracking
FOR ALL
USING (tenant_id = current_setting('app.tenant_id', true));

-- Indexes
CREATE INDEX idx_energy_user_time ON energy_tracking(user_id, timestamp DESC);
CREATE INDEX idx_energy_tenant ON energy_tracking(tenant_id);
CREATE INDEX idx_energy_timestamp ON energy_tracking(timestamp DESC);

-- Composite index for common queries
CREATE INDEX idx_energy_user_date ON energy_tracking(user_id, DATE(timestamp));
```

## Energy Forecasting Logic

### Historical Pattern Analysis

```python
# /root/flourisha/00_AI_Brain/services/energy_forecast_service.py
from datetime import datetime, timedelta
import numpy as np

class EnergyForecastService:
    """Service for energy level forecasting."""

    async def forecast_daily_energy(self, date: datetime) -> dict:
        """
        Forecast energy levels for a given date.

        Uses:
        1. Day-of-week historical patterns
        2. Recent 7-day trend
        3. Schedule density impact
        """
        day_of_week = date.weekday()

        # Get historical pattern for this day of week
        historical = await self.get_historical_pattern(day_of_week)

        # Get recent trend (last 7 days)
        recent_trend = await self.calculate_recent_trend()

        # Estimate schedule impact
        schedule_impact = await self.estimate_schedule_impact(date)

        # Weighted combination
        forecast = {
            'morning': self._forecast_period(historical['morning'], recent_trend, schedule_impact, 0.5, 0.3, 0.2),
            'afternoon': self._forecast_period(historical['afternoon'], recent_trend, schedule_impact, 0.5, 0.3, 0.2),
            'evening': self._forecast_period(historical['evening'], recent_trend, schedule_impact, 0.5, 0.3, 0.2)
        }

        return forecast

    async def get_historical_pattern(self, day_of_week: int) -> dict:
        """Get average energy levels for this day of week."""
        query = """
        SELECT
            CASE
                WHEN EXTRACT(HOUR FROM timestamp) < 12 THEN 'morning'
                WHEN EXTRACT(HOUR FROM timestamp) < 17 THEN 'afternoon'
                ELSE 'evening'
            END as period,
            AVG(energy_level) as avg_energy
        FROM energy_tracking
        WHERE EXTRACT(DOW FROM timestamp) = $1
          AND timestamp > NOW() - INTERVAL '90 days'
        GROUP BY period
        """
        # Execute query and return results

    async def calculate_recent_trend(self) -> float:
        """Calculate recent energy trend (increasing/decreasing)."""
        query = """
        SELECT
            DATE(timestamp) as date,
            AVG(energy_level) as avg_energy
        FROM energy_tracking
        WHERE timestamp > NOW() - INTERVAL '7 days'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        # Calculate linear regression slope

    async def estimate_schedule_impact(self, date: datetime) -> float:
        """Estimate how schedule density affects energy."""
        # Get calendar events for date
        events = await self.get_calendar_events(date)

        meeting_hours = sum(e.duration_hours for e in events if e.type == 'meeting')

        # High meeting load decreases energy
        if meeting_hours > 4:
            return -1.5
        elif meeting_hours > 2:
            return -0.5
        else:
            return 0

    def _forecast_period(self, historical: float, trend: float,
                        impact: float, w1: float, w2: float, w3: float) -> float:
        """Weighted forecast for time period."""
        return (historical * w1) + (trend * w2) + (impact * w3)
```

## Weekend Mode Behavior

**Default**: Weekend tracking suppressed
**Override**: Manual entry available via web interface

**Configuration:**
```json
{
  "weekend_tracking": {
    "enabled": false,
    "weekend_days": [0, 6],  // Sunday, Saturday
    "manual_entry_allowed": true,
    "chrome_extension_suppressed": true,
    "sms_suppressed": true
  }
}
```

## Data Analysis and Insights

### Common Queries

**Daily energy summary:**
```sql
SELECT
    DATE(timestamp) as date,
    AVG(energy_level) as avg_energy,
    MODE() WITHIN GROUP (ORDER BY focus_quality) as primary_focus,
    COUNT(*) as measurement_count
FROM energy_tracking
WHERE user_id = 'gwasmuth@gmail.com'
  AND timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

**Energy by time of day:**
```sql
SELECT
    EXTRACT(HOUR FROM timestamp) as hour,
    AVG(energy_level) as avg_energy,
    COUNT(*) as measurements
FROM energy_tracking
WHERE user_id = 'gwasmuth@gmail.com'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY hour
ORDER BY hour;
```

**Focus quality distribution:**
```sql
SELECT
    focus_quality,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM energy_tracking
WHERE user_id = 'gwasmuth@gmail.com'
  AND timestamp > NOW() - INTERVAL '30 days'
GROUP BY focus_quality;
```

## Integration with Other Systems

### Morning Report
- Display yesterday's energy pattern graph
- Show energy forecast for today
- Recommend optimal task scheduling windows

### Task Scheduling
- Match high-energy tasks to high-energy forecast periods
- Suggest task reordering based on energy availability
- Alert when scheduling demanding tasks during low-energy periods

### OKR System
- Correlate energy patterns with OKR progress
- Identify energy optimization opportunities
- Track energy investment in key results

## Related Documentation

- [MORNING_REPORT.md](./MORNING_REPORT.md) - Energy forecast integration
- [SYSTEM_SPEC.md](../SYSTEM_SPEC.md) - Canonical system reference
- [DATABASE_SCHEMA.md](../database/DATABASE_SCHEMA.md) - Energy tracking schema

---

*Part of Pillar 3: THINK (Strategic Command) in the Flourisha Five Pillars Architecture*
