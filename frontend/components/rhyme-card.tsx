"use client"

import { useState } from "react"
import { Clock, ChevronDown, ChevronUp } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { RatingSliders } from "@/components/rating-sliders"
import { ScoreBadge } from "@/components/score-badge"
import type { Rhyme } from "@/lib/types/rhyme"
import type { RhymeRating } from "@/lib/types/rating"
import { formatTimestamp, getAverageScore } from "@/lib/utils-battle"
import { cn } from "@/lib/utils"

export function RhymeCard({
  rhyme,
  mc1Name,
  mc2Name,
  onTimestampClick,
}: {
  rhyme: Rhyme
  mc1Name: string
  mc2Name: string
  onTimestampClick?: (timestamp: number) => void
}) {
  const [userRating, setUserRating] = useState<RhymeRating>(
    rhyme.userRating ?? { ...rhyme.ratings }
  )
  const [expanded, setExpanded] = useState(false)
  const isMc1 = rhyme.mc === "mc1"
  const mcName = isMc1 ? mc1Name : mc2Name
  const avgScore = getAverageScore(userRating)

  function handleRate(category: keyof RhymeRating, value: number) {
    setUserRating((prev) => ({ ...prev, [category]: value }))
  }

  return (
    <div
      className={cn(
        "group relative rounded-lg border border-border/60 bg-card p-4 transition-all",
        expanded && "border-border bg-secondary/20"
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={cn(
                "text-xs font-bold uppercase",
                isMc1
                  ? "border-mc1/40 bg-mc1/10 text-mc1"
                  : "border-mc2/40 bg-mc2/10 text-mc2"
              )}
            >
              {mcName}
            </Badge>
            <button
              onClick={() => onTimestampClick?.(rhyme.timestamp)}
              className="flex items-center gap-1 text-xs text-muted-foreground transition-colors hover:text-primary"
              aria-label={`Ir a ${formatTimestamp(rhyme.timestamp)}`}
            >
              <Clock className="h-3 w-3" />
              {formatTimestamp(rhyme.timestamp)}
            </button>
          </div>
          <p className="mt-2 text-sm leading-relaxed text-foreground">
            {`"${rhyme.text}"`}
          </p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <ScoreBadge score={avgScore} size="sm" />
        </div>
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-3 flex w-full items-center justify-center gap-1 rounded-md py-1 text-xs font-medium text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
        aria-label={expanded ? "Ocultar calificacion" : "Calificar esta rima"}
      >
        {expanded ? (
          <>
            Ocultar <ChevronUp className="h-3 w-3" />
          </>
        ) : (
          <>
            Calificar <ChevronDown className="h-3 w-3" />
          </>
        )}
      </button>

      {expanded && (
        <div className="mt-3 border-t border-border/50 pt-3">
          <RatingSliders ratings={userRating} onRate={handleRate} />
        </div>
      )}
    </div>
  )
}
