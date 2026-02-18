import { cn } from "@/lib/utils"

function getScoreColor(score: number) {
  if (score >= 4.5) return "bg-rating-respuesta/20 text-rating-respuesta border-rating-respuesta/30"
  if (score >= 3.5) return "bg-primary/20 text-primary border-primary/30"
  if (score >= 2.5) return "bg-rating-ingenio/20 text-rating-ingenio border-rating-ingenio/30"
  return "bg-muted text-muted-foreground border-border"
}

export function ScoreBadge({ score, size = "default" }: { score: number; size?: "sm" | "default" | "lg" }) {
  return (
    <span
      className={cn(
        "inline-flex items-center justify-center rounded-md border font-bold tabular-nums",
        getScoreColor(score),
        size === "sm" && "px-1.5 py-0.5 text-xs",
        size === "default" && "px-2 py-1 text-sm",
        size === "lg" && "px-3 py-1.5 text-base"
      )}
    >
      {score.toFixed(1)}
    </span>
  )
}
