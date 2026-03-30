"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Loader2,
  Mic2,
  Pencil,
  Check,
  Play,
  Swords,
  Save,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { VideoPlayer, type VideoPlayerHandle } from "@/components/video-player";
import type { Battle } from "@/lib/types/battle";
import type { Rhyme } from "@/lib/types/rhyme";
import type { Participant } from "@/lib/types/participant";
import { getTeamLabel } from "@/lib/utils-battle";
import { renameParticipant } from "@/lib/api/participants";
import { updateVerse } from "@/lib/api/battles";
import { cn } from "@/lib/utils";
import Header from "./components/Header/Header";
import BattleHeader from "./components/BattleHeader/BattleHeader";
import Team from "./components/Team/Team";

interface BattleInfoViewProps {
  battle: Battle;
  battleId: number;
  analyzing: boolean;
  onAnalyze: () => void;
}

export default function BattleInfoView({
  battle,
  battleId,
  analyzing,
  onAnalyze,
}: BattleInfoViewProps) {
  const playerRef = useRef<VideoPlayerHandle>(null);
  const [participants, setParticipants] = useState<Participant[]>(
    battle.participants,
  );

  const [rhymes, setRhymes] = useState<Rhyme[]>(battle.rhymes);
  const [editingVerseId, setEditingVerseId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [savingVerseId, setSavingVerseId] = useState<string | null>(null);

  const currentBattle = { ...battle, participants };
  const hasRhymes = rhymes.length > 0;

  console.log(battle);

  // --- Verse editing ---
  function startEditingVerse(rhyme: Rhyme) {
    setEditingVerseId(rhyme.id);
    setEditText(rhyme.text);
  }

  function cancelEditingVerse() {
    setEditingVerseId(null);
    setEditText("");
  }

  async function saveVerse(rhymeId: string) {
    const trimmed = editText.trim();
    const original = rhymes.find((r) => r.id === rhymeId);
    if (!trimmed || trimmed === original?.text) {
      cancelEditingVerse();
      return;
    }

    setSavingVerseId(rhymeId);

    try {
      await updateVerse(Number(rhymeId), { text: trimmed });
      setRhymes((prev) =>
        prev.map((r) => (r.id === rhymeId ? { ...r, text: trimmed } : r)),
      );
    } catch {
      // Silently fail
    }

    setSavingVerseId(null);
    setEditingVerseId(null);
    setEditText("");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8 lg:py-8">
      <div className="flex flex-col gap-4">
        <Header />

        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <BattleHeader battle={battle} />

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <Team
                paricipants={{ value: participants, onChange: setParticipants }}
                team={0}
                battleId={battleId}
              />

              <Swords className="h-4 w-4 text-muted-foreground" />

              <Team
                paricipants={{ value: participants, onChange: setParticipants }}
                team={1}
                battleId={battleId}
              />
            </div>

            <Badge variant="secondary" className="text-xs">
              {battle.battleFormat.toUpperCase()}
            </Badge>

            {!analyzing && !hasRhymes && (
              <Button
                size="sm"
                onClick={onAnalyze}
                className="font-bold uppercase tracking-wide"
              >
                <Play className="h-3.5 w-3.5" />
                Analizar rimas
              </Button>
            )}

            {analyzing && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                Analizando...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Split Layout: Video + Verses */}
      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        {/* Video */}
        <div className="lg:w-[60%]">
          <div className="sticky top-20">
            <VideoPlayer ref={playerRef} battle={currentBattle} />
          </div>
        </div>

        {/* Verses panel */}
        <div className="lg:w-[40%]">
          <div className="flex h-full flex-col rounded-xl border border-border bg-card">
            <div className="flex items-center justify-between border-b border-border p-4">
              <h2 className="text-sm font-bold uppercase tracking-wider text-foreground">
                Versos
              </h2>
              <Badge variant="secondary" className="text-xs tabular-nums">
                {rhymes.length} total
              </Badge>
            </div>

            {hasRhymes ? (
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="flex flex-col gap-3 p-4">
                  {rhymes.map((rhyme) => {
                    const isMc1 = rhyme.mc === "mc1";
                    const mcName = isMc1
                      ? getTeamLabel(participants, 0)
                      : getTeamLabel(participants, 1);
                    const isEditing = editingVerseId === rhyme.id;
                    const isSaving = savingVerseId === rhyme.id;

                    return (
                      <div
                        key={rhyme.id}
                        className={cn(
                          "group relative rounded-lg border border-border/60 bg-card p-4 transition-all",
                          isEditing && "border-primary/50 bg-primary/5",
                        )}
                      >
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="outline"
                            className={cn(
                              "text-xs font-bold uppercase",
                              isMc1
                                ? "border-mc1/40 bg-mc1/10 text-mc1"
                                : "border-mc2/40 bg-mc2/10 text-mc2",
                            )}
                          >
                            {mcName}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            v{rhyme.round}
                          </span>
                        </div>

                        {isEditing ? (
                          <div className="mt-2">
                            <textarea
                              autoFocus
                              value={editText}
                              onChange={(e) => setEditText(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === "Escape") cancelEditingVerse();
                                if (e.key === "Enter" && e.ctrlKey)
                                  saveVerse(rhyme.id);
                              }}
                              rows={4}
                              className="w-full resize-none rounded-md border border-input bg-background px-3 py-2 text-sm leading-relaxed text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                            />
                            <div className="mt-2 flex items-center justify-between">
                              <span className="text-[10px] text-muted-foreground">
                                Ctrl+Enter para guardar, Esc para cancelar
                              </span>
                              <div className="flex items-center gap-1">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={cancelEditingVerse}
                                  disabled={isSaving}
                                >
                                  <X className="h-3.5 w-3.5" />
                                  Cancelar
                                </Button>
                                <Button
                                  size="sm"
                                  onClick={() => saveVerse(rhyme.id)}
                                  disabled={isSaving}
                                >
                                  {isSaving ? (
                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                  ) : (
                                    <Save className="h-3.5 w-3.5" />
                                  )}
                                  Guardar
                                </Button>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div
                            onClick={() => startEditingVerse(rhyme)}
                            className="mt-2 cursor-pointer rounded-md px-1 py-0.5 transition-colors hover:bg-muted/50"
                          >
                            <p className="text-sm leading-relaxed text-foreground">
                              {rhyme.text}
                            </p>
                            <span className="mt-1 block text-[10px] text-muted-foreground/0 transition-colors group-hover:text-muted-foreground/60">
                              Click para editar
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            ) : (
              <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/20">
                  <Mic2 className="h-7 w-7 text-primary" />
                </div>
                {analyzing ? (
                  <>
                    <div className="text-center">
                      <p className="font-bold text-foreground">
                        Analizando rimas...
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Segmentando versos y calculando metricas
                      </p>
                    </div>
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  </>
                ) : (
                  <>
                    <div className="text-center">
                      <p className="font-bold text-foreground">
                        Sin versos aun
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Analiza la batalla para ver los versos detectados
                      </p>
                    </div>
                    <Button
                      size="sm"
                      onClick={onAnalyze}
                      className="font-bold uppercase tracking-wide"
                    >
                      <Play className="h-3.5 w-3.5" />
                      Analizar rimas
                    </Button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
