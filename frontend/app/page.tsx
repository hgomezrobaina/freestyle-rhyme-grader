"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Mic2, Flame, Users, BarChart3, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { BattleCard } from "@/components/battle-card"
import { listBattles } from "@/lib/api"
import { mapBattleResponseToBattle } from "@/lib/utils-battle"
import type { Battle } from "@/lib/types"

export default function HomePage() {
  const [battles, setBattles] = useState<Battle[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listBattles()
      .then((responses) => {
        setBattles(responses.map(mapBattleResponseToBattle))
      })
      .catch(() => {
        setBattles([])
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const stats = [
    { icon: Flame, label: "Batallas", value: String(battles.length) },
    { icon: BarChart3, label: "Rimas Calificadas", value: String(battles.reduce((acc, b) => acc + b.rhymes.length, 0)) },
    { icon: Users, label: "MCs", value: String(battles.length * 2) },
  ]

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
          {loading ? (
            <div className="col-span-full flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : battles.length === 0 ? (
            <div className="col-span-full flex flex-col items-center gap-3 py-12 text-center">
              <p className="text-muted-foreground">No hay batallas todavia</p>
              <Button asChild variant="outline" size="sm">
                <Link href="/upload">Subir la primera batalla</Link>
              </Button>
            </div>
          ) : (
            battles.map((battle, i) => (
              <BattleCard key={battle.id} battle={battle} index={i} />
            ))
          )}
        </div>
      </section>
    </div>
  )
}
