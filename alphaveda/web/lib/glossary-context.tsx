'use client'
// A11 — tap-to-learn glossary. Shared open/close state so any Lex-rendered
// term anywhere on the page can open the same modal card, matching the
// interaction already prototyped in alphaveda_design_catalog_v2.html's g(k)/
// #gloss pattern (tap target -> small overlay card -> "Got it" dismiss).

import { createContext, useContext, useState, type ReactNode } from 'react'
import type { GlossaryKey } from './lexicon'

type GlossaryContextValue = {
  openKey: GlossaryKey | null
  open: (key: GlossaryKey) => void
  close: () => void
}

const GlossaryContext = createContext<GlossaryContextValue | null>(null)

export function GlossaryProvider({ children }: { children: ReactNode }) {
  const [openKey, setOpenKey] = useState<GlossaryKey | null>(null)
  return (
    <GlossaryContext.Provider
      value={{ openKey, open: (k) => setOpenKey(k), close: () => setOpenKey(null) }}
    >
      {children}
    </GlossaryContext.Provider>
  )
}

export function useGlossary(): GlossaryContextValue {
  const ctx = useContext(GlossaryContext)
  if (!ctx) throw new Error('useGlossary must be used within GlossaryProvider')
  return ctx
}
