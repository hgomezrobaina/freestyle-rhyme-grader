"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Mic2, Upload, Home } from "lucide-react"
import { cn } from "@/lib/utils"

const navLinks = [
  { href: "/", label: "Inicio", icon: Home },
  { href: "/upload", label: "Subir", icon: Upload },
]

export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5 transition-opacity hover:opacity-80">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary">
            <Mic2 className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-xl font-black uppercase tracking-tight text-foreground">
            BarCheck
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          {navLinks.map((link) => {
            const isActive = pathname === link.href
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                )}
              >
                <link.icon className="h-4 w-4" />
                <span className="hidden sm:inline">{link.label}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
