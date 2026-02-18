import Link from "next/link"
import { Mic2, Flame, Users, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BattleCard } from "@/components/battle-card"
import { battles } from "@/lib/mock-data"

const stats = [
  { icon: Flame, label: "Batallas", value: "3" },
  { icon: BarChart3, label: "Rimas Calificadas", value: "24" },
  { icon: Users, label: "MCs", value: "6" },
]

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="relative mx-auto flex max-w-7xl flex-col items-center px-4 py-20 text-center lg:px-8 lg:py-28">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/20">
            <Mic2 className="h-8 w-8 text-primary" />
          </div>
          <h1 className="mt-6 max-w-3xl text-4xl font-black uppercase leading-tight tracking-tight text-foreground text-balance sm:text-5xl lg:text-6xl">
            Califica cada barra de las batallas de rap
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-muted-foreground text-pretty sm:text-lg">
            Sube videos de batallas, visualiza las rimas extraidas y califica cada una en Rima, Ingenio, Punchline y Respuesta.
          </p>
          <div className="mt-8 flex items-center gap-3">
            <Button asChild size="lg" className="font-bold uppercase tracking-wide">
              <Link href="#battles">Explorar Batallas</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="font-bold uppercase tracking-wide">
              <Link href="/upload">Subir Batalla</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-border">
        <div className="mx-auto grid max-w-7xl grid-cols-3 divide-x divide-border px-4 lg:px-8">
          {stats.map((stat) => (
            <div key={stat.label} className="flex flex-col items-center py-8">
              <stat.icon className="h-5 w-5 text-primary" />
              <span className="mt-2 text-2xl font-black tabular-nums text-foreground sm:text-3xl">{stat.value}</span>
              <span className="mt-1 text-xs font-medium uppercase tracking-wider text-muted-foreground">{stat.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Battle Grid */}
      <section id="battles" className="mx-auto w-full max-w-7xl px-4 py-12 lg:px-8 lg:py-16">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold uppercase tracking-wide text-foreground sm:text-2xl">
              Batallas Recientes
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Explora y califica las rimas de cada enfrentamiento
            </p>
          </div>
        </div>
        <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {battles.map((battle, i) => (
            <BattleCard key={battle.id} battle={battle} index={i} />
          ))}
        </div>
      </section>
    </div>
  )
}
