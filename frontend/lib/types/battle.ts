import type { MC, Participant } from "./participant"
import type { Rhyme } from "./rhyme"

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
