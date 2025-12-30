'use client'

import { useState } from 'react'
import {
  Box,
  Flex,
  Text,
  Button,
  VStack,
} from '@chakra-ui/react'
import { FormField, Input, Textarea } from '@/components/ui/form'
import { StandaloneModal } from '@/components/ui/modal'
import { StatusBadge } from './status-badge'
import { ProgressRing } from './progress-ring'
import type { KeyResult, RecordMeasurementPayload } from '@/lib/types/okr'
import { useRecordMeasurement, useMeasurements } from '@/hooks/use-okrs'

interface MeasurementFormProps {
  keyResult: KeyResult
  isOpen: boolean
  onClose: () => void
  onSuccess?: () => void
}

/**
 * Measurement form modal for recording OKR progress
 * Shows current state, allows entering new value and notes
 */
export function MeasurementForm({
  keyResult,
  isOpen,
  onClose,
  onSuccess,
}: MeasurementFormProps) {
  const [value, setValue] = useState(keyResult.current_value.toString())
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)

  const recordMeasurement = useRecordMeasurement()

  // Format value with unit for display
  const formatValue = (val: number) => {
    if (keyResult.unit === '%') return `${val}%`
    if (keyResult.unit === '$') return `$${val.toLocaleString()}`
    if (keyResult.unit) return `${val.toLocaleString()} ${keyResult.unit}`
    return val.toLocaleString()
  }

  // Calculate what the new progress would be
  const calculatePreviewProgress = (): number => {
    const numValue = parseFloat(value)
    if (isNaN(numValue)) return keyResult.progress

    const range = keyResult.target_value - keyResult.start_value
    if (range === 0) return numValue >= keyResult.target_value ? 100 : 0

    const progress = ((numValue - keyResult.start_value) / range) * 100
    return Math.min(100, Math.max(0, progress))
  }

  const previewProgress = calculatePreviewProgress()
  const hasChanged = parseFloat(value) !== keyResult.current_value

  const handleSubmit = async () => {
    const numValue = parseFloat(value)

    // Validation
    if (isNaN(numValue)) {
      setError('Please enter a valid number')
      return
    }

    if (numValue < 0) {
      setError('Value cannot be negative')
      return
    }

    setError(null)

    const payload: RecordMeasurementPayload = {
      kr_id: keyResult.id,
      value: numValue,
      notes: notes.trim() || undefined,
    }

    try {
      await recordMeasurement.mutateAsync(payload)
      onSuccess?.()
      handleClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record measurement')
    }
  }

  const handleClose = () => {
    setValue(keyResult.current_value.toString())
    setNotes('')
    setError(null)
    onClose()
  }

  return (
    <StandaloneModal
      isOpen={isOpen}
      onClose={handleClose}
      title="Record Measurement"
      size="md"
      footer={
        <>
          <Button
            variant="ghost"
            colorPalette="gray"
            onClick={handleClose}
            disabled={recordMeasurement.isPending}
          >
            Cancel
          </Button>
          <Button
            colorPalette="purple"
            onClick={handleSubmit}
            disabled={!hasChanged || recordMeasurement.isPending}
            loading={recordMeasurement.isPending}
          >
            Save Measurement
          </Button>
        </>
      }
    >
      <VStack gap={5} align="stretch">
        {/* Key Result Header */}
        <Box
          p={4}
          bg="gray.800/50"
          borderRadius="lg"
          borderWidth={1}
          borderColor="gray.700"
        >
          <Flex align="start" gap={4}>
            <ProgressRing
              progress={previewProgress}
              size={64}
              strokeWidth={6}
            />
            <Box flex={1}>
              <Flex align="center" gap={2} mb={1}>
                <Text color="white" fontWeight="500">
                  {keyResult.title}
                </Text>
                <StatusBadge status={keyResult.status} size="sm" />
              </Flex>
              {keyResult.description && (
                <Text fontSize="sm" color="gray.400" mb={2}>
                  {keyResult.description}
                </Text>
              )}
              <Flex gap={4} fontSize="sm" color="gray.500">
                <Text>
                  Target: {formatValue(keyResult.target_value)}
                </Text>
                <Text>
                  Start: {formatValue(keyResult.start_value)}
                </Text>
              </Flex>
            </Box>
          </Flex>
        </Box>

        {/* Current vs New Value */}
        <Box>
          <Flex gap={4} mb={4}>
            <Box flex={1}>
              <Text fontSize="xs" color="gray.500" textTransform="uppercase" mb={1}>
                Current Value
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="gray.400">
                {formatValue(keyResult.current_value)}
              </Text>
            </Box>
            <Box flex={1}>
              <Text fontSize="xs" color="gray.500" textTransform="uppercase" mb={1}>
                New Value
              </Text>
              <Text
                fontSize="2xl"
                fontWeight="bold"
                color={hasChanged ? 'purple.400' : 'gray.400'}
              >
                {formatValue(parseFloat(value) || 0)}
              </Text>
            </Box>
          </Flex>

          {/* Progress Change Indicator */}
          {hasChanged && (
            <Box
              p={3}
              bg={previewProgress > keyResult.progress ? 'green.500/10' : 'orange.500/10'}
              borderRadius="md"
              mb={4}
            >
              <Flex align="center" gap={2}>
                <ProgressChangeIcon isPositive={previewProgress >= keyResult.progress} />
                <Text
                  fontSize="sm"
                  color={previewProgress > keyResult.progress ? 'green.400' : 'orange.400'}
                >
                  Progress will change from {Math.round(keyResult.progress)}% to{' '}
                  {Math.round(previewProgress)}%
                  {previewProgress > keyResult.progress
                    ? ` (+${Math.round(previewProgress - keyResult.progress)}%)`
                    : ` (${Math.round(previewProgress - keyResult.progress)}%)`}
                </Text>
              </Flex>
            </Box>
          )}
        </Box>

        {/* Value Input */}
        <FormField
          label="New Value"
          error={error || undefined}
          required
          hint={`Enter the current ${keyResult.unit || 'value'} for this key result`}
        >
          <Input
            type="number"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={`e.g., ${keyResult.target_value}`}
            error={!!error}
            rightIcon={
              keyResult.unit ? (
                <Text fontSize="sm" color="gray.500">
                  {keyResult.unit}
                </Text>
              ) : undefined
            }
          />
        </FormField>

        {/* Notes Input */}
        <FormField
          label="Notes"
          hint="Optional context about this measurement"
        >
          <Textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="What progress was made? Any blockers?"
            rows={3}
          />
        </FormField>
      </VStack>
    </StandaloneModal>
  )
}

/**
 * Progress change icon
 */
function ProgressChangeIcon({ isPositive }: { isPositive: boolean }) {
  if (isPositive) {
    return (
      <svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        color="var(--chakra-colors-green-400)"
      >
        <polyline points="18 15 12 9 6 15" />
      </svg>
    )
  }

  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      color="var(--chakra-colors-orange-400)"
    >
      <polyline points="6 9 12 15 18 9" />
    </svg>
  )
}

/**
 * Compact measurement button for inline use
 */
export function MeasurementButton({
  keyResult,
  onOpenForm,
}: {
  keyResult: KeyResult
  onOpenForm: () => void
}) {
  return (
    <Button
      size="sm"
      variant="ghost"
      color="purple.400"
      _hover={{ bg: 'purple.500/20' }}
      onClick={(e) => {
        e.stopPropagation()
        onOpenForm()
      }}
    >
      <Flex align="center" gap={1.5}>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </svg>
        <span>Update</span>
      </Flex>
    </Button>
  )
}

/**
 * Measurement history display
 */
export function MeasurementHistory({ krId }: { krId: string }) {
  const { data: measurements, isLoading } = useMeasurements(krId)

  if (isLoading) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500" fontSize="sm">Loading history...</Text>
      </Box>
    )
  }

  if (!measurements || measurements.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500" fontSize="sm">No measurements recorded yet</Text>
      </Box>
    )
  }

  return (
    <VStack gap={2} align="stretch">
      <Text fontSize="sm" fontWeight="500" color="gray.300">
        Measurement History
      </Text>
      {measurements.slice(0, 5).map((measurement) => (
        <Box
          key={measurement.id}
          p={3}
          bg="gray.800/50"
          borderRadius="md"
          fontSize="sm"
        >
          <Flex justify="space-between" align="center">
            <Text color="white" fontWeight="500">
              {measurement.value.toLocaleString()}
            </Text>
            <Text color="gray.500" fontSize="xs">
              {new Date(measurement.measured_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
              })}
            </Text>
          </Flex>
          {measurement.notes && (
            <Text color="gray.400" mt={1}>
              {measurement.notes}
            </Text>
          )}
        </Box>
      ))}
    </VStack>
  )
}
