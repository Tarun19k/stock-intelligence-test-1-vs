'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import LanguageToggle from './LanguageToggle'

const LINKS = [
  { href: '/', label: 'Market Data' },
  { href: '/signals', label: 'Signals' },
  { href: '/path', label: 'Path' },
  { href: '/accuracy', label: 'Accuracy' },
]

export default function Nav() {
  const pathname = usePathname()
  return (
    <nav className="av-nav" aria-label="Primary navigation">
      <span className="av-nav__brand">AlphaVeda</span>
      <ul className="av-nav__links">
        {LINKS.map(({ href, label }) => (
          <li key={href}>
            <Link
              href={href}
              className={`av-nav__link${pathname === href ? ' av-nav__link--active' : ''}`}
            >
              {label}
            </Link>
          </li>
        ))}
        <li>
          <LanguageToggle />
        </li>
      </ul>
    </nav>
  )
}
