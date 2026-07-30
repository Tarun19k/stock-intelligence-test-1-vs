import { NextRequest, NextResponse } from 'next/server'
import { getServerSupabase } from '@/lib/supabase'

const VALID_STATUSES = ['completed', 'in_progress', 'pending', 'blocked']

export async function PATCH(req: NextRequest) {
  const expectedToken = process.env.BUILD_CHECKLIST_TOKEN
  if (!expectedToken) {
    // Fail-closed, same pattern as COMMERCIAL_GATE.md: if the protection can't
    // be verified (env var unset), deny rather than silently allow.
    return NextResponse.json({ error: 'BUILD_CHECKLIST_TOKEN not configured on the server' }, { status: 503 })
  }
  if (req.headers.get('x-build-token') !== expectedToken) {
    return NextResponse.json({ error: 'unauthorized' }, { status: 401 })
  }

  const body = await req.json().catch(() => null)
  const id = body?.id
  const status = body?.status

  if (typeof id !== 'number' || !VALID_STATUSES.includes(status)) {
    return NextResponse.json({ error: 'id must be a number and status must be one of ' + VALID_STATUSES.join(', ') }, { status: 400 })
  }

  const supabase = getServerSupabase()
  const { data, error } = await supabase
    .from('build_tasks')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id)
    .select()

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
  if (!data || data.length === 0) {
    return NextResponse.json({ error: `No build_tasks row with id ${id}` }, { status: 404 })
  }

  return NextResponse.json({ ok: true, row: data[0] })
}
