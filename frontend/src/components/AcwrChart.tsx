import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts'
import type { LoadPoint } from '../api/trainingLoad'

type Props = { points: LoadPoint[] }

/** ACWR over time as a line chart. */
export function AcwrChart({ points }: Props) {
  return (
    <LineChart
      responsive
      style={{ width: '100%', height: 300 }}
      data={points}
      syncId="training-load"
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="day" tickFormatter={(day: string) => day.slice(5)} />
      <YAxis width="auto" domain={[0, 2]} />
      <Tooltip />
      <Line type="monotone" dataKey="acwr" stroke="#2563eb" dot={false} />
    </LineChart>
  )
}