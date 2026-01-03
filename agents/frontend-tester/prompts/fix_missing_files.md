# Fix Missing Required Files Prompt

When the "missing required error components" error appears, use this prompt to fix it.

## Problem

Next.js App Router requires these files for proper error handling:
- `src/app/error.tsx` - Route-level error boundary
- `src/app/global-error.tsx` - Root error boundary
- `src/app/not-found.tsx` - 404 handler

## Diagnosis

```bash
ls -la /root/flourisha/00_AI_Brain/frontend/src/app/{error,global-error,not-found}.tsx
```

## Fix: Create error.tsx

```tsx
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
            <Box p={4} bg="gray.800" borderRadius="lg" borderWidth={1} borderColor="gray.700" w="full">
              <Text fontSize="sm" color="gray.500" fontFamily="mono">{error.message}</Text>
            </Box>
          )}
          <Button colorPalette="purple" onClick={reset} size="lg">Try Again</Button>
        </VStack>
      </Container>
    </Box>
  )
}
```

## Fix: Create global-error.tsx

```tsx
'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body style={{
        backgroundColor: '#111827',
        color: '#fff',
        fontFamily: 'system-ui, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        margin: 0,
      }}>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: '#f87171' }}>
            Something went wrong
          </h1>
          <p style={{ color: '#9ca3af', marginBottom: '1.5rem' }}>
            A critical error occurred. Please refresh the page.
          </p>
          {error.message && (
            <div style={{
              padding: '1rem',
              backgroundColor: '#1f2937',
              borderRadius: '0.5rem',
              marginBottom: '1.5rem',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              color: '#6b7280',
            }}>
              {error.message}
            </div>
          )}
          <button
            onClick={reset}
            style={{
              backgroundColor: '#8b5cf6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
          >
            Try Again
          </button>
        </div>
      </body>
    </html>
  )
}
```

## Fix: Create not-found.tsx

```tsx
'use client'

import Link from 'next/link'
import { Box, Button, Container, Heading, Text, VStack } from '@chakra-ui/react'

export default function NotFound() {
  return (
    <Box minH="100vh" bg="gray.900" display="flex" alignItems="center" justifyContent="center">
      <Container maxW="md">
        <VStack gap={6} textAlign="center">
          <Heading size="2xl" color="purple.400">404</Heading>
          <Heading size="lg" color="white">Page Not Found</Heading>
          <Text color="gray.400">
            The page you're looking for doesn't exist or has been moved.
          </Text>
          <Link href="/">
            <Button colorPalette="purple" size="lg">Go Home</Button>
          </Link>
        </VStack>
      </Container>
    </Box>
  )
}
```

## After Creating Files

1. Wait 5-10 seconds for hot reload
2. Refresh the browser
3. Run pre-flight tests to verify:
   ```bash
   cd /root/flourisha/00_AI_Brain/frontend
   npx playwright test e2e/preflight.spec.ts
   ```
