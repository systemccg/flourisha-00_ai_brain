import { test, expect } from '@playwright/test'

test('inspect Get Started button HTML', async ({ page }) => {
  await page.goto('http://100.66.28.67:3000')
  await page.waitForSelector('text=Get Started')

  // Get the HTML of the button and its parent
  const buttonHtml = await page.evaluate(() => {
    const button = document.evaluate(
      "//button[contains(text(), 'Get Started')]",
      document,
      null,
      XPathResult.FIRST_ORDERED_NODE_TYPE,
      null
    ).singleNodeValue as HTMLElement

    if (button) {
      const parent = button.parentElement
      return {
        buttonTag: button.tagName,
        parentTag: parent?.tagName,
        parentHref: (parent as HTMLAnchorElement)?.href,
        parentHtml: parent?.outerHTML?.substring(0, 500)
      }
    }
    return null
  })

  console.log('Button info:', JSON.stringify(buttonHtml, null, 2))

  // Should be wrapped in an anchor tag
  expect(buttonHtml?.parentTag).toBe('A')
})
