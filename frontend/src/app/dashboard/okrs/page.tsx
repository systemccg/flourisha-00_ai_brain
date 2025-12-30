'use client'

import { useState } from 'react'
import { Box, Flex, Button, Text, VStack, Spinner } from '@chakra-ui/react'
import { PageContainer, PageHeader } from '@/components/layout'
import {
  QuarterSelector,
  OKRSummary,
  ObjectiveCard,
  MeasurementForm,
} from '@/components/okrs'
import { ErrorDisplay } from '@/components/ui/error-display'
import { useOKRs } from '@/hooks/use-okrs'
import type { Quarter, Objective, KeyResult } from '@/lib/types/okr'
import { getCurrentQuarter } from '@/lib/types/okr'

/**
 * Plus icon component
 */
function PlusIcon() {
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
    >
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  )
}

/**
 * OKR Dashboard Page
 * Displays quarterly objectives with key results
 */
export default function OKRsPage() {
  const [selectedQuarter, setSelectedQuarter] = useState<Quarter>(getCurrentQuarter())
  const [expandedObjectives, setExpandedObjectives] = useState<Set<string>>(new Set())
  const [selectedKeyResult, setSelectedKeyResult] = useState<KeyResult | null>(null)
  const [isMeasurementModalOpen, setIsMeasurementModalOpen] = useState(false)

  const { data, isLoading, error, refetch } = useOKRs(selectedQuarter)

  // Toggle objective expansion
  const toggleObjective = (id: string) => {
    setExpandedObjectives((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  // Expand/collapse all
  const expandAll = () => {
    if (data?.objectives) {
      setExpandedObjectives(new Set(data.objectives.map((o) => o.id)))
    }
  }

  const collapseAll = () => {
    setExpandedObjectives(new Set())
  }

  // Handle key result selection - opens measurement modal
  const handleSelectKeyResult = (kr: KeyResult) => {
    setSelectedKeyResult(kr)
    setIsMeasurementModalOpen(true)
  }

  // Handle closing measurement modal
  const handleCloseMeasurementModal = () => {
    setIsMeasurementModalOpen(false)
    setSelectedKeyResult(null)
  }

  // Handle successful measurement
  const handleMeasurementSuccess = () => {
    refetch() // Refresh the OKR data
  }

  // Handle objective selection (for future edit modal)
  const handleSelectObjective = (objective: Objective) => {
    // TODO: Open objective detail modal
    console.log('Selected Objective:', objective)
  }

  return (
    <PageContainer>
      <PageHeader
        title="OKRs"
        description="Track your quarterly objectives and key results"
        actions={
          <Flex gap={2}>
            <Button
              size="sm"
              variant="ghost"
              color="gray.400"
              _hover={{ color: 'white', bg: 'gray.800' }}
              onClick={() => (expandedObjectives.size > 0 ? collapseAll() : expandAll())}
            >
              {expandedObjectives.size > 0 ? 'Collapse All' : 'Expand All'}
            </Button>
            <Button
              size="sm"
              bg="purple.500"
              color="white"
              _hover={{ bg: 'purple.400' }}
            >
              <Flex align="center" gap={2}>
                <PlusIcon />
                <span>New Objective</span>
              </Flex>
            </Button>
          </Flex>
        }
      />

      {/* Quarter Selector */}
      <Box mb={6}>
        <QuarterSelector selected={selectedQuarter} onChange={setSelectedQuarter} />
      </Box>

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
      {data && (
        <VStack gap={6} align="stretch">
          {/* Summary */}
          <OKRSummary summary={data.summary} />

          {/* Objectives List */}
          {data.objectives.length > 0 ? (
            <VStack gap={4} align="stretch">
              {data.objectives.map((objective) => (
                <ObjectiveCard
                  key={objective.id}
                  objective={objective}
                  isExpanded={expandedObjectives.has(objective.id)}
                  onToggleExpand={() => toggleObjective(objective.id)}
                  onSelectKeyResult={handleSelectKeyResult}
                  onSelectObjective={handleSelectObjective}
                />
              ))}
            </VStack>
          ) : (
            <EmptyOKRs quarter={selectedQuarter} />
          )}
        </VStack>
      )}

      {/* Measurement Modal */}
      {selectedKeyResult && (
        <MeasurementForm
          keyResult={selectedKeyResult}
          isOpen={isMeasurementModalOpen}
          onClose={handleCloseMeasurementModal}
          onSuccess={handleMeasurementSuccess}
        />
      )}
    </PageContainer>
  )
}

/**
 * Empty state when no OKRs exist for the quarter
 */
function EmptyOKRs({ quarter }: { quarter: Quarter }) {
  return (
    <Box
      p={12}
      textAlign="center"
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.800"
    >
      <Box
        w={16}
        h={16}
        mx="auto"
        mb={4}
        borderRadius="full"
        bg="purple.500/20"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          color="var(--chakra-colors-purple-400)"
        >
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" />
        </svg>
      </Box>
      <Text fontSize="xl" fontWeight="600" color="white" mb={2}>
        No objectives for {quarter}
      </Text>
      <Text color="gray.400" mb={6} maxW="md" mx="auto">
        Start by creating your first objective with measurable key results to track your
        quarterly progress.
      </Text>
      <Button
        bg="purple.500"
        color="white"
        _hover={{ bg: 'purple.400' }}
      >
        <Flex align="center" gap={2}>
          <PlusIcon />
          <span>Create First Objective</span>
        </Flex>
      </Button>
    </Box>
  )
}
