'use client'

import { Box, Flex, Text, VStack, Badge, Grid, GridItem } from '@chakra-ui/react'
import { StandaloneModal } from '@/components/ui'
import type { EntityType, ENTITY_TYPES } from '@/lib/types'

/**
 * Entity found in document
 */
export interface DocumentEntity {
  name: string
  type: EntityType
  confidence?: number
  context?: string
}

/**
 * Relationship between entities
 */
export interface DocumentRelationship {
  source: string
  target: string
  type: string
  confidence?: number
}

/**
 * Document preview data
 */
export interface DocumentPreviewData {
  id: string
  name: string
  type: string
  size: number
  uploadedAt: string
  extractedText: string
  summary?: string
  entities: DocumentEntity[]
  relationships?: DocumentRelationship[]
  chunks?: Array<{
    index: number
    text: string
    embedding_id?: string
  }>
  processingDetails?: {
    backend: 'claude' | 'docling'
    duration_ms: number
    extractionMethod: string
    warnings?: string[]
  }
}

/**
 * Entity type colors matching graph types
 */
const ENTITY_COLORS: Record<string, string> = {
  person: 'blue',
  organization: 'purple',
  medication: 'green',
  condition: 'red',
  document: 'yellow',
  project: 'orange',
  topic: 'cyan',
  date: 'gray',
  location: 'green',
  unknown: 'gray',
  vital_sign: 'pink',
  procedure: 'orange',
  instruction: 'cyan',
  allergy: 'red',
}

/**
 * Format file size
 */
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

/**
 * Format date
 */
function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Section header component
 */
function SectionHeader({ title, count }: { title: string; count?: number }) {
  return (
    <Flex align="center" gap={2} mb={3}>
      <Text color="gray.400" fontSize="xs" fontWeight="600" textTransform="uppercase">
        {title}
      </Text>
      {count !== undefined && (
        <Badge colorPalette="gray" size="sm" variant="subtle">
          {count}
        </Badge>
      )}
    </Flex>
  )
}

/**
 * Entity list component
 */
function EntityList({ entities }: { entities: DocumentEntity[] }) {
  // Group by type
  const grouped = entities.reduce((acc, entity) => {
    if (!acc[entity.type]) acc[entity.type] = []
    acc[entity.type].push(entity)
    return acc
  }, {} as Record<string, DocumentEntity[]>)

  return (
    <VStack align="stretch" gap={4}>
      {Object.entries(grouped).map(([type, typeEntities]) => (
        <Box key={type}>
          <Text
            color="gray.400"
            fontSize="xs"
            fontWeight="600"
            textTransform="capitalize"
            mb={2}
          >
            {type} ({typeEntities.length})
          </Text>
          <Flex gap={2} flexWrap="wrap">
            {typeEntities.map((entity, i) => (
              <Badge
                key={i}
                colorPalette={ENTITY_COLORS[type] || 'gray'}
                size="sm"
                variant="subtle"
                title={entity.context || entity.name}
              >
                {entity.name}
                {entity.confidence && entity.confidence < 0.8 && (
                  <Text as="span" color="gray.500" ml={1}>
                    ({Math.round(entity.confidence * 100)}%)
                  </Text>
                )}
              </Badge>
            ))}
          </Flex>
        </Box>
      ))}
    </VStack>
  )
}

/**
 * Relationship visualization (simple list)
 */
function RelationshipList({ relationships }: { relationships: DocumentRelationship[] }) {
  return (
    <VStack align="stretch" gap={2}>
      {relationships.slice(0, 10).map((rel, i) => (
        <Flex
          key={i}
          align="center"
          gap={2}
          px={3}
          py={2}
          bg="gray.850"
          borderRadius="md"
          fontSize="sm"
        >
          <Text color="gray.300" fontWeight="500">
            {rel.source}
          </Text>
          <Box color="gray.500">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </Box>
          <Badge colorPalette="purple" size="sm" variant="subtle">
            {rel.type}
          </Badge>
          <Box color="gray.500">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </Box>
          <Text color="gray.300" fontWeight="500">
            {rel.target}
          </Text>
        </Flex>
      ))}
      {relationships.length > 10 && (
        <Text color="gray.500" fontSize="xs" textAlign="center">
          +{relationships.length - 10} more relationships
        </Text>
      )}
    </VStack>
  )
}

/**
 * Props for DocumentPreviewModal
 */
interface DocumentPreviewModalProps {
  /** Whether the modal is open */
  isOpen: boolean
  /** Called when modal should close */
  onClose: () => void
  /** Document data to display */
  document: DocumentPreviewData | null
}

export function DocumentPreviewModal({
  isOpen,
  onClose,
  document,
}: DocumentPreviewModalProps) {
  if (!document) return null

  return (
    <StandaloneModal
      isOpen={isOpen}
      onClose={onClose}
      title={document.name}
      size="xl"
      showClose
    >
      <VStack align="stretch" gap={6}>
        {/* Document metadata */}
        <Grid templateColumns="repeat(3, 1fr)" gap={4}>
          <GridItem>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={1}>
              TYPE
            </Text>
            <Badge colorPalette="purple" size="sm">
              {document.type.toUpperCase()}
            </Badge>
          </GridItem>
          <GridItem>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={1}>
              SIZE
            </Text>
            <Text color="gray.300" fontSize="sm">
              {formatFileSize(document.size)}
            </Text>
          </GridItem>
          <GridItem>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={1}>
              UPLOADED
            </Text>
            <Text color="gray.300" fontSize="sm">
              {formatDate(document.uploadedAt)}
            </Text>
          </GridItem>
        </Grid>

        {/* Processing details */}
        {document.processingDetails && (
          <Box bg="gray.850" borderRadius="lg" p={4}>
            <SectionHeader title="Processing Details" />
            <Grid templateColumns="repeat(2, 1fr)" gap={4}>
              <Box>
                <Text color="gray.500" fontSize="xs">
                  Backend
                </Text>
                <Badge
                  colorPalette={document.processingDetails.backend === 'claude' ? 'purple' : 'blue'}
                  size="sm"
                  mt={1}
                >
                  {document.processingDetails.backend}
                </Badge>
              </Box>
              <Box>
                <Text color="gray.500" fontSize="xs">
                  Duration
                </Text>
                <Text color="gray.300" fontSize="sm">
                  {(document.processingDetails.duration_ms / 1000).toFixed(1)}s
                </Text>
              </Box>
            </Grid>

            {/* Warnings */}
            {document.processingDetails.warnings && document.processingDetails.warnings.length > 0 && (
              <Box mt={3} pt={3} borderTopWidth={1} borderColor="gray.700">
                <Text color="yellow.400" fontSize="xs" fontWeight="600" mb={2}>
                  WARNINGS
                </Text>
                {document.processingDetails.warnings.map((warning, i) => (
                  <Text key={i} color="yellow.200" fontSize="sm">
                    {warning}
                  </Text>
                ))}
              </Box>
            )}
          </Box>
        )}

        {/* Summary */}
        {document.summary && (
          <Box>
            <SectionHeader title="AI Summary" />
            <Box bg="gray.850" borderRadius="lg" p={4}>
              <Text color="gray.300" fontSize="sm" lineHeight="1.7">
                {document.summary}
              </Text>
            </Box>
          </Box>
        )}

        {/* Extracted entities */}
        {document.entities.length > 0 && (
          <Box>
            <SectionHeader title="Extracted Entities" count={document.entities.length} />
            <Box bg="gray.850" borderRadius="lg" p={4}>
              <EntityList entities={document.entities} />
            </Box>
          </Box>
        )}

        {/* Relationships */}
        {document.relationships && document.relationships.length > 0 && (
          <Box>
            <SectionHeader title="Relationships" count={document.relationships.length} />
            <Box bg="gray.850" borderRadius="lg" p={4}>
              <RelationshipList relationships={document.relationships} />
            </Box>
          </Box>
        )}

        {/* Extracted text preview */}
        <Box>
          <SectionHeader title="Extracted Text" />
          <Box
            bg="gray.850"
            borderRadius="lg"
            p={4}
            maxH="300px"
            overflowY="auto"
          >
            <Text
              color="gray.300"
              fontSize="sm"
              lineHeight="1.7"
              whiteSpace="pre-wrap"
              fontFamily="mono"
            >
              {document.extractedText.length > 5000
                ? `${document.extractedText.substring(0, 5000)}...`
                : document.extractedText}
            </Text>
          </Box>
        </Box>

        {/* Chunks info */}
        {document.chunks && document.chunks.length > 0 && (
          <Box>
            <SectionHeader title="Vector Chunks" count={document.chunks.length} />
            <Text color="gray.500" fontSize="sm">
              Document split into {document.chunks.length} chunks for semantic search.
              Each chunk is approximately 1000 characters with 200 character overlap.
            </Text>
          </Box>
        )}
      </VStack>
    </StandaloneModal>
  )
}
