import type { LoadPoint } from '../api/trainingLoad'
import { useApi } from '../hooks/useApi'
import { AcwrChart } from './AcwrChart'
import { LoadBars } from './LoadBars'

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

  return (
    <section>
      <h2>Acute:Chronic Workload Ratio</h2>
      <AcwrChart points={load.data} />

      <h3>Daily load (TRIMP)</h3>
      <LoadBars points={load.data} />

    </section>
  )
}