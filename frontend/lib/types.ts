export type RhymeRating = {
  rima: number
  ingenio: number
  punchline: number
  respuesta: number
}

export type Rhyme = {
  id: string
  text: string
  mc: "mc1" | "mc2"
  participantId?: number
  timestamp: number
  round: number
  ratings: RhymeRating
  userRating?: RhymeRating
}

export type MC = {
  name: string
  avatar: string
}

export type Participant = {
  id: number
  name: string
  avatar: string
  teamNumber: number
  positionInTeam: number
}

export type BattleFormat = "1v1" | "2v2" | "3v3" | "3v1" | "1v2" | "multi"

export type Battle = {
  id: string
  title: string
  mc1: MC
  mc2: MC
  participants: Participant[]
  battleFormat: BattleFormat
  videoUrl: string
  youtubeUrl?: string
  thumbnail: string
  date: string
  event: string
  rounds: number
  rhymes: Rhyme[]
}

export const RATING_CATEGORIES: { key: keyof RhymeRating; label: string; colorClass: string }[] = [
  { key: "rima", label: "Rima", colorClass: "bg-rating-rima" },
  { key: "ingenio", label: "Ingenio", colorClass: "bg-rating-ingenio" },
  { key: "punchline", label: "Punchline", colorClass: "bg-rating-punchline" },
  { key: "respuesta", label: "Respuesta", colorClass: "bg-rating-respuesta" },
]
