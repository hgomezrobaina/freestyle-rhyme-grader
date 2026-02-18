"use client";

import { useEffect, useState } from "react";
import {
  getBattleStatus,
  BattleSourceType,
  BattleStatus,
  ApiError,
} from "@/lib/api";

export interface BattleStatusData {
  id: number;
  status: BattleStatus;
  progressMessage?: string;
  versesCount: number;
  isLoading: boolean;
  error?: string;
}

/**
 * Hook para hacer polling automático del estado de una batalla
 * Se detiene automáticamente cuando el estado es 'completed' o 'failed'
 */
export function useBattleStatus(
  battleId: number | null,
  source: BattleSourceType,
) {
  const [data, setData] = useState<BattleStatusData>({
    id: battleId || 0,
    status: "pending",
    progressMessage: undefined,
    versesCount: 0,
    isLoading: true,
    error: undefined,
  });

  useEffect(() => {
    if (!battleId) {
      return;
    }

    let isMounted = true;
    let intervalId: NodeJS.Timeout;

    async function fetchStatus() {
      try {
        const response = await getBattleStatus(battleId, source);
        if (isMounted) {
          setData({
            id: response.id,
            status: response.status,
            progressMessage: response.progress_message,
            versesCount: response.verses_count,
            isLoading: false,
            error: undefined,
          });

          // Detener polling si el procesamiento terminó
          if (response.status === "completed" || response.status === "failed") {
            if (intervalId) clearInterval(intervalId);
          }
        }
      } catch (err) {
        if (isMounted) {
          const errorMessage =
            err instanceof ApiError
              ? err.message
              : "Error al obtener estado de la batalla";
          setData((prev) => ({
            ...prev,
            isLoading: false,
            error: errorMessage,
          }));
        }
      }
    }

    // Primera llamada inmediata
    fetchStatus();

    // Polling cada 2 segundos
    intervalId = setInterval(fetchStatus, 2000);

    return () => {
      isMounted = false;
      if (intervalId) clearInterval(intervalId);
    };
  }, [battleId, source]);

  return data;
}
