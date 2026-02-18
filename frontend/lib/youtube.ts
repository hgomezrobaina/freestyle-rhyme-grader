/**
 * Extracts a YouTube video ID from various URL formats:
 * - https://www.youtube.com/watch?v=VIDEO_ID
 * - https://youtu.be/VIDEO_ID
 * - https://www.youtube.com/embed/VIDEO_ID
 * - https://youtube.com/shorts/VIDEO_ID
 */
export function extractYoutubeId(url: string): string | null {
  if (!url) return null

  const patterns = [
    /(?:youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})/,
    /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    /(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})/,
  ]

  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match?.[1]) return match[1]
  }

  return null
}

export function getYoutubeEmbedUrl(url: string, start?: number): string | null {
  const id = extractYoutubeId(url)
  if (!id) return null
  const params = new URLSearchParams({
    rel: "0",
    modestbranding: "1",
  })
  if (start && start > 0) {
    params.set("start", String(Math.floor(start)))
  }
  return `https://www.youtube.com/embed/${id}?${params.toString()}`
}

export function getYoutubeThumbnail(url: string): string | null {
  const id = extractYoutubeId(url)
  if (!id) return null
  return `https://img.youtube.com/vi/${id}/hqdefault.jpg`
}

export function isValidYoutubeUrl(url: string): boolean {
  return extractYoutubeId(url) !== null
}
