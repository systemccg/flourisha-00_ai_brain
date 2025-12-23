# Evening Productivity Analysis Hook - Registration Guide

## Overview

The `evening-productivity-analysis.ts` hook automatically analyzes daily productivity after work sessions ending after 5 PM. It generates comprehensive JSON reports consumed by the morning report generator.

## Hook Configuration

### Claude Code settings.json

Add this hook configuration to your Claude Code `settings.json`:

```json
{
  "hooks": [
    {
      "trigger": "SessionEnd",
      "condition": "timeOfDay >= 17:00",
      "script": "/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts",
      "description": "Generate evening productivity analysis after 5 PM sessions",
      "enabled": true
    }
  ]
}
```

### Configuration Properties

- **trigger**: `SessionEnd` - Fires when Claude Code session ends
- **condition**: `timeOfDay >= 17:00` - Only runs after 5 PM (17:00)
- **script**: Absolute path to the TypeScript hook file
- **description**: Human-readable description for documentation
- **enabled**: Set to `true` to activate the hook

## Hook Behavior

### Trigger Conditions

The hook will execute when:
1. ✅ A Claude Code session ends
2. ✅ Current time is 17:00 (5 PM) or later
3. ✅ Hook is enabled in settings.json

The hook will **NOT** execute when:
- ❌ Session ends before 17:00
- ❌ Hook is disabled in settings
- ❌ Script file is missing or has errors

### Execution Flow

1. **Session End Triggered**
   - Claude Code detects session termination
   - Checks current time against condition

2. **Time Check** (Internal to hook)
   ```typescript
   const currentHour = getCurrentHour();
   if (currentHour < 17) {
     console.log('Skipping - too early');
     return;
   }
   ```

3. **Parse Session Logs**
   - Reads Claude Code session log (default: `/tmp/claude-session.log`)
   - Extracts timestamps, tool usage, files modified, commits
   - Calculates session duration

4. **Analyze Productivity**
   - Calculate productivity score (1-10)
   - Detect focus quality patterns
   - Identify project activity
   - Extract accomplishments

5. **Generate Analysis**
   - Creates comprehensive DailyAnalysis object
   - Includes all metrics and patterns

6. **Save to JSON**
   - Writes to `/root/flourisha/00_AI_Brain/history/daily-analysis/YYYY-MM-DD.json`
   - Creates directory if needed
   - Handles errors gracefully

## Output Format

### File Location
```
/root/flourisha/00_AI_Brain/history/daily-analysis/2025-12-06.json
```

### JSON Structure

```json
{
  "date": "2025-12-06",
  "productivityScore": 8.5,
  "hoursWorked": 6.2,
  "deepWorkHours": 4.5,
  "shallowWorkHours": 1.2,
  "accomplishments": [
    "Created 2 database migration(s)",
    "Implemented 1 automation hook(s)",
    "Modified 8 file(s)",
    "Made 2 git commit(s)"
  ],
  "toolsUsed": {
    "Edit": 12,
    "Write": 8,
    "Read": 5,
    "Bash": 15,
    "Grep": 3
  },
  "projectsWorkedOn": {
    "00_AI_Brain": {
      "filesModified": 6,
      "commits": 2,
      "timeSpent": 320
    }
  },
  "patternsDetected": [
    "Database schema development",
    "High code output (6 code files modified)",
    "Long focused session (6+ hours)"
  ],
  "blockers": [],
  "energyTracking": {
    "readings": [],
    "averageEnergy": 7.0,
    "peakEnergyTime": "10:00 AM",
    "lowEnergyTime": "2:00 PM"
  },
  "focusQuality": {
    "deepWorkHours": 4.5,
    "shallowWorkHours": 1.2,
    "distractedHours": 0.5,
    "contextSwitches": 6,
    "focusScore": 8.2
  },
  "okrContribution": {
    "objectivesWorkedOn": ["OBJ-001"],
    "keyResultsProgressed": [
      {
        "objectiveId": "OBJ-001",
        "keyResultId": "KR-002",
        "progressMade": 1,
        "unit": "count"
      }
    ]
  },
  "rawSessionData": {
    "startTime": "2025-12-06T14:30:00Z",
    "endTime": "2025-12-06T20:42:00Z",
    "filesModified": [
      "/root/flourisha/00_AI_Brain/database/migrations/001_create_energy_tracking.sql",
      "/root/flourisha/00_AI_Brain/database/migrations/002_create_okr_tracking.sql"
    ],
    "filesCreated": [
      "/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts"
    ],
    "commits": 2
  }
}
```

## Testing the Hook

### Manual Test (Without Waiting for Session End)

```bash
# Run hook directly
cd /root/flourisha/00_AI_Brain/hooks
node evening-productivity-analysis.ts

# Or with ts-node
ts-node evening-productivity-analysis.ts
```

### Expected Output

```
================================================================================
Flourisha AI Brain - Evening Productivity Analysis
================================================================================
Current hour: 20:00
✅ Time check passed - proceeding with analysis...

Parsing session logs...
Calculating productivity score...
Detecting patterns...
Analyzing focus quality...
Extracting accomplishments...
Analyzing project activity...
✅ Analysis saved to: /root/flourisha/00_AI_Brain/history/daily-analysis/2025-12-06.json
📊 Productivity Score: 8.5/10
⏱️  Hours Worked: 6.2
🎯 Accomplishments: 4

================================================================================
✅ Evening productivity analysis complete!
================================================================================
```

### Test Before 5 PM

If run before 5 PM, you'll see:
```
Current hour: 14:00
⏭️  Skipping analysis: Session ended before 17:00
   (Evening analysis only runs after 5 PM)
```

## Integration with Morning Report

The generated JSON files are consumed by:
- **Script**: `/root/flourisha/00_AI_Brain/scripts/morning-report-generator.py`
- **Trigger**: Morning planning session
- **Purpose**: Review previous day's productivity and plan today

The morning report will:
1. Read yesterday's daily analysis JSON
2. Combine with energy tracking data from database
3. Calculate trends and patterns
4. Generate actionable insights
5. Suggest focus areas for today

## Environment Variables

### Optional Configuration

```bash
# Custom session log path (defaults to /tmp/claude-session.log)
export CLAUDE_SESSION_LOG="/custom/path/to/session.log"

# Run hook
node evening-productivity-analysis.ts
```

## Troubleshooting

### Hook Not Running

**Check 1**: Verify hook is enabled
```bash
cat ~/.config/claude-code/settings.json | grep -A 5 "evening-productivity"
```

**Check 2**: Verify script is executable
```bash
chmod +x /root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts
```

**Check 3**: Check time condition
```bash
date +%H  # Should be >= 17
```

### Missing Session Log

If session log is not found at `/tmp/claude-session.log`:
1. Check Claude Code logs for actual log location
2. Set `CLAUDE_SESSION_LOG` environment variable
3. Hook will still generate analysis with limited data

### JSON Not Generated

**Check 1**: Directory permissions
```bash
ls -ld /root/flourisha/00_AI_Brain/history/daily-analysis/
```

**Check 2**: Disk space
```bash
df -h /root
```

**Check 3**: Manual test
```bash
node /root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts
```

### Partial Data

The hook is designed to handle errors gracefully:
- If session log is missing, it generates analysis with default values
- If save fails, it attempts to save partial data with `-partial.json` suffix
- All errors are logged to console

## Advanced Configuration

### Custom Analysis Logic

To customize productivity scoring or pattern detection:

1. Edit `/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts`
2. Modify functions:
   - `calculateProductivityScore()` - Adjust scoring algorithm
   - `detectPatterns()` - Add new pattern detection rules
   - `analyzeFocusQuality()` - Customize focus quality calculation

### Database Integration (Future)

To integrate with `energy_tracking` and `okr_tracking` tables:

1. Install Supabase client:
   ```bash
   npm install @supabase/supabase-js
   ```

2. Add to hook imports:
   ```typescript
   import { createClient } from '@supabase/supabase-js'
   ```

3. Query energy data:
   ```typescript
   const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
   const { data } = await supabase
     .from('energy_tracking')
     .select('*')
     .eq('user_id', userId)
     .gte('timestamp', startOfDay)
     .lte('timestamp', endOfDay)
   ```

## Dependencies

### Runtime Requirements
- Node.js >= 16.x
- TypeScript (if using ts-node)
- File system write access to `/root/flourisha/00_AI_Brain/history/`

### NPM Packages (Built-in)
- `fs` - File system operations
- `path` - Path manipulation

### Optional Dependencies (Future)
- `@supabase/supabase-js` - Database integration
- `axios` - HTTP requests for external APIs

## Security Considerations

### File Permissions
- Hook script: `chmod 700` (owner read/write/execute only)
- Output directory: `chmod 755` (owner full, others read)
- JSON files: Contain productivity data, may be sensitive

### Data Privacy
- Session logs may contain file paths and code snippets
- JSON output includes work patterns and timing
- Ensure proper access controls on output directory

## Version History

- **v1.0** (2025-12-06): Initial implementation
  - Session log parsing
  - Productivity scoring
  - Pattern detection
  - JSON output generation
  - Time-based triggering

## Next Steps

1. ✅ Complete hook implementation
2. ✅ Create registration documentation
3. Register hook in Claude Code settings.json
4. Test with real sessions
5. Build morning report generator integration
6. Add database integration for energy tracking
7. Add database updates for OKR progress
8. Create Chrome extension for energy tracking input
9. Build SMS integration for energy tracking
10. Create UI dashboard for viewing analysis history

## Support

For issues or questions:
- Check logs: Claude Code session output
- Manual test: Run hook directly
- Review code: `/root/flourisha/00_AI_Brain/hooks/evening-productivity-analysis.ts`
- Documentation: `/root/flourisha/00_AI_Brain/documentation/`
