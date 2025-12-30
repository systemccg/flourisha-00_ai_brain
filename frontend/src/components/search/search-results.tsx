'use client'

import { Box, Flex, Text, VStack, Badge } from '@chakra-ui/react'
import { type SearchResult, getContentTypeMeta } from '@/lib/types'
import { Loading } from '@/components/ui'

/**
 * Content type icons
 */
const ContentIcons: Record<string, React.ReactNode> = {
  youtube_video: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
    </svg>
  ),
  document: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  ),
  email: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  ),
  note: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  ),
  webpage: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
    </svg>
  ),
  unknown: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  ),
}

/**
 * Get icon for content type
 */
function getContentIcon(type: string): React.ReactNode {
  return ContentIcons[type] || ContentIcons.unknown
}

/**
 * Color mappings for content types
 */
const typeColors: Record<string, string> = {
  youtube_video: 'red.400',
  document: 'blue.400',
  email: 'green.400',
  note: 'yellow.400',
  webpage: 'purple.400',
  unknown: 'gray.400',
}

/**
 * Individual search result item
 */
interface SearchResultItemProps {
  result: SearchResult
  isSelected: boolean
  onSelect: (id: string) => void
  onHover: () => void
}

function SearchResultItem({
  result,
  isSelected,
  onSelect,
  onHover,
}: SearchResultItemProps) {
  const typeMeta = getContentTypeMeta(result.content_type)
  const iconColor = typeColors[result.content_type] || typeColors.unknown

  return (
    <button
      type="button"
      onClick={() => onSelect(result.id)}
      onMouseEnter={onHover}
      style={{
        display: 'block',
        width: '100%',
        textAlign: 'left',
        padding: '12px 16px',
        background: isSelected ? '#1f2937' : 'transparent',
        border: 'none',
        borderLeft: `3px solid ${isSelected ? '#a855f7' : 'transparent'}`,
        transition: 'all 0.1s',
        cursor: 'pointer',
      }}
    >
      <Flex align="flex-start" gap={3}>
        {/* Icon */}
        <Box
          color={iconColor}
          flexShrink={0}
          mt={0.5}
        >
          {getContentIcon(result.content_type)}
        </Box>

        {/* Content */}
        <Box flex={1} overflow="hidden">
          <Flex align="center" gap={2} mb={1}>
            <Text
              color="white"
              fontWeight="500"
              fontSize="sm"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              {result.title}
            </Text>
            <Badge
              fontSize="xs"
              colorPalette={typeMeta.color as 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'gray'}
              variant="subtle"
              flexShrink={0}
            >
              {typeMeta.label}
            </Badge>
          </Flex>

          {result.preview && (
            <Text
              color="gray.400"
              fontSize="xs"
              overflow="hidden"
              textOverflow="ellipsis"
              whiteSpace="nowrap"
            >
              {result.preview}
            </Text>
          )}

          {result.tags.length > 0 && (
            <Flex gap={1} mt={1.5} flexWrap="wrap">
              {result.tags.slice(0, 3).map((tag) => (
                <Text
                  key={tag}
                  fontSize="xs"
                  color="gray.500"
                  bg="gray.800"
                  px={1.5}
                  py={0.5}
                  borderRadius="sm"
                >
                  #{tag}
                </Text>
              ))}
              {result.tags.length > 3 && (
                <Text fontSize="xs" color="gray.600">
                  +{result.tags.length - 3}
                </Text>
              )}
            </Flex>
          )}
        </Box>

        {/* Similarity Score */}
        <Box flexShrink={0}>
          <Text
            fontSize="xs"
            color={result.similarity > 0.85 ? 'green.400' : result.similarity > 0.75 ? 'yellow.400' : 'gray.500'}
            fontWeight="500"
          >
            {Math.round(result.similarity * 100)}%
          </Text>
        </Box>
      </Flex>
    </button>
  )
}

/**
 * Empty state when no results
 */
function NoResults({ query }: { query: string }) {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      py={8}
      px={4}
    >
      <Box color="gray.600" mb={3}>
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <path d="M21 21l-4.35-4.35" />
        </svg>
      </Box>
      <Text color="gray.400" fontSize="sm" fontWeight="500" mb={1}>
        No results found
      </Text>
      <Text color="gray.600" fontSize="xs" textAlign="center">
        No matches for "{query}". Try a different search term.
      </Text>
    </Flex>
  )
}

/**
 * Initial empty state before search
 */
function InitialState() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      py={8}
      px={4}
    >
      <Text color="gray.500" fontSize="sm">
        Start typing to search your knowledge base
      </Text>
      <Flex gap={4} mt={4}>
        <Flex align="center" gap={2}>
          <Box color="red.400">{ContentIcons.youtube_video}</Box>
          <Text fontSize="xs" color="gray.600">Videos</Text>
        </Flex>
        <Flex align="center" gap={2}>
          <Box color="blue.400">{ContentIcons.document}</Box>
          <Text fontSize="xs" color="gray.600">Docs</Text>
        </Flex>
        <Flex align="center" gap={2}>
          <Box color="green.400">{ContentIcons.email}</Box>
          <Text fontSize="xs" color="gray.600">Emails</Text>
        </Flex>
        <Flex align="center" gap={2}>
          <Box color="purple.400">{ContentIcons.webpage}</Box>
          <Text fontSize="xs" color="gray.600">Web</Text>
        </Flex>
      </Flex>
    </Flex>
  )
}

/**
 * Search results list component
 */
interface SearchResultsProps {
  results: SearchResult[]
  isLoading: boolean
  selectedIndex: number
  onSelect: (id: string) => void
  onHover: (index: number) => void
  query: string
}

export function SearchResults({
  results,
  isLoading,
  selectedIndex,
  onSelect,
  onHover,
  query,
}: SearchResultsProps) {
  // Loading state
  if (isLoading) {
    return (
      <Box py={8}>
        <Loading message="Searching..." size="md" />
      </Box>
    )
  }

  // No query entered yet
  if (!query || query.length < 2) {
    return <InitialState />
  }

  // No results found
  if (results.length === 0) {
    return <NoResults query={query} />
  }

  // Results list
  return (
    <Box maxH="400px" overflowY="auto">
      <VStack gap={0} align="stretch">
        {results.map((result, index) => (
          <SearchResultItem
            key={result.id}
            result={result}
            isSelected={index === selectedIndex}
            onSelect={onSelect}
            onHover={() => onHover(index)}
          />
        ))}
      </VStack>

      {/* Results count */}
      <Box px={4} py={2} borderTopWidth={1} borderColor="gray.800">
        <Text fontSize="xs" color="gray.600">
          {results.length} result{results.length !== 1 ? 's' : ''} found
        </Text>
      </Box>
    </Box>
  )
}
