import type { Metadata } from 'next'
import './globals.css'
import Nav from '@/components/Nav'
import SebiDisclaimer from '@/components/SebiDisclaimer'
import GlossaryModal from '@/components/GlossaryModal'
import { LanguageModeProvider } from '@/lib/language-mode'
import { GlossaryProvider } from '@/lib/glossary-context'

export const metadata: Metadata = {
  title: 'AlphaVeda — Indian Stock Research',
  description: 'Signal-based stock research for Indian markets. Research purposes only — not investment advice.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageModeProvider>
          <GlossaryProvider>
            <Nav />
            <main className="av-page">{children}</main>
            <SebiDisclaimer />
            <GlossaryModal />
          </GlossaryProvider>
        </LanguageModeProvider>
      </body>
    </html>
  )
}
