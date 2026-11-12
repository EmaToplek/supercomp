import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis, ReferenceArea, ReferenceLine } from 'recharts'
import type { LoadPoint } from '../api/trainingLoad'
import { axisTick, colors, formatDay, formatValue, tooltipStyle } from '../chartTheme'

// ACWR risk zones (Gabbett 2016)
const SWEET_SPOT_MIN = 0.8
const SWEET_SPOT_MAX = 1.3
const DANGER_MIN = 1.5

// Y-axis never goes below this, so the danger line at 1.5 is always visible
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

/** Ticks every 0.5 from 0 up to max: [0, 0.5, 1, ...]. */
function halfSteps(max: number): number[] {
  const ticks = []
  for (let tick = 0; tick <= max; tick += 0.5) {
    ticks.push(tick)
  }
  return ticks
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
      <CartesianGrid vertical={false} stroke={colors.faint} strokeDasharray="2 4" />
      <XAxis 
        dataKey="day"
        tickFormatter={formatDay}
        tick={axisTick}
        tickLine={false}
        axisLine={{ stroke: colors.ink }}
        minTickGap={24}
      />

      <YAxis 
        width="auto"
        domain={[0, yMax]}
        ticks={halfSteps(yMax)}
        tick={axisTick}
        tickLine={false}
        axisLine={{ stroke: colors.ink }}
      />

      {/* Zones go before the line so the line is drawn on top */}
      <ReferenceArea 
        y1={SWEET_SPOT_MIN}   
        y2={SWEET_SPOT_MAX} 
        fill={colors.yellow} 
        fillOpacity={0.35}
      />
      <ReferenceLine
        y={DANGER_MIN}
        stroke={colors.ink}
        strokeDasharray="4 4"
        label={{ value: 'spike 1.5', position: 'insideTopLeft', ...axisTick }}
      />
      
      <Tooltip
        {...tooltipStyle}
        cursor={{ stroke: colors.ink }}
        labelFormatter={(day) => formatDay(String(day))}
        formatter={formatValue}
      />
      <Line
        type="monotone"
        dataKey="acwr"
        name="ACWR"
        stroke={colors.ink}
        strokeWidth={2}
        dot={false}
        activeDot={{ r: 5, fill: colors.yellow, stroke: colors.ink, strokeWidth: 2 }}
      />
    </LineChart>
  )
} 