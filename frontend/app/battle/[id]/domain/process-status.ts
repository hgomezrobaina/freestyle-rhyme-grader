export enum ProcessStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

export enum PipelineStep {
  DOWNLOAD = "download",
  TRANSCRIBE = "transcribe",
  SEPARATE = "separate",
  DIARIZE = "diarize",
  ANALYZE = "analyze",
}
