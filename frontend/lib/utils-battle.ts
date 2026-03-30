import type { Battle, BattleFormat, Participant, RhymeRating } from "./types";
import type {
  BattleDetailResponse,
  BattleParticipantResponse,
  BattleResponse,
} from "./api";
import { API_BASE_URL } from "./api/base";

export function getAverageScore(ratings: RhymeRating): number {
  return Number(
    (
      (ratings.rima + ratings.ingenio + ratings.punchline + ratings.respuesta) /
      4
    ).toFixed(1),
  );
}

export function getBattleAverageScore(battle: Battle): number {
  if (battle.rhymes.length === 0) return 0;
  const total = battle.rhymes.reduce(
    (acc, rhyme) => acc + getAverageScore(rhyme.ratings),
    0,
  );
  return Number((total / battle.rhymes.length).toFixed(1));
}

export function formatTimestamp(seconds: number): string {
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  return `${min}:${sec.toString().padStart(2, "0")}`;
}

function mapParticipants(
  apiParticipants: BattleParticipantResponse[],
): Participant[] {
  return apiParticipants.map((p) => ({
    id: p.id,
    name: p.mc_name,
    avatar: p.mc_name.charAt(0).toUpperCase(),
    teamNumber: p.team_number,
    positionInTeam: p.position_in_team,
  }));
}

export function getTeamLabel(
  participants: Participant[],
  teamNumber: number,
): string {
  const team = participants.filter((p) => p.teamNumber === teamNumber);
  if (team.length === 0) return teamNumber === 0 ? "MC1" : "MC2";
  return team.map((p) => p.name).join(" & ");
}

/**
 * Map API BattleDetailResponse to frontend Battle type
 */
export function mapBattleDetailToBattle(detail: BattleDetailResponse): Battle {
  // Build participants from API data
  const participants = mapParticipants(detail.participants ?? []);

  const team1 = participants.filter((p) => p.teamNumber === 0);
  const team2 = participants.filter((p) => p.teamNumber === 1);

  // Fallback: extract unique speakers from verses
  const speakers = [
    ...new Set(detail.verses.map((v) => v.speaker).filter(Boolean)),
  ] as string[];

  const mc1Name = team1[0]?.name ?? speakers[0] ?? "MC1";
  const mc2Name = team2[0]?.name ?? speakers[1] ?? "MC2";

  // If no participants from API, create defaults
  if (participants.length === 0) {
    participants.push(
      {
        id: 0,
        name: mc1Name,
        avatar: mc1Name.charAt(0).toUpperCase(),
        teamNumber: 0,
        positionInTeam: 0,
      },
      {
        id: 0,
        name: mc2Name,
        avatar: mc2Name.charAt(0).toUpperCase(),
        teamNumber: 1,
        positionInTeam: 0,
      },
    );
  }

  // Build participant_id -> mc mapping (primary source)
  const participantToMc = new Map<number, "mc1" | "mc2">();
  for (const p of participants) {
    participantToMc.set(p.id, p.teamNumber === 0 ? "mc1" : "mc2");
  }

  // Fallback: speaker string -> mc mapping (for old data without participant_id)
  const speakerToMc = new Map<string, "mc1" | "mc2">();
  for (const verse of detail.verses) {
    if (!verse.speaker) continue;
    if (!speakerToMc.has(verse.speaker)) {
      if (verse.speaker === mc1Name || speakerToMc.size === 0) {
        speakerToMc.set(verse.speaker, "mc1");
      } else {
        speakerToMc.set(verse.speaker, "mc2");
      }
    }
  }

  // Calculate rounds from verses
  const maxRound = Math.max(
    ...detail.verses.map((v) => v.round_number ?? 1),
    1,
  );

  // Map verses to rhymes
  const rhymes = detail.verses.map((verse) => {
    // Use participant_id as primary source, fallback to speaker string
    const mc = verse.participant_id
      ? (participantToMc.get(verse.participant_id) ?? "mc1")
      : (speakerToMc.get(verse.speaker ?? "") ??
        (verse.verse_number % 2 === 1 ? "mc1" : "mc2"));
    const metric = verse.rhyme_metric;

    const ratings: RhymeRating = metric
      ? {
          rima: Math.min(5, metric.rhyme_density * 5),
          ingenio: Math.min(5, (metric.rhyme_diversity ?? 0) * 5),
          punchline: Math.min(5, metric.multisyllabic_ratio * 5),
          respuesta: Math.min(
            5,
            metric.internal_rhymes_count > 0
              ? Math.min(metric.internal_rhymes_count, 5)
              : 0,
          ),
        }
      : { rima: 0, ingenio: 0, punchline: 0, respuesta: 0 };

    return {
      id: String(verse.id),
      text: verse.text,
      mc: mc as "mc1" | "mc2",
      participantId: verse.participant_id ?? undefined,
      timestamp: 0,
      round: verse.round_number ?? Math.ceil(verse.verse_number / 2),
      ratings,
    };
  });

  return {
    id: String(detail.id),
    title: detail.title,
    mc1: { name: mc1Name, avatar: mc1Name.charAt(0).toUpperCase() },
    mc2: { name: mc2Name, avatar: mc2Name.charAt(0).toUpperCase() },
    participants,
    battleFormat: (detail.battle_format as BattleFormat) ?? "1v1",
    videoUrl:
      detail.source_type === "upload" && detail.source_url
        ? `${API_BASE_URL}${detail.source_url}`
        : "",
    youtubeUrl:
      detail.source_type === "youtube"
        ? (detail.source_url ?? undefined)
        : undefined,
    thumbnail: "",
    date: detail.battle_date ?? detail.created_at,
    event: detail.federation ?? detail.description ?? "",
    rounds: detail.total_rounds ?? maxRound,
    rhymes,
  };
}

/**
 * Map API BattleResponse (list item) to a minimal frontend Battle type
 */
export function mapBattleResponseToBattle(response: BattleResponse): Battle {
  const participants = mapParticipants(response.participants ?? []);

  const team1 = participants.filter((p) => p.teamNumber === 0);
  const team2 = participants.filter((p) => p.teamNumber === 1);

  const mc1Name = team1[0]?.name ?? "MC1";
  const mc2Name = team2[0]?.name ?? "MC2";

  if (participants.length === 0) {
    participants.push(
      { id: 0, name: "MC1", avatar: "1", teamNumber: 0, positionInTeam: 0 },
      { id: 0, name: "MC2", avatar: "2", teamNumber: 1, positionInTeam: 0 },
    );
  }

  return {
    id: String(response.id),
    title: response.title,
    mc1: { name: mc1Name, avatar: mc1Name.charAt(0).toUpperCase() },
    mc2: { name: mc2Name, avatar: mc2Name.charAt(0).toUpperCase() },
    participants,
    battleFormat: (response.battle_format as BattleFormat) ?? "1v1",
    videoUrl:
      response.source_type === "upload" && response.source_url
        ? `${API_BASE_URL}${response.source_url}`
        : "",
    youtubeUrl:
      response.source_type === "youtube"
        ? (response.source_url ?? undefined)
        : undefined,
    thumbnail: "",
    date: response.battle_date ?? response.created_at,
    event: response.federation ?? response.description ?? "",
    rounds: response.total_rounds ?? 0,
    rhymes: [],
  };
}
