'use client'

import { useState } from 'react'
import { Box, Flex, Text } from '@chakra-ui/react'
import type { DailyEnergySummary, HourlyEnergyPattern, FocusQuality } from '@/lib/types/energy'
import { getEnergyColor, getFocusOption } from '@/lib/types/energy'

interface EnergyChartProps {
  dailySummaries?: DailyEnergySummary[]
  hourlyPatterns?: HourlyEnergyPattern[]
  isLoading?: boolean
}

type ViewMode = 'day' | 'week' | 'month'

/**
 * Energy timeline chart with area fill
 * Shows energy levels over time with focus quality overlay
 */
export function EnergyChart({
  dailySummaries = [],
  hourlyPatterns = [],
  isLoading = false,
}: EnergyChartProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('week')

  if (isLoading) {
    return <ChartSkeleton />
  }

  // Prepare data based on view mode
  const chartData = viewMode === 'day' ? hourlyPatterns : dailySummaries

  if (chartData.length === 0) {
    return <EmptyChart />
  }

  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      {/* Header with View Toggle */}
      <Flex justify="space-between" align="center" mb={4}>
        <Box>
          <Text fontSize="lg" fontWeight="600" color="white">
            Energy Timeline
          </Text>
          <Text fontSize="sm" color="gray.400">
            {viewMode === 'day' ? 'Hourly patterns' : 'Daily averages'}
          </Text>
        </Box>
        <ViewToggle value={viewMode} onChange={setViewMode} />
      </Flex>

      {/* Chart */}
      {viewMode === 'day' ? (
        <HourlyChart data={hourlyPatterns} />
      ) : (
        <DailyChart data={dailySummaries} mode={viewMode} />
      )}

      {/* Average Line Legend */}
      <Flex justify="center" gap={6} mt={4}>
        <Flex align="center" gap={2}>
          <Box w="12px" h="3px" bg="purple.400" borderRadius="full" />
          <Text fontSize="xs" color="gray.400">
            Energy Level
          </Text>
        </Flex>
        <Flex align="center" gap={2}>
          <Box
            w="12px"
            h="3px"
            bg="gray.500"
            borderRadius="full"
            borderStyle="dashed"
            borderWidth={1}
            borderColor="gray.500"
          />
          <Text fontSize="xs" color="gray.400">
            Average
          </Text>
        </Flex>
      </Flex>
    </Box>
  )
}

/**
 * Hourly chart for day view
 */
function HourlyChart({ data }: { data: HourlyEnergyPattern[] }) {
  const maxEnergy = 10
  const chartHeight = 200

  // Calculate average
  const avgEnergy = data.length > 0
    ? data.reduce((sum, d) => sum + d.avg_energy, 0) / data.length
    : 5

  // Filter to active hours (8 AM - 6 PM)
  const activeHours = data.filter(d => d.hour >= 8 && d.hour <= 18)

  // Create full 8-18 range
  const fullRange = Array.from({ length: 11 }, (_, i) => i + 8).map(hour => {
    const existing = activeHours.find(d => d.hour === hour)
    return existing || { hour, avg_energy: 0, measurements: 0 }
  })

  return (
    <Box position="relative" h={`${chartHeight}px`}>
      {/* Grid Lines */}
      <GridLines height={chartHeight} maxValue={maxEnergy} />

      {/* Average Line */}
      <Box
        position="absolute"
        left={0}
        right={0}
        top={`${((maxEnergy - avgEnergy) / maxEnergy) * chartHeight}px`}
        h="1px"
        borderTopWidth={1}
        borderTopStyle="dashed"
        borderTopColor="gray.600"
        zIndex={1}
      />

      {/* Bars */}
      <Flex
        position="absolute"
        left={0}
        right={0}
        bottom={0}
        top={0}
        align="flex-end"
        justify="space-between"
        px={2}
      >
        {fullRange.map((point) => {
          const height = (point.avg_energy / maxEnergy) * chartHeight
          const color = getEnergyColor(point.avg_energy)

          return (
            <Box
              key={point.hour}
              w="full"
              maxW="40px"
              mx="2px"
              position="relative"
            >
              {/* Bar */}
              <Box
                h={`${height}px`}
                bg={point.measurements > 0 ? `${color}.500` : 'gray.700'}
                borderRadius="sm"
                opacity={point.measurements > 0 ? 0.8 : 0.3}
                transition="height 0.3s ease-out"
              />
              {/* Time Label */}
              <Text
                fontSize="xs"
                color="gray.500"
                textAlign="center"
                mt={1}
              >
                {point.hour % 12 || 12}{point.hour >= 12 ? 'p' : 'a'}
              </Text>
            </Box>
          )
        })}
      </Flex>

      {/* Y-axis Labels */}
      <YAxisLabels height={chartHeight} maxValue={maxEnergy} />
    </Box>
  )
}

/**
 * Daily chart for week/month view
 */
function DailyChart({
  data,
  mode,
}: {
  data: DailyEnergySummary[]
  mode: 'week' | 'month'
}) {
  const maxEnergy = 10
  const chartHeight = 200

  // Calculate average
  const avgEnergy = data.length > 0
    ? data.reduce((sum, d) => sum + d.avg_energy, 0) / data.length
    : 5

  // Limit data based on mode
  const displayData = mode === 'week' ? data.slice(-7) : data.slice(-30)

  return (
    <Box position="relative" h={`${chartHeight}px`}>
      {/* Grid Lines */}
      <GridLines height={chartHeight} maxValue={maxEnergy} />

      {/* Average Line */}
      <Box
        position="absolute"
        left={0}
        right={0}
        top={`${((maxEnergy - avgEnergy) / maxEnergy) * chartHeight}px`}
        h="1px"
        borderTopWidth={1}
        borderTopStyle="dashed"
        borderTopColor="gray.600"
        zIndex={1}
      />

      {/* Area Chart */}
      <Box
        position="absolute"
        left={0}
        right={0}
        bottom={0}
        top={0}
      >
        <svg width="100%" height="100%" viewBox={`0 0 ${displayData.length * 40} ${chartHeight}`} preserveAspectRatio="none">
          {/* Area Fill */}
          <defs>
            <linearGradient id="energyGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="var(--chakra-colors-purple-500)" stopOpacity="0.4" />
              <stop offset="100%" stopColor="var(--chakra-colors-purple-500)" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Area Path */}
          <path
            d={getAreaPath(displayData, chartHeight, maxEnergy)}
            fill="url(#energyGradient)"
          />

          {/* Line Path */}
          <path
            d={getLinePath(displayData, chartHeight, maxEnergy)}
            fill="none"
            stroke="var(--chakra-colors-purple-400)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Data Points */}
          {displayData.map((point, i) => {
            const x = (i / (displayData.length - 1 || 1)) * (displayData.length * 40 - 20) + 10
            const y = ((maxEnergy - point.avg_energy) / maxEnergy) * chartHeight

            return (
              <circle
                key={point.date}
                cx={x}
                cy={y}
                r="4"
                fill="var(--chakra-colors-purple-400)"
              />
            )
          })}
        </svg>
      </Box>

      {/* Focus Quality Overlay */}
      <Flex
        position="absolute"
        left={0}
        right={0}
        bottom="-24px"
        justify="space-between"
        px={2}
      >
        {displayData.map((point) => (
          <FocusOverlayDot
            key={point.date}
            focus={point.primary_focus}
            date={point.date}
          />
        ))}
      </Flex>

      {/* Y-axis Labels */}
      <YAxisLabels height={chartHeight} maxValue={maxEnergy} />
    </Box>
  )
}

/**
 * Generate SVG path for line
 */
function getLinePath(data: DailyEnergySummary[], height: number, maxValue: number): string {
  if (data.length === 0) return ''

  const width = data.length * 40
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * (width - 20) + 10
    const y = ((maxValue - d.avg_energy) / maxValue) * height
    return `${x},${y}`
  })

  return `M ${points.join(' L ')}`
}

/**
 * Generate SVG path for area fill
 */
function getAreaPath(data: DailyEnergySummary[], height: number, maxValue: number): string {
  if (data.length === 0) return ''

  const width = data.length * 40
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * (width - 20) + 10
    const y = ((maxValue - d.avg_energy) / maxValue) * height
    return `${x},${y}`
  })

  const startX = 10
  const endX = ((data.length - 1) / (data.length - 1 || 1)) * (width - 20) + 10

  return `M ${startX},${height} L ${points.join(' L ')} L ${endX},${height} Z`
}

/**
 * Grid lines component
 */
function GridLines({ height, maxValue }: { height: number; maxValue: number }) {
  const lines = [2, 4, 6, 8]

  return (
    <>
      {lines.map((value) => (
        <Box
          key={value}
          position="absolute"
          left={0}
          right={0}
          top={`${((maxValue - value) / maxValue) * height}px`}
          h="1px"
          bg="gray.800"
        />
      ))}
    </>
  )
}

/**
 * Y-axis labels
 */
function YAxisLabels({ height, maxValue }: { height: number; maxValue: number }) {
  const labels = [10, 8, 6, 4, 2]

  return (
    <Box position="absolute" left="-24px" top={0} h={`${height}px`}>
      {labels.map((value) => (
        <Text
          key={value}
          position="absolute"
          top={`${((maxValue - value) / maxValue) * height}px`}
          transform="translateY(-50%)"
          fontSize="xs"
          color="gray.500"
        >
          {value}
        </Text>
      ))}
    </Box>
  )
}

/**
 * Focus quality overlay dot
 */
function FocusOverlayDot({ focus, date }: { focus: FocusQuality; date: string }) {
  const option = getFocusOption(focus)
  const dayLabel = new Date(date).toLocaleDateString('en-US', { weekday: 'short' })

  return (
    <Box textAlign="center" w="full" maxW="40px">
      <Box
        w="8px"
        h="8px"
        borderRadius="full"
        bg={`${option.color}.400`}
        mx="auto"
        mb={1}
      />
      <Text fontSize="xs" color="gray.500">
        {dayLabel}
      </Text>
    </Box>
  )
}

/**
 * View mode toggle
 */
function ViewToggle({
  value,
  onChange,
}: {
  value: ViewMode
  onChange: (mode: ViewMode) => void
}) {
  const options: ViewMode[] = ['day', 'week', 'month']

  return (
    <Flex
      bg="gray.800"
      borderRadius="lg"
      p={1}
    >
      {options.map((mode) => (
        <Box
          key={mode}
          as="button"
          px={3}
          py={1.5}
          borderRadius="md"
          fontSize="sm"
          fontWeight={value === mode ? '500' : '400'}
          color={value === mode ? 'white' : 'gray.400'}
          bg={value === mode ? 'gray.700' : 'transparent'}
          transition="all 0.15s"
          _hover={{ color: 'white' }}
          onClick={() => onChange(mode)}
          textTransform="capitalize"
        >
          {mode}
        </Box>
      ))}
    </Flex>
  )
}

/**
 * Loading skeleton
 */
function ChartSkeleton() {
  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <Box h="40px" bg="gray.800" borderRadius="md" mb={4} w="200px" />
      <Box h="200px" bg="gray.800" borderRadius="md" />
    </Box>
  )
}

/**
 * Empty state
 */
function EmptyChart() {
  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
      textAlign="center"
    >
      <Text fontSize="3xl" mb={2}>
        📊
      </Text>
      <Text fontSize="lg" fontWeight="600" color="white" mb={1}>
        No Energy Data Yet
      </Text>
      <Text fontSize="sm" color="gray.400">
        Start logging your energy to see patterns over time
      </Text>
    </Box>
  )
}
