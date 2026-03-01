import Link from "next/link"
import { Calendar, MapPin, Swords } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScoreBadge } from "@/components/score-badge"
import type { Battle } from "@/lib/types"
import { getBattleAverageScore, getTeamLabel } from "@/lib/utils-battle"
import { getYoutubeThumbnail } from "@/lib/youtube"

const gradients = [
  "from-primary/30 via-accent/20 to-transparent",
  "from-accent/30 via-primary/20 to-transparent",
  "from-rating-ingenio/30 via-primary/20 to-transparent",
]

export function BattleCard({ battle, index = 0 }: { battle: Battle; index?: number }) {
  const avgScore = getBattleAverageScore(battle)
  const ytThumb = battle.youtubeUrl ? getYoutubeThumbnail(battle.youtubeUrl) : null

  return (
    <Link href={`/battle/${battle.id}`}>
      <Card className="group relative overflow-hidden border-border/50 bg-card py-0 transition-all duration-300 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5">
        <div className={`relative flex aspect-video items-center justify-center bg-gradient-to-br ${gradients[index % gradients.length]}`}>
          {ytThumb && (
            <>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={ytThumb}
                alt={`Thumbnail de ${battle.title}`}
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-card via-card/40 to-transparent" />
            </>
          )}
          <div className="relative flex items-center gap-4 text-foreground">
            <div className="flex flex-col items-center gap-1">
              <div className="flex -space-x-2">
                {battle.participants.filter((p) => p.teamNumber === 0).map((p, i) => (
                  <div key={i} className="flex h-14 w-14 items-center justify-center rounded-full bg-mc1/20 text-2xl font-black text-mc1 ring-2 ring-mc1/30 backdrop-blur-sm">
                    {p.avatar}
                  </div>
                ))}
              </div>
              <span className="mt-1.5 text-xs font-bold uppercase drop-shadow-md">
                {getTeamLabel(battle.participants, 0)}
              </span>
            </div>
            <Swords className="h-6 w-6 text-muted-foreground drop-shadow-md" />
            <div className="flex flex-col items-center gap-1">
              <div className="flex -space-x-2">
                {battle.participants.filter((p) => p.teamNumber === 1).map((p, i) => (
                  <div key={i} className="flex h-14 w-14 items-center justify-center rounded-full bg-mc2/20 text-2xl font-black text-mc2 ring-2 ring-mc2/30 backdrop-blur-sm">
                    {p.avatar}
                  </div>
                ))}
              </div>
              <span className="mt-1.5 text-xs font-bold uppercase drop-shadow-md">
                {getTeamLabel(battle.participants, 1)}
              </span>
            </div>
          </div>
          <div className="absolute right-3 top-3">
            <ScoreBadge score={avgScore} />
          </div>
          {battle.youtubeUrl && (
            <span className="absolute left-3 top-3 inline-flex items-center gap-1 rounded-md bg-destructive/90 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-destructive-foreground backdrop-blur-sm">
              YouTube
            </span>
          )}
        </div>

        <div className="flex flex-col gap-2 p-4">
          <h3 className="text-sm font-bold uppercase tracking-wide text-foreground text-balance group-hover:text-primary transition-colors">
            {battle.title}
          </h3>
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {battle.event}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              {new Date(battle.date).toLocaleDateString("es-ES", { year: "numeric", month: "short", day: "numeric" })}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs">
              {battle.rounds} {battle.rounds === 1 ? "round" : "rounds"}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              {battle.rhymes.length} rimas
            </Badge>
          </div>
        </div>
      </Card>
    </Link>
  )
}
