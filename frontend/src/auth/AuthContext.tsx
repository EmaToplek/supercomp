import { createContext } from 'react'

export type AuthState = {
  apiKey: string | null
  login: (apiKey: string) => void
  logout: () => void
}

export const AuthContext = createContext<AuthState | null>(null)