import crypto from 'crypto'
import { cookies } from 'next/headers'

// Fail-closed shared-secret gate for /portfolio, same pattern as
// BUILD_CHECKLIST_TOKEN (api/build-checklist/route.ts): if the env var
// protecting this route is unset, deny access rather than silently allow it.
// PORTFOLIO_ACCESS_TOKEN must be set in Vercel project env vars — never
// committed to the repo.
export const PORTFOLIO_COOKIE_NAME = 'av_portfolio_session'

function timingSafeStringEqual(a: string, b: string): boolean {
  const bufA = Buffer.from(a)
  const bufB = Buffer.from(b)
  if (bufA.length !== bufB.length) return false
  return crypto.timingSafeEqual(bufA, bufB)
}

function hashToken(token: string): string {
  return crypto.createHash('sha256').update(token).digest('hex')
}

// The cookie never stores the raw token, only a hash of it -- so a leaked
// cookie value isn't directly usable as the login token itself.
export function sessionValueForToken(token: string): string {
  return hashToken(token)
}

export function tokenMatchesConfigured(token: string): boolean {
  const expected = process.env.PORTFOLIO_ACCESS_TOKEN
  if (!expected) return false
  return timingSafeStringEqual(token, expected)
}

export async function isPortfolioSessionValid(): Promise<boolean> {
  const expectedToken = process.env.PORTFOLIO_ACCESS_TOKEN
  if (!expectedToken) return false
  const cookieStore = await cookies()
  const session = cookieStore.get(PORTFOLIO_COOKIE_NAME)?.value
  if (!session) return false
  return timingSafeStringEqual(session, hashToken(expectedToken))
}
