import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis, ReferenceArea } from 'recharts'
import type { LoadPoint } from '../api/trainingLoad'

// ACWR risk zones (Gabbett 2016)
const UNDERTRAINING_MAX = 0.8
const SWEET_SPOT_MAX = 1.3
const DANGER_MIN = 1.5

// Y-axis never goes below this, so all zones are always visible
const Y_AXIS_MIN_TOP= 2

/** Highest ACWR in the data. Days without a value are skipped. */
function highestAcwr(points: LoadPoint[]): number {
  let highest = 0
  for (const point of points) {
    if (point.acwr !== null && point.acwr > highest) {
      highest = point.acwr
    }
  }
  return highest
}

/** Rounds up to the next 0.5 (2.3 -> 2.5), so axis ticks stay tidy. */
function roundUpToHalf(value: number): number {
  return Math.ceil(value * 2) / 2
}

type Props = { points: LoadPoint[] }

/** ACWR over time as a line chart. */
export function AcwrChart({ points }: Props) {

  const yMax = Math.max(Y_AXIS_MIN_TOP, roundUpToHalf(highestAcwr(points)))

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

      {/* Zones go before the line so the line is drawn on top */}
      <ReferenceArea y1={0} y2={UNDERTRAINING_MAX} fill="#94a3b8" fillOpacity={0.15} />
      <ReferenceArea y1={UNDERTRAINING_MAX} y2={SWEET_SPOT_MAX} fill="#22c55e" fillOpacity={0.15} />
      <ReferenceArea y1={DANGER_MIN} y2={yMax} fill="#ef4444" fillOpacity={0.15} />


      <Tooltip />
      <Line type="monotone" dataKey="acwr" stroke="#2563eb" dot={false} />
    </LineChart>
  )
}