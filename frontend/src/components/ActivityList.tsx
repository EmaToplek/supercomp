import type { Activity } from '../api/activities'
import { useApi } from '../hooks/useApi'
import { formatDate, formatDuration } from '../utils/format'

/** Loads /activities and shows them as a table. */
export function ActivityList() {
  const activities = useApi<Activity[]>('/activities')

  if (activities.status === 'loading') return <p>Loading…</p>

  if (activities.status === 'error') {
    return (
      <p role="alert">
        Error: {activities.error} <button onClick={activities.reload}>Retry</button>
      </p>
    )
  }

  if (activities.data.length === 0) {
    return <p>No activities yet.</p>
  }

  return (
    <section>
      <h2>Activities</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Duration</th>
            <th>TRIMP</th>
          </tr>
        </thead>
        <tbody>
          {activities.data.map((activity) => (
            <tr key={activity.id}>
              <td>{formatDate(activity.start_time)}</td>
              <td>{formatDuration(activity.duration_s)}</td>
              <td>{Math.round(activity.trimp_banister)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}