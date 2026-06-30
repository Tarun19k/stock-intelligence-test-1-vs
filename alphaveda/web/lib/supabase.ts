import { createClient, SupabaseClient } from '@supabase/supabase-js'

const url = process.env.SUPABASE_URL
const key = process.env.SUPABASE_SERVICE_KEY

if (!url || !key) {
  throw new Error(
    'Missing SUPABASE_URL or SUPABASE_SERVICE_KEY — set these in Vercel project settings before deploying.'
  )
}

// Module-level singleton — one client per server process.
// Service key bypasses RLS; never expose to client components.
const supabase: SupabaseClient = createClient(url, key)

export function getServerSupabase(): SupabaseClient {
  return supabase
}
