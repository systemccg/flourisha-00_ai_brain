'use client'

import { Box, Grid, GridItem, VStack, Spinner, Flex } from '@chakra-ui/react'
import { PageContainer, PageHeader } from '@/components/layout'
import {
  EnergyWidget,
  EnergyChart,
  EnergyForecastDisplay,
} from '@/components/energy'
import { ErrorDisplay } from '@/components/ui/error-display'
import { useEnergyDashboard } from '@/hooks/use-energy'

/**
 * Energy Dashboard Page
 * Track and visualize energy patterns
 */
export default function EnergyPage() {
  const { history, forecast, isLoading, error, refetch } = useEnergyDashboard()

  return (
    <PageContainer>
      <PageHeader
        title="Energy Tracking"
        description="Monitor your energy levels and focus quality throughout the day"
      />

      {/* Loading State */}
      {isLoading && (
        <Flex justify="center" align="center" py={20}>
          <Spinner size="xl" color="purple.500" />
        </Flex>
      )}

      {/* Error State */}
      {error && (
        <ErrorDisplay
          error={error}
          onRetry={refetch}
        />
      )}

      {/* Content */}
      {!isLoading && !error && (
        <Grid
          templateColumns={{ base: '1fr', lg: 'minmax(400px, 1fr) 2fr' }}
          gap={6}
        >
          {/* Left Column - Input & Forecast */}
          <GridItem>
            <VStack gap={6} align="stretch">
              {/* Energy Widget */}
              <EnergyWidget onSuccess={refetch} />

              {/* Energy Forecast */}
              <EnergyForecastDisplay forecast={forecast} />
            </VStack>
          </GridItem>

          {/* Right Column - Charts */}
          <GridItem>
            <VStack gap={6} align="stretch">
              {/* Energy Timeline */}
              <EnergyChart
                dailySummaries={history?.daily_summaries}
                hourlyPatterns={history?.hourly_patterns}
              />

              {/* Stats Summary */}
              {history && (
                <StatsSummary
                  avgEnergy={history.summary.avg_energy}
                  totalEntries={history.summary.total_entries}
                  focusDistribution={history.summary.focus_distribution}
                />
              )}
            </VStack>
          </GridItem>
        </Grid>
      )}
    </PageContainer>
  )
}

/**
 * Stats summary component
 */
function StatsSummary({
  avgEnergy,
  totalEntries,
  focusDistribution,
}: {
  avgEnergy: number
  totalEntries: number
  focusDistribution: { deep: number; shallow: number; distracted: number; total: number }
}) {
  const deepPercent = focusDistribution.total > 0
    ? Math.round((focusDistribution.deep / focusDistribution.total) * 100)
    : 0
  const shallowPercent = focusDistribution.total > 0
    ? Math.round((focusDistribution.shallow / focusDistribution.total) * 100)
    : 0
  const distractedPercent = focusDistribution.total > 0
    ? Math.round((focusDistribution.distracted / focusDistribution.total) * 100)
    : 0

  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <Box mb={4}>
        <Box fontSize="sm" color="gray.400" fontWeight="500" mb={3}>
          Last 7 Days Summary
        </Box>
        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
          <StatCard
            label="Average Energy"
            value={avgEnergy.toFixed(1)}
            suffix="/10"
          />
          <StatCard
            label="Total Entries"
            value={totalEntries.toString()}
            suffix="logs"
          />
        </Grid>
      </Box>

      {/* Focus Distribution */}
      <Box>
        <Box fontSize="sm" color="gray.400" fontWeight="500" mb={3}>
          Focus Quality Distribution
        </Box>
        <Flex direction="column" gap={2}>
          <FocusBar label="Deep Focus" percent={deepPercent} color="green" emoji="🎯" />
          <FocusBar label="Shallow" percent={shallowPercent} color="yellow" emoji="📋" />
          <FocusBar label="Distracted" percent={distractedPercent} color="red" emoji="🌀" />
        </Flex>
      </Box>
    </Box>
  )
}

/**
 * Stat card component
 */
function StatCard({
  label,
  value,
  suffix,
}: {
  label: string
  value: string
  suffix: string
}) {
  return (
    <Box p={4} bg="gray.800/50" borderRadius="lg">
      <Box fontSize="xs" color="gray.500" textTransform="uppercase" mb={1}>
        {label}
      </Box>
      <Flex align="baseline" gap={1}>
        <Box fontSize="2xl" fontWeight="bold" color="white">
          {value}
        </Box>
        <Box fontSize="sm" color="gray.500">
          {suffix}
        </Box>
      </Flex>
    </Box>
  )
}

/**
 * Focus distribution bar
 */
function FocusBar({
  label,
  percent,
  color,
  emoji,
}: {
  label: string
  percent: number
  color: string
  emoji: string
}) {
  return (
    <Flex align="center" gap={3}>
      <Box fontSize="sm" w="20px" textAlign="center">
        {emoji}
      </Box>
      <Box flex={1}>
        <Flex justify="space-between" mb={1}>
          <Box fontSize="sm" color="gray.300">
            {label}
          </Box>
          <Box fontSize="sm" color={`${color}.400`} fontWeight="500">
            {percent}%
          </Box>
        </Flex>
        <Box h="6px" bg="gray.700" borderRadius="full" overflow="hidden">
          <Box
            h="full"
            w={`${percent}%`}
            bg={`${color}.500`}
            borderRadius="full"
            transition="width 0.3s"
          />
        </Box>
      </Box>
    </Flex>
  )
}
