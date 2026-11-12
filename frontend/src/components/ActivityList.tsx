import type { Activity } from '../api/activities'
import { useApi } from '../hooks/useApi'
import { formatDate, formatDuration, formatNumber} from '../utils/format'
import { Link } from 'react-router'

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
    return <p className='muted'>No activities yet.</p>
  }

  return (
    <section>
      <h2>Sessions</h2>
      <div className="table-wrap">
        <table className="log">
          <thead>
            <tr>
              <th>date</th>
              <th className="num">time</th>
              <th className="num">avg hr</th>
              <th className="num">trimp</th>
            </tr>
          </thead>
          <tbody>
            {activities.data.map((activity) => (
              <tr key={activity.id}>
                <td>
                  <Link to={`/activities/${activity.id}`}>{formatDate(activity.start_time)}</Link>
                </td>
                <td className="num">{formatDuration(activity.duration_s)}</td>
                <td className="num">{formatNumber(activity.avg_hr)}</td>
                <td className="num">{formatNumber(activity.trimp_banister)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}