'use client'

import { useState } from 'react'
import { Box, Flex, Text, Button, VStack, Spinner } from '@chakra-ui/react'
import { EnergySlider, EnergyBadge } from './energy-slider'
import { FocusButtons, FocusBadge } from './focus-buttons'
import { useLogEnergy, useEnergyStreak, useTodayEnergy } from '@/hooks/use-energy'
import type { FocusQuality, LogEnergyPayload } from '@/lib/types/energy'

interface EnergyWidgetProps {
  onSuccess?: () => void
  compact?: boolean
}

/**
 * Energy tracking widget for quick energy logging
 * Includes energy slider, focus quality buttons, and streak display
 */
export function EnergyWidget({ onSuccess, compact = false }: EnergyWidgetProps) {
  const [energyLevel, setEnergyLevel] = useState(5)
  const [focusQuality, setFocusQuality] = useState<FocusQuality | null>(null)
  const [currentTask, setCurrentTask] = useState('')
  const [showTaskInput, setShowTaskInput] = useState(false)

  const logEnergy = useLogEnergy()
  const { data: streak, isLoading: streakLoading } = useEnergyStreak()
  const { data: todayEntries } = useTodayEnergy()

  const canSubmit = focusQuality !== null

  const handleSubmit = async () => {
    if (!canSubmit) return

    const payload: LogEnergyPayload = {
      energy_level: energyLevel,
      focus_quality: focusQuality,
      current_task: currentTask.trim() || undefined,
    }

    try {
      await logEnergy.mutateAsync(payload)
      // Reset form
      setEnergyLevel(5)
      setFocusQuality(null)
      setCurrentTask('')
      setShowTaskInput(false)
      onSuccess?.()
    } catch (error) {
      console.error('Failed to log energy:', error)
    }
  }

  if (compact) {
    return (
      <CompactEnergyWidget
        energyLevel={energyLevel}
        focusQuality={focusQuality}
        onEnergyChange={setEnergyLevel}
        onFocusChange={setFocusQuality}
        onSubmit={handleSubmit}
        isSubmitting={logEnergy.isPending}
        canSubmit={canSubmit}
        todayCount={todayEntries?.length ?? 0}
      />
    )
  }

  return (
    <Box
      p={6}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <VStack gap={6} align="stretch">
        {/* Header with Streak */}
        <Flex justify="space-between" align="center">
          <Box>
            <Text fontSize="lg" fontWeight="600" color="white">
              Energy Check
            </Text>
            <Text fontSize="sm" color="gray.400">
              How are you feeling right now?
            </Text>
          </Box>
          {streak && !streakLoading && (
            <StreakDisplay
              currentStreak={streak.current_streak}
              entriesToday={streak.entries_today}
            />
          )}
        </Flex>

        {/* Energy Slider */}
        <Box>
          <Text fontSize="sm" color="gray.400" mb={3} fontWeight="500">
            Energy Level
          </Text>
          <EnergySlider
            value={energyLevel}
            onChange={setEnergyLevel}
            disabled={logEnergy.isPending}
          />
        </Box>

        {/* Focus Quality */}
        <Box>
          <Text fontSize="sm" color="gray.400" mb={3} fontWeight="500">
            Focus Quality
          </Text>
          <FocusButtons
            value={focusQuality}
            onChange={setFocusQuality}
            disabled={logEnergy.isPending}
            showDescriptions
          />
        </Box>

        {/* Optional Task Input */}
        <Box>
          {!showTaskInput ? (
            <Button
              variant="ghost"
              size="sm"
              color="gray.500"
              _hover={{ color: 'gray.300' }}
              onClick={() => setShowTaskInput(true)}
            >
              + Add current task (optional)
            </Button>
          ) : (
            <Box>
              <Text fontSize="sm" color="gray.400" mb={2} fontWeight="500">
                Current Task
              </Text>
              <input
                type="text"
                value={currentTask}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setCurrentTask(e.target.value)
                }
                placeholder="What are you working on?"
                disabled={logEnergy.isPending}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  backgroundColor: 'var(--chakra-colors-gray-800)',
                  borderRadius: '8px',
                  border: '1px solid var(--chakra-colors-gray-700)',
                  color: 'white',
                  fontSize: '14px',
                  outline: 'none',
                }}
              />
            </Box>
          )}
        </Box>

        {/* Submit Button */}
        <Button
          bg="purple.500"
          color="white"
          _hover={{ bg: 'purple.400' }}
          _disabled={{ bg: 'gray.700', cursor: 'not-allowed' }}
          disabled={!canSubmit || logEnergy.isPending}
          onClick={handleSubmit}
          size="lg"
        >
          {logEnergy.isPending ? (
            <Flex align="center" gap={2}>
              <Spinner size="sm" />
              <span>Saving...</span>
            </Flex>
          ) : (
            'Log Energy'
          )}
        </Button>

        {/* Today's Entries */}
        {todayEntries && todayEntries.length > 0 && (
          <Box pt={4} borderTopWidth={1} borderColor="gray.800">
            <Text fontSize="sm" color="gray.400" mb={3}>
              Today&apos;s Entries ({todayEntries.length})
            </Text>
            <Flex gap={2} flexWrap="wrap">
              {todayEntries.map((entry) => (
                <TodayEntryBadge key={entry.id} entry={entry} />
              ))}
            </Flex>
          </Box>
        )}
      </VStack>
    </Box>
  )
}

/**
 * Compact version of the energy widget
 */
function CompactEnergyWidget({
  energyLevel,
  focusQuality,
  onEnergyChange,
  onFocusChange,
  onSubmit,
  isSubmitting,
  canSubmit,
  todayCount,
}: {
  energyLevel: number
  focusQuality: FocusQuality | null
  onEnergyChange: (value: number) => void
  onFocusChange: (value: FocusQuality) => void
  onSubmit: () => void
  isSubmitting: boolean
  canSubmit: boolean
  todayCount: number
}) {
  return (
    <Box
      p={4}
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <VStack gap={4} align="stretch">
        <Flex justify="space-between" align="center">
          <Text fontSize="sm" fontWeight="600" color="white">
            Quick Energy Log
          </Text>
          {todayCount > 0 && (
            <Text fontSize="xs" color="gray.500">
              {todayCount} today
            </Text>
          )}
        </Flex>

        <EnergySlider
          value={energyLevel}
          onChange={onEnergyChange}
          disabled={isSubmitting}
          size="sm"
          showLabels={false}
        />

        <FocusButtons
          value={focusQuality}
          onChange={onFocusChange}
          disabled={isSubmitting}
          size="sm"
        />

        <Button
          bg="purple.500"
          color="white"
          _hover={{ bg: 'purple.400' }}
          _disabled={{ bg: 'gray.700' }}
          disabled={!canSubmit || isSubmitting}
          onClick={onSubmit}
          size="sm"
        >
          {isSubmitting ? <Spinner size="xs" /> : 'Log'}
        </Button>
      </VStack>
    </Box>
  )
}

/**
 * Streak display component
 */
function StreakDisplay({
  currentStreak,
  entriesToday,
}: {
  currentStreak: number
  entriesToday: number
}) {
  return (
    <Flex align="center" gap={3}>
      <Box textAlign="right">
        <Flex align="center" gap={1}>
          <Text fontSize="lg">🔥</Text>
          <Text fontSize="lg" fontWeight="bold" color="orange.400">
            {currentStreak}
          </Text>
        </Flex>
        <Text fontSize="xs" color="gray.500">
          day streak
        </Text>
      </Box>
      <Box
        w="1px"
        h="30px"
        bg="gray.700"
      />
      <Box textAlign="right">
        <Text fontSize="lg" fontWeight="bold" color="purple.400">
          {entriesToday}
        </Text>
        <Text fontSize="xs" color="gray.500">
          today
        </Text>
      </Box>
    </Flex>
  )
}

/**
 * Today's entry badge
 */
function TodayEntryBadge({ entry }: { entry: { energy_level: number; focus_quality: FocusQuality; timestamp: string } }) {
  const time = new Date(entry.timestamp).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  })

  return (
    <Flex
      align="center"
      gap={2}
      px={3}
      py={1.5}
      bg="gray.800/50"
      borderRadius="full"
    >
      <EnergyBadge value={entry.energy_level} />
      <FocusBadge value={entry.focus_quality} size="sm" showEmoji={false} />
      <Text fontSize="xs" color="gray.500">
        {time}
      </Text>
    </Flex>
  )
}
