#!/usr/bin/env node

/**
 * browser-test-template.js
 *
 * Playwright browser testing template for automated QA testing
 *
 * Usage:
 *   node browser-test-template.js <url>
 *
 * Example:
 *   node browser-test-template.js https://example.com
 */

const { chromium } = require('playwright');

// ANSI color codes for output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m'
};

// Logging helpers
const log = {
    info: (msg) => console.log(`${colors.blue}[INFO]${colors.reset} ${msg}`),
    success: (msg) => console.log(`${colors.green}[SUCCESS]${colors.reset} ${msg}`),
    error: (msg) => console.error(`${colors.red}[ERROR]${colors.reset} ${msg}`),
    warn: (msg) => console.warn(`${colors.yellow}[WARN]${colors.reset} ${msg}`)
};

/**
 * Main test function
 * @param {string} url - The URL to test
 */
async function runBrowserTest(url) {
    let browser = null;
    let context = null;
    let page = null;

    try {
        log.info(`Starting browser test for: ${url}`);

        // Launch browser
        log.info('Launching Chromium browser...');
        browser = await chromium.launch({
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });
        log.success('Browser launched successfully');

        // Create browser context
        context = await browser.newContext({
            viewport: { width: 1920, height: 1080 },
            userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        });

        // Create new page
        page = await context.newPage();

        // Enable console logging from the page
        page.on('console', msg => log.info(`[PAGE] ${msg.text()}`));
        page.on('pageerror', err => log.error(`[PAGE ERROR] ${err.message}`));

        // Navigate to URL
        log.info(`Navigating to: ${url}`);
        const response = await page.goto(url, {
            waitUntil: 'networkidle',
            timeout: 30000
        });

        if (!response) {
            throw new Error('Failed to load page - no response received');
        }

        const status = response.status();
        log.info(`Page loaded with status: ${status}`);

        if (status >= 400) {
            log.warn(`HTTP error status: ${status}`);
        }

        // Wait for page to be ready
        await page.waitForLoadState('domcontentloaded');
        log.success('Page DOM loaded');

        // Example: Click a button (placeholder - customize based on actual test requirements)
        log.info('Looking for interactive elements...');

        // Wait for any button to be available (with timeout)
        try {
            const buttonSelector = 'button, input[type="submit"], input[type="button"], a.button';
            await page.waitForSelector(buttonSelector, { timeout: 5000 });

            // Get first button text
            const buttonText = await page.locator(buttonSelector).first().textContent();
            log.info(`Found button: "${buttonText}"`);

            // Uncomment to actually click the button:
            // await page.locator(buttonSelector).first().click();
            // log.success('Button clicked successfully');

        } catch (e) {
            log.warn('No buttons found on page (this may be expected)');
        }

        // Take screenshot
        const screenshotPath = '/root/flourisha/00_AI_Brain/scripts/screenshot.png';
        log.info(`Taking screenshot: ${screenshotPath}`);
        await page.screenshot({
            path: screenshotPath,
            fullPage: true
        });
        log.success(`Screenshot saved to: ${screenshotPath}`);

        // Get page title
        const title = await page.title();
        log.info(`Page title: "${title}"`);

        // Get page URL (in case of redirects)
        const finalUrl = page.url();
        if (finalUrl !== url) {
            log.info(`Final URL after redirects: ${finalUrl}`);
        }

        log.success('Browser test completed successfully');

        return {
            success: true,
            url: finalUrl,
            title: title,
            status: status,
            screenshot: screenshotPath
        };

    } catch (error) {
        log.error(`Test failed: ${error.message}`);

        // Take error screenshot if page is available
        if (page) {
            try {
                const errorScreenshot = '/root/flourisha/00_AI_Brain/scripts/error-screenshot.png';
                await page.screenshot({ path: errorScreenshot });
                log.info(`Error screenshot saved: ${errorScreenshot}`);
            } catch (screenshotError) {
                log.warn('Failed to capture error screenshot');
            }
        }

        throw error;

    } finally {
        // Cleanup
        log.info('Cleaning up browser resources...');

        if (page) {
            await page.close().catch(e => log.warn(`Failed to close page: ${e.message}`));
        }

        if (context) {
            await context.close().catch(e => log.warn(`Failed to close context: ${e.message}`));
        }

        if (browser) {
            await browser.close().catch(e => log.warn(`Failed to close browser: ${e.message}`));
        }

        log.info('Cleanup complete');
    }
}

// Main execution
(async () => {
    // Validate command-line arguments
    const url = process.argv[2];

    if (!url) {
        log.error('URL argument is required');
        console.log('\nUsage:');
        console.log('  node browser-test-template.js <url>');
        console.log('\nExample:');
        console.log('  node browser-test-template.js https://example.com');
        process.exit(1);
    }

    // Validate URL format
    try {
        new URL(url);
    } catch (error) {
        log.error(`Invalid URL format: ${url}`);
        process.exit(1);
    }

    // Run the test
    try {
        const result = await runBrowserTest(url);
        console.log('\n' + '='.repeat(60));
        console.log('TEST RESULTS:');
        console.log('='.repeat(60));
        console.log(JSON.stringify(result, null, 2));
        console.log('='.repeat(60));
        process.exit(0);
    } catch (error) {
        console.log('\n' + '='.repeat(60));
        console.log('TEST FAILED:');
        console.log('='.repeat(60));
        console.log(error.message);
        console.log('='.repeat(60));
        process.exit(1);
    }
})();
