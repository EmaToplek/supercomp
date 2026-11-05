import { useEffect, useState } from 'react'
import { apiGet } from '../api/client'

type State<T> =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: T }

/** Fetches data from the API and tracks loading, error and success states. */
export function useApi<T>(path: string) {
  const [state, setState] = useState<State<T>>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
  
    apiGet<T>(path, controller.signal)
      .then((data) => setState({ status: 'success', data }))
      .catch((err) => {
        if (controller.signal.aborted) return
        setState({ status: 'error', error: err instanceof Error ? err.message : 'Unknown error' })
      })
    return () => controller.abort()
  }, [path, reloadKey])
  
  /** Shows the loading state and fetches the data again, e.g. from a Retry button. */
  const reload = () => {
    setState({ status: 'loading' })
    setReloadKey((k) => k + 1)
  }

  return { ...state, reload }
}