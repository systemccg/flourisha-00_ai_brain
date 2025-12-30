'use client'

import { Box, Flex, Text, Grid, GridItem } from '@chakra-ui/react'
import type { QuarterlySummary } from '@/lib/types/okr'
import { ProgressRing } from './progress-ring'

interface OKRSummaryProps {
  summary: QuarterlySummary
}

/**
 * OKR quarterly summary component
 * Shows overall progress and status breakdown
 */
export function OKRSummary({ summary }: OKRSummaryProps) {
  const {
    quarter,
    total_objectives,
    total_key_results,
    overall_progress,
    status_breakdown,
    week_number,
    weeks_remaining,
  } = summary

  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <Grid templateColumns={{ base: '1fr', md: 'auto 1fr auto' }} gap={6} alignItems="center">
        {/* Progress Ring */}
        <GridItem>
          <Flex align="center" gap={4}>
            <ProgressRing progress={overall_progress} size={100} strokeWidth={10} />
            <Box display={{ base: 'block', md: 'none' }}>
              <Text fontSize="sm" color="gray.400">
                Overall Progress
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="white">
                {quarter}
              </Text>
            </Box>
          </Flex>
        </GridItem>

        {/* Stats */}
        <GridItem>
          <Flex gap={6} flexWrap="wrap">
            <StatItem label="Objectives" value={total_objectives} />
            <StatItem label="Key Results" value={total_key_results} />
            <StatItem label="Week" value={`${week_number}/12`} />
            <StatItem
              label="Remaining"
              value={`${weeks_remaining}w`}
              color={weeks_remaining <= 2 ? 'orange.400' : undefined}
            />
          </Flex>
        </GridItem>

        {/* Status Breakdown */}
        <GridItem>
          <StatusBreakdown breakdown={status_breakdown} />
        </GridItem>
      </Grid>
    </Box>
  )
}

/**
 * Individual stat display
 */
function StatItem({
  label,
  value,
  color,
}: {
  label: string
  value: string | number
  color?: string
}) {
  return (
    <Box>
      <Text fontSize="xs" color="gray.500" textTransform="uppercase" letterSpacing="wide">
        {label}
      </Text>
      <Text fontSize="xl" fontWeight="bold" color={color || 'white'}>
        {value}
      </Text>
    </Box>
  )
}

/**
 * Status breakdown mini bars
 */
function StatusBreakdown({
  breakdown,
}: {
  breakdown: QuarterlySummary['status_breakdown']
}) {
  const items = [
    { key: 'on_track', label: 'On Track', color: 'green.400', value: breakdown.on_track },
    { key: 'needs_attention', label: 'Attention', color: 'yellow.400', value: breakdown.needs_attention },
    { key: 'at_risk', label: 'At Risk', color: 'red.400', value: breakdown.at_risk },
    { key: 'blocked', label: 'Blocked', color: 'gray.400', value: breakdown.blocked },
    { key: 'completed', label: 'Done', color: 'purple.400', value: breakdown.completed },
  ]

  const total = items.reduce((sum, item) => sum + item.value, 0)

  return (
    <Box minW="160px">
      <Text fontSize="xs" color="gray.500" mb={2} textTransform="uppercase">
        Status
      </Text>
      <Flex direction="column" gap={1.5}>
        {items.map(
          (item) =>
            item.value > 0 && (
              <Flex key={item.key} align="center" gap={2} fontSize="xs">
                <Box w="8px" h="8px" borderRadius="sm" bg={item.color} />
                <Text color="gray.400" flex={1}>
                  {item.label}
                </Text>
                <Text color="gray.300" fontWeight="500">
                  {item.value}
                </Text>
              </Flex>
            )
        )}
      </Flex>
    </Box>
  )
}

/**
 * Compact summary for sidebar/header
 */
export function OKRSummaryCompact({ summary }: OKRSummaryProps) {
  const { overall_progress, total_objectives, week_number, weeks_remaining } = summary

  return (
    <Flex align="center" gap={3}>
      <ProgressRing progress={overall_progress} size={48} strokeWidth={5} labelSize="sm" />
      <Box>
        <Text fontSize="sm" color="white" fontWeight="500">
          {total_objectives} Objectives
        </Text>
        <Text fontSize="xs" color="gray.500">
          Week {week_number} | {weeks_remaining}w left
        </Text>
      </Box>
    </Flex>
  )
}
