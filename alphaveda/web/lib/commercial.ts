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
