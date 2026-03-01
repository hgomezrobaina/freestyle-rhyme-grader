export type RhymeRating = {
  rima: number
  ingenio: number
  punchline: number
  respuesta: number
}

export const RATING_CATEGORIES: { key: keyof RhymeRating; label: string; colorClass: string }[] = [
  { key: "rima", label: "Rima", colorClass: "bg-rating-rima" },
  { key: "ingenio", label: "Ingenio", colorClass: "bg-rating-ingenio" },
  { key: "punchline", label: "Punchline", colorClass: "bg-rating-punchline" },
  { key: "respuesta", label: "Respuesta", colorClass: "bg-rating-respuesta" },
]
