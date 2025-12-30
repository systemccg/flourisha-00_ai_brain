'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import type { KeyResult } from '@/lib/types/okr'
import { StatusDot } from './status-badge'

interface KeyResultItemProps {
  keyResult: KeyResult
  onSelect?: (kr: KeyResult) => void
  isCompact?: boolean
}

/**
 * Custom progress bar component for Chakra UI v3
 */
function ProgressBar({
  value,
  colorScheme = 'purple',
  size = 'md',
}: {
  value: number
  colorScheme?: string
  size?: 'sm' | 'md'
}) {
  const height = size === 'sm' ? '6px' : '8px'
  const normalizedValue = Math.min(100, Math.max(0, value))

  return (
    <Box h={height} bg="gray.700" borderRadius="full" overflow="hidden">
      <Box
        h="full"
        w={`${normalizedValue}%`}
        bg={`${colorScheme}.500`}
        transition="width 0.3s ease-out"
      />
    </Box>
  )
}

/**
 * Key Result item component
 * Shows progress bar, current/target values, and status
 */
export function KeyResultItem({
  keyResult,
  onSelect,
  isCompact = false,
}: KeyResultItemProps) {
  const { title, description, progress, current_value, target_value, unit, status, velocity, forecast_date } =
    keyResult

  // Determine progress bar color based on status
  const getProgressColor = () => {
    switch (status) {
      case 'ON_TRACK':
      case 'COMPLETED':
        return 'green'
      case 'NEEDS_ATTENTION':
        return 'yellow'
      case 'AT_RISK':
        return 'red'
      case 'BLOCKED':
        return 'gray'
      default:
        return 'purple'
    }
  }

  // Format value with unit
  const formatValue = (value: number) => {
    if (unit === '%') return `${value}%`
    if (unit === '$') return `$${value.toLocaleString()}`
    if (unit) return `${value.toLocaleString()} ${unit}`
    return value.toLocaleString()
  }

  if (isCompact) {
    return (
      <Box
        p={3}
        borderRadius="md"
        bg="gray.800/50"
        cursor={onSelect ? 'pointer' : 'default'}
        _hover={onSelect ? { bg: 'gray.800' } : undefined}
        onClick={() => onSelect?.(keyResult)}
        transition="all 0.15s"
      >
        <Flex justify="space-between" align="center" mb={2}>
          <Flex align="center" gap={2} flex={1} minW={0}>
            <StatusDot status={status} />
            <Text
              fontSize="sm"
              color="gray.300"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              {title}
            </Text>
          </Flex>
          <Text fontSize="sm" color="gray.500" flexShrink={0} ml={2}>
            {Math.round(progress)}%
          </Text>
        </Flex>
        <ProgressBar value={progress} colorScheme={getProgressColor()} size="sm" />
      </Box>
    )
  }

  return (
    <Box
      p={4}
      borderRadius="lg"
      bg="gray.800/50"
      borderWidth={1}
      borderColor="gray.700"
      cursor={onSelect ? 'pointer' : 'default'}
      _hover={onSelect ? { borderColor: 'gray.600', bg: 'gray.800' } : undefined}
      onClick={() => onSelect?.(keyResult)}
      transition="all 0.15s"
    >
      {/* Header */}
      <Flex justify="space-between" align="start" mb={3}>
        <Box flex={1} pr={4}>
          <Flex align="center" gap={2} mb={1}>
            <StatusDot status={status} />
            <Text color="white" fontWeight="500">
              {title}
            </Text>
          </Flex>
          {description && (
            <Text
              fontSize="sm"
              color="gray.400"
              overflow="hidden"
              textOverflow="ellipsis"
              display="-webkit-box"
              css={{
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {description}
            </Text>
          )}
        </Box>
        <Text
          fontSize="2xl"
          fontWeight="bold"
          color={progress >= 100 ? 'green.400' : 'white'}
        >
          {Math.round(progress)}%
        </Text>
      </Flex>

      {/* Progress bar */}
      <Box mb={3}>
        <ProgressBar value={progress} colorScheme={getProgressColor()} size="md" />
      </Box>

      {/* Footer stats */}
      <Flex justify="space-between" align="center" flexWrap="wrap" gap={2}>
        <Flex gap={4}>
          <Box>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase">
              Current
            </Text>
            <Text fontSize="sm" color="gray.300" fontWeight="500">
              {formatValue(current_value)}
            </Text>
          </Box>
          <Box>
            <Text fontSize="xs" color="gray.500" textTransform="uppercase">
              Target
            </Text>
            <Text fontSize="sm" color="gray.300" fontWeight="500">
              {formatValue(target_value)}
            </Text>
          </Box>
        </Flex>

        <Flex gap={4}>
          {velocity !== undefined && (
            <Box textAlign="right">
              <Text fontSize="xs" color="gray.500" textTransform="uppercase">
                Velocity
              </Text>
              <Text
                fontSize="sm"
                color={velocity >= 0 ? 'green.400' : 'red.400'}
                fontWeight="500"
              >
                {velocity >= 0 ? '+' : ''}
                {velocity.toFixed(1)}/wk
              </Text>
            </Box>
          )}
          {forecast_date && (
            <Box textAlign="right">
              <Text fontSize="xs" color="gray.500" textTransform="uppercase">
                Forecast
              </Text>
              <Text fontSize="sm" color="gray.300" fontWeight="500">
                {new Date(forecast_date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                })}
              </Text>
            </Box>
          )}
        </Flex>
      </Flex>
    </Box>
  )
}

/**
 * Key Results list component
 */
export function KeyResultsList({
  keyResults,
  onSelectKeyResult,
  isCompact = false,
}: {
  keyResults: KeyResult[]
  onSelectKeyResult?: (kr: KeyResult) => void
  isCompact?: boolean
}) {
  if (keyResults.length === 0) {
    return (
      <Box p={4} textAlign="center" color="gray.500" fontSize="sm">
        No key results defined
      </Box>
    )
  }

  return (
    <Flex direction="column" gap={isCompact ? 2 : 3}>
      {keyResults.map((kr) => (
        <KeyResultItem
          key={kr.id}
          keyResult={kr}
          onSelect={onSelectKeyResult}
          isCompact={isCompact}
        />
      ))}
    </Flex>
  )
}
