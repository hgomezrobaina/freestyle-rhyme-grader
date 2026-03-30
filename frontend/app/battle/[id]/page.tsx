"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams } from "next/navigation";
import Link from "next/link";
import { BattleView } from "@/components/battle-view";
import { getBattleDetail, analyzeBattle } from "@/lib/api/battles";
import type { BattleDetailResponse } from "@/lib/api/types";
import { mapBattleDetailToBattle } from "@/lib/utils-battle";
import type { Battle } from "@/lib/types/battle";
import { Loader2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import ProcessingView from "./components/ProcessingView/ProcessingView";
import BattleInfoView from "./components/BattleInfoView/BattleInfoView";

export default function BattlePage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const isUploading = searchParams.get("uploading") === "true";

  const [detail, setDetail] = useState<BattleDetailResponse | null>(null);
  const [battle, setBattle] = useState<Battle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProcessing, setShowProcessing] = useState(isUploading);
  const [analyzing, setAnalyzing] = useState(false);

  const battleId = Number(params.id);

  const fetchBattle = useCallback(() => {
    if (isNaN(battleId)) {
      setError("ID de batalla invalido");
      setLoading(false);
      return;
    }

    getBattleDetail(battleId)
      .then((d) => {
        setDetail(d);
        if (d.status === "completed") {
          setBattle(mapBattleDetailToBattle(d));
          setShowProcessing(false);
        } else if (d.status === "diarized") {
          setBattle(mapBattleDetailToBattle(d));
          setShowProcessing(false);
        } else if (d.status === "failed") {
          setShowProcessing(true);
        } else if (
          isUploading ||
          d.status === "processing" ||
          d.status === "pending"
        ) {
          setShowProcessing(true);
        } else {
          setBattle(mapBattleDetailToBattle(d));
        }
        setLoading(false);
      })
      .catch((err) => {
        if (isUploading) {
          setShowProcessing(true);
        } else {
          setError(err.message || "Error al cargar la batalla");
        }
        setLoading(false);
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
        const d = await getBattleDetail(battleId);
        if (!mounted) return;
        if (d.status === "diarized") {
          setDetail(d);
          setBattle(mapBattleDetailToBattle(d));
          setShowProcessing(false);
          clearInterval(interval);
        } else if (d.status === "completed") {
          setDetail(d);
          setBattle(mapBattleDetailToBattle(d));
          setShowProcessing(false);
          setAnalyzing(false);
          clearInterval(interval);
        }
      } catch {
        // keep polling
      }
    }, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [showProcessing, loading, battleId]);

  // Poll while analyzing
  useEffect(() => {
    if (!analyzing) return;

    let interval: NodeJS.Timeout;
    let mounted = true;

    interval = setInterval(async () => {
      try {
        const d = await getBattleDetail(battleId);
        if (!mounted) return;
        if (d.status === "completed") {
          setDetail(d);
          setBattle(mapBattleDetailToBattle(d));
          setAnalyzing(false);
          clearInterval(interval);
        } else if (d.status === "failed") {
          setDetail(d);
          setAnalyzing(false);
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
  }, [analyzing, battleId]);

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      await analyzeBattle(battleId);
    } catch {
      setAnalyzing(false);
    }
  };

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

  // Battle is diarized but not yet analyzed
  if (detail?.status === "diarized" || analyzing) {
    return (
      <BattleInfoView
        battle={battle}
        battleId={battleId}
        analyzing={analyzing}
        onAnalyze={handleAnalyze}
      />
    );
  }

  return <BattleView battle={battle} />;
}
