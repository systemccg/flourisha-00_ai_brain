'use client'

import { Box, Flex, Text, VStack, Badge, Button, Spinner } from '@chakra-ui/react'
import type {
  ForceGraphNode,
  GraphEntity,
  RelatedEntitiesResponse,
  EntityType,
  RelationshipType,
} from '@/lib/types'
import { getEntityTypeMeta, getRelationshipTypeMeta } from '@/lib/types'

/**
 * Icons for entity types
 */
const EntityIcons: Record<EntityType, React.ReactNode> = {
  person: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  ),
  organization: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 21h18" />
      <path d="M9 8h1" />
      <path d="M9 12h1" />
      <path d="M9 16h1" />
      <path d="M14 8h1" />
      <path d="M14 12h1" />
      <path d="M14 16h1" />
      <path d="M5 21V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16" />
    </svg>
  ),
  medication: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z" />
      <path d="m8.5 8.5 7 7" />
    </svg>
  ),
  condition: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
    </svg>
  ),
  document: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  ),
  project: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </svg>
  ),
  topic: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 9h16" />
      <path d="M4 15h16" />
      <path d="M10 3L8 21" />
      <path d="M16 3l-2 18" />
    </svg>
  ),
  date: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  ),
  location: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  ),
  unknown: (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
}

/**
 * Close icon
 */
const CloseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

/**
 * Expand icon
 */
const ExpandIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="15 3 21 3 21 9" />
    <polyline points="9 21 3 21 3 15" />
    <line x1="21" y1="3" x2="14" y2="10" />
    <line x1="3" y1="21" x2="10" y2="14" />
  </svg>
)

/**
 * Related entity item component
 */
interface RelatedItemProps {
  entity: GraphEntity
  relationship: {
    type: RelationshipType
    properties?: Record<string, unknown>
  }
  onClick?: () => void
}

function RelatedItem({ entity, relationship, onClick }: RelatedItemProps) {
  const entityMeta = getEntityTypeMeta(entity.type)
  const relMeta = getRelationshipTypeMeta(relationship.type)

  return (
    <Box
      as="button"
      display="flex"
      alignItems="center"
      gap={3}
      w="full"
      p={2}
      bg="transparent"
      border="none"
      borderRadius="md"
      cursor="pointer"
      textAlign="left"
      transition="all 0.1s"
      _hover={{ bg: 'gray.800' }}
      onClick={onClick}
    >
      <Box color={`${entityMeta.color}.400`} flexShrink={0}>
        {EntityIcons[entity.type] || EntityIcons.unknown}
      </Box>
      <Box flex={1} overflow="hidden">
        <Text
          color="gray.200"
          fontSize="sm"
          fontWeight="500"
          overflow="hidden"
          textOverflow="ellipsis"
          whiteSpace="nowrap"
        >
          {entity.name}
        </Text>
        <Badge colorPalette={relMeta.color as any} size="sm" variant="subtle">
          {relMeta.label}
        </Badge>
      </Box>
    </Box>
  )
}

/**
 * Props for NodeDetailSidebar
 */
interface NodeDetailSidebarProps {
  /** Selected node to display */
  node: ForceGraphNode | null
  /** Related entities data */
  relatedData?: RelatedEntitiesResponse | null
  /** Whether related data is loading */
  isLoading?: boolean
  /** Error from loading related data */
  error?: Error | null
  /** Called when close button is clicked */
  onClose: () => void
  /** Called when expand button is clicked */
  onExpand?: (entityName: string) => void
  /** Called when a related entity is clicked */
  onRelatedClick?: (entity: GraphEntity) => void
}

export function NodeDetailSidebar({
  node,
  relatedData,
  isLoading,
  error,
  onClose,
  onExpand,
  onRelatedClick,
}: NodeDetailSidebarProps) {
  if (!node) {
    return (
      <Box
        bg="gray.900"
        borderRadius="xl"
        p={6}
        h="full"
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
      >
        <Box color="gray.600" mb={4}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        </Box>
        <Text color="gray.500" fontSize="sm" textAlign="center">
          Select a node in the graph to see details
        </Text>
      </Box>
    )
  }

  const entityMeta = getEntityTypeMeta(node.type)

  return (
    <Box
      bg="gray.900"
      borderRadius="xl"
      overflow="hidden"
      h="full"
      display="flex"
      flexDirection="column"
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
        <Text color="gray.400" fontSize="sm" fontWeight="500">
          Node Details
        </Text>
        <button
          type="button"
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#6b7280',
            cursor: 'pointer',
            padding: '4px',
          }}
        >
          <CloseIcon />
        </button>
      </Flex>

      {/* Content */}
      <Box flex={1} overflowY="auto" p={4}>
        <VStack align="stretch" gap={4}>
          {/* Entity icon and name */}
          <Flex align="center" gap={3}>
            <Box
              p={3}
              bg={`${entityMeta.color}.900`}
              color={`${entityMeta.color}.400`}
              borderRadius="xl"
            >
              {EntityIcons[node.type] || EntityIcons.unknown}
            </Box>
            <Box flex={1}>
              <Text color="white" fontSize="lg" fontWeight="600">
                {node.name}
              </Text>
              <Badge colorPalette={entityMeta.color as any} size="sm" variant="solid">
                {entityMeta.label}
              </Badge>
            </Box>
          </Flex>

          {/* Actions */}
          <Flex gap={2}>
            <Button
              size="sm"
              colorPalette="purple"
              variant="solid"
              flex={1}
              onClick={() => onExpand?.(node.name)}
            >
              <ExpandIcon />
              <Text ml={2}>Expand</Text>
            </Button>
          </Flex>

          {/* Related entities */}
          <Box>
            <Flex align="center" justify="space-between" mb={3}>
              <Text color="gray.500" fontSize="xs" fontWeight="600" textTransform="uppercase">
                Related Entities
              </Text>
              {relatedData && (
                <Text color="gray.600" fontSize="xs">
                  {relatedData.related.length} found
                </Text>
              )}
            </Flex>

            {isLoading ? (
              <Flex align="center" justify="center" py={8}>
                <Spinner size="md" color="purple.400" />
              </Flex>
            ) : error ? (
              <Box
                bg="red.900"
                borderWidth={1}
                borderColor="red.700"
                borderRadius="lg"
                p={3}
              >
                <Text color="red.300" fontSize="sm">
                  Failed to load related entities
                </Text>
              </Box>
            ) : relatedData && relatedData.related.length > 0 ? (
              <VStack align="stretch" gap={1}>
                {relatedData.related.map(({ entity, relationship }) => (
                  <RelatedItem
                    key={entity.id}
                    entity={entity}
                    relationship={relationship}
                    onClick={() => onRelatedClick?.(entity)}
                  />
                ))}
              </VStack>
            ) : (
              <Text color="gray.600" fontSize="sm" textAlign="center" py={4}>
                No related entities found
              </Text>
            )}
          </Box>

          {/* Properties */}
          {node.val && (
            <Box>
              <Text color="gray.500" fontSize="xs" fontWeight="600" textTransform="uppercase" mb={2}>
                Properties
              </Text>
              <Box bg="gray.800" borderRadius="lg" p={3}>
                <Flex justify="space-between" align="center">
                  <Text color="gray.400" fontSize="sm">
                    Connections
                  </Text>
                  <Text color="white" fontSize="sm" fontWeight="500">
                    {node.val}
                  </Text>
                </Flex>
              </Box>
            </Box>
          )}
        </VStack>
      </Box>
    </Box>
  )
}
