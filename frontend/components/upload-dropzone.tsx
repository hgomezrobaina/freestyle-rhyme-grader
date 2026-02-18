"use client"

import { useState, useRef, type DragEvent } from "react"
import { Upload, X, Film } from "lucide-react"
import { cn } from "@/lib/utils"

export function UploadDropzone({
  onFileSelect,
}: {
  onFileSelect: (file: File | null) => void
}) {
  const [isDragging, setIsDragging] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function handleFile(file: File) {
    if (!file.type.startsWith("video/")) return
    setFileName(file.name)
    const url = URL.createObjectURL(file)
    setPreview(url)
    onFileSelect(file)
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault()
    setIsDragging(true)
  }

  function handleDragLeave() {
    setIsDragging(false)
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  function clear() {
    if (preview) URL.revokeObjectURL(preview)
    setPreview(null)
    setFileName(null)
    onFileSelect(null)
    if (inputRef.current) inputRef.current.value = ""
  }

  if (preview) {
    return (
      <div className="relative overflow-hidden rounded-xl border border-border bg-card">
        <video
          src={preview}
          className="aspect-video w-full object-cover"
          controls
        />
        <div className="flex items-center justify-between border-t border-border px-4 py-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Film className="h-4 w-4" />
            <span className="max-w-[200px] truncate">{fileName}</span>
          </div>
          <button
            onClick={clear}
            className="flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-destructive transition-colors hover:bg-destructive/10"
          >
            <X className="h-3 w-3" />
            Quitar
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "group flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all",
        isDragging
          ? "border-primary bg-primary/5"
          : "border-border bg-card hover:border-primary/40 hover:bg-primary/5"
      )}
      role="button"
      tabIndex={0}
      aria-label="Subir video"
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") inputRef.current?.click()
      }}
    >
      <div
        className={cn(
          "flex h-14 w-14 items-center justify-center rounded-full transition-colors",
          isDragging ? "bg-primary/20 text-primary" : "bg-secondary text-muted-foreground group-hover:bg-primary/20 group-hover:text-primary"
        )}
      >
        <Upload className="h-6 w-6" />
      </div>
      <p className="mt-4 text-sm font-medium text-foreground">
        Arrastra tu video aqui
      </p>
      <p className="mt-1 text-xs text-muted-foreground">
        o haz clic para seleccionar un archivo
      </p>
      <p className="mt-2 text-xs text-muted-foreground/60">
        MP4, WebM, MOV (max 500MB)
      </p>
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        onChange={handleChange}
        className="hidden"
        aria-hidden="true"
      />
    </div>
  )
}
