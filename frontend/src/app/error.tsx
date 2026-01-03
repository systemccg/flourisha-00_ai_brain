'use client'

import { useEffect } from 'react'
import { Box, Button, Container, Heading, Text, VStack } from '@chakra-ui/react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Application error:', error)
  }, [error])

  return (
    <Box minH="100vh" bg="gray.900" display="flex" alignItems="center" justifyContent="center">
      <Container maxW="md">
        <VStack gap={6} textAlign="center">
          <Heading size="xl" color="red.400">
            Something went wrong
          </Heading>

          <Text color="gray.400">
            An unexpected error occurred. Please try again.
          </Text>

          {error.message && (
            <Box
              p={4}
              bg="gray.800"
              borderRadius="lg"
              borderWidth={1}
              borderColor="gray.700"
              w="full"
            >
              <Text fontSize="sm" color="gray.500" fontFamily="mono">
                {error.message}
              </Text>
            </Box>
          )}

          <Button
            colorPalette="purple"
            onClick={reset}
            size="lg"
          >
            Try Again
          </Button>
        </VStack>
      </Container>
    </Box>
  )
}
