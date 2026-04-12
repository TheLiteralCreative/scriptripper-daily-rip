import { Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Subscriptions from './pages/Subscriptions'
import RipLibrary from './pages/RipLibrary'
import UserProfile from './pages/UserProfile'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/subscriptions" element={<Subscriptions />} />
      <Route path="/rips" element={<RipLibrary />} />
      <Route path="/profile" element={<UserProfile />} />
      <Route path="/settings" element={<Settings />} />
    </Routes>
  )
}
