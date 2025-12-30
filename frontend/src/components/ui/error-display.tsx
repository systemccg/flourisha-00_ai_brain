'use client'

import { Box, Button, Heading, Text, VStack } from '@chakra-ui/react'

interface ErrorDisplayProps {
  error: Error | string | null
  title?: string
  onRetry?: () => void
  fullPage?: boolean
}

export function ErrorDisplay({
  error,
  title = 'Something went wrong',
  onRetry,
  fullPage = false,
}: ErrorDisplayProps) {
  const errorMessage = error instanceof Error ? error.message : error || 'An unexpected error occurred'

  const content = (
    <VStack gap={4} textAlign="center" maxW="md">
      <Text fontSize="4xl">😕</Text>
      <Heading as="h2" size="lg">
        {title}
      </Heading>
      <Text color="gray.600" _dark={{ color: 'gray.400' }}>
        {errorMessage}
      </Text>
      {onRetry && (
        <Button
          colorPalette="blue"
          onClick={onRetry}
        >
          Try Again
        </Button>
      )}
    </VStack>
  )

  if (fullPage) {
    return (
      <Box
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="gray.50"
        _dark={{ bg: 'gray.900' }}
        p={8}
      >
        {content}
      </Box>
    )
  }

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      py={12}
      px={4}
    >
      {content}
    </Box>
  )
}

interface EmptyStateProps {
  title: string
  description?: string
  icon?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({
  title,
  description,
  icon = '📭',
  action,
}: EmptyStateProps) {
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      py={12}
      px={4}
    >
      <VStack gap={4} textAlign="center" maxW="md">
        <Text fontSize="4xl">{icon}</Text>
        <Heading as="h3" size="md">
          {title}
        </Heading>
        {description && (
          <Text color="gray.600" _dark={{ color: 'gray.400' }}>
            {description}
          </Text>
        )}
        {action && (
          <Button
            colorPalette="blue"
            onClick={action.onClick}
          >
            {action.label}
          </Button>
        )}
      </VStack>
    </Box>
  )
}
