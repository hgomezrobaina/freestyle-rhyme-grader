"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { Mic2, Loader2, Upload, Link2, CheckCircle2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { UploadDropzone } from "@/components/upload-dropzone"
import { isValidYoutubeUrl, getYoutubeThumbnail, extractYoutubeId } from "@/lib/youtube"
import { uploadBattle, createBattleFromYouTube, ApiError } from "@/lib/api"

type SourceMode = "upload" | "youtube"

export default function UploadPage() {
  const router = useRouter()
  const [mode, setMode] = useState<SourceMode>("youtube")
  const [file, setFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState("")
  const [title, setTitle] = useState("")
  const [mc1, setMc1] = useState("")
  const [mc2, setMc2] = useState("")
  const [event, setEvent] = useState("")
  const [rounds, setRounds] = useState("3")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const youtubeValid = youtubeUrl.length > 0 && isValidYoutubeUrl(youtubeUrl)
  const youtubeInvalid = youtubeUrl.length > 10 && !isValidYoutubeUrl(youtubeUrl)
  const youtubeThumbnail = youtubeValid ? getYoutubeThumbnail(youtubeUrl) : null

  const hasSource = mode === "upload" ? !!file : youtubeValid

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!hasSource) {
      toast.error(
        mode === "upload"
          ? "Selecciona un video para subir"
          : "Introduce un enlace de YouTube valido"
      )
      return
    }
    if (!title.trim() || !mc1.trim() || !mc2.trim()) {
      toast.error("Completa los campos obligatorios")
      return
    }

    setIsSubmitting(true)

    try {
      let battleId: number

      if (mode === "upload" && file) {
        // Subir archivo
        const response = await uploadBattle(file, title, mc1, mc2, event, parseInt(rounds))
        battleId = response.id
        toast.success("Batalla subida exitosamente", {
          description: `${mc1} vs ${mc2} - procesando análisis`,
        })
      } else {
        // Subir desde YouTube
        const response = await createBattleFromYouTube(youtubeUrl, title, event || undefined)
        battleId = response.id
        toast.success("Batalla añadida desde YouTube", {
          description: `${mc1} vs ${mc2} - procesando análisis`,
        })
      }

      // Limpiar formulario
      setFile(null)
      setYoutubeUrl("")
      setTitle("")
      setMc1("")
      setMc2("")
      setEvent("")
      setRounds("3")

      // Redirigir a la página de batalla con parámetro de carga
      router.push(`/battle/${battleId}?uploading=true`)
    } catch (error) {
      setIsSubmitting(false)
      if (error instanceof ApiError) {
        toast.error("Error al subir batalla", {
          description: error.message,
        })
      } else {
        toast.error("Error desconocido", {
          description: "No se pudo procesar la solicitud",
        })
      }
    }
  }

  function handleModeSwitch(newMode: SourceMode) {
    setMode(newMode)
    // Clear the other source when switching
    if (newMode === "upload") {
      setYoutubeUrl("")
    } else {
      setFile(null)
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 lg:px-8 lg:py-14">
      <div className="flex flex-col items-center text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20">
          <Mic2 className="h-6 w-6 text-primary" />
        </div>
        <h1 className="mt-4 text-2xl font-black uppercase tracking-tight text-foreground sm:text-3xl">
          Subir Batalla
        </h1>
        <p className="mt-2 text-sm text-muted-foreground text-pretty">
          Sube un video o pega un link de YouTube para que la comunidad califique las rimas.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="mt-8 flex flex-col gap-6">
        {/* Source Mode Toggle */}
        <div className="flex rounded-xl border border-border bg-card p-1.5">
          <button
            type="button"
            onClick={() => handleModeSwitch("youtube")}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-bold uppercase tracking-wide transition-all ${
              mode === "youtube"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Link2 className="h-4 w-4" />
            Link de YouTube
          </button>
          <button
            type="button"
            onClick={() => handleModeSwitch("upload")}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-bold uppercase tracking-wide transition-all ${
              mode === "upload"
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Upload className="h-4 w-4" />
            Subir Video
          </button>
        </div>

        {/* YouTube URL Input */}
        {mode === "youtube" && (
          <Card className="border-border/60 bg-card">
            <CardContent className="flex flex-col gap-4 pt-6">
              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="youtube-url"
                  className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                >
                  URL de YouTube
                </label>
                <div className="relative">
                  <input
                    id="youtube-url"
                    type="url"
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className={`h-11 w-full rounded-lg border bg-background px-3 pr-10 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 ${
                      youtubeValid
                        ? "border-green-500/50 focus:border-green-500 focus:ring-green-500/30"
                        : youtubeInvalid
                          ? "border-destructive/50 focus:border-destructive focus:ring-destructive/30"
                          : "border-input focus:border-primary focus:ring-primary"
                    }`}
                  />
                  {youtubeValid && (
                    <CheckCircle2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-green-500" />
                  )}
                  {youtubeInvalid && (
                    <AlertCircle className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-destructive" />
                  )}
                </div>
                <p className="text-xs text-muted-foreground/60">
                  Formatos aceptados: youtube.com/watch, youtu.be, youtube.com/shorts
                </p>
              </div>

              {/* YouTube Preview Thumbnail */}
              {youtubeValid && youtubeThumbnail && (
                <div className="overflow-hidden rounded-lg border border-border">
                  <div className="relative aspect-video bg-background/50">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={youtubeThumbnail}
                      alt="Vista previa del video de YouTube"
                      className="h-full w-full object-cover"
                    />
                    <div className="absolute inset-0 flex items-center justify-center bg-background/20">
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-destructive/90 text-destructive-foreground shadow-lg">
                        <svg viewBox="0 0 24 24" fill="currentColor" className="ml-0.5 h-6 w-6">
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 border-t border-border px-3 py-2">
                    <span className="inline-flex items-center gap-1 rounded-md bg-destructive/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-destructive">
                      YouTube
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      ID: {extractYoutubeId(youtubeUrl)}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* File Upload */}
        {mode === "upload" && <UploadDropzone onFileSelect={setFile} />}

        <Separator />

        {/* Form Fields */}
        <Card className="border-border/60 bg-card">
          <CardHeader>
            <CardTitle className="text-base font-bold uppercase tracking-wide">
              Detalles de la Batalla
            </CardTitle>
            <CardDescription>
              Completa la informacion sobre el enfrentamiento
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-5">
            {/* Title */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="title" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Titulo *
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="ej. Chuty vs Aczino"
                className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                required
              />
            </div>

            {/* MCs */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="mc1" className="text-xs font-semibold uppercase tracking-wider text-mc1">
                  MC 1 *
                </label>
                <input
                  id="mc1"
                  type="text"
                  value={mc1}
                  onChange={(e) => setMc1(e.target.value)}
                  placeholder="Nombre del MC"
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:border-mc1 focus:outline-none focus:ring-1 focus:ring-mc1"
                  required
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label htmlFor="mc2" className="text-xs font-semibold uppercase tracking-wider text-mc2">
                  MC 2 *
                </label>
                <input
                  id="mc2"
                  type="text"
                  value={mc2}
                  onChange={(e) => setMc2(e.target.value)}
                  placeholder="Nombre del MC"
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:border-mc2 focus:outline-none focus:ring-1 focus:ring-mc2"
                  required
                />
              </div>
            </div>

            {/* Event + Rounds */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="event" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Evento
                </label>
                <input
                  id="event"
                  type="text"
                  value={event}
                  onChange={(e) => setEvent(e.target.value)}
                  placeholder="ej. FMS Internacional"
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground placeholder:text-muted-foreground/50 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label htmlFor="rounds" className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Rounds
                </label>
                <select
                  id="rounds"
                  value={rounds}
                  onChange={(e) => setRounds(e.target.value)}
                  className="h-10 rounded-lg border border-input bg-background px-3 text-sm text-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n} {n === 1 ? "round" : "rounds"}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        <Button
          type="submit"
          size="lg"
          disabled={isSubmitting || !hasSource}
          className="w-full font-bold uppercase tracking-wide"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              {mode === "youtube" ? "Procesando enlace..." : "Subiendo batalla..."}
            </>
          ) : (
            <>
              {mode === "youtube" ? (
                <>
                  <Link2 className="h-4 w-4" />
                  Agregar desde YouTube
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  Subir Batalla
                </>
              )}
            </>
          )}
        </Button>
      </form>
    </div>
  )
}
