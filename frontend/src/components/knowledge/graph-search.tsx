'use client'

import { Box, Flex, Text, Badge } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import type { EntityType, GraphEntity } from '@/lib/types'
import { ENTITY_TYPES } from '@/lib/types'

/**
 * Search icon
 */
const SearchIcon = () => (
  <svg
    width="18"
    height="18"
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
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

/**
 * Filter chip component
 */
interface FilterChipProps {
  label: string
  color: string
  isActive: boolean
  onClick: () => void
}

function FilterChip({ label, color, isActive, onClick }: FilterChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 10px',
        fontSize: '12px',
        fontWeight: 500,
        borderRadius: '9999px',
        border: '1px solid',
        borderColor: isActive ? `var(--chakra-colors-${color}-500)` : '#374151',
        background: isActive ? `var(--chakra-colors-${color}-900)` : 'transparent',
        color: isActive ? `var(--chakra-colors-${color}-300)` : '#9ca3af',
        cursor: 'pointer',
        transition: 'all 0.15s',
      }}
    >
      {isActive && (
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
        </svg>
      )}
      {label}
    </button>
  )
}

/**
 * Search result item
 */
interface SearchResultProps {
  entity: GraphEntity
  isSelected: boolean
  onClick: () => void
}

function SearchResultItem({ entity, isSelected, onClick }: SearchResultProps) {
  const typeMeta = ENTITY_TYPES[entity.type] || ENTITY_TYPES.unknown

  return (
    <Box
      as="button"
      display="flex"
      alignItems="center"
      gap={3}
      w="full"
      px={3}
      py={2}
      bg={isSelected ? 'purple.900' : 'transparent'}
      border="none"
      borderRadius="md"
      cursor="pointer"
      textAlign="left"
      transition="all 0.1s"
      _hover={{ bg: isSelected ? 'purple.900' : 'gray.800' }}
      onClick={onClick}
    >
      <Box
        w={2}
        h={2}
        borderRadius="full"
        bg={`${typeMeta.color}.400`}
        flexShrink={0}
      />
      <Text
        color={isSelected ? 'white' : 'gray.300'}
        fontSize="sm"
        fontWeight={isSelected ? 500 : 400}
        flex={1}
        overflow="hidden"
        textOverflow="ellipsis"
        whiteSpace="nowrap"
      >
        {entity.name}
      </Text>
      <Badge colorPalette={typeMeta.color as any} size="sm" variant="subtle">
        {typeMeta.label}
      </Badge>
    </Box>
  )
}

/**
 * Props for GraphSearch
 */
interface GraphSearchProps {
  /** Current search query */
  query: string
  /** Selected entity types filter */
  selectedTypes: EntityType[]
  /** Search results */
  results: GraphEntity[]
  /** Total count */
  total: number
  /** Whether search is loading */
  isLoading: boolean
  /** Selected entity ID */
  selectedId?: string
  /** Called when query changes */
  onQueryChange: (query: string) => void
  /** Called to search */
  onSearch: (query: string, types?: EntityType[]) => void
  /** Called to toggle type filter */
  onToggleType: (type: EntityType) => void
  /** Called to clear filters */
  onClearFilters: () => void
  /** Called when an entity is selected */
  onSelect: (entity: GraphEntity) => void
}

export function GraphSearch({
  query,
  selectedTypes,
  results,
  total,
  isLoading,
  selectedId,
  onQueryChange,
  onSearch,
  onToggleType,
  onClearFilters,
  onSelect,
}: GraphSearchProps) {
  const [isFiltersExpanded, setFiltersExpanded] = useState(false)

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault()
      onSearch(query, selectedTypes.length > 0 ? selectedTypes : undefined)
    },
    [query, selectedTypes, onSearch]
  )

  const handleClear = useCallback(() => {
    onQueryChange('')
    onClearFilters()
  }, [onQueryChange, onClearFilters])

  // Entity types to show in filter
  const filterTypes: EntityType[] = ['person', 'organization', 'topic', 'document', 'project', 'location']

  return (
    <Box bg="gray.900" borderRadius="xl" overflow="hidden">
      {/* Search input */}
      <form onSubmit={handleSubmit}>
        <Flex
          align="center"
          gap={3}
          px={4}
          py={3}
          borderBottomWidth={1}
          borderColor="gray.800"
        >
          <Box color="gray.500">
            <SearchIcon />
          </Box>

          <input
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Search entities..."
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '14px',
              color: 'white',
            }}
          />

          {query && (
            <button
              type="button"
              onClick={handleClear}
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
      </form>

      {/* Filters toggle */}
      <Flex
        align="center"
        justify="space-between"
        px={4}
        py={2}
        borderBottomWidth={isFiltersExpanded ? 1 : 0}
        borderColor="gray.800"
        cursor="pointer"
        onClick={() => setFiltersExpanded(!isFiltersExpanded)}
        _hover={{ bg: 'gray.800' }}
        transition="all 0.15s"
      >
        <Flex align="center" gap={2}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
          </svg>
          <Text fontSize="sm" color="gray.400">
            Entity Types
          </Text>
          {selectedTypes.length > 0 && (
            <Badge colorPalette="purple" size="sm" variant="solid">
              {selectedTypes.length}
            </Badge>
          )}
        </Flex>
        <Box
          color="gray.500"
          transform={isFiltersExpanded ? 'rotate(180deg)' : 'rotate(0deg)'}
          transition="transform 0.2s"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </Box>
      </Flex>

      {/* Filter chips */}
      {isFiltersExpanded && (
        <Flex gap={2} px={4} py={3} flexWrap="wrap">
          {filterTypes.map((type) => {
            const meta = ENTITY_TYPES[type]
            return (
              <FilterChip
                key={type}
                label={meta.label}
                color={meta.color}
                isActive={selectedTypes.includes(type)}
                onClick={() => onToggleType(type)}
              />
            )
          })}
        </Flex>
      )}

      {/* Results */}
      <Box maxH="300px" overflowY="auto">
        {isLoading ? (
          <Flex align="center" justify="center" py={8}>
            <Box
              w={6}
              h={6}
              borderWidth={2}
              borderColor="purple.400"
              borderTopColor="transparent"
              borderRadius="full"
              animation="spin 0.8s linear infinite"
            />
          </Flex>
        ) : results.length > 0 ? (
          <>
            {results.map((entity) => (
              <SearchResultItem
                key={entity.id}
                entity={entity}
                isSelected={entity.id === selectedId}
                onClick={() => onSelect(entity)}
              />
            ))}
            {total > results.length && (
              <Text color="gray.600" fontSize="xs" textAlign="center" py={2}>
                Showing {results.length} of {total} results
              </Text>
            )}
          </>
        ) : query.length >= 2 ? (
          <Text color="gray.600" fontSize="sm" textAlign="center" py={6}>
            No entities found for &ldquo;{query}&rdquo;
          </Text>
        ) : (
          <Text color="gray.600" fontSize="sm" textAlign="center" py={6}>
            Type at least 2 characters to search
          </Text>
        )}
      </Box>

      {/* Stats bar */}
      {results.length > 0 && (
        <Flex
          align="center"
          justify="space-between"
          px={4}
          py={2}
          borderTopWidth={1}
          borderColor="gray.800"
          bg="gray.850"
        >
          <Text fontSize="xs" color="gray.500">
            {results.length} result{results.length !== 1 ? 's' : ''}
          </Text>
        </Flex>
      )}
    </Box>
  )
}
