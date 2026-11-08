import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from 'recharts'
import type { Activity } from '../api/activities'

/** Minutes spent in each HR zone, from the zone*_time fields (seconds). */
function toZoneMinutes(activity: Activity) {
  return [
    { zone: 'Zone 1', minutes: activity.zone1_time / 60 },
    { zone: 'Zone 2', minutes: activity.zone2_time / 60 },
    { zone: 'Zone 3', minutes: activity.zone3_time / 60 },
    { zone: 'Zone 4', minutes: activity.zone4_time / 60 },
    { zone: 'Zone 5', minutes: activity.zone5_time / 60 },
  ]
}

type Props = { activity: Activity }

/** Time spent in each HR zone as horizontal bars. */
export function ZoneBars({ activity }: Props) {
  return (
    <BarChart
      responsive
      style={{ width: '100%', height: 220 }}
      data={toZoneMinutes(activity)}
      layout="vertical"
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis type="number" unit=" min" />
      <YAxis type="category" dataKey="zone" width="auto" />
      <Tooltip formatter={(minutes: number) => `${Math.round(minutes)} min`} />
      <Bar dataKey="minutes" name="Time" fill="#64748b" />
    </BarChart>
  )
}