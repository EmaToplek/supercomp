import { NavLink, Route, Routes } from 'react-router'
import { RequireOwner } from './auth/RequireOwner'
import { useAuth } from './auth/useAuth'
import { ActivityDetailPage } from './components/ActivityDetailPage'
import { ActivityList } from './components/ActivityList'
import { LoginPage } from './components/LoginPage'
import { TrainingLoad } from './components/TrainingLoad'
import { UploadPage } from './components/UploadPage'

function App() {
  const { apiKey, logout } = useAuth()

  return (
    <>
      <header>
        <h1>Supercomp</h1>
        <nav>
          <NavLink to="/" end>Training load</NavLink>
          {' | '}
          <NavLink to="/activities">Activities</NavLink>
          {' | '}
          {apiKey ? (
            <>
              <NavLink to="/upload">Upload</NavLink>
              {' | '}
              <button onClick={logout}>Log out</button>
            </>
          ) : (
            <NavLink to="/login">Owner login</NavLink>
          )}
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<TrainingLoad />} />
          <Route path="/activities" element={<ActivityList />} />
          <Route path="/activities/:id" element={<ActivityDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/upload"
            element={
              <RequireOwner>
                <UploadPage />
              </RequireOwner>
            }
          />
        </Routes>
      </main>
    </>
  )
}

export default App