'use client'

import { useEffect, type ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Center, Spinner, VStack, Text } from '@chakra-ui/react'
import { useAuth } from '@/hooks/use-auth'

/**
 * Props for ProtectedRoute component
 */
interface ProtectedRouteProps {
  children: ReactNode
  /**
   * Fallback component to show while checking auth
   * @default Loading spinner
   */
  fallback?: ReactNode
  /**
   * Path to redirect to if not authenticated
   * @default '/login'
   */
  redirectTo?: string
}

/**
 * ProtectedRoute component
 * Wraps children and only renders them if user is authenticated
 * Redirects to login page if not authenticated
 */
export function ProtectedRoute({
  children,
  fallback,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { user, loading } = useAuth()

  useEffect(() => {
    // Don't redirect while still loading
    if (loading) return

    // If not authenticated, redirect to login with return URL
    if (!user) {
      const returnUrl = encodeURIComponent(pathname)
      router.push(`${redirectTo}?returnUrl=${returnUrl}`)
    }
  }, [user, loading, router, pathname, redirectTo])

  // Show loading state
  if (loading) {
    return (
      fallback || (
        <Center h="100vh" bg="gray.900">
          <VStack gap={4}>
            <Spinner size="xl" color="purple.500" borderWidth={3} />
            <Text color="gray.400">Loading...</Text>
          </VStack>
        </Center>
      )
    )
  }

  // Don't render children if not authenticated
  if (!user) {
    return (
      fallback || (
        <Center h="100vh" bg="gray.900">
          <VStack gap={4}>
            <Spinner size="xl" color="purple.500" borderWidth={3} />
            <Text color="gray.400">Redirecting to login...</Text>
          </VStack>
        </Center>
      )
    )
  }

  // User is authenticated, render children
  return <>{children}</>
}

/**
 * Higher-order component for protecting pages
 * Use this when you need to wrap a page component
 */
export function withProtectedRoute<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<ProtectedRouteProps, 'children'>
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}
