"use client"

import { useRef, useState } from "react"
import Link from "next/link"
import { ArrowLeft, Calendar, MapPin, Swords, Pencil, Check } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScoreBadge } from "@/components/score-badge"
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video-player"
import { RhymePanel } from "@/components/rhyme-panel"
import type { Battle } from "@/lib/types/battle"
import type { Participant } from "@/lib/types/participant"
import { getBattleAverageScore, getTeamLabel } from "@/lib/utils-battle"
import { renameParticipant } from "@/lib/api/participants"

export function BattleView({ battle }: { battle: Battle }) {
  const playerRef = useRef<VideoPlayerHandle>(null)
  const [participants, setParticipants] = useState<Participant[]>(battle.participants)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editName, setEditName] = useState("")
  const avgScore = getBattleAverageScore(battle)

  // Derived battle with live participants for child components
  const currentBattle = { ...battle, participants }

  function handleTimestampClick(timestamp: number) {
    playerRef.current?.seekTo(timestamp)
  }

  function startEditing(p: Participant) {
    setEditingId(p.id)
    setEditName(p.name)
  }

  async function confirmRename(participantId: number) {
    const trimmed = editName.trim()
    if (!trimmed || trimmed === participants.find((p) => p.id === participantId)?.name) {
      setEditingId(null)
      return
    }

    try {
      const updated = await renameParticipant(Number(battle.id), participantId, trimmed)
      setParticipants((prev) =>
        prev.map((p) =>
          p.id === participantId
            ? { ...p, name: updated.mc_name, avatar: updated.mc_name.charAt(0).toUpperCase() }
            : p
        )
      )
    } catch {
      // Silently fail — name stays as-is
    }
    setEditingId(null)
  }

  function renderTeamNames(teamNumber: number) {
    const teamMembers = participants.filter((p) => p.teamNumber === teamNumber)
    return (
      <div className="flex items-center gap-1">
        {teamMembers.map((p, i) => (
          <span key={p.id} className="flex items-center">
            {i > 0 && <span className="mx-0.5 text-muted-foreground">&</span>}
            {editingId === p.id ? (
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  confirmRename(p.id)
                }}
                className="inline-flex items-center gap-1"
              >
                <input
                  autoFocus
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onBlur={() => confirmRename(p.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Escape") setEditingId(null)
                  }}
                  className="h-6 w-28 rounded border border-primary bg-background px-1.5 text-sm font-bold text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                />
                <button type="submit" className="text-primary">
                  <Check className="h-3.5 w-3.5" />
                </button>
              </form>
            ) : (
              <button
                onClick={() => startEditing(p)}
                className="group/edit flex items-center gap-1 text-sm font-bold text-foreground transition-colors hover:text-primary"
              >
                {p.name}
                <Pencil className="h-3 w-3 opacity-0 transition-opacity group-hover/edit:opacity-60" />
              </button>
            )}
          </span>
        ))}
      </div>
    )
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
                <div className="flex -space-x-1">
                  {participants.filter((p) => p.teamNumber === 0).map((p) => (
                    <div key={p.id} className="flex h-8 w-8 items-center justify-center rounded-full bg-mc1/20 text-sm font-black text-mc1 ring-1 ring-mc1/30">
                      {p.avatar}
                    </div>
                  ))}
                </div>
                {renderTeamNames(0)}
              </div>
              <Swords className="h-4 w-4 text-muted-foreground" />
              <div className="flex items-center gap-2">
                <div className="flex -space-x-1">
                  {participants.filter((p) => p.teamNumber === 1).map((p) => (
                    <div key={p.id} className="flex h-8 w-8 items-center justify-center rounded-full bg-mc2/20 text-sm font-black text-mc2 ring-1 ring-mc2/30">
                      {p.avatar}
                    </div>
                  ))}
                </div>
                {renderTeamNames(1)}
              </div>
            </div>
            <Badge variant="secondary" className="text-xs">
              {currentBattle.battleFormat.toUpperCase()}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {currentBattle.rounds} {currentBattle.rounds === 1 ? "round" : "rounds"}
            </Badge>
          </div>
        </div>
      </div>

      {/* Split Layout: Video + Rhymes */}
      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        <div className="lg:w-[60%]">
          <div className="sticky top-20">
            <VideoPlayer ref={playerRef} battle={currentBattle} />
          </div>
        </div>
        <div className="lg:w-[40%]">
          <RhymePanel battle={currentBattle} onTimestampClick={handleTimestampClick} />
        </div>
      </div>
    </div>
  )
}
