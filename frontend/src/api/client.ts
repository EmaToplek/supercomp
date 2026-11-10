import type { Activity } from './activities'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'


/** Builds an ApiError from a failed response, using FastAPI's detail message if there is one. */
async function toApiError(res: Response): Promise<ApiError> {
  const body = await res.json().catch(() => null)
  const message = typeof body?.detail === 'string' ? body.detail : res.statusText
  return new ApiError(res.status, message)
}

/** Error thrown for failed API calls. status is 0 when the server is unreachable. */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/** Sends a GET request to the backend and returns the parsed JSON as type T. */
export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}${path}`, { signal })
  } catch (err) {
    if (signal?.aborted) throw err
    throw new ApiError(0, 'Server not reachable')
  }

  if (!res.ok) throw await toApiError(res)

  return res.json() as Promise<T>
}

/** Asks the backend whether the API key is valid. */
export async function checkApiKey(apiKey: string): Promise<boolean> {
  let res: Response
  try {
    res = await fetch(`${BASE_URL}/auth/check`, { headers: { 'X-API-Key': apiKey } })
  } catch {
    throw new ApiError(0, 'Server not reachable')
  }

  if (res.status === 401) return false
  if (!res.ok) throw await toApiError(res)
  return true
}

/** Uploads one FIT file. Only works with the owner's API key. */
export async function uploadActivity(file: File, apiKey: string): Promise<Activity> {
  const form = new FormData()
  form.append('file', file) 

  let res: Response
  try {
    res = await fetch(`${BASE_URL}/activities/upload`, {
      method: 'POST',
      headers: { 'X-API-Key': apiKey },
      body: form,
    })
  } catch {
    throw new ApiError(0, 'Server not reachable')
  }

  if (!res.ok) throw await toApiError(res)
  return res.json()
}