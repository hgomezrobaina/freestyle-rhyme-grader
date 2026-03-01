"use client"

import { useRef, useImperativeHandle, forwardRef, useState, useCallback } from "react"
import { Play, Volume2, VolumeX, Maximize } from "lucide-react"
import type { Battle } from "@/lib/types/battle"
import { getYoutubeEmbedUrl } from "@/lib/youtube"

export type VideoPlayerHandle = {
  seekTo: (seconds: number) => void
  getCurrentTime: () => number
}

const VideoPlayer = forwardRef<VideoPlayerHandle, { battle: Battle }>(
  function VideoPlayer({ battle }, ref) {
    const videoRef = useRef<HTMLVideoElement>(null)
    const iframeRef = useRef<HTMLIFrameElement>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [isMuted, setIsMuted] = useState(false)

    const isYoutube = !!battle.youtubeUrl
    const embedUrl = battle.youtubeUrl
      ? getYoutubeEmbedUrl(battle.youtubeUrl)
      : null

    const seekYoutube = useCallback((seconds: number) => {
      if (iframeRef.current?.contentWindow) {
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({
            event: "command",
            func: "seekTo",
            args: [seconds, true],
          }),
          "*"
        )
        iframeRef.current.contentWindow.postMessage(
          JSON.stringify({
            event: "command",
            func: "playVideo",
            args: [],
          }),
          "*"
        )
      }
    }, [])

    useImperativeHandle(ref, () => ({
      seekTo(seconds: number) {
        if (isYoutube) {
          seekYoutube(seconds)
        } else if (videoRef.current) {
          videoRef.current.currentTime = seconds
          videoRef.current.play().catch(() => {})
          setIsPlaying(true)
        }
      },
      getCurrentTime() {
        return videoRef.current?.currentTime ?? 0
      },
    }))

    function togglePlay() {
      if (!videoRef.current) return
      if (videoRef.current.paused) {
        videoRef.current.play().catch(() => {})
        setIsPlaying(true)
      } else {
        videoRef.current.pause()
        setIsPlaying(false)
      }
    }

    function toggleMute() {
      if (!videoRef.current) return
      videoRef.current.muted = !videoRef.current.muted
      setIsMuted(!isMuted)
    }

    function toggleFullscreen() {
      if (isYoutube && iframeRef.current) {
        iframeRef.current.requestFullscreen()
        return
      }
      if (!videoRef.current) return
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        videoRef.current.requestFullscreen()
      }
    }

    // YouTube embed
    if (isYoutube && embedUrl) {
      const embedWithApi = embedUrl + "&enablejsapi=1&origin=" + (typeof window !== "undefined" ? window.location.origin : "")

      return (
        <div className="relative overflow-hidden rounded-xl border border-border bg-card">
          <div className="relative aspect-video bg-background/50">
            <iframe
              ref={iframeRef}
              src={embedWithApi}
              className="h-full w-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
              title={battle.title}
            />
          </div>
          <div className="flex items-center justify-between border-t border-border px-4 py-2">
            <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
              <span className="inline-flex items-center gap-1.5 rounded-md bg-destructive/10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-destructive">
                YouTube
              </span>
              {battle.event}
            </div>
            <button
              onClick={toggleFullscreen}
              className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              aria-label="Pantalla completa"
            >
              <Maximize className="h-4 w-4" />
            </button>
          </div>
        </div>
      )
    }

    // Native video or fallback placeholder
    return (
      <div className="relative overflow-hidden rounded-xl border border-border bg-card">
        <div className="relative aspect-video bg-background/50">
          <video
            ref={videoRef}
            className="h-full w-full object-cover"
            src={battle.videoUrl || undefined}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            playsInline
          />

          {!battle.videoUrl && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-primary/10 via-background to-accent/10">
              <div className="flex items-center gap-6">
                <div className="flex flex-col items-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-mc1/20 text-3xl font-black text-mc1 ring-2 ring-mc1/30">
                    {battle.mc1.avatar}
                  </div>
                  <span className="mt-2 text-sm font-bold uppercase text-foreground">{battle.mc1.name}</span>
                </div>
                <span className="text-2xl font-black text-muted-foreground">VS</span>
                <div className="flex flex-col items-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-mc2/20 text-3xl font-black text-mc2 ring-2 ring-mc2/30">
                    {battle.mc2.avatar}
                  </div>
                  <span className="mt-2 text-sm font-bold uppercase text-foreground">{battle.mc2.name}</span>
                </div>
              </div>
              <p className="mt-4 text-xs text-muted-foreground">Video no disponible - Vista de demo</p>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between border-t border-border px-4 py-2">
          <div className="flex items-center gap-2">
            <button
              onClick={togglePlay}
              className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              aria-label={isPlaying ? "Pausar" : "Reproducir"}
            >
              <Play className={`h-4 w-4 ${isPlaying ? "text-primary" : ""}`} />
            </button>
            <button
              onClick={toggleMute}
              className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              aria-label={isMuted ? "Activar sonido" : "Silenciar"}
            >
              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
            </button>
          </div>
          <div className="text-xs font-medium text-muted-foreground">
            {battle.event}
          </div>
          <button
            onClick={toggleFullscreen}
            className="flex h-8 w-8 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            aria-label="Pantalla completa"
          >
            <Maximize className="h-4 w-4" />
          </button>
        </div>
      </div>
    )
  }
)

export { VideoPlayer }
