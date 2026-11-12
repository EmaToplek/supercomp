import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts'
import type { Sample } from '../api/activities'
import { formatMinutes } from '../utils/format'
import { axisTick, colors, tooltipStyle } from '../chartTheme'

type ChartPoint = { minute: number; heartRate: number | null }

/** Converts raw samples to minutes since start, for the x-axis. */
function toChartPoints(samples: Sample[]): ChartPoint[] {
  if (samples.length === 0) return []

  const start = new Date(samples[0].timestamp).getTime()
  return samples.map((sample) => ({
    minute: (new Date(sample.timestamp).getTime() - start) / 60_000,
    heartRate: sample.heart_rate,
  }))
}

type Props = { samples: Sample[] }

/** Heart rate over the course of one activity. */
export function HeartRateChart({ samples }: Props) {
  const points = toChartPoints(samples)
  const hasHeartRate = points.some((point) => point.heartRate !== null)

  if (!hasHeartRate) return <p>No heart rate data for this activity.</p>

  return (
    <LineChart responsive style={{ width: '100%', height: 300 }} data={points}>
      <CartesianGrid vertical={false} stroke={colors.faint} strokeDasharray="2 4" />
      <XAxis
        dataKey="minute"
        type="number"
        domain={['dataMin', 'dataMax']}
        tickFormatter={(minute: number) => `${Math.round(minute)} min`}
        tick={axisTick}
        tickLine={false}
        axisLine={{ stroke: colors.ink }}
      />
      <YAxis
        width="auto"
        domain={['dataMin - 10', 'dataMax + 10']}
        unit=" bpm"
        tick={axisTick}
        tickLine={false}
        axisLine={{ stroke: colors.ink }}
      />
      <Tooltip
        {...tooltipStyle}
        separator=": "
        cursor={{ stroke: colors.ink }}
        labelFormatter={(minute) => formatMinutes(Number(minute))}
        formatter={(value) => `${Math.round(Number(value))} bpm`}
      />
      <Line
        type="monotone"
        dataKey="heartRate"
        name="Heart rate"
        stroke={colors.ink}
        strokeWidth={1.5}
        dot={false}
        activeDot={{ r: 5, fill: colors.yellow, stroke: colors.ink, strokeWidth: 2 }}
        isAnimationActive={false}
      />
    </LineChart>
  )
}