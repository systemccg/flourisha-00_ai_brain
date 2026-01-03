import { defineConfig, devices } from '@playwright/test';

/**
 * Flourisha Frontend E2E Test Configuration
 *
 * CRITICAL: FALSE POSITIVE PREVENTION
 * ====================================
 * Tests MUST run against the LIVE dev server on port 3000, NOT a Playwright-managed
 * webserver on port 3002. Using a separate webserver causes tests to pass against
 * stale/cached code while the user sees failures on the actual running server.
 *
 * Run tests with:
 *   bun run test:e2e           # Run all E2E tests against live server
 *   bun run test:e2e:ui        # Run with UI mode
 *   bun run test:e2e:headed    # Run with visible browser
 *
 * BEFORE RUNNING TESTS:
 *   1. Ensure dev server is running: bun run dev (port 3000)
 *   2. Verify required files exist: error.tsx, global-error.tsx, not-found.tsx
 *   3. DO NOT rely on the webServer config - it's disabled by default
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],

  // Increase timeout for slow CI/VPS environments
  timeout: 60000,
  expect: {
    timeout: 10000,
  },

  use: {
    // CRITICAL: Default to the LIVE dev server (port 3000), not a managed server
    // The Tailscale IP ensures we test against the actual running server
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://100.66.28.67:3000',

    // Increase action timeout
    actionTimeout: 15000,
    navigationTimeout: 30000,

    // Collect trace on failure
    trace: 'on-first-retry',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Video on failure
    video: 'on-first-retry',
  },

  projects: [
    // Setup project - runs auth.setup.ts to establish authenticated session
    // Run with: npx playwright test --project=setup --headed
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
      use: { ...devices['Desktop Chrome'] },
    },

    // Unauthenticated tests (smoke tests, public pages)
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testIgnore: /auth\.setup\.ts/,
    },

    // Authenticated tests - depend on setup project
    // These tests run with saved auth state from .auth/user.json
    {
      name: 'authenticated',
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
      dependencies: ['setup'],
      testMatch: /.*\.auth\.spec\.ts/,
    },
  ],

  // DISABLED: Do NOT use Playwright's managed webserver
  // This was causing false positives - tests passed against port 3002
  // while users saw failures on the live server (port 3000).
  //
  // Tests now run against the externally-managed dev server.
  // Ensure `bun run dev` is running before executing tests.
  //
  // webServer: {
  //   command: 'bun run dev --port 3002',
  //   url: 'http://localhost:3002',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120000,
  // },
});
