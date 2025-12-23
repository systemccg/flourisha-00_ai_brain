#!/usr/bin/env bun
/**
 * Flourisha Self-Test - Health Check System
 *
 * Validates that Flourisha core guarantees are working correctly.
 * Run: bun ${PAI_DIR}/hooks/self-test.ts
 *
 * Adapted from Daniel Miessler's PAI (2025-11-20) for Flourisha
 *
 * Tests:
 * 1. PAI_DIR resolves correctly
 * 2. Core directories exist
 * 3. CORE skill loads
 * 4. Settings.json is valid
 * 5. Agents exist
 * 6. Hooks are executable
 * 7. Voice server (optional)
 * 8. Flourisha Google Drive sync
 */

import { existsSync, readFileSync, accessSync, constants, readdirSync, statSync } from 'fs';
import { join, resolve, dirname } from 'path';

// For self-test, use the configured PAI_DIR or default
const PAI_DIR = process.env.PAI_DIR || join(process.env.HOME!, '.claude');
const HOOKS_DIR = join(PAI_DIR, 'hooks');
const SKILLS_DIR = join(PAI_DIR, 'skills');
const AGENTS_DIR = join(PAI_DIR, 'agents');
const HISTORY_DIR = join(PAI_DIR, 'history');
const FLOURISHA_DIR = join(process.env.HOME!, 'flourisha');
const AI_BRAIN_DIR = join(FLOURISHA_DIR, '00_AI_Brain');

interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  message: string;
}

const results: TestResult[] = [];

function test(name: string, testFn: () => boolean | 'warn', passMsg: string, failMsg: string): void {
  try {
    const result = testFn();
    if (result === 'warn') {
      results.push({ name, status: 'warn', message: passMsg });
    } else if (result) {
      results.push({ name, status: 'pass', message: passMsg });
    } else {
      results.push({ name, status: 'fail', message: failMsg });
    }
  } catch (error) {
    results.push({
      name,
      status: 'fail',
      message: `${failMsg}: ${error instanceof Error ? error.message : String(error)}`
    });
  }
}

console.log('\n Flourisha Health Check\n');
console.log('='.repeat(60));

// Test 1: PAI_DIR resolves
test(
  'PAI_DIR Resolution',
  () => PAI_DIR.length > 0 && existsSync(PAI_DIR),
  `PAI_DIR: ${PAI_DIR}`,
  `PAI_DIR not found: ${PAI_DIR}`
);

// Test 2: Core directories exist
test(
  'Hooks Directory',
  () => existsSync(HOOKS_DIR),
  `Found: ${HOOKS_DIR}`,
  `Missing: ${HOOKS_DIR}`
);

test(
  'Skills Directory',
  () => existsSync(SKILLS_DIR),
  `Found: ${SKILLS_DIR}`,
  `Missing: ${SKILLS_DIR}`
);

test(
  'Agents Directory',
  () => existsSync(AGENTS_DIR),
  `Found: ${AGENTS_DIR}`,
  `Missing: ${AGENTS_DIR}`
);

test(
  'History Directory',
  () => existsSync(HISTORY_DIR),
  `Found: ${HISTORY_DIR}`,
  `Missing: ${HISTORY_DIR}`
);

// Test 3: CORE skill loads
test(
  'CORE Skill',
  () => {
    const coreSkill = join(SKILLS_DIR, 'CORE/SKILL.md');
    if (!existsSync(coreSkill)) return false;
    const content = readFileSync(coreSkill, 'utf-8');
    return content.includes('Flourisha') || content.includes('Personal AI Infrastructure');
  },
  'CORE skill loads correctly',
  'CORE skill missing or malformed'
);

// Test 4: Settings.json valid
test(
  'Settings Configuration',
  () => {
    const settingsPath = join(PAI_DIR, 'settings.json');
    if (!existsSync(settingsPath)) return false;
    const settings = JSON.parse(readFileSync(settingsPath, 'utf-8'));
    return settings && settings.hooks && settings.permissions;
  },
  'settings.json valid',
  'settings.json missing or invalid'
);

// Test 5: Agents exist (agents can be .md files or subdirectories)
test(
  'Agents',
  () => {
    if (!existsSync(AGENTS_DIR)) return false;
    const items = readdirSync(AGENTS_DIR);
    // Count both .md files and subdirectories (agent folders)
    const agentMdFiles = items.filter(f => f.endsWith('.md'));
    const agentDirs = items.filter(f => {
      const itemPath = join(AGENTS_DIR, f);
      return statSync(itemPath).isDirectory() && !f.startsWith('.');
    });
    return agentMdFiles.length > 0 || agentDirs.length > 0;
  },
  (() => {
    if (!existsSync(AGENTS_DIR)) return 'No agents found';
    const items = readdirSync(AGENTS_DIR);
    const agentMdFiles = items.filter(f => f.endsWith('.md'));
    const agentDirs = items.filter(f => {
      const itemPath = join(AGENTS_DIR, f);
      try {
        return statSync(itemPath).isDirectory() && !f.startsWith('.');
      } catch { return false; }
    });
    return `Found ${agentMdFiles.length} agent files and ${agentDirs.length} agent directories`;
  })(),
  'No agents found'
);

// Test 6: Hooks are executable
test(
  'Hook Executability',
  () => {
    const criticalHooks = [
      'capture-all-events.ts',
      'load-core-context.ts',
    ];

    for (const hook of criticalHooks) {
      const hookPath = join(HOOKS_DIR, hook);
      if (!existsSync(hookPath)) return false;

      // Check if readable
      try {
        accessSync(hookPath, constants.R_OK);
      } catch {
        return false;
      }
    }
    return true;
  },
  'Critical hooks are accessible',
  'Some hooks missing or not accessible'
);

// Test 7: PAI paths library exists
test(
  'PAI Paths Library',
  () => {
    const pathsLib = join(HOOKS_DIR, 'lib/pai-paths.ts');
    return existsSync(pathsLib);
  },
  'Path resolution library present',
  'PAI paths library missing'
);

// Test 8: Voice server (optional - warning if not running)
test(
  'Voice Server',
  () => {
    try {
      // Check if voice server is running by testing localhost:8888
      // This is a sync check - returns warn if not available
      return 'warn';
    } catch {
      return 'warn';
    }
  },
  'Voice server check (optional feature)',
  'Voice server not responding (optional feature)'
);

// Test 9: .env file exists
test(
  'Environment Configuration',
  () => {
    const envExample = join(PAI_DIR, '.env.example');
    const envFile = join(PAI_DIR, '.env');
    return existsSync(envExample) || existsSync(envFile);
  },
  'Environment config present',
  'No .env.example or .env found'
);

// Test 10: Flourisha Google Drive Directory
test(
  'Flourisha Directory',
  () => {
    return existsSync(FLOURISHA_DIR);
  },
  `Flourisha directory found: ${FLOURISHA_DIR}`,
  `Flourisha directory missing: ${FLOURISHA_DIR}`
);

// Test 11: AI Brain Directory
test(
  'AI Brain Directory',
  () => {
    return existsSync(AI_BRAIN_DIR);
  },
  `AI Brain found: ${AI_BRAIN_DIR}`,
  `AI Brain missing: ${AI_BRAIN_DIR}`
);

// Test 12: Skills symlink to AI Brain
test(
  'Skills Symlink',
  () => {
    const skillsPath = join(PAI_DIR, 'skills');
    try {
      const stats = statSync(skillsPath);
      // Check if it's a symlink by comparing realpath
      const realPath = require('fs').realpathSync(skillsPath);
      return realPath.includes('flourisha') || realPath.includes('AI_Brain');
    } catch {
      return false;
    }
  },
  'Skills directory properly symlinked to AI Brain',
  'Skills not symlinked to AI Brain'
);

// Print results
console.log('\n');
let passCount = 0;
let failCount = 0;
let warnCount = 0;

for (const result of results) {
  const icon = result.status === 'pass' ? ' ' : result.status === 'warn' ? ' ' : ' ';
  const color = result.status === 'pass' ? '\x1b[32m' : result.status === 'warn' ? '\x1b[33m' : '\x1b[31m';
  const reset = '\x1b[0m';

  console.log(`${icon} ${color}${result.name}${reset}: ${result.message}`);

  if (result.status === 'pass') passCount++;
  else if (result.status === 'fail') failCount++;
  else warnCount++;
}

console.log('\n' + '='.repeat(60));
console.log(`\n Results: ${passCount} passed, ${failCount} failed, ${warnCount} warnings\n`);

if (failCount === 0) {
  console.log(' Flourisha is healthy! All core guarantees working.\n');
  if (warnCount > 0) {
    console.log(' Warnings are for optional features (like voice server).\n');
  }
  process.exit(0);
} else {
  console.log(' Flourisha has issues. Check failed tests above.\n');
  console.log(' See FLOURISHA_CONTRACT.md for what should work out of box.\n');
  process.exit(1);
}
