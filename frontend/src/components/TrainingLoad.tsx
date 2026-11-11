import type { LoadPoint } from '../api/trainingLoad'
import { useApi } from '../hooks/useApi'
import { AcwrChart } from './AcwrChart'
import { LoadBars } from './LoadBars'
import { LoadSummary } from './LoadSummary'

/** True if at least one day has an ACWR value (needs about 4 weeks of history). */
function hasAcwrData(points: LoadPoint[]): boolean {
  return points.some((point) => point.status === 'ok')
} 


/** Loads /load and shows the ACWR chart. */
export function TrainingLoad() {
  const load = useApi<LoadPoint[]>('/load')

  if (load.status === 'loading') return <p>Loading…</p>

  if (load.status === 'error') {
    return (
      <p role="alert">
        Error: {load.error} <button onClick={load.reload}>Retry</button>
      </p>
    )
  }

  const points = load.data

  if (points.length === 0) {
    return <p>No activities yet. Upload a FIT file to see your training load.</p>
  }

  return (
    <>
      <LoadSummary points={points} />
      <section>
        <h2>Acute:Chronic Workload Ratio</h2>
          {hasAcwrData(points) ? (
            <AcwrChart points={points} />
          ) : (
            <p>Insufficient data: ACWR needs about 4 weeks of training history.</p>
          )}

        <h3>Daily load (TRIMP)</h3>
        <LoadBars points={points} />
      </section>
    </>
  )
}