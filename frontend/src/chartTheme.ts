/** Shared colours and formatters for Recharts. */

export const colors = {
  ink: '#111111',
  paper: '#f1f0ec',
  grey: '#5c5a55',
  faint: '#cfcdc6',
  bar: '#9b9890',
  yellow: '#ffd400',
}

export const axisTick = {
  fill: colors.grey,
  fontSize: 11,
  fontFamily: 'IBM Plex Mono, monospace',
}

export const tooltipStyle = {
  contentStyle: {
    background: colors.ink,
    border: 'none',
    borderRadius: 0,
    fontFamily: 'IBM Plex Mono, monospace',
    fontSize: 12,
  },
  labelStyle: { color: '#c9c7c0' },
  itemStyle: { color: colors.paper },
}

/** "2026-10-14" -> "14 Oct". Read as UTC so the date never shifts a day. */
export function formatDay(day: string): string {
  return new Date(day).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    timeZone: 'UTC',
  })
}

/** Numbers in the tooltip with two decimals */
export function formatValue(value: unknown): string {
  return typeof value === 'number' ? value.toFixed(2) : String(value ?? '–')
}