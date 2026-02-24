const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  battle_date?: string;
  federation?: string;
  total_rounds?: number;
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

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let details: unknown;
    try {
      details = await response.json();
    } catch {
      details = response.statusText;
    }
    throw new ApiError(
      response.status,
      `API Error: ${response.status}`,
      details,
    );
  }
  return response.json();
}

/**
 * Subir una batalla a partir de un archivo de video
 */
export async function uploadBattle(
  file: File,
  title: string,
  mc1: string,
  mc2: string,
  event?: string,
  rounds?: number,
): Promise<BattleResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);
  formData.append("description", event || `${mc1} vs ${mc2}`);

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
