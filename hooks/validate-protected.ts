#!/usr/bin/env bun
/**
 * Flourisha Protected Files Validator
 *
 * Ensures Flourisha-specific files haven't been compromised with sensitive data.
 * Run before committing changes to any repository.
 *
 * Adapted from Daniel Miessler's PAI (2025-11-20) for Flourisha
 *
 * Usage:
 *   bun ~/.claude/hooks/validate-protected.ts
 *   bun ~/.claude/hooks/validate-protected.ts --staged  (check only staged files)
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';
import { execSync } from 'child_process';

interface ProtectedManifest {
  version: string;
  protected: {
    [category: string]: {
      description: string;
      files?: string[];
      patterns?: string[];
      exception_files?: string[];
      validation?: string;
    };
  };
}

const PAI_DIR = process.env.PAI_DIR || join(process.env.HOME!, '.claude');
const FLOURISHA_DIR = join(process.env.HOME!, 'flourisha');
const MANIFEST_PATH = join(PAI_DIR, '.flourisha-protected.json');

// Colors for terminal output
const RED = '\x1b[31m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const BLUE = '\x1b[34m';
const RESET = '\x1b[0m';

function loadManifest(): ProtectedManifest {
  if (!existsSync(MANIFEST_PATH)) {
    console.error(`${RED} Protected files manifest not found: ${MANIFEST_PATH}${RESET}`);
    console.error(`${YELLOW}Creating default manifest...${RESET}`);

    // Return a default manifest
    return {
      version: "1.0",
      protected: {
        protected_patterns: {
          description: "String patterns that should never appear in committed files",
          patterns: [
            "sk-ant-",
            "sk-proj-",
            "ANTHROPIC_API_KEY=sk-",
            "@gmail.com",
            "password=",
            "secret=",
            "api_key="
          ],
          exception_files: [
            ".env.example",
            ".flourisha-protected.json"
          ]
        }
      }
    };
  }

  return JSON.parse(readFileSync(MANIFEST_PATH, 'utf-8'));
}

function getStagedFiles(): string[] {
  try {
    const output = execSync('git diff --cached --name-only 2>/dev/null', {
      cwd: PAI_DIR,
      encoding: 'utf-8'
    });
    return output.trim().split('\n').filter(f => f.length > 0);
  } catch {
    return [];
  }
}

function getAllProtectedFiles(manifest: ProtectedManifest): string[] {
  const files: string[] = [];

  for (const category of Object.values(manifest.protected)) {
    if (category.files) {
      files.push(...category.files);
    }
  }

  return files;
}

function checkFileContent(filePath: string, manifest: ProtectedManifest): {
  valid: boolean;
  violations: string[];
} {
  const fullPath = join(PAI_DIR, filePath);

  if (!existsSync(fullPath)) {
    return { valid: true, violations: [] };
  }

  const content = readFileSync(fullPath, 'utf-8');
  const violations: string[] = [];

  // Get exception files list
  const patternCategory = manifest.protected.protected_patterns;
  const exceptions = patternCategory?.exception_files || [];
  const isException = exceptions.includes(filePath);

  // Check for forbidden patterns (skip if exception)
  if (patternCategory && patternCategory.patterns && !isException) {
    for (const pattern of patternCategory.patterns) {
      const regex = new RegExp(pattern, 'gi');
      const matches = content.match(regex);

      if (matches) {
        violations.push(`Found forbidden pattern: "${pattern}" (${matches.length} occurrence(s))`);
      }
    }
  }

  // Flourisha-specific checks
  // Check for personal data patterns
  const personalPatterns = [
    { pattern: /sk-ant-[a-zA-Z0-9_-]+/, name: 'Anthropic API key' },
    { pattern: /sk-proj-[a-zA-Z0-9_-]+/, name: 'Project API key' },
    { pattern: /ghp_[a-zA-Z0-9]+/, name: 'GitHub personal token' },
    { pattern: /gho_[a-zA-Z0-9]+/, name: 'GitHub OAuth token' },
  ];

  if (!isException) {
    for (const { pattern, name } of personalPatterns) {
      if (pattern.test(content)) {
        violations.push(`Contains ${name}`);
      }
    }
  }

  return { valid: violations.length === 0, violations };
}

async function main() {
  const args = process.argv.slice(2);
  const stagedOnly = args.includes('--staged');

  console.log(`\n${BLUE} Flourisha Protected Files Validator${RESET}\n`);
  console.log('='.repeat(60));

  const manifest = loadManifest();
  const allProtectedFiles = getAllProtectedFiles(manifest);

  // Determine which files to check
  let filesToCheck: string[];

  if (stagedOnly) {
    const stagedFiles = getStagedFiles();
    filesToCheck = stagedFiles.filter(f => allProtectedFiles.includes(f) || f.endsWith('.ts') || f.endsWith('.json'));

    if (filesToCheck.length === 0) {
      console.log(`\n${GREEN} No protected files staged for commit${RESET}\n`);
      process.exit(0);
    }

    console.log(`\n${YELLOW}Checking ${filesToCheck.length} staged file(s)...${RESET}\n`);
  } else {
    // Check all files in key directories
    filesToCheck = [];

    // Check hooks directory
    if (existsSync(join(PAI_DIR, 'hooks'))) {
      const hookFiles = readdirSync(join(PAI_DIR, 'hooks'))
        .filter(f => f.endsWith('.ts'))
        .map(f => `hooks/${f}`);
      filesToCheck.push(...hookFiles);
    }

    // Check settings.json
    if (existsSync(join(PAI_DIR, 'settings.json'))) {
      filesToCheck.push('settings.json');
    }

    // Check .env files
    if (existsSync(join(PAI_DIR, '.env'))) {
      filesToCheck.push('.env');
    }

    console.log(`\n${YELLOW}Checking ${filesToCheck.length} files...${RESET}\n`);
  }

  let hasViolations = false;
  const results: { file: string; valid: boolean; violations: string[] }[] = [];

  // Check each file
  for (const file of filesToCheck) {
    const result = checkFileContent(file, manifest);
    results.push({ file, ...result });

    if (!result.valid) {
      hasViolations = true;
    }
  }

  // Print results
  for (const result of results) {
    if (result.valid) {
      console.log(`${GREEN} ${RESET} ${result.file}`);
    } else {
      console.log(`${RED} ${RESET} ${result.file}`);
      for (const violation of result.violations) {
        console.log(`   ${RED}${RESET} ${violation}`);
      }
    }
  }

  console.log('\n' + '='.repeat(60));

  if (hasViolations) {
    console.log(`\n${RED} VALIDATION FAILED${RESET}\n`);
    console.log('Files contain content that should not be committed.');
    console.log('\n' + YELLOW + 'Common fixes:' + RESET);
    console.log('  1. Remove API keys and secrets');
    console.log('  2. Remove personal email addresses');
    console.log('  3. Use .env.example with placeholders instead of real values');
    console.log('  4. Add sensitive files to .gitignore');
    console.log('\n See .flourisha-protected.json for details\n');
    process.exit(1);
  } else {
    console.log(`\n${GREEN} All files validated successfully!${RESET}\n`);
    console.log('Safe to commit.\n');
    process.exit(0);
  }
}

main();
