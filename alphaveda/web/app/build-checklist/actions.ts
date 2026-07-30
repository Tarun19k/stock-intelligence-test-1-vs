'use server'

import { getServerSupabase } from '@/lib/supabase'

const VALID_STATUSES = ['completed', 'in_progress', 'pending', 'blocked']

// Server Action, not a client fetch to /api/build-checklist — this runs
// server-side only and is never shipped to the browser bundle, so the UI's
// own toggle doesn't need (and must never carry) BUILD_CHECKLIST_TOKEN.
// The public API route stays separately available and token-protected for
// external callers (e.g. curl-based testing).
export async function toggleTaskStatus(id: number, status: string) {
  if (!VALID_STATUSES.includes(status)) {
    throw new Error('invalid status: ' + status)
  }
  const supabase = getServerSupabase()
  const { data, error } = await supabase
    .from('build_tasks')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id)
    .select()

  if (error) throw new Error(error.message)
  if (!data || data.length === 0) throw new Error(`No build_tasks row with id ${id}`)
  return data[0]
}
