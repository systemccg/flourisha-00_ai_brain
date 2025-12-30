'use client'

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  type ReactNode,
} from 'react'
import {
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  sendPasswordResetEmail,
  type User as FirebaseUser,
} from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { api, endpoints } from '@/lib/api'
import type { User } from '@/types'

/**
 * Auth state interface
 */
interface AuthState {
  user: User | null
  firebaseUser: FirebaseUser | null
  loading: boolean
  error: string | null
}

/**
 * Auth context interface
 */
interface AuthContextType extends AuthState {
  signIn: (email: string, password: string) => Promise<void>
  signInWithGoogle: () => Promise<void>
  signOut: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * Google OAuth provider instance
 */
const googleProvider = new GoogleAuthProvider()
googleProvider.addScope('email')
googleProvider.addScope('profile')

/**
 * AuthProvider component
 * Manages Firebase authentication state and provides auth methods
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    firebaseUser: null,
    loading: true,
    error: null,
  })

  /**
   * Fetch user profile from backend after Firebase auth
   */
  const fetchUserProfile = useCallback(async (firebaseUser: FirebaseUser): Promise<User | null> => {
    try {
      // Get Firebase ID token
      const token = await firebaseUser.getIdToken()

      // Store token for API requests
      localStorage.setItem('auth_token', token)

      // Fetch user profile from backend
      const response = await api.post<{ success: boolean; data: User }>(endpoints.auth.login, {
        email: firebaseUser.email,
        token: token,
      })

      if (response.data.success && response.data.data) {
        return response.data.data
      }

      return null
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      return null
    }
  }, [])

  /**
   * Listen to Firebase auth state changes
   */
  useEffect(() => {
    if (!auth) {
      setState(prev => ({ ...prev, loading: false }))
      return
    }

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setState(prev => ({ ...prev, loading: true, error: null }))

        const user = await fetchUserProfile(firebaseUser)

        setState({
          user,
          firebaseUser,
          loading: false,
          error: user ? null : 'Failed to load user profile',
        })
      } else {
        // User signed out
        localStorage.removeItem('auth_token')
        setState({
          user: null,
          firebaseUser: null,
          loading: false,
          error: null,
        })
      }
    })

    return () => unsubscribe()
  }, [fetchUserProfile])

  /**
   * Sign in with email and password
   */
  const signIn = useCallback(async (email: string, password: string) => {
    if (!auth) {
      setState(prev => ({ ...prev, error: 'Authentication not initialized' }))
      return
    }

    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      await signInWithEmailAndPassword(auth, email, password)
      // Auth state change listener will handle the rest
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Sign in failed'
      setState(prev => ({ ...prev, loading: false, error: message }))
      throw error
    }
  }, [])

  /**
   * Sign in with Google OAuth
   */
  const signInWithGoogle = useCallback(async () => {
    if (!auth) {
      setState(prev => ({ ...prev, error: 'Authentication not initialized' }))
      return
    }

    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      await signInWithPopup(auth, googleProvider)
      // Auth state change listener will handle the rest
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Google sign in failed'
      setState(prev => ({ ...prev, loading: false, error: message }))
      throw error
    }
  }, [])

  /**
   * Sign out
   */
  const signOut = useCallback(async () => {
    if (!auth) return

    try {
      // Call backend logout endpoint
      await api.post(endpoints.auth.logout)
    } catch {
      // Ignore backend logout errors
    }

    // Clear local storage
    localStorage.removeItem('auth_token')

    // Sign out from Firebase
    await firebaseSignOut(auth)
  }, [])

  /**
   * Send password reset email
   */
  const resetPassword = useCallback(async (email: string) => {
    if (!auth) {
      setState(prev => ({ ...prev, error: 'Authentication not initialized' }))
      return
    }

    try {
      await sendPasswordResetEmail(auth, email)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Password reset failed'
      setState(prev => ({ ...prev, error: message }))
      throw error
    }
  }, [])

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }))
  }, [])

  const value: AuthContextType = {
    ...state,
    signIn,
    signInWithGoogle,
    signOut,
    resetPassword,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to access auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
