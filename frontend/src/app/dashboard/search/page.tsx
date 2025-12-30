'use client'

import { Box, Flex, Grid, GridItem, Text, VStack, Badge, Button } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { SearchFiltersPanel, ActiveFilters, InlineSearchFilters } from '@/components/search/search-filters'
import { SearchResults } from '@/components/search/search-results'
import { useSearch } from '@/hooks/use-search'
import type { SearchResult } from '@/lib/types'

/**
 * Search icon
 */
const SearchIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <path d="M21 21l-4.35-4.35" />
  </svg>
)

/**
 * Clear icon
 */
const ClearIcon = () => (
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
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

/**
 * Search page - dedicated search interface
 * Full-featured search with filters, results, and detail preview
 */
export default function SearchPage() {
  const {
    query,
    results,
    filters,
    isLoading,
    setQuery,
    setFilters,
    removeFilter,
    clearAll,
  } = useSearch()

  const [filtersExpanded, setFiltersExpanded] = useState(false)
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null)

  const handleResultSelect = useCallback((id: string) => {
    const result = results.find((r) => r.id === id)
    if (result) {
      setSelectedResult(result)
    }
  }, [results])

  const handleResultHover = useCallback((index: number) => {
    // Optional: preview on hover
  }, [])

  return (
    <PageContainer maxW="full">
      <PageHeader
        title="Search Knowledge Base"
        description="Search across all your documents, videos, emails, and notes using semantic AI search."
      />

      <Grid
        templateColumns={{ base: '1fr', lg: selectedResult ? '2fr 1fr' : '1fr' }}
        gap={6}
      >
        {/* Main Search Panel */}
        <GridItem>
          <Box bg="gray.900" borderRadius="xl" overflow="hidden">
            {/* Search Input */}
            <Flex
              align="center"
              gap={3}
              px={4}
              py={4}
              borderBottomWidth={1}
              borderColor="gray.800"
            >
              <Box color="gray.500">
                <SearchIcon />
              </Box>

              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search your knowledge base..."
                style={{
                  flex: 1,
                  background: 'transparent',
                  border: 'none',
                  outline: 'none',
                  fontSize: '16px',
                  color: 'white',
                }}
              />

              {query && (
                <button
                  type="button"
                  onClick={() => clearAll()}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#6b7280',
                    cursor: 'pointer',
                    padding: '4px',
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  <ClearIcon />
                </button>
              )}
            </Flex>

            {/* Active Filters Display */}
            <ActiveFilters filters={filters} onRemove={removeFilter} />

            {/* Filters Panel */}
            <SearchFiltersPanel
              filters={filters}
              onChange={setFilters}
              isExpanded={filtersExpanded}
              onToggleExpanded={() => setFiltersExpanded((prev) => !prev)}
            />

            {/* Search Results */}
            <SearchResults
              results={results}
              isLoading={isLoading}
              selectedIndex={selectedResult ? results.findIndex(r => r.id === selectedResult.id) : 0}
              onSelect={handleResultSelect}
              onHover={handleResultHover}
              query={query}
            />
          </Box>
        </GridItem>

        {/* Detail Preview Panel */}
        {selectedResult && (
          <GridItem>
            <ResultDetailPanel
              result={selectedResult}
              onClose={() => setSelectedResult(null)}
            />
          </GridItem>
        )}
      </Grid>
    </PageContainer>
  )
}

/**
 * Result detail panel component
 */
interface ResultDetailPanelProps {
  result: SearchResult
  onClose: () => void
}

function ResultDetailPanel({ result, onClose }: ResultDetailPanelProps) {
  return (
    <Box
      bg="gray.900"
      borderRadius="xl"
      overflow="hidden"
      position="sticky"
      top={4}
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
          Preview
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
          <ClearIcon />
        </button>
      </Flex>

      {/* Content */}
      <VStack align="stretch" gap={4} p={4}>
        {/* Title */}
        <Box>
          <Text color="white" fontWeight="600" fontSize="lg">
            {result.title}
          </Text>
          <Flex gap={2} mt={2}>
            <Badge
              colorPalette={getTypeColor(result.content_type)}
              size="sm"
            >
              {result.content_type.replace('_', ' ')}
            </Badge>
            <Text fontSize="xs" color="gray.500">
              {Math.round(result.similarity * 100)}% match
            </Text>
          </Flex>
        </Box>

        {/* Preview */}
        {result.preview && (
          <Box>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={1} textTransform="uppercase">
              Preview
            </Text>
            <Text color="gray.300" fontSize="sm" lineHeight="tall">
              {result.preview}
            </Text>
          </Box>
        )}

        {/* Tags */}
        {result.tags.length > 0 && (
          <Box>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={2} textTransform="uppercase">
              Tags
            </Text>
            <Flex gap={1} flexWrap="wrap">
              {result.tags.map((tag) => (
                <Text
                  key={tag}
                  fontSize="xs"
                  color="gray.400"
                  bg="gray.800"
                  px={2}
                  py={1}
                  borderRadius="md"
                >
                  #{tag}
                </Text>
              ))}
            </Flex>
          </Box>
        )}

        {/* Source URL */}
        {result.source_url && (
          <Box>
            <Text color="gray.500" fontSize="xs" fontWeight="600" mb={1} textTransform="uppercase">
              Source
            </Text>
            <a
              href={result.source_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#a855f7',
                fontSize: '14px',
                textDecoration: 'none',
              }}
              onMouseOver={(e) => e.currentTarget.style.textDecoration = 'underline'}
              onMouseOut={(e) => e.currentTarget.style.textDecoration = 'none'}
            >
              {result.source_url}
            </a>
          </Box>
        )}

        {/* Actions */}
        <Flex gap={2} pt={2}>
          <Button
            size="sm"
            colorPalette="purple"
            variant="solid"
            flex={1}
          >
            Open
          </Button>
          <Button
            size="sm"
            variant="outline"
            colorPalette="gray"
          >
            Copy Link
          </Button>
        </Flex>
      </VStack>
    </Box>
  )
}

/**
 * Get badge color for content type
 */
function getTypeColor(type: string): 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'gray' {
  const colors: Record<string, 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'gray'> = {
    youtube_video: 'red',
    document: 'blue',
    email: 'green',
    note: 'yellow',
    webpage: 'purple',
  }
  return colors[type] || 'gray'
}
