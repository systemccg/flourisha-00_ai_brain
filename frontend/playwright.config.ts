import { defineConfig, devices } from '@playwright/test';

/**
 * Flourisha Frontend E2E Test Configuration
 *
 * Run tests with:
 *   bun run test:e2e           # Run all E2E tests
 *   bun run test:e2e:ui        # Run with UI mode
 *   bun run test:e2e:headed    # Run with visible browser
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
    // Base URL for the frontend dev server
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3002',

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
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Dev server configuration
  webServer: {
    command: 'bun run dev --port 3002',
    url: 'http://localhost:3002',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
