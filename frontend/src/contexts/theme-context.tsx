'use client'

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'

/**
 * Theme mode options
 */
export type ThemeMode = 'light' | 'dark' | 'system'

/**
 * Theme context interface
 */
interface ThemeContextType {
  /** Current theme mode preference */
  mode: ThemeMode
  /** Resolved theme (light or dark) based on mode and system preference */
  resolvedTheme: 'light' | 'dark'
  /** Set the theme mode */
  setMode: (mode: ThemeMode) => void
  /** Toggle between light and dark (ignores system) */
  toggle: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

/**
 * Storage key for theme preference
 */
const THEME_STORAGE_KEY = 'flourisha-theme-mode'

/**
 * Get system color scheme preference
 */
function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/**
 * ThemeProvider component
 * Manages theme state with system preference detection and localStorage persistence
 */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>('dark')
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('dark')
  const [mounted, setMounted] = useState(false)

  // Initialize theme from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null
    if (stored && ['light', 'dark', 'system'].includes(stored)) {
      setModeState(stored)
    }
    setMounted(true)
  }, [])

  // Resolve theme based on mode and system preference
  useEffect(() => {
    if (!mounted) return

    const resolved = mode === 'system' ? getSystemTheme() : mode
    setResolvedTheme(resolved)

    // Apply theme to document
    document.documentElement.setAttribute('data-theme', resolved)
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(resolved)

    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', resolved === 'dark' ? '#111827' : '#ffffff')
    }
  }, [mode, mounted])

  // Listen for system theme changes when in system mode
  useEffect(() => {
    if (!mounted || mode !== 'system') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      setResolvedTheme(e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [mode, mounted])

  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode)
    localStorage.setItem(THEME_STORAGE_KEY, newMode)
  }, [])

  const toggle = useCallback(() => {
    const newMode = resolvedTheme === 'dark' ? 'light' : 'dark'
    setMode(newMode)
  }, [resolvedTheme, setMode])

  const value: ThemeContextType = {
    mode,
    resolvedTheme,
    setMode,
    toggle,
  }

  // Prevent flash of wrong theme by not rendering until mounted
  if (!mounted) {
    return null
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

/**
 * Hook to access theme context
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext)

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }

  return context
}
