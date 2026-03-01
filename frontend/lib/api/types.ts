export type BattleSourceType = "youtube" | "upload" | "text";
export type BattleStatus = "pending" | "processing" | "completed" | "failed";

export interface BattleParticipantResponse {
  id: number;
  mc_name: string;
  team_number: number;
  position_in_team: number;
}

export interface BattleResponse {
  id: number;
  title: string;
  description?: string;
  source_type: BattleSourceType;
  source_url?: string;
  status: BattleStatus;
  progress_step?: string;
  battle_format?: string;
  battle_date?: string;
  federation?: string;
  total_rounds?: number;
  participants: BattleParticipantResponse[];
  created_at: string;
  updated_at: string;
}

export interface BattleStatusResponse {
  id: number;
  title: string;
  status: BattleStatus;
  progress_step?: string;
  progress_message?: string;
  verses_count: number;
  created_at: string;
  updated_at: string;
}

export interface VerseResponse {
  id: number;
  battle_id: number;
  verse_number: number;
  speaker?: string;
  participant_id?: number;
  text: string;
  duration_seconds?: number;
  round_number?: number;
  rhyme_metric?: {
    id: number;
    rhyme_density: number;
    multisyllabic_ratio: number;
    internal_rhymes_count: number;
    rhyme_diversity?: number;
    total_syllables: number;
    rhymed_syllables: number;
  };
}

export interface BattleDetailResponse extends BattleResponse {
  verses: VerseResponse[];
  participants: BattleParticipantResponse[];
}
