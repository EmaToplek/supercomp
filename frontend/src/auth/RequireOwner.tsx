import type { ReactNode } from 'react'
import { Navigate } from 'react-router'
import { useAuth } from './useAuth'

/** Shows its children only to the logged-in owner, otherwise redirects to /login. */
export function RequireOwner({ children }: { children: ReactNode }) {
  const { apiKey } = useAuth()
  if (!apiKey) return <Navigate to="/login" replace />
  return children
}