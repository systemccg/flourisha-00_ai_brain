import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'

/**
 * Pre-Flight Verification Tests
 *
 * CRITICAL: These tests MUST pass before running any other E2E tests.
 * They verify that required files exist and the server is responsive.
 *
 * This prevents false positives where tests pass against stale/incomplete code.
 */

const FRONTEND_DIR = '/root/flourisha/00_AI_Brain/frontend'

// Required files for Next.js App Router to work correctly
const REQUIRED_FILES = [
  'src/app/error.tsx',
  'src/app/global-error.tsx',
  'src/app/not-found.tsx',
  'src/app/layout.tsx',
  'src/app/page.tsx',
  '.env.local',
]

test.describe('Pre-Flight Verification', () => {
  test.describe('Required Files', () => {
    for (const file of REQUIRED_FILES) {
      test(`${file} exists`, () => {
        const filePath = path.join(FRONTEND_DIR, file)
        expect(fs.existsSync(filePath), `Missing required file: ${file}`).toBe(true)
      })
    }
  })

  test('.env.local has real Firebase credentials (not placeholders)', () => {
    const envPath = path.join(FRONTEND_DIR, '.env.local')
    const content = fs.readFileSync(envPath, 'utf-8')

    // Check for placeholder values that indicate incomplete setup
    expect(content).not.toContain('your-api-key')
    expect(content).not.toContain('your-auth-domain')
    expect(content).not.toContain('your-project-id')
    expect(content).not.toContain('YOUR_')
    expect(content).not.toContain('PLACEHOLDER')

    // Verify real Firebase config exists
    expect(content).toContain('NEXT_PUBLIC_FIREBASE_API_KEY=')
    expect(content).toContain('NEXT_PUBLIC_FIREBASE_PROJECT_ID=')
  })

  test('error.tsx has proper error boundary structure', () => {
    const filePath = path.join(FRONTEND_DIR, 'src/app/error.tsx')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Must be a client component
    expect(content).toContain("'use client'")

    // Must have error and reset props
    expect(content).toContain('error')
    expect(content).toContain('reset')

    // Must export default
    expect(content).toContain('export default')
  })

  test('global-error.tsx has proper structure', () => {
    const filePath = path.join(FRONTEND_DIR, 'src/app/global-error.tsx')
    const content = fs.readFileSync(filePath, 'utf-8')

    // Must be a client component
    expect(content).toContain("'use client'")

    // Must have html and body tags (required for global-error)
    expect(content).toContain('<html>')
    expect(content).toContain('<body')

    // Must export default
    expect(content).toContain('export default')
  })

  test.describe('Server Connectivity', () => {
    test('dev server responds on configured baseURL', async ({ page }) => {
      // This uses the baseURL from playwright.config.ts
      const response = await page.goto('/')
      expect(response?.status()).toBeLessThan(500)
    })

    test('login page loads without errors', async ({ page }) => {
      const response = await page.goto('/login')
      expect(response?.status()).toBe(200)

      // Check for the "missing required error components" message
      const content = await page.content()
      expect(content).not.toContain('missing required error components')
    })

    test('no console errors on homepage', async ({ page }) => {
      const consoleErrors: string[] = []
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text())
        }
      })

      await page.goto('/')
      await page.waitForTimeout(2000) // Wait for any async errors

      // Filter out known benign errors (like favicon)
      const realErrors = consoleErrors.filter(e => !e.includes('favicon'))
      expect(realErrors, `Console errors found: ${realErrors.join(', ')}`).toHaveLength(0)
    })
  })
})
