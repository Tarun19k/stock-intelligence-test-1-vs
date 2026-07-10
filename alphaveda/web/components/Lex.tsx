'use client'
// A10 — renders a lexicon key's mode-appropriate string (plain text only).
// Tap-to-learn glossary interaction (entry.learn) is added in A11's commit —
// this component intentionally does not reference the glossary yet, so A10
// stands alone as the string-architecture foundation.

import type { LexKey } from '@/lib/lexicon'
import { lex } from '@/lib/lexicon'
import { useLanguageMode } from '@/lib/language-mode'

export default function Lex({ k, className }: { k: LexKey; className?: string }) {
  const { mode } = useLanguageMode()
  return <span className={className}>{lex(k, mode)}</span>
}

/** Renders <Lex k={k}/> when k resolves to a known LexKey, else the raw fallback text as-is. */
export function LexOrRaw({ k, fallback, className }: { k: LexKey | null; fallback: string; className?: string }) {
  if (!k) return <span className={className}>{fallback}</span>
  return <Lex k={k} className={className} />
}
