'use client'

import { Box, Flex, Text, IconButton } from '@chakra-ui/react'
import { useState } from 'react'
import type { Objective, KeyResult } from '@/lib/types/okr'
import { ProgressRing } from './progress-ring'
import { StatusBadge } from './status-badge'
import { KeyResultsList } from './key-result-item'

interface ObjectiveCardProps {
  objective: Objective
  isExpanded?: boolean
  onToggleExpand?: () => void
  onSelectKeyResult?: (kr: KeyResult) => void
  onSelectObjective?: (objective: Objective) => void
}

/**
 * Simple collapse component for Chakra UI v3
 */
function Collapsible({
  isOpen,
  children,
}: {
  isOpen: boolean
  children: React.ReactNode
}) {
  return (
    <Box
      overflow="hidden"
      maxH={isOpen ? '2000px' : '0px'}
      opacity={isOpen ? 1 : 0}
      transition="all 0.3s ease-in-out"
    >
      {children}
    </Box>
  )
}

/**
 * Objective card component
 * Shows progress ring, title, status, and expandable key results
 */
export function ObjectiveCard({
  objective,
  isExpanded: controlledExpanded,
  onToggleExpand,
  onSelectKeyResult,
  onSelectObjective,
}: ObjectiveCardProps) {
  const [internalExpanded, setInternalExpanded] = useState(false)

  // Support both controlled and uncontrolled expand state
  const isExpanded = controlledExpanded ?? internalExpanded
  const handleToggle = onToggleExpand ?? (() => setInternalExpanded(!internalExpanded))

  const { title, description, progress, status, key_results, owner_name } = objective

  return (
    <Box
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
      overflow="hidden"
      transition="all 0.2s"
      _hover={{ borderColor: 'gray.700' }}
    >
      {/* Header */}
      <Flex
        p={5}
        gap={4}
        align="start"
        cursor={onSelectObjective ? 'pointer' : 'default'}
        onClick={() => onSelectObjective?.(objective)}
      >
        {/* Progress Ring */}
        <Box flexShrink={0}>
          <ProgressRing progress={progress} size={72} strokeWidth={7} />
        </Box>

        {/* Content */}
        <Box flex={1} minW={0}>
          <Flex align="center" gap={2} mb={1} flexWrap="wrap">
            <Text
              fontSize="lg"
              fontWeight="600"
              color="white"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              {title}
            </Text>
            <StatusBadge status={status} size="sm" />
          </Flex>

          {description && (
            <Text
              fontSize="sm"
              color="gray.400"
              mb={2}
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

          <Flex align="center" gap={4} fontSize="sm" color="gray.500">
            <Text>
              {key_results.length} Key Result{key_results.length !== 1 ? 's' : ''}
            </Text>
            {owner_name && (
              <>
                <Text color="gray.600">|</Text>
                <Text>Owner: {owner_name}</Text>
              </>
            )}
          </Flex>
        </Box>

        {/* Expand Button */}
        <IconButton
          aria-label={isExpanded ? 'Collapse key results' : 'Expand key results'}
          variant="ghost"
          size="sm"
          color="gray.400"
          _hover={{ color: 'white', bg: 'gray.800' }}
          onClick={(e) => {
            e.stopPropagation()
            handleToggle()
          }}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s',
            }}
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </IconButton>
      </Flex>

      {/* Key Results (Expandable) */}
      <Collapsible isOpen={isExpanded}>
        <Box
          px={5}
          pb={5}
          pt={0}
          borderTopWidth={1}
          borderColor="gray.800"
          bg="gray.900/50"
        >
          <Box pt={4}>
            <KeyResultsList
              keyResults={key_results}
              onSelectKeyResult={onSelectKeyResult}
            />
          </Box>
        </Box>
      </Collapsible>
    </Box>
  )
}

/**
 * Compact objective card for sidebar/summary views
 */
export function ObjectiveCardCompact({
  objective,
  onClick,
}: {
  objective: Objective
  onClick?: () => void
}) {
  const { title, progress, status, key_results } = objective

  return (
    <Box
      p={3}
      bg="gray.800/50"
      borderRadius="lg"
      cursor={onClick ? 'pointer' : 'default'}
      _hover={onClick ? { bg: 'gray.800' } : undefined}
      onClick={onClick}
      transition="all 0.15s"
    >
      <Flex align="center" gap={3}>
        <ProgressRing progress={progress} size={40} strokeWidth={4} showLabel={false} />
        <Box flex={1} minW={0}>
          <Text
            fontSize="sm"
            color="white"
            fontWeight="500"
            overflow="hidden"
            textOverflow="ellipsis"
            whiteSpace="nowrap"
          >
            {title}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {key_results.length} KRs | {Math.round(progress)}%
          </Text>
        </Box>
        <StatusBadge status={status} size="sm" showIcon={false} />
      </Flex>
    </Box>
  )
}
