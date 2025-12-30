'use client'

import { Box, Flex, Text, Grid, GridItem } from '@chakra-ui/react'
import type { EnergyForecast, EnergyPeriodForecast } from '@/lib/types/energy'
import { getEnergyColor, getEnergyLabel } from '@/lib/types/energy'

interface EnergyForecastProps {
  forecast?: EnergyForecast | null
  isLoading?: boolean
}

/**
 * Energy forecast display component
 * Shows predicted energy levels for today/tomorrow
 */
export function EnergyForecastDisplay({
  forecast,
  isLoading = false,
}: EnergyForecastProps) {
  if (isLoading) {
    return <ForecastSkeleton />
  }

  if (!forecast) {
    return <EmptyForecast />
  }

  const {
    date,
    morning,
    afternoon,
    evening,
    overall_predicted,
    best_hours,
    historical_accuracy,
  } = forecast

  const isToday = new Date(date).toDateString() === new Date().toDateString()
  const dateLabel = isToday
    ? "Today's Forecast"
    : new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'short',
        day: 'numeric',
      })

  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      {/* Header */}
      <Flex justify="space-between" align="start" mb={5}>
        <Box>
          <Text fontSize="lg" fontWeight="600" color="white">
            {dateLabel}
          </Text>
          <Flex align="center" gap={2} mt={1}>
            <ConfidenceIndicator value={historical_accuracy} />
            <Text fontSize="xs" color="gray.500">
              {historical_accuracy}% historical accuracy
            </Text>
          </Flex>
        </Box>
        <OverallPrediction value={overall_predicted} />
      </Flex>

      {/* Period Forecasts */}
      <Grid templateColumns="repeat(3, 1fr)" gap={4} mb={5}>
        <PeriodCard period={morning} label="Morning" icon="🌅" hours="8am-12pm" />
        <PeriodCard period={afternoon} label="Afternoon" icon="☀️" hours="12pm-5pm" />
        <PeriodCard period={evening} label="Evening" icon="🌙" hours="5pm-8pm" />
      </Grid>

      {/* Best Hours */}
      {best_hours.length > 0 && (
        <BestHoursDisplay hours={best_hours} />
      )}

      {/* Recommendations */}
      <RecommendationsSection forecast={forecast} />
    </Box>
  )
}

/**
 * Overall prediction display
 */
function OverallPrediction({ value }: { value: number }) {
  const color = getEnergyColor(value)
  const label = getEnergyLabel(value)

  return (
    <Box textAlign="right">
      <Flex align="baseline" gap={1} justify="flex-end">
        <Text fontSize="3xl" fontWeight="bold" color={`${color}.400`} lineHeight="1">
          {Math.round(value * 10) / 10}
        </Text>
        <Text fontSize="sm" color="gray.500">/10</Text>
      </Flex>
      <Text fontSize="xs" color={`${color}.400`}>
        {label}
      </Text>
    </Box>
  )
}

/**
 * Period forecast card
 */
function PeriodCard({
  period,
  label,
  icon,
  hours,
}: {
  period: EnergyPeriodForecast
  label: string
  icon: string
  hours: string
}) {
  const color = getEnergyColor(period.predicted_energy)

  return (
    <Box
      p={4}
      bg="gray.800/50"
      borderRadius="lg"
      borderWidth={1}
      borderColor="gray.700"
    >
      <Flex align="center" gap={2} mb={3}>
        <Text fontSize="lg">{icon}</Text>
        <Box>
          <Text fontSize="sm" fontWeight="500" color="white">
            {label}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {hours}
          </Text>
        </Box>
      </Flex>

      {/* Energy Bar */}
      <Box mb={2}>
        <Flex justify="space-between" align="baseline" mb={1}>
          <Text fontSize="2xl" fontWeight="bold" color={`${color}.400`}>
            {Math.round(period.predicted_energy)}
          </Text>
          <ConfidenceBadge value={period.confidence} />
        </Flex>
        <Box h="6px" bg="gray.700" borderRadius="full" overflow="hidden">
          <Box
            h="full"
            w={`${(period.predicted_energy / 10) * 100}%`}
            bg={`${color}.500`}
            borderRadius="full"
            transition="width 0.3s"
          />
        </Box>
      </Box>

      {/* Period Recommendation */}
      {period.recommendation && (
        <Text fontSize="xs" color="gray.400" mt={2}>
          {period.recommendation}
        </Text>
      )}
    </Box>
  )
}

/**
 * Confidence indicator bar
 */
function ConfidenceIndicator({ value }: { value: number }) {
  const color = value >= 80 ? 'green' : value >= 60 ? 'yellow' : 'orange'

  return (
    <Box w="40px" h="4px" bg="gray.700" borderRadius="full" overflow="hidden">
      <Box
        h="full"
        w={`${value}%`}
        bg={`${color}.500`}
        borderRadius="full"
      />
    </Box>
  )
}

/**
 * Confidence badge
 */
function ConfidenceBadge({ value }: { value: number }) {
  const color = value >= 80 ? 'green' : value >= 60 ? 'yellow' : 'orange'

  return (
    <Text fontSize="xs" color={`${color}.400`}>
      {value}% conf
    </Text>
  )
}

/**
 * Best hours display
 */
function BestHoursDisplay({ hours }: { hours: number[] }) {
  const formatHour = (h: number) => {
    const hour12 = h % 12 || 12
    const ampm = h >= 12 ? 'pm' : 'am'
    return `${hour12}${ampm}`
  }

  // Group consecutive hours
  const ranges: string[] = []
  let start = hours[0]
  let end = hours[0]

  for (let i = 1; i <= hours.length; i++) {
    if (i < hours.length && hours[i] === end + 1) {
      end = hours[i]
    } else {
      if (start === end) {
        ranges.push(formatHour(start))
      } else {
        ranges.push(`${formatHour(start)}-${formatHour(end)}`)
      }
      if (i < hours.length) {
        start = hours[i]
        end = hours[i]
      }
    }
  }

  return (
    <Box
      p={4}
      bg="green.500/10"
      borderRadius="lg"
      borderWidth={1}
      borderColor="green.500/30"
      mb={4}
    >
      <Flex align="center" gap={3}>
        <Text fontSize="xl">⚡</Text>
        <Box>
          <Text fontSize="sm" fontWeight="500" color="green.400">
            Peak Performance Windows
          </Text>
          <Text fontSize="sm" color="gray.300">
            {ranges.join(', ')}
          </Text>
        </Box>
      </Flex>
    </Box>
  )
}

/**
 * Recommendations based on forecast
 */
function RecommendationsSection({ forecast }: { forecast: EnergyForecast }) {
  const recommendations = generateRecommendations(forecast)

  if (recommendations.length === 0) return null

  return (
    <Box>
      <Text fontSize="sm" fontWeight="500" color="gray.400" mb={3}>
        Recommendations
      </Text>
      <Flex direction="column" gap={2}>
        {recommendations.map((rec, i) => (
          <Flex key={i} align="start" gap={2}>
            <Text fontSize="sm">{rec.icon}</Text>
            <Text fontSize="sm" color="gray.300">
              {rec.text}
            </Text>
          </Flex>
        ))}
      </Flex>
    </Box>
  )
}

/**
 * Generate recommendations from forecast
 */
function generateRecommendations(forecast: EnergyForecast): Array<{ icon: string; text: string }> {
  const recs: Array<{ icon: string; text: string }> = []

  // Schedule impact recommendation
  if (forecast.schedule_impact < -1) {
    recs.push({
      icon: '📅',
      text: 'Heavy meeting schedule detected. Consider blocking focus time.',
    })
  }

  // Morning energy recommendation
  if (forecast.morning.predicted_energy >= 7) {
    recs.push({
      icon: '🎯',
      text: 'Morning looks great for deep work. Tackle complex tasks early.',
    })
  } else if (forecast.morning.predicted_energy < 5) {
    recs.push({
      icon: '☕',
      text: 'Slow morning predicted. Start with lighter tasks.',
    })
  }

  // Afternoon recommendation
  if (forecast.afternoon.predicted_energy < forecast.morning.predicted_energy - 2) {
    recs.push({
      icon: '🚶',
      text: 'Energy dip expected afternoon. Plan a walk or break.',
    })
  }

  // Low confidence warning
  if (forecast.historical_accuracy < 60) {
    recs.push({
      icon: '📊',
      text: 'Limited data for this pattern. More tracking will improve accuracy.',
    })
  }

  return recs
}

/**
 * Loading skeleton
 */
function ForecastSkeleton() {
  return (
    <Box
      p={5}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <Flex justify="space-between" mb={5}>
        <Box h="40px" w="150px" bg="gray.800" borderRadius="md" />
        <Box h="40px" w="80px" bg="gray.800" borderRadius="md" />
      </Flex>
      <Grid templateColumns="repeat(3, 1fr)" gap={4}>
        {[1, 2, 3].map((i) => (
          <Box key={i} h="120px" bg="gray.800" borderRadius="lg" />
        ))}
      </Grid>
    </Box>
  )
}

/**
 * Empty state
 */
function EmptyForecast() {
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
        🔮
      </Text>
      <Text fontSize="lg" fontWeight="600" color="white" mb={1}>
        No Forecast Available
      </Text>
      <Text fontSize="sm" color="gray.400">
        Log more energy data to enable predictions
      </Text>
    </Box>
  )
}

/**
 * Compact forecast widget for dashboard
 */
export function ForecastCompact({ forecast }: { forecast?: EnergyForecast | null }) {
  if (!forecast) {
    return null
  }

  const { overall_predicted, best_hours } = forecast
  const color = getEnergyColor(overall_predicted)

  const formatHour = (h: number) => {
    const hour12 = h % 12 || 12
    const ampm = h >= 12 ? 'pm' : 'am'
    return `${hour12}${ampm}`
  }

  return (
    <Flex
      align="center"
      gap={3}
      p={3}
      bg="gray.800/50"
      borderRadius="lg"
    >
      <Box
        w="40px"
        h="40px"
        borderRadius="full"
        bg={`${color}.500/20`}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text fontSize="sm" fontWeight="bold" color={`${color}.400`}>
          {Math.round(overall_predicted)}
        </Text>
      </Box>
      <Box>
        <Text fontSize="sm" color="white" fontWeight="500">
          Predicted Energy
        </Text>
        {best_hours.length > 0 && (
          <Text fontSize="xs" color="gray.500">
            Peak: {formatHour(best_hours[0])}-{formatHour(best_hours[best_hours.length - 1])}
          </Text>
        )}
      </Box>
    </Flex>
  )
}
