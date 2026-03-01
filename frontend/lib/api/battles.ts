import { API_BASE_URL, handleResponse } from "./base";
import type {
  BattleSourceType,
  BattleResponse,
  BattleStatusResponse,
  BattleDetailResponse,
} from "./types";

/**
 * Subir una batalla a partir de un archivo de video
 */
export async function uploadBattle(
  file: File,
  title: string,
  event?: string,
): Promise<BattleResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  formData.append("description", event || "");

  const response = await fetch(`${API_BASE_URL}/api/battles/upload/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<BattleResponse>(response);
}

/**
 * Crear una batalla a partir de una URL de YouTube
 */
export async function createBattleFromYouTube(
  url: string,
  title: string,
  description?: string,
): Promise<BattleResponse> {
  const params = new URLSearchParams({
    url,
    title,
    ...(description && { description }),
  });

  const response = await fetch(
    `${API_BASE_URL}/api/battles/youtube/youtube?${params}`,
    {
      method: "POST",
    },
  );

  return handleResponse<BattleResponse>(response);
}

/**
 * Obtener el estado de una batalla en procesamiento
 */
export async function getBattleStatus(
  battleId: number,
  source: BattleSourceType,
): Promise<BattleStatusResponse> {
  const endpoint =
    source === "youtube"
      ? `/api/battles/youtube/${battleId}/status`
      : `/api/battles/upload/${battleId}/status`;

  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  return handleResponse<BattleStatusResponse>(response);
}

/**
 * Obtener detalles completos de una batalla con versos
 */
export async function getBattleDetail(
  battleId: number,
): Promise<BattleDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/battles/${battleId}`);

  return handleResponse<BattleDetailResponse>(response);
}

/**
 * Obtener listado de todas las batallas
 */
export async function listBattles(skip = 0, limit = 100) {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/battles/?${params}`);

  return handleResponse<BattleResponse[]>(response);
}
