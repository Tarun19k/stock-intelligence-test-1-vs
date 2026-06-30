import type { Metadata } from 'next'
import './globals.css'
import Nav from '@/components/Nav'
import SebiDisclaimer from '@/components/SebiDisclaimer'

export const metadata: Metadata = {
  title: 'AlphaVeda — Indian Stock Research',
  description: 'Signal-based stock research for Indian markets. Research purposes only — not investment advice.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="av-page">{children}</main>
        <SebiDisclaimer />
      </body>
    </html>
  )
}
