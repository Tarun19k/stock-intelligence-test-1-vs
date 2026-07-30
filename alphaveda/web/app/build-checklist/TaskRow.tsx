'use client'

import { useState } from 'react'

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
}

const STATUS_ORDER = ['pending', 'in_progress', 'blocked', 'completed']

export default function TaskRow({ task }: { task: BuildTask }) {
  const [open, setOpen] = useState(false)
  const [status, setStatus] = useState(task.status)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  async function cycleStatus() {
    const next = STATUS_ORDER[(STATUS_ORDER.indexOf(status) + 1) % STATUS_ORDER.length]
    setSaving(true)
    setSaveError(null)
    try {
      const res = await fetch('/api/build-checklist', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: task.id, status: next }),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.error ?? `HTTP ${res.status}`)
      }
      setStatus(next)
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Update failed')
    } finally {
      setSaving(false)
    }
  }

  const pillColor: Record<string, string> = {
    completed: 'var(--emerald)',
    in_progress: 'var(--indigo)',
    pending: 'var(--text-muted)',
    blocked: 'var(--terra)',
  }

  return (
    <div className="av-card" style={{ overflow: 'hidden' }}>
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', padding: '0.9rem 1.1rem', cursor: 'pointer' }}
        onClick={() => setOpen((o) => !o)}
      >
        <button
          onClick={(e) => {
            e.stopPropagation()
            cycleStatus()
          }}
          disabled={saving}
          style={{
            fontFamily: 'monospace', fontSize: '0.62rem', textTransform: 'uppercase', letterSpacing: '0.03em',
            padding: '0.22rem 0.55rem', borderRadius: '4px', border: `1px solid ${pillColor[status]}`,
            color: pillColor[status], background: 'transparent', cursor: saving ? 'wait' : 'pointer', flexShrink: 0,
          }}
          title="Click to cycle status (writes to build_tasks via /api/build-checklist)"
        >
          {saving ? 'saving…' : status.replace('_', ' ')}
        </button>
        <span style={{ fontSize: '0.92rem', fontWeight: 600, flex: 1 }}>{task.title}</span>
        <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{open ? '▾' : '▸'}</span>
      </div>
      {saveError && (
        <div style={{ padding: '0 1.1rem 0.6rem', fontSize: '0.75rem', color: 'var(--terra)' }}>
          Update failed: {saveError}
        </div>
      )}
      {open && (
        <div style={{ padding: '0 1.1rem 1.1rem', display: 'flex', flexDirection: 'column', gap: '0.8rem', borderTop: '1px solid var(--border)', paddingTop: '0.9rem' }}>
          <Field label="Explanation" value={task.explanation} />
          <Field label="In plain language" value={task.simplification} />
          <Field label="Background context" value={task.background_context} />
          <Field label="Acceptance criteria" value={task.acceptance_criteria} />
          <Field label="Test result" value={task.test_result} mono />
        </div>
      )}
    </div>
  )
}

function Field({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      <span style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
      <span style={{
        fontSize: mono ? '0.78rem' : '0.85rem', lineHeight: 1.55,
        fontFamily: mono ? 'monospace' : 'inherit',
        background: mono ? 'var(--surface2)' : 'transparent',
        border: mono ? '1px solid var(--border)' : 'none',
        borderRadius: mono ? '6px' : 0,
        padding: mono ? '0.6rem 0.75rem' : 0,
        whiteSpace: mono ? 'pre-wrap' : 'normal',
      }}>
        {value}
      </span>
    </div>
  )
}
