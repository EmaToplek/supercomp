import { NavLink, Route, Routes } from 'react-router'
import { ActivityDetailPage } from './components/ActivityDetailPage'
import { ActivityList } from './components/ActivityList'
import { TrainingLoad } from './components/TrainingLoad'

function App() {
  return (
    <>
      <header>
        <h1>Supercomp</h1>
        <nav>
          <NavLink to="/" end>Training load</NavLink>
          {' | '}
          <NavLink to="/activities">Activities</NavLink>
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<TrainingLoad />} />
          <Route path="/activities" element={<ActivityList />} />
          <Route path="/activities/:id" element={<ActivityDetailPage />} />
        </Routes>
      </main>
    </>
  )
}

export default App