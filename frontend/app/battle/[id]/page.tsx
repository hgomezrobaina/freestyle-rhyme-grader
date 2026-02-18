import { notFound } from "next/navigation"
import { getBattleById, battles } from "@/lib/mock-data"
import { BattleView } from "@/components/battle-view"
import type { Metadata } from "next"

export function generateStaticParams() {
  return battles.map((battle) => ({ id: battle.id }))
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params
  const battle = getBattleById(id)
  if (!battle) return { title: "Batalla no encontrada" }

  return {
    title: `${battle.title} - BarCheck`,
    description: `Califica las rimas de ${battle.mc1.name} vs ${battle.mc2.name} en ${battle.event}`,
  }
}

export default async function BattlePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const battle = getBattleById(id)

  if (!battle) {
    notFound()
  }

  return <BattleView battle={battle} />
}
