import { API_BASE_URL, handleResponse } from "./base";
import type { BattleParticipantResponse } from "./types";

/**
 * Renombrar un participante de una batalla
 */
export async function renameParticipant(
  battleId: number,
  participantId: number,
  newName: string,
): Promise<BattleParticipantResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/battles/${battleId}/participants/${participantId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mc_name: newName }),
    },
  );

  return handleResponse<BattleParticipantResponse>(response);
}
