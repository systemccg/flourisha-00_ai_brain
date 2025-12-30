'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { type OKRStatus, getStatusColor, getStatusLabel } from '@/lib/types/okr'

interface StatusBadgeProps {
  status: OKRStatus
  size?: 'sm' | 'md'
  showIcon?: boolean
}

/**
 * Status badge component for OKRs
 * Shows colored badge with status text
 */
export function StatusBadge({
  status,
  size = 'md',
  showIcon = true,
}: StatusBadgeProps) {
  const color = getStatusColor(status)
  const label = getStatusLabel(status)

  const sizes = {
    sm: {
      px: 2,
      py: 0.5,
      fontSize: 'xs',
      iconSize: 8,
    },
    md: {
      px: 3,
      py: 1,
      fontSize: 'sm',
      iconSize: 10,
    },
  }

  const sizeProps = sizes[size]

  return (
    <Flex
      display="inline-flex"
      align="center"
      gap={1.5}
      px={sizeProps.px}
      py={sizeProps.py}
      bg={`${color}.500/20`}
      color={`${color}.300`}
      borderRadius="full"
      fontSize={sizeProps.fontSize}
      fontWeight="500"
    >
      {showIcon && <StatusIcon status={status} size={sizeProps.iconSize} />}
      <Text>{label}</Text>
    </Flex>
  )
}

/**
 * Status icon based on status type
 */
function StatusIcon({ status, size = 10 }: { status: OKRStatus; size?: number }) {
  switch (status) {
    case 'ON_TRACK':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="20 6 9 17 4 12" />
        </svg>
      )
    case 'COMPLETED':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <polyline points="16 8 10 14 8 12" />
        </svg>
      )
    case 'NEEDS_ATTENTION':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      )
    case 'AT_RISK':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      )
    case 'BLOCKED':
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
        </svg>
      )
    default:
      return null
  }
}

/**
 * Status dot for compact display
 */
export function StatusDot({ status, size = 8 }: { status: OKRStatus; size?: number }) {
  const color = getStatusColor(status)

  return (
    <Box
      w={`${size}px`}
      h={`${size}px`}
      borderRadius="full"
      bg={`${color}.400`}
      title={getStatusLabel(status)}
    />
  )
}
