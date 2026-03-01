import type { RhymeRating } from "./rating"

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
