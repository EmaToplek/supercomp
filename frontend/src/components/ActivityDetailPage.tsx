import { Link, useParams } from 'react-router'
import type { ActivityDetail } from '../api/activities'
import { useApi } from '../hooks/useApi'
import { formatDate, formatDuration, formatNumber } from '../utils/format'
import { HeartRateChart } from './HeartRateChart'

/** Detail page for one activity, opened from /activities/:id. */
export function ActivityDetailPage() {
  const { id } = useParams()
  const activity = useApi<ActivityDetail>(`/activities/${id}`)

  if (activity.status === 'loading') return <p>Loading…</p>

  if (activity.status === 'error') {
    return (
      <p role="alert">
        Error: {activity.error} <Link to="/activities">Back to activities</Link>
      </p>
    )
  }

  const data = activity.data

  return (
    <section>
      <Link to="/activities">← Back to activities</Link>
      <h2>{formatDate(data.start_time)}</h2>

      <dl>
        <dt>Duration</dt>
        <dd>{formatDuration(data.duration_s)}</dd>
        <dt>Average HR</dt>
        <dd>{formatNumber(data.avg_hr)} bpm</dd>
        <dt>Max HR</dt>
        <dd>{formatNumber(data.max_hr)} bpm</dd>
        <dt>TRIMP</dt>
        <dd>{formatNumber(data.trimp_banister)}</dd>
      </dl>

      <h3>Heart rate</h3>
      <HeartRateChart samples={data.samples} />
    </section>
  )
}