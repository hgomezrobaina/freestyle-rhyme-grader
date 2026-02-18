"use client"

import { RATING_CATEGORIES, type RhymeRating } from "@/lib/types"
import { cn } from "@/lib/utils"

const cssVars: Record<string, string> = {
  rima: "var(--rating-rima)",
  ingenio: "var(--rating-ingenio)",
  punchline: "var(--rating-punchline)",
  respuesta: "var(--rating-respuesta)",
}

const textColorClasses: Record<string, string> = {
  rima: "text-rating-rima",
  ingenio: "text-rating-ingenio",
  punchline: "text-rating-punchline",
  respuesta: "text-rating-respuesta",
}

export function RatingSliders({
  ratings,
  onRate,
  disabled = false,
}: {
  ratings: RhymeRating
  onRate?: (category: keyof RhymeRating, value: number) => void
  disabled?: boolean
}) {
  return (
    <div className="flex flex-col gap-3">
      {RATING_CATEGORIES.map((cat) => {
        const value = ratings[cat.key]
        const percent = ((value - 1) / 4) * 100

        return (
          <div key={cat.key} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className={cn("text-xs font-semibold uppercase tracking-wider", textColorClasses[cat.key])}>
                {cat.label}
              </span>
              <span className="text-xs font-bold tabular-nums text-foreground">
                {value.toFixed(1)}
              </span>
            </div>
            <div className="relative flex items-center">
              <input
                type="range"
                min={1}
                max={5}
                step={0.5}
                value={value}
                disabled={disabled}
                onChange={(e) => onRate?.(cat.key, parseFloat(e.target.value))}
                className="rating-slider w-full"
                style={{
                  "--slider-color": cssVars[cat.key],
                  "--slider-percent": `${percent}%`,
                } as React.CSSProperties}
                aria-label={`Calificar ${cat.label}`}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
