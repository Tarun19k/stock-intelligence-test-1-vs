'use client'
// Per-user language_mode state (A10 / addendum R11 §6.1). Default 'simple'.
// Persisted via localStorage — matches the pattern used elsewhere in this app
// for client-only state (no existing client-state library in lib/, so this
// introduces the minimal React context + localStorage pattern, nothing more).

import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { LanguageMode } from './lexicon'

const STORAGE_KEY = 'av_language_mode'

type LanguageModeContextValue = {
  mode: LanguageMode
  setMode: (m: LanguageMode) => void
  toggle: () => void
}

const LanguageModeContext = createContext<LanguageModeContextValue | null>(null)

export function LanguageModeProvider({ children }: { children: ReactNode }) {
  // Server-rendered markup and first client render must match, so we always
  // start at the default 'simple' and only read localStorage after mount.
  const [mode, setModeState] = useState<LanguageMode>('simple')

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY)
      if (stored === 'simple' || stored === 'pro') setModeState(stored)
    } catch {
      // localStorage unavailable (private mode, etc.) — silently keep default.
    }
  }, [])

  const setMode = (m: LanguageMode) => {
    setModeState(m)
    try {
      window.localStorage.setItem(STORAGE_KEY, m)
    } catch {
      // ignore persistence failure — in-memory state still works for this session
    }
  }

  const toggle = () => setMode(mode === 'simple' ? 'pro' : 'simple')

  return (
    <LanguageModeContext.Provider value={{ mode, setMode, toggle }}>
      {children}
    </LanguageModeContext.Provider>
  )
}

export function useLanguageMode(): LanguageModeContextValue {
  const ctx = useContext(LanguageModeContext)
  if (!ctx) throw new Error('useLanguageMode must be used within LanguageModeProvider')
  return ctx
}
