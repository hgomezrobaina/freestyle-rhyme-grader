"use client";

import { Button } from "@/components/ui/button";
import { getBattleDetail } from "@/lib/api";
import { CheckCircle2, Loader2, Mic2, XCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { PipelineStep, ProcessStatus } from "../../domain/process-status";

const STEPS = [
  { key: PipelineStep.DOWNLOAD, label: "Descargando audio" },
  { key: PipelineStep.TRANSCRIBE, label: "Transcribiendo con Whisper" },
  { key: PipelineStep.SEPARATE, label: "Separando voces" },
  { key: PipelineStep.DIARIZE, label: "Identificando MCs" },
  { key: PipelineStep.ANALYZE, label: "Analizando rimas" },
];

function getStepIndex(progressStep?: string): number {
  if (!progressStep) return 0;
  const idx = STEPS.findIndex((s) => s.key === progressStep);
  return idx >= 0 ? idx : 0;
}

export default function ProcessingView({ battleId }: { battleId: number }) {
  const [status, setStatus] = useState(ProcessStatus.PENDING);
  const [stepIndex, setStepIndex] = useState(0);
  const [failedStep, setFailedStep] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    let interval: NodeJS.Timeout;

    async function poll() {
      try {
        const detail = await getBattleDetail(battleId);
        if (!mounted) return;

        if (detail.status === ProcessStatus.COMPLETED) {
          setStepIndex(STEPS.length);
          setStatus(ProcessStatus.COMPLETED);
          clearInterval(interval);
        } else if (detail.status === ProcessStatus.FAILED) {
          setFailedStep(detail.progress_step ?? null);
          setStepIndex(getStepIndex(detail.progress_step));
          setStatus(ProcessStatus.FAILED);
          clearInterval(interval);
        } else {
          setStepIndex(getStepIndex(detail.progress_step));
          setStatus(ProcessStatus.PROCESSING);
        }
      } catch {
        // API might not be ready yet, keep polling
      }
    }

    poll();
    interval = setInterval(poll, 3000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [battleId]);

  if (status === ProcessStatus.COMPLETED) {
    return null; // Will be handled by parent
  }

  const isFailed = status === ProcessStatus.FAILED;
  const failedStepLabel = failedStep
    ? STEPS.find((s) => s.key === failedStep)?.label
    : null;

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="flex w-full max-w-md flex-col items-center gap-8 px-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/20">
          <Mic2 className="h-8 w-8 text-primary" />
        </div>

        <div className="text-center">
          <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
            {isFailed ? "Error en el analisis" : "Analizando batalla"}
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {isFailed
              ? failedStepLabel
                ? `Fallo en: ${failedStepLabel}`
                : "Hubo un problema al procesar la batalla"
              : "Esto puede tardar unos minutos..."}
          </p>
        </div>

        {isFailed ? (
          <div className="flex flex-col items-center gap-3">
            <XCircle className="h-10 w-10 text-destructive" />
            <Button asChild variant="outline" size="sm">
              <Link href="/">Volver al inicio</Link>
            </Button>
          </div>
        ) : (
          <div className="flex w-full flex-col gap-3">
            {STEPS.map((step, i) => {
              const isDone = i < stepIndex;
              const isCurrent = i === stepIndex;
              return (
                <div key={step.key} className="flex items-center gap-3">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center">
                    {isDone ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : isCurrent ? (
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    ) : (
                      <div className="h-2.5 w-2.5 rounded-full bg-muted-foreground/20" />
                    )}
                  </div>
                  <span
                    className={`text-sm ${
                      isDone
                        ? "font-medium text-muted-foreground line-through"
                        : isCurrent
                          ? "font-bold text-foreground"
                          : "text-muted-foreground/50"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
