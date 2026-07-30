import { getServerSupabase } from '@/lib/supabase'
import TaskRow from './TaskRow'

export const dynamic = 'force-dynamic'

type BuildTask = {
  id: number
  title: string
  status: string
  explanation: string
  simplification: string
  background_context: string
  acceptance_criteria: string
  test_result: string
  test_status: string
  updated_at: string
}

export default async function BuildChecklistPage() {
  const supabase = getServerSupabase()
  const { data: tasks, error } = await supabase
    .from('build_tasks')
    .select('*')
    .order('id', { ascending: true })

  if (error) {
    return (
      <div className="av-page">
        <p>Could not load build_tasks: {error.message}</p>
      </div>
    )
  }

  const rows = (tasks ?? []) as BuildTask[]
  const counts = rows.reduce<Record<string, number>>((acc, t) => {
    acc[t.status] = (acc[t.status] ?? 0) + 1
    return acc
  }, {})

  return (
    <div className="av-page" style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <div style={{ fontFamily: 'monospace', fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
          Real backend — Supabase build_tasks table, not a static page
        </div>
        <h1 style={{ margin: '0.2rem 0 0', fontSize: '1.6rem' }}>AlphaVeda — Build Verification Checklist</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.7rem' }}>
        {['completed', 'in_progress', 'pending', 'blocked'].map((key) => (
          <div key={key} className="av-card" style={{ padding: '0.8rem 1rem' }}>
            <div style={{ fontFamily: 'monospace', fontSize: '1.5rem', fontWeight: 600 }}>{counts[key] ?? 0}</div>
            <div style={{ fontSize: '0.68rem', textTransform: 'uppercase', color: 'var(--text-muted)' }}>{key.replace('_', ' ')}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.7rem' }}>
        {rows.map((task) => (
          <TaskRow key={task.id} task={task} />
        ))}
      </div>

      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
        This page reads live from Supabase on every load (force-dynamic, no cache) — toggling a
        task&apos;s status below writes to the database via a server API route and reflects on
        the next load, not instantly without refresh.
      </p>
    </div>
  )
}
