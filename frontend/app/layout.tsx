import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { Toaster } from 'sonner'
import { Header } from '@/components/header'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'BarCheck - Califica las Rimas de Batallas de Rap',
  description: 'Sube videos de batallas de rap, visualiza las rimas y califica cada una en rima, ingenio, punchline y respuesta.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  themeColor: '#0a0a0a',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className="dark">
      <body className="font-sans antialiased">
        <Header />
        <main className="min-h-[calc(100vh-4rem)]">
          {children}
        </main>
        <Toaster
          theme="dark"
          position="bottom-right"
          toastOptions={{
            className: "bg-card text-card-foreground border-border",
          }}
        />
        <Analytics />
      </body>
    </html>
  )
}
