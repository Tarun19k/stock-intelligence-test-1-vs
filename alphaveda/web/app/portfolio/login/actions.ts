'use server'

import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { PORTFOLIO_COOKIE_NAME, sessionValueForToken, tokenMatchesConfigured } from '@/lib/portfolio-auth'

export async function loginToPortfolio(formData: FormData) {
  const token = String(formData.get('token') ?? '')

  if (!token || !tokenMatchesConfigured(token)) {
    redirect('/portfolio/login?error=1')
  }

  const cookieStore = await cookies()
  cookieStore.set(PORTFOLIO_COOKIE_NAME, sessionValueForToken(token), {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    maxAge: 60 * 60 * 24 * 30, // 30 days
  })

  redirect('/portfolio')
}

export async function logoutOfPortfolio() {
  const cookieStore = await cookies()
  cookieStore.delete(PORTFOLIO_COOKIE_NAME)
  redirect('/portfolio/login')
}
