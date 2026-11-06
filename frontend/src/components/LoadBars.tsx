import { Bar, BarChart, Tooltip, XAxis, YAxis } from 'recharts'
import type { LoadPoint } from '../api/trainingLoad'

type Props = { points: LoadPoint[] }

/** Daily training load (TRIMP) as bars, synced with the ACWR chart. */
export function LoadBars({ points }: Props) {
  return (
    <BarChart
      responsive
      style={{ width: '100%', height: 150 }}
      data={points}
      syncId="training-load"
    >
      <XAxis dataKey="day" tickFormatter={(day: string) => day.slice(5)} />
      <YAxis width="auto" />
      <Tooltip />
      <Bar dataKey="load" name="TRIMP" fill="#64748b" />
    </BarChart>
  )
}