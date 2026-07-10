'use client'
// Visible Pro-mode toggle (A10). Lives in Nav — the natural home for a
// persistent, on-every-page control per the task brief.

import { useLanguageMode } from '@/lib/language-mode'

export default function LanguageToggle() {
  const { mode, toggle } = useLanguageMode()
  const isPro = mode === 'pro'
  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={isPro}
      className="av-nav__link"
      style={{
        cursor: 'pointer',
        background: 'none',
        border: '1px solid currentColor',
        borderRadius: '999px',
        padding: '0.2rem 0.75rem',
        fontSize: '0.75rem',
        lineHeight: 1.4,
      }}
      title={isPro ? 'Showing professional terms — tap to switch to plain language' : 'Showing plain language — tap to switch to professional terms'}
    >
      {isPro ? 'Pro mode' : 'Simple mode'}
    </button>
  )
}
