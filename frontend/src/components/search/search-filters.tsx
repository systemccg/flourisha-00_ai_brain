'use client'

import { Box, Flex, Text, Badge } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import {
  type SearchFilters,
  CONTENT_TYPES,
  CONTENT_SOURCES,
  DATE_PRESETS,
  type DatePresetKey,
  getDateRangeFromPreset,
} from '@/lib/types'

/**
 * Filter chip component - toggleable button
 */
interface FilterChipProps {
  label: string
  isActive: boolean
  color?: string
  onClick: () => void
}

function FilterChip({ label, isActive, color = 'gray', onClick }: FilterChipProps) {
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
 * Filter section with label
 */
interface FilterSectionProps {
  label: string
  children: React.ReactNode
}

function FilterSection({ label, children }: FilterSectionProps) {
  return (
    <Box>
      <Text fontSize="xs" fontWeight="600" color="gray.500" mb={2} textTransform="uppercase" letterSpacing="wide">
        {label}
      </Text>
      <Flex gap={2} flexWrap="wrap">
        {children}
      </Flex>
    </Box>
  )
}

/**
 * Clear all filters button
 */
function ClearFiltersButton({ onClick, count }: { onClick: () => void; count: number }) {
  if (count === 0) return null

  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        fontSize: '12px',
        fontWeight: 500,
        borderRadius: '6px',
        border: 'none',
        background: '#374151',
        color: '#f3f4f6',
        cursor: 'pointer',
        transition: 'all 0.15s',
      }}
    >
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
      Clear {count} filter{count !== 1 ? 's' : ''}
    </button>
  )
}

/**
 * Collapsible filter panel
 */
interface SearchFiltersProps {
  filters: SearchFilters
  onChange: (filters: SearchFilters) => void
  isExpanded?: boolean
  onToggleExpanded?: () => void
}

export function SearchFiltersPanel({
  filters,
  onChange,
  isExpanded = false,
  onToggleExpanded,
}: SearchFiltersProps) {
  // Track selected date preset
  const [datePreset, setDatePreset] = useState<DatePresetKey>('all')

  // Toggle a type filter
  const toggleType = useCallback(
    (type: string) => {
      const currentTypes = filters.types || []
      const newTypes = currentTypes.includes(type)
        ? currentTypes.filter((t) => t !== type)
        : [...currentTypes, type]
      onChange({ ...filters, types: newTypes.length > 0 ? newTypes : undefined })
    },
    [filters, onChange]
  )

  // Toggle a source filter
  const toggleSource = useCallback(
    (source: string) => {
      const currentSources = filters.sources || []
      const newSources = currentSources.includes(source)
        ? currentSources.filter((s) => s !== source)
        : [...currentSources, source]
      onChange({ ...filters, sources: newSources.length > 0 ? newSources : undefined })
    },
    [filters, onChange]
  )

  // Set date range from preset
  const setDateRange = useCallback(
    (preset: DatePresetKey) => {
      setDatePreset(preset)
      const range = getDateRangeFromPreset(preset)
      onChange({
        ...filters,
        dateRange: range.start ? range : undefined,
      })
    },
    [filters, onChange]
  )

  // Clear all filters
  const clearFilters = useCallback(() => {
    setDatePreset('all')
    onChange({})
  }, [onChange])

  // Count active filters
  const activeFilterCount =
    (filters.types?.length || 0) +
    (filters.sources?.length || 0) +
    (filters.dateRange?.start ? 1 : 0)

  return (
    <Box>
      {/* Filter toggle header */}
      <Flex
        align="center"
        justify="space-between"
        px={4}
        py={2}
        borderBottomWidth={isExpanded ? 1 : 0}
        borderColor="gray.800"
        cursor="pointer"
        onClick={onToggleExpanded}
        _hover={{ bg: 'gray.800' }}
        transition="all 0.15s"
      >
        <Flex align="center" gap={2}>
          <Box color="gray.500">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
          </Box>
          <Text fontSize="sm" color="gray.400" fontWeight="500">
            Filters
          </Text>
          {activeFilterCount > 0 && (
            <Badge colorPalette="purple" size="sm" variant="solid">
              {activeFilterCount}
            </Badge>
          )}
        </Flex>
        <Box
          color="gray.500"
          transform={isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'}
          transition="transform 0.2s"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </Box>
      </Flex>

      {/* Expanded filter content */}
      {isExpanded && (
        <Box px={4} py={3} spaceY={4}>
          {/* Content Type Filter */}
          <FilterSection label="Content Type">
            {Object.entries(CONTENT_TYPES)
              .filter(([key]) => key !== 'unknown')
              .map(([key, meta]) => (
                <FilterChip
                  key={key}
                  label={meta.label}
                  isActive={filters.types?.includes(key) || false}
                  color={meta.color}
                  onClick={() => toggleType(key)}
                />
              ))}
          </FilterSection>

          {/* Date Range Filter */}
          <FilterSection label="Date Range">
            {(Object.entries(DATE_PRESETS) as [DatePresetKey, typeof DATE_PRESETS[DatePresetKey]][]).map(
              ([key, preset]) => (
                <FilterChip
                  key={key}
                  label={preset.label}
                  isActive={datePreset === key}
                  color="blue"
                  onClick={() => setDateRange(key)}
                />
              )
            )}
          </FilterSection>

          {/* Source Filter */}
          <FilterSection label="Source">
            {Object.entries(CONTENT_SOURCES).map(([key, meta]) => (
              <FilterChip
                key={key}
                label={meta.label}
                isActive={filters.sources?.includes(key) || false}
                color={meta.color}
                onClick={() => toggleSource(key)}
              />
            ))}
          </FilterSection>

          {/* Clear filters */}
          <Flex justify="flex-end" pt={2}>
            <ClearFiltersButton onClick={clearFilters} count={activeFilterCount} />
          </Flex>
        </Box>
      )}
    </Box>
  )
}

/**
 * Compact inline filter bar for smaller spaces
 */
interface InlineFiltersProps {
  filters: SearchFilters
  onChange: (filters: SearchFilters) => void
}

export function InlineSearchFilters({ filters, onChange }: InlineFiltersProps) {
  const [datePreset, setDatePreset] = useState<DatePresetKey>('all')

  // Toggle a type filter
  const toggleType = useCallback(
    (type: string) => {
      const currentTypes = filters.types || []
      const newTypes = currentTypes.includes(type)
        ? currentTypes.filter((t) => t !== type)
        : [...currentTypes, type]
      onChange({ ...filters, types: newTypes.length > 0 ? newTypes : undefined })
    },
    [filters, onChange]
  )

  // Set date range from preset
  const setDateRange = useCallback(
    (preset: DatePresetKey) => {
      setDatePreset(preset)
      const range = getDateRangeFromPreset(preset)
      onChange({
        ...filters,
        dateRange: range.start ? range : undefined,
      })
    },
    [filters, onChange]
  )

  // Quick type filters (most common)
  const quickTypes = ['youtube_video', 'document', 'email', 'webpage']

  return (
    <Flex
      align="center"
      gap={3}
      px={4}
      py={2}
      borderBottomWidth={1}
      borderColor="gray.800"
      overflowX="auto"
      css={{
        '&::-webkit-scrollbar': { display: 'none' },
        scrollbarWidth: 'none',
      }}
    >
      {/* Quick type filters */}
      {quickTypes.map((type) => {
        const meta = CONTENT_TYPES[type]
        return (
          <FilterChip
            key={type}
            label={meta.label}
            isActive={filters.types?.includes(type) || false}
            color={meta.color}
            onClick={() => toggleType(type)}
          />
        )
      })}

      {/* Separator */}
      <Box h={4} w="1px" bg="gray.700" flexShrink={0} />

      {/* Quick date filters */}
      {(['week', 'month', 'all'] as DatePresetKey[]).map((key) => (
        <FilterChip
          key={key}
          label={DATE_PRESETS[key].label}
          isActive={datePreset === key}
          color="blue"
          onClick={() => setDateRange(key)}
        />
      ))}
    </Flex>
  )
}

/**
 * Active filter tags display
 */
interface ActiveFiltersProps {
  filters: SearchFilters
  onRemove: (filterType: 'type' | 'source' | 'date', value?: string) => void
}

export function ActiveFilters({ filters, onRemove }: ActiveFiltersProps) {
  const hasFilters =
    (filters.types?.length || 0) > 0 ||
    (filters.sources?.length || 0) > 0 ||
    !!filters.dateRange?.start

  if (!hasFilters) return null

  return (
    <Flex
      align="center"
      gap={2}
      px={4}
      py={2}
      borderBottomWidth={1}
      borderColor="gray.800"
      flexWrap="wrap"
    >
      <Text fontSize="xs" color="gray.500">
        Filtering by:
      </Text>

      {/* Type filters */}
      {filters.types?.map((type) => {
        const meta = CONTENT_TYPES[type] || CONTENT_TYPES.unknown
        return (
          <Badge
            key={`type-${type}`}
            colorPalette={meta.color as 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'gray'}
            size="sm"
            display="flex"
            alignItems="center"
            gap={1}
            cursor="pointer"
            onClick={() => onRemove('type', type)}
          >
            {meta.label}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" />
            </svg>
          </Badge>
        )
      })}

      {/* Source filters */}
      {filters.sources?.map((source) => {
        const meta = CONTENT_SOURCES[source] || { label: source, color: 'gray' }
        return (
          <Badge
            key={`source-${source}`}
            colorPalette={meta.color as 'red' | 'blue' | 'green' | 'yellow' | 'purple' | 'gray' | 'orange' | 'cyan'}
            size="sm"
            display="flex"
            alignItems="center"
            gap={1}
            cursor="pointer"
            onClick={() => onRemove('source', source)}
          >
            {meta.label}
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" />
            </svg>
          </Badge>
        )
      })}

      {/* Date filter */}
      {filters.dateRange?.start && (
        <Badge
          colorPalette="blue"
          size="sm"
          display="flex"
          alignItems="center"
          gap={1}
          cursor="pointer"
          onClick={() => onRemove('date')}
        >
          {filters.dateRange.start} - {filters.dateRange.end || 'Now'}
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" />
          </svg>
        </Badge>
      )}
    </Flex>
  )
}
