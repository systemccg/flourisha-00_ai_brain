'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  Box,
  Button,
  Container,
  Fieldset,
  Flex,
  Heading,
  Input,
  Stack,
  Text,
  VStack,
} from '@chakra-ui/react'
import { useAuth } from '@/hooks/use-auth'

/**
 * Login page component
 * Supports email/password and Google OAuth
 */
export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { signIn, signInWithGoogle, loading, error, clearError, user } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Get return URL from query params
  const returnUrl = searchParams.get('returnUrl') || '/dashboard'

  // Redirect when user becomes authenticated
  useEffect(() => {
    if (user) {
      router.push(returnUrl)
    }
  }, [user, router, returnUrl])

  // Don't render form if already authenticated
  if (user) {
    return null
  }

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    setIsSubmitting(true)

    try {
      await signIn(email, password)
      // Don't redirect here - useEffect will handle it when user state updates
    } catch {
      // Error is handled by auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGoogleSignIn = async () => {
    clearError()
    setIsSubmitting(true)

    try {
      await signInWithGoogle()
      // Don't redirect here - useEffect will handle it when user state updates
    } catch {
      // Error is handled by auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  const isLoading = loading || isSubmitting

  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.900">
      <Container maxW="md" py={12}>
        <VStack gap={8}>
          {/* Logo and Title */}
          <VStack gap={2}>
            <Heading
              size="2xl"
              bgGradient="to-r"
              gradientFrom="purple.400"
              gradientTo="cyan.400"
              bgClip="text"
            >
              Flourisha
            </Heading>
            <Text color="gray.400">Personal AI Infrastructure</Text>
          </VStack>

          {/* Login Form */}
          <Box
            w="full"
            bg="gray.800"
            borderRadius="xl"
            p={8}
            borderWidth={1}
            borderColor="gray.700"
          >
            <VStack gap={6}>
              {/* Error Display */}
              {error && (
                <Box
                  w="full"
                  p={4}
                  bg="red.900/30"
                  borderRadius="md"
                  borderWidth={1}
                  borderColor="red.500"
                >
                  <Text color="red.300" fontSize="sm">
                    {error}
                  </Text>
                </Box>
              )}

              {/* Google Sign In */}
              <Button
                w="full"
                size="lg"
                variant="outline"
                colorPalette="gray"
                onClick={handleGoogleSignIn}
                disabled={isLoading}
              >
                <Flex align="center" gap={2}>
                  <GoogleIcon />
                  <Text>Continue with Google</Text>
                </Flex>
              </Button>

              {/* Divider */}
              <Flex w="full" align="center" gap={4}>
                <Box flex={1} h="1px" bg="gray.600" />
                <Text color="gray.500" fontSize="sm">
                  or
                </Text>
                <Box flex={1} h="1px" bg="gray.600" />
              </Flex>

              {/* Email/Password Form */}
              <form onSubmit={handleEmailSignIn} style={{ width: '100%' }}>
                <Stack gap={4}>
                  <Fieldset.Root>
                    <Fieldset.Legend color="gray.300">Email</Fieldset.Legend>
                    <Input
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      bg="gray.900"
                      borderColor="gray.600"
                      _hover={{ borderColor: 'gray.500' }}
                      _focus={{ borderColor: 'purple.500', boxShadow: 'none' }}
                      required
                    />
                  </Fieldset.Root>

                  <Fieldset.Root>
                    <Fieldset.Legend color="gray.300">Password</Fieldset.Legend>
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      bg="gray.900"
                      borderColor="gray.600"
                      _hover={{ borderColor: 'gray.500' }}
                      _focus={{ borderColor: 'purple.500', boxShadow: 'none' }}
                      required
                    />
                  </Fieldset.Root>

                  <Button
                    type="submit"
                    w="full"
                    size="lg"
                    colorPalette="purple"
                    loading={isLoading}
                    loadingText="Signing in..."
                  >
                    Sign In
                  </Button>
                </Stack>
              </form>

              {/* Forgot Password Link */}
              <Button variant="ghost" size="sm" colorPalette="gray">
                Forgot your password?
              </Button>
            </VStack>
          </Box>

          {/* Footer */}
          <Text color="gray.500" fontSize="sm">
            Built with Claude Code
          </Text>
        </VStack>
      </Container>
    </Flex>
  )
}

/**
 * Google icon SVG component
 */
function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  )
}
