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
    <div className="page">
      <header className="site-header">
        <div className="header-top">
          <h1 className="logo">
            Super<span>comp</span>
          </h1>
          <p className="header-subtitle">Training log · Ema T.</p>
        </div>

        <nav className="nav" aria-label="Main">
          <div className="nav-links">
            <NavLink to="/" end>Load</NavLink>
            <NavLink to="/activities">Sessions</NavLink>
            {apiKey && <NavLink to="/upload">Upload</NavLink>}
          </div>
          {apiKey ? (
            <button className="link-button" onClick={logout}>Log out</button>
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
    </div>
  )
}

export default App