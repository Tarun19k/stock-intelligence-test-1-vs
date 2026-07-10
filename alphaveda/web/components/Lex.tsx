'use client'
// A10/A11 — renders a lexicon key's mode-appropriate string. When the entry
// has a `learn` glossary key, Simple-mode renders it as a tap-to-learn target
// (dotted underline, matches the catalog v2 mock's interaction) that opens
// GlossaryModal. Pro-mode never shows the tap target — Pro users already use
// the professional term directly (lexicon §5 rule 3: "the product teaches
// upward" only applies when simplifying, not when already at the pro level).

import type { LexKey } from '@/lib/lexicon'
import { lex, LEXICON } from '@/lib/lexicon'
import { useLanguageMode } from '@/lib/language-mode'
import { useGlossary } from '@/lib/glossary-context'

export default function Lex({ k, className }: { k: LexKey; className?: string }) {
  const { mode } = useLanguageMode()
  const { open } = useGlossary()
  const entry = LEXICON[k]
  const text = lex(k, mode)

  if (mode === 'simple' && entry.learn) {
    return (
      <button
        type="button"
        onClick={() => open(entry.learn!)}
        className={className}
        aria-haspopup="dialog"
        style={{
          background: 'none',
          border: 'none',
          padding: 0,
          font: 'inherit',
          color: 'inherit',
          cursor: 'pointer',
          textDecoration: 'underline dotted',
          textUnderlineOffset: '3px',
        }}
      >
        {text}
      </button>
    )
  }

  return <span className={className}>{text}</span>
}

/** Renders <Lex k={k}/> when k resolves to a known LexKey, else the raw fallback text as-is. */
export function LexOrRaw({ k, fallback, className }: { k: LexKey | null; fallback: string; className?: string }) {
  if (!k) return <span className={className}>{fallback}</span>
  return <Lex k={k} className={className} />
}
