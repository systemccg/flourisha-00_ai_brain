import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../.auth/user.json');

/**
 * Authentication Setup for Playwright
 *
 * This runs ONCE before all tests to establish an authenticated session.
 * The session is saved and reused by all tests that need authentication.
 *
 * SETUP INSTRUCTIONS:
 * 1. Run: npx playwright test --project=setup --headed
 * 2. Complete Google login manually in the browser
 * 3. The session will be saved to .auth/user.json
 * 4. Future tests will reuse this session
 *
 * Alternative: Use email/password test account
 */
setup('authenticate', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Check if we have a test account configured
  const testEmail = process.env.TEST_USER_EMAIL;
  const testPassword = process.env.TEST_USER_PASSWORD;

  if (testEmail && testPassword) {
    // Use email/password login
    console.log('Using email/password authentication...');

    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await expect(page).toHaveURL(/dashboard/, { timeout: 30000 });
  } else {
    // Manual Google OAuth - requires human interaction
    console.log('');
    console.log('='.repeat(60));
    console.log('MANUAL AUTHENTICATION REQUIRED');
    console.log('='.repeat(60));
    console.log('1. Click "Continue with Google" in the browser');
    console.log('2. Complete Google sign-in');
    console.log('3. Wait for redirect to dashboard');
    console.log('4. The session will be saved automatically');
    console.log('='.repeat(60));
    console.log('');

    // Wait for manual login - user has 2 minutes
    await expect(page).toHaveURL(/dashboard/, { timeout: 120000 });
  }

  // Verify we're authenticated
  await expect(page.locator('text=Welcome back')).toBeVisible({ timeout: 10000 });

  // Save authentication state
  await page.context().storageState({ path: authFile });

  console.log('Authentication successful! Session saved to .auth/user.json');
});
