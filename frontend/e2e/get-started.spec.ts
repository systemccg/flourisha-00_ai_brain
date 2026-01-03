import { test, expect } from '@playwright/test'

test.describe('Get Started Button', () => {
  test('clicking Get Started navigates to login', async ({ page }) => {
    // Use the live dev server directly
    await page.goto('http://100.66.28.67:3000')

    // Wait for the button to be visible
    await page.waitForSelector('text=Get Started')

    // Click the Get Started button (which should be a link)
    const button = page.locator('a:has-text("Get Started")')
    await button.click()

    // Wait for navigation
    await page.waitForURL(/login/, { timeout: 10000 })

    // Verify we're on the login page
    await expect(page).toHaveURL(/login/)
  })
})
