"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { BattleView } from "@/components/battle-view";
import { getBattleDetail } from "@/lib/api/battles";
import type { BattleDetailResponse } from "@/lib/api/types";
import { mapBattleDetailToBattle } from "@/lib/utils-battle";
import type { Battle } from "@/lib/types/battle";
import { Loader2, Mic2, CheckCircle2, XCircle, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import ProcessingView from "./components/ProcessingView/ProcessingView";

export default function BattlePage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const isUploading = searchParams.get("uploading") === "true";
  const [battle, setBattle] = useState<Battle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProcessing, setShowProcessing] = useState(isUploading);

  const battleId = Number(params.id);

  const fetchBattle = useCallback(() => {
    if (isNaN(battleId)) {
      setError("ID de batalla invalido");
      setLoading(false);
      return;
    }

    getBattleDetail(battleId)
      .then((detail) => {
        if (detail.status === "completed") {
          setBattle(mapBattleDetailToBattle(detail));
          setShowProcessing(false);
          setLoading(false);
        } else if (detail.status === "failed") {
          setShowProcessing(true);
          setLoading(false);
        } else if (
          isUploading ||
          detail.status === "processing" ||
          detail.status === "pending"
        ) {
          setShowProcessing(true);
          setLoading(false);
        } else {
          setBattle(mapBattleDetailToBattle(detail));
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isUploading) {
          // Battle might not be ready yet, show processing
          setShowProcessing(true);
          setLoading(false);
        } else {
          setError(err.message || "Error al cargar la batalla");
          setLoading(false);
        }
      });
  }, [battleId, isUploading]);

  useEffect(() => {
    fetchBattle();
  }, [fetchBattle]);

  // When processing finishes, re-fetch the battle data
  useEffect(() => {
    if (!showProcessing || loading) return;

    let interval: NodeJS.Timeout;
    let mounted = true;

    interval = setInterval(async () => {
      try {
        const detail = await getBattleDetail(battleId);
        if (!mounted) return;
        if (detail.status === "completed") {
          setBattle(mapBattleDetailToBattle(detail));
          setShowProcessing(false);
          clearInterval(interval);
        }
      } catch {
        // keep polling
      }
    }, 3000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [showProcessing, loading, battleId]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-muted-foreground">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-sm">Cargando batalla...</p>
        </div>
      </div>
    );
  }

  if (showProcessing) {
    return <ProcessingView battleId={battleId} />;
  }

  if (error || !battle) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-center">
          <p className="text-lg font-bold text-foreground">
            Batalla no encontrada
          </p>
          <p className="text-sm text-muted-foreground">
            {error ?? "No se pudo cargar la batalla"}
          </p>
          <Button asChild variant="outline" size="sm" className="mt-2">
            <Link href="/">
              <ArrowLeft className="h-4 w-4" />
              Volver al inicio
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return <BattleView battle={battle} />;
}
