'use client'

import { Box, Flex, Text, VStack, Badge } from '@chakra-ui/react'
import type { UploadFile } from './document-upload-dropzone'

/**
 * Processing stages for document upload
 */
export type ProcessingStage =
  | 'queued'
  | 'uploading'
  | 'extracting'
  | 'analyzing'
  | 'embedding'
  | 'indexing'
  | 'complete'
  | 'error'

/**
 * Stage metadata for display
 */
const STAGE_META: Record<ProcessingStage, { label: string; description: string; color: string }> = {
  queued: { label: 'Queued', description: 'Waiting to start', color: 'gray' },
  uploading: { label: 'Uploading', description: 'Sending file to server', color: 'blue' },
  extracting: { label: 'Extracting', description: 'Extracting text and structure', color: 'cyan' },
  analyzing: { label: 'Analyzing', description: 'AI analyzing content', color: 'purple' },
  embedding: { label: 'Embedding', description: 'Creating vector embeddings', color: 'orange' },
  indexing: { label: 'Indexing', description: 'Saving to knowledge base', color: 'green' },
  complete: { label: 'Complete', description: 'Document processed', color: 'green' },
  error: { label: 'Error', description: 'Processing failed', color: 'red' },
}

/**
 * Processing stage order for progress calculation
 */
const STAGE_ORDER: ProcessingStage[] = [
  'queued',
  'uploading',
  'extracting',
  'analyzing',
  'embedding',
  'indexing',
  'complete',
]

/**
 * Extended file info with processing details
 */
export interface ProcessingFile extends UploadFile {
  stage: ProcessingStage
  stageProgress: number
  extractedText?: string
  entities?: Array<{ name: string; type: string }>
  errorDetails?: string
}

/**
 * Checkmark icon
 */
const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
    <polyline points="20 6 9 17 4 12" />
  </svg>
)

/**
 * Error icon
 */
const ErrorIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="15" y1="9" x2="9" y2="15" />
    <line x1="9" y1="9" x2="15" y2="15" />
  </svg>
)

/**
 * Spinner icon
 */
const SpinnerIcon = () => (
  <Box
    as="span"
    display="inline-block"
    w="14px"
    h="14px"
    borderWidth="2px"
    borderStyle="solid"
    borderColor="currentColor"
    borderTopColor="transparent"
    borderRadius="full"
    animation="spin 0.8s linear infinite"
  />
)

/**
 * Stage indicator component
 */
interface StageIndicatorProps {
  stage: ProcessingStage
  currentStage: ProcessingStage
  isComplete: boolean
  isError: boolean
}

function StageIndicator({ stage, currentStage, isComplete, isError }: StageIndicatorProps) {
  const meta = STAGE_META[stage]
  const currentIndex = STAGE_ORDER.indexOf(currentStage)
  const stageIndex = STAGE_ORDER.indexOf(stage)

  const isPast = stageIndex < currentIndex || isComplete
  const isCurrent = stage === currentStage && !isComplete && !isError
  const isFuture = stageIndex > currentIndex && !isComplete

  const getIcon = () => {
    if (isError && stage === currentStage) return <ErrorIcon />
    if (isPast || (isComplete && stage === 'complete')) return <CheckIcon />
    if (isCurrent) return <SpinnerIcon />
    return null
  }

  const getColor = () => {
    if (isError && stage === currentStage) return 'red'
    if (isPast || (isComplete && stage === 'complete')) return 'green'
    if (isCurrent) return meta.color
    return 'gray'
  }

  return (
    <Flex align="center" gap={3}>
      {/* Stage circle */}
      <Flex
        align="center"
        justify="center"
        w="28px"
        h="28px"
        borderRadius="full"
        borderWidth={2}
        borderColor={`${getColor()}.500`}
        bg={isPast || (isComplete && stage === 'complete') ? `${getColor()}.500` : 'transparent'}
        color={isPast || (isComplete && stage === 'complete') ? 'white' : `${getColor()}.400`}
        transition="all 0.2s"
      >
        {getIcon()}
        {!getIcon() && (
          <Text fontSize="xs" fontWeight="600" color={`${getColor()}.500`}>
            {stageIndex + 1}
          </Text>
        )}
      </Flex>

      {/* Stage label */}
      <Box>
        <Text
          fontSize="sm"
          fontWeight={isCurrent ? '600' : '400'}
          color={isFuture ? 'gray.500' : 'gray.200'}
        >
          {meta.label}
        </Text>
        {isCurrent && (
          <Text fontSize="xs" color="gray.500">
            {meta.description}
          </Text>
        )}
      </Box>
    </Flex>
  )
}

/**
 * Props for UploadProgressIndicator
 */
interface UploadProgressIndicatorProps {
  /** File being processed */
  file: ProcessingFile
  /** Whether to show all stages */
  showAllStages?: boolean
  /** Whether to show extracted content */
  showPreview?: boolean
  /** Callback when user clicks retry */
  onRetry?: () => void
  /** Callback when user clicks cancel */
  onCancel?: () => void
}

export function UploadProgressIndicator({
  file,
  showAllStages = true,
  showPreview = false,
  onRetry,
  onCancel,
}: UploadProgressIndicatorProps) {
  const meta = STAGE_META[file.stage]
  const isComplete = file.stage === 'complete'
  const isError = file.stage === 'error'

  // Calculate overall progress
  const stageIndex = STAGE_ORDER.indexOf(file.stage)
  const overallProgress = isComplete
    ? 100
    : isError
    ? Math.round((stageIndex / (STAGE_ORDER.length - 1)) * 100)
    : Math.round(((stageIndex + file.stageProgress / 100) / (STAGE_ORDER.length - 1)) * 100)

  return (
    <Box
      w="full"
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor={isError ? 'red.500' : isComplete ? 'green.500' : 'gray.700'}
      overflow="hidden"
    >
      {/* Header */}
      <Flex
        align="center"
        justify="space-between"
        px={4}
        py={3}
        borderBottomWidth={1}
        borderColor="gray.800"
      >
        <Flex align="center" gap={3}>
          <Text color="gray.200" fontSize="sm" fontWeight="500">
            {file.name}
          </Text>
          <Badge
            colorPalette={meta.color as any}
            size="sm"
            variant={isComplete || isError ? 'solid' : 'subtle'}
          >
            {meta.label}
          </Badge>
        </Flex>

        <Text color="gray.500" fontSize="sm">
          {overallProgress}%
        </Text>
      </Flex>

      {/* Overall progress bar */}
      <Box px={4} py={2}>
        <Box h="6px" bg="gray.800" borderRadius="full" overflow="hidden">
          <Box
            h="full"
            w={`${overallProgress}%`}
            bg={isError ? 'red.500' : isComplete ? 'green.500' : `${meta.color}.500`}
            transition="width 0.3s ease-out"
          />
        </Box>
      </Box>

      {/* Stage indicators */}
      {showAllStages && (
        <Box px={4} py={3}>
          <VStack align="stretch" gap={2}>
            {STAGE_ORDER.slice(1).map((stage) => (
              <StageIndicator
                key={stage}
                stage={stage}
                currentStage={file.stage}
                isComplete={isComplete}
                isError={isError}
              />
            ))}
          </VStack>
        </Box>
      )}

      {/* Error details */}
      {isError && file.errorDetails && (
        <Box px={4} py={3} bg="red.900" borderTopWidth={1} borderColor="red.800">
          <Text color="red.200" fontSize="sm">
            {file.errorDetails}
          </Text>
          {(onRetry || onCancel) && (
            <Flex gap={2} mt={3}>
              {onRetry && (
                <Box
                  as="button"
                  px={3}
                  py={1}
                  bg="red.700"
                  borderRadius="md"
                  fontSize="sm"
                  fontWeight="500"
                  color="white"
                  _hover={{ bg: 'red.600' }}
                  onClick={onRetry}
                >
                  Retry
                </Box>
              )}
              {onCancel && (
                <Box
                  as="button"
                  px={3}
                  py={1}
                  bg="gray.700"
                  borderRadius="md"
                  fontSize="sm"
                  fontWeight="500"
                  color="gray.200"
                  _hover={{ bg: 'gray.600' }}
                  onClick={onCancel}
                >
                  Cancel
                </Box>
              )}
            </Flex>
          )}
        </Box>
      )}

      {/* Preview extracted content */}
      {showPreview && isComplete && file.extractedText && (
        <Box px={4} py={3} bg="gray.850" borderTopWidth={1} borderColor="gray.800">
          <Text color="gray.400" fontSize="xs" fontWeight="600" mb={2}>
            EXTRACTED CONTENT
          </Text>
          <Text color="gray.300" fontSize="sm" lineHeight="1.6">
            {file.extractedText.length > 300
              ? `${file.extractedText.substring(0, 300)}...`
              : file.extractedText}
          </Text>

          {/* Extracted entities */}
          {file.entities && file.entities.length > 0 && (
            <Box mt={3}>
              <Text color="gray.400" fontSize="xs" fontWeight="600" mb={2}>
                ENTITIES FOUND ({file.entities.length})
              </Text>
              <Flex gap={2} flexWrap="wrap">
                {file.entities.slice(0, 10).map((entity, i) => (
                  <Badge
                    key={i}
                    colorPalette="purple"
                    size="sm"
                    variant="subtle"
                  >
                    {entity.name}
                  </Badge>
                ))}
                {file.entities.length > 10 && (
                  <Badge colorPalette="gray" size="sm" variant="subtle">
                    +{file.entities.length - 10} more
                  </Badge>
                )}
              </Flex>
            </Box>
          )}
        </Box>
      )}

      {/* Completion message */}
      {isComplete && !showPreview && (
        <Box px={4} py={3} bg="green.900" borderTopWidth={1} borderColor="green.800">
          <Flex align="center" gap={2}>
            <Box color="green.400">
              <CheckIcon />
            </Box>
            <Text color="green.200" fontSize="sm">
              Document successfully processed and added to your knowledge base
            </Text>
          </Flex>
        </Box>
      )}
    </Box>
  )
}

/**
 * Compact progress indicator for multiple files
 */
interface CompactProgressProps {
  files: ProcessingFile[]
}

export function CompactUploadProgress({ files }: CompactProgressProps) {
  const completedCount = files.filter((f) => f.stage === 'complete').length
  const errorCount = files.filter((f) => f.stage === 'error').length
  const processingCount = files.filter(
    (f) => f.stage !== 'complete' && f.stage !== 'error' && f.stage !== 'queued'
  ).length
  const queuedCount = files.filter((f) => f.stage === 'queued').length

  // Calculate overall progress
  const totalProgress = files.reduce((sum, file) => {
    const stageIndex = STAGE_ORDER.indexOf(file.stage)
    const stageProgress = file.stage === 'complete' ? 100 : file.stage === 'error' ? 0 : file.stageProgress
    return sum + (stageIndex / (STAGE_ORDER.length - 1)) * 100 + stageProgress / (STAGE_ORDER.length - 1)
  }, 0)
  const averageProgress = Math.round(totalProgress / files.length)

  return (
    <Box
      w="full"
      bg="gray.900"
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.700"
      p={4}
    >
      {/* Header */}
      <Flex align="center" justify="space-between" mb={3}>
        <Text color="gray.200" fontSize="md" fontWeight="600">
          Processing {files.length} files
        </Text>
        <Text color="gray.500" fontSize="sm">
          {averageProgress}%
        </Text>
      </Flex>

      {/* Progress bar */}
      <Box h="8px" bg="gray.800" borderRadius="full" overflow="hidden" mb={3}>
        <Box
          h="full"
          w={`${averageProgress}%`}
          bg="purple.500"
          transition="width 0.3s ease-out"
        />
      </Box>

      {/* Status summary */}
      <Flex gap={4} justify="center">
        {completedCount > 0 && (
          <Flex align="center" gap={1}>
            <Box color="green.400">
              <CheckIcon />
            </Box>
            <Text color="green.400" fontSize="sm">
              {completedCount} complete
            </Text>
          </Flex>
        )}
        {processingCount > 0 && (
          <Flex align="center" gap={1}>
            <Box color="purple.400">
              <SpinnerIcon />
            </Box>
            <Text color="purple.400" fontSize="sm">
              {processingCount} processing
            </Text>
          </Flex>
        )}
        {queuedCount > 0 && (
          <Text color="gray.500" fontSize="sm">
            {queuedCount} queued
          </Text>
        )}
        {errorCount > 0 && (
          <Flex align="center" gap={1}>
            <Box color="red.400">
              <ErrorIcon />
            </Box>
            <Text color="red.400" fontSize="sm">
              {errorCount} failed
            </Text>
          </Flex>
        )}
      </Flex>
    </Box>
  )
}
