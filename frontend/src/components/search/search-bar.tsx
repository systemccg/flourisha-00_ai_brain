'use client'

import {
  Box,
  Flex,
  Text,
  Portal,
} from '@chakra-ui/react'
import { useState, useRef, useEffect, type KeyboardEvent } from 'react'
import { useSearch, useSearchModal } from '@/hooks/use-search'
import { SearchResults } from './search-results'
import { SearchFiltersPanel, ActiveFilters } from './search-filters'

/**
 * Search icon component
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
 * Close icon component
 */
const CloseIcon = () => (
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
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

/**
 * Keyboard shortcut display
 */
function KbdShortcut({ children }: { children: React.ReactNode }) {
  return (
    <Box
      as="kbd"
      display="inline-flex"
      alignItems="center"
      justifyContent="center"
      px={1.5}
      py={0.5}
      fontSize="xs"
      fontWeight="500"
      color="gray.500"
      bg="gray.800"
      borderRadius="md"
      borderWidth={1}
      borderColor="gray.700"
      fontFamily="mono"
    >
      {children}
    </Box>
  )
}

/**
 * Unified search bar component
 * Opens as a command palette modal with CMD+K
 */
export function UnifiedSearchBar() {
  const { isOpen, close } = useSearchModal()
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
  const inputRef = useRef<HTMLInputElement>(null)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [filtersExpanded, setFiltersExpanded] = useState(false)

  // Focus input when modal opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
      setSelectedIndex(0)
    }
  }, [isOpen])

  // Reset selection when results change
  useEffect(() => {
    setSelectedIndex(0)
  }, [results])

  // Handle keyboard navigation
  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1))
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => Math.max(prev - 1, 0))
        break
      case 'Enter':
        e.preventDefault()
        if (results[selectedIndex]) {
          handleResultSelect(results[selectedIndex].id)
        }
        break
      case 'Escape':
        e.preventDefault()
        handleClose()
        break
      case 'Tab':
        // Tab toggles filters panel
        e.preventDefault()
        setFiltersExpanded((prev) => !prev)
        break
    }
  }

  const handleClose = () => {
    clearAll()
    setFiltersExpanded(false)
    close()
  }

  const handleResultSelect = (id: string) => {
    // TODO: Navigate to result detail or open in panel
    console.log('Selected result:', id)
    handleClose()
  }

  if (!isOpen) return null

  return (
    <Portal>
      {/* Overlay */}
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bg="blackAlpha.700"
        backdropFilter="blur(4px)"
        zIndex={1000}
        onClick={handleClose}
      />

      {/* Search Modal */}
      <Box
        position="fixed"
        top="15%"
        left="50%"
        transform="translateX(-50%)"
        w="full"
        maxW="680px"
        bg="gray.900"
        borderWidth={1}
        borderColor="gray.700"
        borderRadius="xl"
        shadow="2xl"
        zIndex={1001}
        overflow="hidden"
      >
        {/* Search Input */}
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
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search knowledge base..."
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
              onClick={() => setQuery('')}
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
          )}

          <KbdShortcut>ESC</KbdShortcut>
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

        {/* Results */}
        <SearchResults
          results={results}
          isLoading={isLoading}
          selectedIndex={selectedIndex}
          onSelect={handleResultSelect}
          onHover={setSelectedIndex}
          query={query}
        />

        {/* Footer */}
        <Flex
          align="center"
          justify="space-between"
          px={4}
          py={2}
          borderTopWidth={1}
          borderColor="gray.800"
          bg="gray.900"
        >
          <Flex align="center" gap={4}>
            <Flex align="center" gap={1}>
              <KbdShortcut>↑</KbdShortcut>
              <KbdShortcut>↓</KbdShortcut>
              <Text fontSize="xs" color="gray.500" ml={1}>
                navigate
              </Text>
            </Flex>
            <Flex align="center" gap={1}>
              <KbdShortcut>↵</KbdShortcut>
              <Text fontSize="xs" color="gray.500" ml={1}>
                select
              </Text>
            </Flex>
            <Flex align="center" gap={1}>
              <KbdShortcut>Tab</KbdShortcut>
              <Text fontSize="xs" color="gray.500" ml={1}>
                filters
              </Text>
            </Flex>
          </Flex>

          <Text fontSize="xs" color="gray.600">
            Semantic search powered by AI
          </Text>
        </Flex>
      </Box>
    </Portal>
  )
}

/**
 * Compact search trigger button for header
 */
export function SearchTrigger() {
  const { open } = useSearchModal()

  return (
    <button
      type="button"
      onClick={open}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 12px',
        background: 'transparent',
        border: 'none',
        borderRadius: '8px',
        color: '#9ca3af',
        cursor: 'pointer',
        transition: 'all 0.15s',
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.background = '#1f2937'
        e.currentTarget.style.color = '#ffffff'
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'transparent'
        e.currentTarget.style.color = '#9ca3af'
      }}
    >
      <SearchIcon />
      <Text display={{ base: 'none', md: 'block' }} fontSize="sm">
        Search
      </Text>
      <Flex display={{ base: 'none', md: 'flex' }} align="center" gap={0.5} ml={2}>
        <KbdShortcut>
          <Text as="span" fontSize="10px">
            CMD
          </Text>
        </KbdShortcut>
        <KbdShortcut>K</KbdShortcut>
      </Flex>
    </button>
  )
}
