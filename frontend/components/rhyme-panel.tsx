"use client"

import { useState, useMemo } from "react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { RhymeCard } from "@/components/rhyme-card"
import type { Battle } from "@/lib/types"
import { getTeamLabel } from "@/lib/utils-battle"
import { cn } from "@/lib/utils"

type MCFilter = "all" | "mc1" | "mc2"

export function RhymePanel({
  battle,
  onTimestampClick,
}: {
  battle: Battle
  onTimestampClick?: (timestamp: number) => void
}) {
  const [mcFilter, setMcFilter] = useState<MCFilter>("all")
  const rounds = Array.from({ length: battle.rounds }, (_, i) => i + 1)

  const filteredRhymes = useMemo(() => {
    if (mcFilter === "all") return battle.rhymes
    return battle.rhymes.filter((r) => r.mc === mcFilter)
  }, [battle.rhymes, mcFilter])

  const mc1Count = battle.rhymes.filter((r) => r.mc === "mc1").length
  const mc2Count = battle.rhymes.filter((r) => r.mc === "mc2").length

  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      <div className="flex flex-col gap-3 border-b border-border p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">
            Rimas
          </h2>
          <Badge variant="secondary" className="text-xs tabular-nums">
            {filteredRhymes.length} total
          </Badge>
        </div>

        <div className="flex items-center gap-1">
          {(
            [
              { key: "all", label: "Todos", count: battle.rhymes.length },
              { key: "mc1", label: getTeamLabel(battle.participants, 0), count: mc1Count },
              { key: "mc2", label: getTeamLabel(battle.participants, 1), count: mc2Count },
            ] as const
          ).map((filter) => (
            <button
              key={filter.key}
              onClick={() => setMcFilter(filter.key)}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors",
                mcFilter === filter.key
                  ? filter.key === "mc1"
                    ? "bg-mc1/15 text-mc1"
                    : filter.key === "mc2"
                      ? "bg-mc2/15 text-mc2"
                      : "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              {filter.label}
              <span className="tabular-nums opacity-60">{filter.count}</span>
            </button>
          ))}
        </div>
      </div>

      <Tabs defaultValue="1" className="flex flex-1 flex-col overflow-hidden">
        <div className="border-b border-border px-4 py-2">
          <TabsList className="w-full">
            {rounds.map((round) => (
              <TabsTrigger key={round} value={String(round)} className="flex-1 text-xs">
                Round {round}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        {rounds.map((round) => {
          const roundRhymes = filteredRhymes.filter((r) => r.round === round)
          return (
            <TabsContent key={round} value={String(round)} className="flex-1 overflow-hidden">
              <ScrollArea className="h-[calc(100vh-380px)] lg:h-[calc(100vh-340px)]">
                <div className="flex flex-col gap-3 p-4">
                  {roundRhymes.length === 0 ? (
                    <p className="py-8 text-center text-sm text-muted-foreground">
                      No hay rimas en este round para el filtro seleccionado.
                    </p>
                  ) : (
                    roundRhymes.map((rhyme) => (
                      <RhymeCard
                        key={rhyme.id}
                        rhyme={rhyme}
                        mc1Name={getTeamLabel(battle.participants, 0)}
                        mc2Name={getTeamLabel(battle.participants, 1)}
                        onTimestampClick={onTimestampClick}
                      />
                    ))
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          )
        })}
      </Tabs>
    </div>
  )
}
