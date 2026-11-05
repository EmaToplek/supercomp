/** One day of training load and ACWR, matches LoadPoint in the backend schemas.py. */
export type LoadPoint = {
  day: string 
  load: number
  acute: number
  chronic: number
  acwr: number | null
  status: 'ok' | 'insufficient_data'
}