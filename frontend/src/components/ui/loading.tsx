'use client'

import { Box, Spinner, Text, VStack } from '@chakra-ui/react'

interface LoadingProps {
  message?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  fullPage?: boolean
}

export function Loading({ message, size = 'lg', fullPage = false }: LoadingProps) {
  const content = (
    <VStack gap={4}>
      <Spinner
        size={size}
        color="blue.500"
        borderWidth="4px"
      />
      {message && (
        <Text color="gray.500" fontSize="sm">
          {message}
        </Text>
      )}
    </VStack>
  )

  if (fullPage) {
    return (
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="white"
        _dark={{ bg: 'gray.900' }}
        zIndex={9999}
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
      py={8}
    >
      {content}
    </Box>
  )
}

export function Skeleton({
  height = '20px',
  width = '100%',
  borderRadius = 'md',
}: {
  height?: string
  width?: string
  borderRadius?: string
}) {
  return (
    <Box
      height={height}
      width={width}
      borderRadius={borderRadius}
      bg="gray.200"
      _dark={{ bg: 'gray.700' }}
      animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite"
      css={{
        '@keyframes pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
      }}
    />
  )
}

export function CardSkeleton() {
  return (
    <Box
      p={6}
      bg="white"
      _dark={{ bg: 'gray.800' }}
      borderRadius="lg"
      shadow="sm"
    >
      <VStack gap={4} align="stretch">
        <Skeleton height="24px" width="60%" />
        <Skeleton height="16px" width="100%" />
        <Skeleton height="16px" width="80%" />
        <Skeleton height="40px" width="120px" />
      </VStack>
    </Box>
  )
}
