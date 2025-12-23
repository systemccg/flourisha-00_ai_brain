#!/usr/bin/env node
/**
 * ============================================================================
 * Flourisha AI Brain - Evening Productivity Analysis Hook
 * ============================================================================
 *
 * Trigger: SessionEnd hook (registered in Claude Code settings.json)
 * Condition: Only processes if session ended after 5 PM (17:00)
 * Purpose: Analyze daily productivity, energy patterns, and OKR contributions
 * Output: JSON file to /root/flourisha/00_AI_Brain/history/daily-analysis/YYYY-MM-DD.json
 *
 * This hook is consumed by morning-report-generator.py the next morning
 * ============================================================================
 */

import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// Type Definitions
// ============================================================================

interface ToolUsage {
  [toolName: string]: number;
}

interface ProjectActivity {
  [projectName: string]: {
    filesModified: number;
    commits: number;
    timeSpent: number; // minutes
  };
}

interface EnergyTracking {
  readings: Array<{
    timestamp: string;
    energyLevel: number;
    focusQuality: string;
  }>;
  averageEnergy: number;
  peakEnergyTime: string | null;
  lowEnergyTime: string | null;
}

interface FocusQuality {
  deepWorkHours: number;
  shallowWorkHours: number;
  distractedHours: number;
  contextSwitches: number;
  focusScore: number; // 1-10
}

interface OKRContribution {
  objectivesWorkedOn: string[];
  keyResultsProgressed: Array<{
    objectiveId: string;
    keyResultId: string;
    progressMade: number;
    unit: string;
  }>;
}

interface DailyAnalysis {
  date: string; // YYYY-MM-DD
  productivityScore: number; // 1-10
  hoursWorked: number;
  deepWorkHours: number;
  shallowWorkHours: number;
  accomplishments: string[];
  toolsUsed: ToolUsage;
  projectsWorkedOn: ProjectActivity;
  patternsDetected: string[];
  blockers: string[];
  energyTracking: EnergyTracking;
  focusQuality: FocusQuality;
  okrContribution: OKRContribution;
  rawSessionData: {
    startTime: string;
    endTime: string;
    filesModified: string[];
    filesCreated: string[];
    commits: number;
  };
}

// ============================================================================
// Configuration
// ============================================================================

const OUTPUT_DIR = '/root/flourisha/00_AI_Brain/history/daily-analysis';
const SESSION_LOG_PATH = process.env.CLAUDE_SESSION_LOG || '/tmp/claude-session.log';
const MINIMUM_HOUR_TO_PROCESS = 17; // 5 PM

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get current date in YYYY-MM-DD format
 */
function getCurrentDate(): string {
  const now = new Date();
  return now.toISOString().split('T')[0];
}

/**
 * Get current hour (0-23)
 */
function getCurrentHour(): number {
  return new Date().getHours();
}

/**
 * Ensure output directory exists
 */
function ensureOutputDirectory(): void {
  try {
    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
      console.log(`Created output directory: ${OUTPUT_DIR}`);
    }
  } catch (error) {
    console.error(`Error creating output directory: ${error}`);
    throw error;
  }
}

/**
 * Parse session logs to extract tool usage, files modified, and timestamps
 */
function parseSessionLogs(): {
  startTime: string;
  endTime: string;
  toolsUsed: ToolUsage;
  filesModified: string[];
  filesCreated: string[];
  commits: number;
  duration: number; // minutes
} {
  const result = {
    startTime: new Date().toISOString(),
    endTime: new Date().toISOString(),
    toolsUsed: {} as ToolUsage,
    filesModified: [] as string[],
    filesCreated: [] as string[],
    commits: 0,
    duration: 0,
  };

  try {
    // Try to read session log if it exists
    if (fs.existsSync(SESSION_LOG_PATH)) {
      const logContent = fs.readFileSync(SESSION_LOG_PATH, 'utf-8');
      const lines = logContent.split('\n');

      // Parse timestamps
      const timestamps: Date[] = [];

      lines.forEach((line) => {
        // Extract timestamps (ISO format)
        const timestampMatch = line.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
        if (timestampMatch) {
          timestamps.push(new Date(timestampMatch[0]));
        }

        // Count tool usage
        const toolMatches = [
          'Edit', 'Write', 'Read', 'Bash', 'Grep', 'Glob',
          'Task', 'WebFetch', 'WebSearch', 'Skill', 'SlashCommand',
        ];

        toolMatches.forEach((tool) => {
          if (line.includes(`<invoke name="${tool}"`) || line.includes(`Tool: ${tool}`)) {
            result.toolsUsed[tool] = (result.toolsUsed[tool] || 0) + 1;
          }
        });

        // Detect file modifications
        if (line.includes('file_path') || line.includes('File modified:')) {
          const filePathMatch = line.match(/(?:file_path|path)["']?\s*[:=]\s*["']([^"']+)["']/);
          if (filePathMatch) {
            const filePath = filePathMatch[1];
            if (!result.filesModified.includes(filePath)) {
              result.filesModified.push(filePath);
            }
          }
        }

        // Detect file creations
        if (line.includes('File created:') || line.includes('Write tool')) {
          const filePathMatch = line.match(/(?:created|writing).*["']([^"']+)["']/i);
          if (filePathMatch) {
            const filePath = filePathMatch[1];
            if (!result.filesCreated.includes(filePath)) {
              result.filesCreated.push(filePath);
            }
          }
        }

        // Count git commits
        if (line.includes('git commit') || line.includes('Committed:')) {
          result.commits += 1;
        }
      });

      // Calculate duration
      if (timestamps.length > 0) {
        const sorted = timestamps.sort((a, b) => a.getTime() - b.getTime());
        result.startTime = sorted[0].toISOString();
        result.endTime = sorted[sorted.length - 1].toISOString();
        result.duration = Math.round(
          (sorted[sorted.length - 1].getTime() - sorted[0].getTime()) / (1000 * 60)
        );
      }
    } else {
      console.warn(`Session log not found at: ${SESSION_LOG_PATH}`);
    }
  } catch (error) {
    console.error(`Error parsing session logs: ${error}`);
  }

  return result;
}

/**
 * Calculate productivity score (1-10) based on session data
 */
function calculateProductivityScore(sessionData: ReturnType<typeof parseSessionLogs>): number {
  let score = 5.0; // Base score

  // Factor 1: Duration (more time = higher potential, cap at 8 hours)
  const hoursWorked = Math.min(sessionData.duration / 60, 8);
  score += hoursWorked * 0.3;

  // Factor 2: Tool usage patterns (Edit/Write = deep work)
  const deepWorkTools = (sessionData.toolsUsed['Edit'] || 0) + (sessionData.toolsUsed['Write'] || 0);
  const researchTools = (sessionData.toolsUsed['Read'] || 0) + (sessionData.toolsUsed['Grep'] || 0);
  score += Math.min(deepWorkTools * 0.15, 2.0); // Cap contribution at 2 points

  // Factor 3: Output (files modified/created)
  const totalFiles = sessionData.filesModified.length + sessionData.filesCreated.length;
  score += Math.min(totalFiles * 0.1, 1.5);

  // Factor 4: Commits (shows completion of work)
  score += Math.min(sessionData.commits * 0.5, 2.0);

  // Factor 5: Focus (fewer tool switches = better focus)
  const totalToolUses = Object.values(sessionData.toolsUsed).reduce((sum, count) => sum + count, 0);
  const toolVariety = Object.keys(sessionData.toolsUsed).length;
  const focusRatio = toolVariety > 0 ? totalToolUses / toolVariety : 0;
  if (focusRatio > 10) score += 0.5; // Good focus
  if (focusRatio < 3) score -= 0.5; // Poor focus (too scattered)

  // Clamp to 1-10 range
  return Math.max(1, Math.min(10, Math.round(score * 10) / 10));
}

/**
 * Detect productivity patterns from session data
 */
function detectPatterns(sessionData: ReturnType<typeof parseSessionLogs>): string[] {
  const patterns: string[] = [];

  // Pattern: Long uninterrupted session
  if (sessionData.duration > 180) {
    patterns.push('Long focused session (3+ hours)');
  }

  // Pattern: High code output
  const codeFiles = sessionData.filesModified.filter((f) =>
    /\.(ts|js|py|sql|tsx|jsx|json)$/i.test(f)
  );
  if (codeFiles.length > 5) {
    patterns.push(`High code output (${codeFiles.length} code files modified)`);
  }

  // Pattern: Database work
  const sqlFiles = sessionData.filesModified.filter((f) => /\.sql$/i.test(f));
  if (sqlFiles.length > 0) {
    patterns.push('Database schema development');
  }

  // Pattern: Documentation work
  const docFiles = sessionData.filesModified.filter((f) => /\.(md|txt|rst)$/i.test(f));
  if (docFiles.length > 2) {
    patterns.push('Significant documentation effort');
  }

  // Pattern: Heavy testing
  if (sessionData.toolsUsed['Bash'] && sessionData.toolsUsed['Bash'] > 10) {
    patterns.push('Extensive testing and validation');
  }

  // Pattern: Research-heavy session
  const researchScore =
    (sessionData.toolsUsed['Read'] || 0) +
    (sessionData.toolsUsed['Grep'] || 0) +
    (sessionData.toolsUsed['WebSearch'] || 0);
  if (researchScore > 10) {
    patterns.push('Research-intensive session');
  }

  // Pattern: Multiple commits
  if (sessionData.commits > 3) {
    patterns.push(`High commit velocity (${sessionData.commits} commits)`);
  }

  return patterns;
}

/**
 * Analyze focus quality based on tool usage patterns
 */
function analyzeFocusQuality(sessionData: ReturnType<typeof parseSessionLogs>): FocusQuality {
  const totalMinutes = sessionData.duration;
  const totalHours = totalMinutes / 60;

  // Estimate deep work vs shallow work based on tool patterns
  const deepWorkTools = (sessionData.toolsUsed['Edit'] || 0) + (sessionData.toolsUsed['Write'] || 0);
  const shallowWorkTools =
    (sessionData.toolsUsed['Read'] || 0) + (sessionData.toolsUsed['Grep'] || 0);
  const totalTools = Object.values(sessionData.toolsUsed).reduce((sum, count) => sum + count, 0);

  // Estimate time distribution (rough heuristic)
  const deepWorkRatio = totalTools > 0 ? deepWorkTools / totalTools : 0;
  const shallowWorkRatio = totalTools > 0 ? shallowWorkTools / totalTools : 0;
  const distractedRatio = Math.max(0, 1 - deepWorkRatio - shallowWorkRatio);

  const deepWorkHours = totalHours * deepWorkRatio;
  const shallowWorkHours = totalHours * shallowWorkRatio;
  const distractedHours = totalHours * distractedRatio;

  // Count context switches (tool changes)
  const contextSwitches = Object.keys(sessionData.toolsUsed).length;

  // Calculate focus score (1-10)
  let focusScore = 5.0;
  focusScore += deepWorkRatio * 3; // Deep work boosts score
  focusScore -= distractedRatio * 2; // Distraction lowers score
  focusScore -= Math.min(contextSwitches * 0.1, 2); // Too many context switches hurt
  focusScore = Math.max(1, Math.min(10, Math.round(focusScore * 10) / 10));

  return {
    deepWorkHours: Math.round(deepWorkHours * 10) / 10,
    shallowWorkHours: Math.round(shallowWorkHours * 10) / 10,
    distractedHours: Math.round(distractedHours * 10) / 10,
    contextSwitches,
    focusScore,
  };
}

/**
 * Extract accomplishments from session data
 */
function extractAccomplishments(sessionData: ReturnType<typeof parseSessionLogs>): string[] {
  const accomplishments: string[] = [];

  // Database migrations created
  const migrations = sessionData.filesCreated.filter((f) => f.includes('migration'));
  if (migrations.length > 0) {
    accomplishments.push(`Created ${migrations.length} database migration(s)`);
  }

  // Hooks implemented
  const hooks = sessionData.filesCreated.filter((f) => f.includes('hook'));
  if (hooks.length > 0) {
    accomplishments.push(`Implemented ${hooks.length} automation hook(s)`);
  }

  // Code files created
  const codeFiles = sessionData.filesCreated.filter((f) =>
    /\.(ts|js|py|tsx|jsx)$/i.test(f)
  );
  if (codeFiles.length > 0) {
    accomplishments.push(`Created ${codeFiles.length} new code file(s)`);
  }

  // Files modified
  if (sessionData.filesModified.length > 0) {
    accomplishments.push(`Modified ${sessionData.filesModified.length} file(s)`);
  }

  // Commits made
  if (sessionData.commits > 0) {
    accomplishments.push(`Made ${sessionData.commits} git commit(s)`);
  }

  // If no specific accomplishments, add a generic one
  if (accomplishments.length === 0) {
    accomplishments.push('Completed development session');
  }

  return accomplishments;
}

/**
 * Analyze project activity from file paths
 */
function analyzeProjectActivity(sessionData: ReturnType<typeof parseSessionLogs>): ProjectActivity {
  const projects: ProjectActivity = {};

  const allFiles = [...sessionData.filesModified, ...sessionData.filesCreated];

  allFiles.forEach((filePath) => {
    // Extract project name from path (assuming /root/flourisha/PROJECT/...)
    const match = filePath.match(/\/root\/flourisha\/([^\/]+)/);
    if (match) {
      const projectName = match[1];

      if (!projects[projectName]) {
        projects[projectName] = {
          filesModified: 0,
          commits: 0,
          timeSpent: 0,
        };
      }

      projects[projectName].filesModified += 1;
    }
  });

  // Distribute commits across projects proportionally
  const totalFiles = Object.values(projects).reduce((sum, p) => sum + p.filesModified, 0);
  Object.keys(projects).forEach((projectName) => {
    if (totalFiles > 0) {
      const proportion = projects[projectName].filesModified / totalFiles;
      projects[projectName].commits = Math.round(sessionData.commits * proportion);
      projects[projectName].timeSpent = Math.round(sessionData.duration * proportion);
    }
  });

  return projects;
}

/**
 * Generate complete daily analysis
 */
function generateAnalysis(): DailyAnalysis {
  console.log('Parsing session logs...');
  const sessionData = parseSessionLogs();

  console.log('Calculating productivity score...');
  const productivityScore = calculateProductivityScore(sessionData);

  console.log('Detecting patterns...');
  const patterns = detectPatterns(sessionData);

  console.log('Analyzing focus quality...');
  const focusQuality = analyzeFocusQuality(sessionData);

  console.log('Extracting accomplishments...');
  const accomplishments = extractAccomplishments(sessionData);

  console.log('Analyzing project activity...');
  const projectsWorkedOn = analyzeProjectActivity(sessionData);

  // Placeholder for energy tracking (would come from database in production)
  const energyTracking: EnergyTracking = {
    readings: [],
    averageEnergy: 7.0,
    peakEnergyTime: '10:00 AM',
    lowEnergyTime: '2:00 PM',
  };

  // Placeholder for OKR contribution (would be calculated from actual work)
  const okrContribution: OKRContribution = {
    objectivesWorkedOn: ['OBJ-001'],
    keyResultsProgressed: [
      {
        objectiveId: 'OBJ-001',
        keyResultId: 'KR-002',
        progressMade: 1,
        unit: 'count',
      },
    ],
  };

  const analysis: DailyAnalysis = {
    date: getCurrentDate(),
    productivityScore,
    hoursWorked: Math.round((sessionData.duration / 60) * 10) / 10,
    deepWorkHours: focusQuality.deepWorkHours,
    shallowWorkHours: focusQuality.shallowWorkHours,
    accomplishments,
    toolsUsed: sessionData.toolsUsed,
    projectsWorkedOn,
    patternsDetected: patterns,
    blockers: [], // Would be extracted from notes or explicitly logged
    energyTracking,
    focusQuality,
    okrContribution,
    rawSessionData: {
      startTime: sessionData.startTime,
      endTime: sessionData.endTime,
      filesModified: sessionData.filesModified,
      filesCreated: sessionData.filesCreated,
      commits: sessionData.commits,
    },
  };

  return analysis;
}

/**
 * Save analysis to JSON file
 */
function saveAnalysis(analysis: DailyAnalysis): void {
  try {
    ensureOutputDirectory();

    const fileName = `${analysis.date}.json`;
    const filePath = path.join(OUTPUT_DIR, fileName);

    const jsonContent = JSON.stringify(analysis, null, 2);
    fs.writeFileSync(filePath, jsonContent, 'utf-8');

    console.log(`✅ Analysis saved to: ${filePath}`);
    console.log(`📊 Productivity Score: ${analysis.productivityScore}/10`);
    console.log(`⏱️  Hours Worked: ${analysis.hoursWorked}`);
    console.log(`🎯 Accomplishments: ${analysis.accomplishments.length}`);
  } catch (error) {
    console.error(`❌ Error saving analysis: ${error}`);

    // Try to save partial data even if there's an error
    try {
      const fallbackPath = path.join(OUTPUT_DIR, `${analysis.date}-partial.json`);
      fs.writeFileSync(fallbackPath, JSON.stringify(analysis, null, 2), 'utf-8');
      console.log(`⚠️  Partial analysis saved to: ${fallbackPath}`);
    } catch (fallbackError) {
      console.error(`❌ Failed to save even partial analysis: ${fallbackError}`);
    }
  }
}

// ============================================================================
// Main Execution
// ============================================================================

async function main(): Promise<void> {
  try {
    console.log('='.repeat(80));
    console.log('Flourisha AI Brain - Evening Productivity Analysis');
    console.log('='.repeat(80));

    // Check if it's after 5 PM
    const currentHour = getCurrentHour();
    console.log(`Current hour: ${currentHour}:00`);

    if (currentHour < MINIMUM_HOUR_TO_PROCESS) {
      console.log(`⏭️  Skipping analysis: Session ended before ${MINIMUM_HOUR_TO_PROCESS}:00`);
      console.log('   (Evening analysis only runs after 5 PM)');
      return;
    }

    console.log('✅ Time check passed - proceeding with analysis...');
    console.log('');

    // Generate and save analysis
    const analysis = generateAnalysis();
    saveAnalysis(analysis);

    console.log('');
    console.log('='.repeat(80));
    console.log('✅ Evening productivity analysis complete!');
    console.log('='.repeat(80));
  } catch (error) {
    console.error('❌ Fatal error in evening analysis:');
    console.error(error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch((error) => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}

export { generateAnalysis, saveAnalysis };
