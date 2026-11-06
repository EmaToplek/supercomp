/** One activity as returned by GET /activities, matches ActivityOut in the backend schemas.py. */
export type Activity = {
  id: number
  start_time: string // ISO datetime, e.g. "2026-10-24T07:00:00Z"
  duration_s: number
  avg_hr: number
  max_hr: number
  trimp_banister: number
  trimp_edwards: number
  zone1_time: number // seconds in each HR zone
  zone2_time: number
  zone3_time: number
  zone4_time: number
  zone5_time: number
}