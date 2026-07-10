import { getServerSupabase } from './supabase'

// Mirrors alphaveda/src/config.py is_commercial().
// Fail-closed: any exception → assume commercial=True (blocks yfinance display path).
export async function isCommercial(): Promise<boolean> {
  try {
    const sb = getServerSupabase()
    const { data } = await sb
      .from('waitlist')
      .select('id')
      .not('converted_at', 'is', null)
      .limit(1)
    return (data?.length ?? 0) > 0
  } catch {
    return true
  }
}

// NG-2 / A5: there is no auth/login layer in this app yet — every visitor is
// currently indistinguishable from an anonymous public visitor. Before this
// flag, the Path page showed Tarun's personal PORTFOLIO_VALUE-derived rupee
// figures to anyone, gated only on `!isCommercial()` (i.e. "no paying
// subscriber yet"), which is not the same thing as "this is Tarun looking at
// his own tool." This is a server-only, non-public env var — it is never sent
// to the client and cannot be toggled by a site visitor. Fail-closed by
// default (unset/anything-but-'true' => rupee amounts stay suppressed), same
// posture as isCommercial().
export function isPersonalContext(): boolean {
  return process.env.ALPHAVEDA_PERSONAL_CONTEXT === 'true'
}
