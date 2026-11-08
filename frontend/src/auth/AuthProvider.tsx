import { useState, type ReactNode } from 'react'
import { AuthContext } from './AuthContext'

const STORAGE_KEY = 'supercomp-api-key'

/** Reads the saved key. Storage can be unavailable (e.g. private mode), which means "not logged in". */
function readSavedKey(): string | null {
  try {
    return sessionStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

/** Keeps the owner's API key for this browser tab and shares it with all components. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKey] = useState<string | null>(readSavedKey)

  const login = (key: string) => {
    setApiKey(key)
    try {
      sessionStorage.setItem(STORAGE_KEY, key)
    } catch {
      // Storage not available, the key stays in memory only
    }
  }

  const logout = () => {
    setApiKey(null)
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // Nothing was saved
    }
  }

  return <AuthContext.Provider value={{ apiKey, login, logout }}>{children}</AuthContext.Provider>
}