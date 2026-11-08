/** Formats an ISO datetime as a short date, e.g. "24 Oct 2026". */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

/** Formats seconds as "36 min" or "1 h 3 min". */
export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / 60)
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  if (hours === 0) return `${minutes} min`
  return `${hours} h ${minutes} min`
}

/** Rounds a number for display, or shows a dash when the value is missing. */
export function formatNumber(value: number | null): string {
  if (value === null) return '–'
  return String(Math.round(value))
}

/** Formats minutes as mm:ss, e.g. 32.78 -> "32:47". */
export function formatMinutes(minutes: number): string {
  const totalSeconds = Math.round(minutes * 60)
  const mm = Math.floor(totalSeconds / 60)
  const ss = String(totalSeconds % 60).padStart(2, '0')
  return `${mm}:${ss}`
}