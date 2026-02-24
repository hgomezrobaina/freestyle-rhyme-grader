"use client"

import { useRef } from "react"
import Link from "next/link"
import { ArrowLeft, Calendar, MapPin, Swords } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScoreBadge } from "@/components/score-badge"
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video-player"
import { RhymePanel } from "@/components/rhyme-panel"
import type { Battle } from "@/lib/types"
import { getBattleAverageScore } from "@/lib/utils-battle"

export function BattleView({ battle }: { battle: Battle }) {
  const playerRef = useRef<VideoPlayerHandle>(null)
  const avgScore = getBattleAverageScore(battle)

  function handleTimestampClick(timestamp: number) {
    playerRef.current?.seekTo(timestamp)
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8 lg:py-8">
      {/* Back + Title */}
      <div className="flex flex-col gap-4">
        <Button asChild variant="ghost" size="sm" className="w-fit text-muted-foreground">
          <Link href="/">
            <ArrowLeft className="h-4 w-4" />
            Volver a batallas
          </Link>
        </Button>

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-black uppercase tracking-tight text-foreground sm:text-2xl">
                {battle.title}
              </h1>
              <ScoreBadge score={avgScore} />
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5" />
                {battle.event}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5" />
                {new Date(battle.date).toLocaleDateString("es-ES", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-mc1/20 text-sm font-black text-mc1 ring-1 ring-mc1/30">
                  {battle.mc1.avatar}
                </div>
                <span className="text-sm font-bold text-foreground">{battle.mc1.name}</span>
              </div>
              <Swords className="h-4 w-4 text-muted-foreground" />
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-mc2/20 text-sm font-black text-mc2 ring-1 ring-mc2/30">
                  {battle.mc2.avatar}
                </div>
                <span className="text-sm font-bold text-foreground">{battle.mc2.name}</span>
              </div>
            </div>
            <Badge variant="secondary" className="text-xs">
              {battle.rounds} {battle.rounds === 1 ? "round" : "rounds"}
            </Badge>
          </div>
        </div>
      </div>

      {/* Split Layout: Video + Rhymes */}
      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        <div className="lg:w-[60%]">
          <div className="sticky top-20">
            <VideoPlayer ref={playerRef} battle={battle} />
          </div>
        </div>
        <div className="lg:w-[40%]">
          <RhymePanel battle={battle} onTimestampClick={handleTimestampClick} />
        </div>
      </div>
    </div>
  )
}
