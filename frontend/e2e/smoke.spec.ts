import { test, expect } from '@playwright/test';

/**
 * Smoke Tests - Basic app functionality
 *
 * These tests verify the app loads and basic navigation works.
 * Run after each feature implementation to catch regressions.
 */

test.describe('Smoke Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Flourisha/i);
  });

  test('login page is accessible', async ({ page }) => {
    await page.goto('/login');
    // Should show login form or redirect
    await expect(page.locator('body')).toBeVisible();
  });

  test('dashboard redirects unauthenticated users', async ({ page }) => {
    await page.goto('/dashboard');
    // Should redirect to login or show auth prompt
    await expect(page).toHaveURL(/login|auth/);
  });
});

test.describe('Navigation', () => {
  test('main navigation elements are present', async ({ page }) => {
    await page.goto('/');

    // Check for main navigation structure
    const nav = page.locator('nav, [role="navigation"]');
    await expect(nav.first()).toBeVisible();
  });
});

test.describe('API Health', () => {
  test('API health endpoint responds', async ({ request }) => {
    const response = await request.get('http://100.66.28.67:8001/api/health');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data).toHaveProperty('status');
  });

  test('API health dashboard returns service statuses', async ({ request }) => {
    const response = await request.get('http://100.66.28.67:8001/api/health/dashboard');
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    expect(data.success).toBe(true);
    expect(data.data).toHaveProperty('services');
  });
});
