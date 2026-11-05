import { useApi } from './hooks/useApi'

function App() {
  const health = useApi<{ status: string }>('/health')

  return (
    <main>
      <h1>Supercomp</h1>

      {health.status === 'loading' && <p>Loading…</p>}

      {health.status === 'error' && (
        <p role="alert">
          Error: {health.error} <button onClick={health.reload}>Retry</button>
        </p>
      )}

      {health.status === 'success' && <p>API: {health.data.status}</p>}
    </main>
  )
}

export default App