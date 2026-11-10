import { useState, type ChangeEvent, type DragEvent } from 'react'
import type { Activity } from '../api/activities'
import { ApiError, uploadActivity } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { Link } from 'react-router'
import { formatDate, formatDuration, formatNumber } from '../utils/format'

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; fileName: string }
  | { status: 'done'; activity: Activity }
  | { status: 'error'; message: string }

/** Short summary of what the backend calculated for the uploaded activity. */
function UploadResult({ activity }: { activity: Activity }) {
  const zones = [
    activity.zone1_time,
    activity.zone2_time,
    activity.zone3_time,
    activity.zone4_time,
    activity.zone5_time,
  ]

  return (
    <div>
      <h3>Upload successful</h3>
      <dl>
        <dt>Date</dt>
        <dd>{formatDate(activity.start_time)}</dd>
        <dt>Duration</dt>
        <dd>{formatDuration(activity.duration_s)}</dd>
        <dt>Avg HR</dt>
        <dd>{formatNumber(activity.avg_hr)}</dd>
        <dt>TRIMP (Banister)</dt>
        <dd>{formatNumber(activity.trimp_banister)}</dd>
        <dt>TRIMP (Edwards)</dt>
        <dd>{formatNumber(activity.trimp_edwards)}</dd>
      </dl>

      <ul>
        {zones.map((seconds, i) => (
          <li key={i}>
            Zone {i + 1}: {formatDuration(seconds)}
          </li>
        ))}
      </ul>

      <Link to={`/activities/${activity.id}`}>Show details</Link>
    </div>
  )
}

/** Upload page for FIT files: drag & drop or file picker. */
export function UploadPage() {
  const { apiKey, logout } = useAuth()
  const [dragging, setDragging] = useState(false)
  const [state, setState] = useState<UploadState>({ status: 'idle' })

  const upload = async (file: File) => {
    if (state.status === 'uploading' || !apiKey) return

    if (!file.name.toLowerCase().endsWith('.fit')) {
      setState({ status: 'error', message: 'Only .fit files are supported' })
      return
    }

    setState({ status: 'uploading', fileName: file.name })
    try {
      const activity = await uploadActivity(file, apiKey)
      setState({ status: 'done', activity })
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout()
        return
      }
      setState({ status: 'error', message: err instanceof Error ? err.message : 'Unknown error' })
    }
  }

  const handleDragOver = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault() 
    setDragging(true)
  }

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files[0]
    if (file) upload(file)
  }

  const handlePick = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) upload(file)
    event.target.value = '' 
  }

  return (
    <section>
      <h2>Upload activity</h2>

      <label
        className={dragging ? 'dropzone dragging' : 'dropzone'}
        onDragOver={handleDragOver}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input type="file" accept=".fit" onChange={handlePick} hidden />
        {state.status === 'uploading'
          ? `Uploading ${state.fileName}…`
          : 'Drop a .fit file here or click to choose one'}
      </label>

      {state.status === 'error' && <p role="alert">{state.message}</p>}
      {state.status === 'done' && <UploadResult activity={state.activity} />}
    </section>
  )
}