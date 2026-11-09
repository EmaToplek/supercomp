import { useState, type SubmitEvent } from 'react'
import { useNavigate } from 'react-router'
import { checkApiKey } from '../api/client'
import { useAuth } from '../auth/useAuth'

/** Form where the owner enters the API key to unlock uploads. */
export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [key, setKey] = useState('')
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: SubmitEvent) => {
    event.preventDefault()
    setChecking(true)
    setError(null)

    try {
      if (await checkApiKey(key)) {
        login(key)
        navigate('/upload')
      } else {
        setError('Invalid API key')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setChecking(false)
    }
  }

  return (
    <section>
      <h2>Owner login</h2>
      <p>Uploading activities is only available to the owner of this demo.</p>

      <form onSubmit={handleSubmit}>
        <label>
          API key{' '}
          <input
            type="password"
            value={key}
            onChange={(event) => setKey(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>{' '}
        <button type="submit" disabled={checking}>
          {checking ? 'Checking…' : 'Log in'}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}
    </section>
  )
}