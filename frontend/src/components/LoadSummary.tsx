import type { LoadPoint } from '../api/trainingLoad'

/** Short text label for where an ACWR value sits. */
function acwrLabel(acwr: number): string {
  if (acwr < 0.8) return 'below 0.8 · low load'
  if (acwr <= 1.3) return 'within 0.8–1.3'
  if (acwr <= 1.5) return 'above 1.3 · careful'
  return 'above 1.5 · spike'
}

/** Summary above the charts: since when data exists, today's ACWR and load. */
export function LoadSummary({ points }: { points: LoadPoint[] }) {
  const latest = points[points.length - 1]
  const trainingDays = points.filter((point) => point.load > 0).length
  const restDays = points.length - trainingDays

  // "day" is a plain date string, read it as UTC so it never shifts a day
  const since = new Date(points[0].day).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    timeZone: 'UTC',
  })

  return (
    <div className="summary">
      <div className="lead">
        <p>
          Training logged since <mark>{since}</mark>: {points.length} days, {trainingDays} of them
          with training.
        </p>
        {latest.acwr === null && (
          <p className="lead-note">
            ACWR compares the last 7 days to the last 28, so it starts once there are 4 weeks of
            data.
          </p>
        )}
      </div>

      <div className="acwr-box">
        <span className="acwr-label">ACWR today</span>
        <span className="acwr-value">{latest.acwr === null ? '–' : latest.acwr.toFixed(2)}</span>
        <span className="acwr-label">
          {latest.acwr === null ? 'not enough data yet' : acwrLabel(latest.acwr)}
        </span>
      </div>

      <dl className="stats">
        <div>
          <dt>acute</dt>
          <dd>{latest.acute.toFixed(1)}</dd>
        </div>
        <div>
          <dt>chronic</dt>
          <dd>{latest.chronic.toFixed(1)}</dd>
        </div>
        <div>
          <dt>training days</dt>
          <dd>{trainingDays}</dd>
        </div>
        <div>
          <dt>rest days</dt>
          <dd>{restDays}</dd>
        </div>
      </dl>
    </div>
  )
}