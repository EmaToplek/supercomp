import { Bar, BarChart, Tooltip, XAxis, YAxis } from 'recharts'
import type { LoadPoint } from '../api/trainingLoad'
import { axisTick, colors, formatDay, formatValue, tooltipStyle } from '../chartTheme'

type Props = { days: LoadPoint[] }

/** Daily training load (TRIMP) as bars, synced with the ACWR chart. */
export function LoadBars({ days }: Props) {
  return (
    <BarChart
      responsive
      style={{ width: '100%', height: 150 }}
      data={days}
      syncId="training-load"
    >
      <XAxis
          dataKey="day"
          tickFormatter={formatDay}
          tick={axisTick}
          tickLine={false}
          axisLine={{ stroke: colors.ink }}
          minTickGap={24}
      />
      <YAxis width="auto" tick={axisTick} tickLine={false} axisLine={{ stroke: colors.ink }} />
      <Tooltip
        {...tooltipStyle}
        cursor={{ fill: colors.ink, fillOpacity: 0.06 }}
        labelFormatter={(day) => formatDay(String(day))}
        formatter={formatValue}
      />
      <Bar dataKey="load" name="TRIMP" fill={colors.bar} activeBar={{ fill: colors.yellow }} />
    </BarChart>
  )
}