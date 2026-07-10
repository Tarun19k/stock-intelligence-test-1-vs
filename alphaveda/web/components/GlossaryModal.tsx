'use client'
// A11 — modal card rendering the glossary entry opened via useGlossary().
// Mounted once in the root layout. Styling is deliberately minimal/neutral
// (overlay + centered card using existing --text/--surface/--border tokens)
// so it does not encode a D1/D2/D3 visual direction — it is functional
// scaffolding, not a design decision.

import { GLOSSARY } from '@/lib/lexicon'
import { useGlossary } from '@/lib/glossary-context'

export default function GlossaryModal() {
  const { openKey, close } = useGlossary()
  if (!openKey) return null
  const entry = GLOSSARY[openKey]

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={entry.headline}
      onClick={close}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1rem',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: 'var(--surface, #fff)',
          color: 'var(--text, #1A1A2E)',
          borderRadius: '12px',
          border: '1px solid var(--border, #E5E7EB)',
          maxWidth: '360px',
          width: '100%',
          padding: '1.25rem',
        }}
      >
        <h4 style={{ margin: '0 0 0.5rem', fontSize: '1rem' }}>{entry.headline}</h4>
        <p style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', lineHeight: 1.5 }}>{entry.body}</p>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted, #6B7280)' }}>{entry.term}</div>
        <button
          type="button"
          onClick={close}
          style={{
            marginTop: '1rem',
            padding: '0.4rem 0.9rem',
            borderRadius: '999px',
            border: '1px solid currentColor',
            background: 'none',
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Got it
        </button>
      </div>
    </div>
  )
}
