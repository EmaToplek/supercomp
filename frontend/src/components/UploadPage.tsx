import { useState, type ChangeEvent, type DragEvent } from 'react'
import type { Activity } from '../api/activities'
import { ApiError, uploadActivity } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { Link } from 'react-router'
import { formatDate, formatDuration, formatNumber } from '../utils/format'
import { ZoneBars } from './ZoneBars'

type UploadState =
  | { status: 'idle' }
  | { status: 'uploading'; fileName: string }
  | { status: 'done'; activity: Activity }
  | { status: 'error'; message: string }

/** Short summary of what the backend calculated for the uploaded activity. */
function UploadResult({ activity }: { activity: Activity }) {
  return (
    <div className='upload-result'>
      <h3>Upload · {formatDate(activity.start_time)}</h3>

      <dl className='stats'>
        <div>
          <dt>Duration</dt>
          <dd>{formatDuration(activity.duration_s)}</dd>
        </div>
        <div>
          <dt>Avg HR</dt>
          <dd>{formatNumber(activity.avg_hr)}</dd>
        </div>
        <div>
          <dt>TRIMP (Banister)</dt>
          <dd>{formatNumber(activity.trimp_banister)}</dd>
        </div>
        <div>
          <dt>TRIMP (Edwards)</dt>
          <dd>{formatNumber(activity.trimp_edwards)}</dd>
        </div>
      </dl>
      
      <ZoneBars activity={activity} />
      <Link to={`/activities/${activity.id}`}>Show details →</Link>
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
        <input type="file" accept=".fit" onChange={handlePick} className="visually-hidden" />
        <span className="dropzone-title">
          {state.status === 'uploading'
            ? `Uploading ${state.fileName}…`
            : 'Drop a .fit file here or click to choose one'}
        </span>
        <span className="dropzone-hint">Garmin export · one activity per file</span>
      </label>

      {state.status === 'error' && <p role="alert" className="alert">{state.message}</p>}
      {state.status === 'done' && <UploadResult activity={state.activity} />}
    </section>
  )
}