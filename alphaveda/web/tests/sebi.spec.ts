import { test, expect } from '@playwright/test'
import { SEBI_DISCLAIMER } from '../lib/sebi-disclaimer.generated'

const ROUTES = ['/', '/signals', '/path', '/accuracy']

const PROHIBITED = ['BUY', 'SELL', 'invest in', 'you should buy', 'recommended for you', 'put money into']

for (const route of ROUTES) {
  test(`SEBI disclaimer present on ${route}`, async ({ page }) => {
    await page.goto(route)
    const footer = page.locator('.sebi-footer')
    await expect(footer).toBeVisible()
    const text = await footer.textContent()
    // Assert the FULL canonical text, imported from the single source of truth
    // (constants.py via sebi-disclaimer.generated.ts) — not just 2 substrings.
    // This is the oracle fix from RF-D: a wording drift anywhere else (e.g.
    // lexicon.ts's SEBI_LEGAL) can no longer pass silently, because this test
    // can never be checking stale/duplicated wording — it reads the same
    // generated constant the footer itself renders.
    expect(text).toContain(SEBI_DISCLAIMER)
  })

  test(`No prohibited advice language on ${route}`, async ({ page }) => {
    await page.goto(route)
    const body = await page.textContent('body') ?? ''
    for (const phrase of PROHIBITED) {
      expect(body.toLowerCase()).not.toContain(phrase.toLowerCase())
    }
  })

  test(`SEBI footer not dismissable on ${route}`, async ({ page }) => {
    await page.goto(route)
    const footer = page.locator('.sebi-footer')
    // No close/dismiss button inside footer
    const closeBtn = footer.locator('button, [aria-label*="close"], [aria-label*="dismiss"]')
    await expect(closeBtn).toHaveCount(0)
    // Footer remains visible after scrolling
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
    await expect(footer).toBeVisible()
  })
}

test('Nav contains all 4 links', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.av-nav__link', { hasText: 'Market Data' })).toBeVisible()
  await expect(page.locator('.av-nav__link', { hasText: 'Signals' })).toBeVisible()
  await expect(page.locator('.av-nav__link', { hasText: 'Path' })).toBeVisible()
  await expect(page.locator('.av-nav__link', { hasText: 'Accuracy' })).toBeVisible()
})
