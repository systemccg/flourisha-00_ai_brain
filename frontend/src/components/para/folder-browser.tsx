'use client'

import { Box, Flex, Text, Spinner, Grid, GridItem } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import {
  type PARAItem,
  type PARACategory,
  PARA_CATEGORIES,
  getFileIcon,
  formatFileSize,
  getPARACategoryFromPath,
} from '@/lib/types'

/**
 * Icons for the folder browser
 */
const Icons = {
  folder: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
    </svg>
  ),
  file: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  ),
  markdown: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M14.85 3H5.15C4.5 3 4 3.5 4 4.15v15.69C4 20.5 4.5 21 5.15 21h13.69c.66 0 1.15-.5 1.15-1.15V8L14.85 3zM7 15l2-2-2-2h1.5l1.25 1.5L11 11h1.5l-2 2 2 2H11l-1.25-1.5L8.5 15H7zm8 0h-1.5v-3h-1v2l-2-2.5 2-2.5v2h1V8H15v7z" />
    </svg>
  ),
  image: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </svg>
  ),
  pdf: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
      <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z" />
      <path d="M7 13h3v1H8v1h2v1H8v2H7v-5zm5 2.5c0 .28.22.5.5.5h1c.28 0 .5-.22.5-.5v-2c0-.28-.22-.5-.5-.5h-1c-.28 0-.5.22-.5.5v2zm1-.5v1h-1v-1h1zm2-2h1.5c.28 0 .5.22.5.5v3c0 .28-.22.5-.5.5H15v-4zm1 1v2h.5v-2h-.5z" />
    </svg>
  ),
  home: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  ),
  chevronRight: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  ),
  arrowUp: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M5 12h14M12 5l7 7M12 5L5 12" />
    </svg>
  ),
  refresh: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 4 23 10 17 10" />
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
    </svg>
  ),
  gridView: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
    </svg>
  ),
  listView: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="8" y1="6" x2="21" y2="6" />
      <line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <line x1="3" y1="6" x2="3.01" y2="6" />
      <line x1="3" y1="12" x2="3.01" y2="12" />
      <line x1="3" y1="18" x2="3.01" y2="18" />
    </svg>
  ),
}

/**
 * Get icon for file type
 */
function getItemIcon(item: PARAItem) {
  if (item.isDirectory) return Icons.folder

  const ext = item.extension?.toLowerCase()
  switch (ext) {
    case 'md':
    case 'mdx':
      return Icons.markdown
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'webp':
    case 'svg':
      return Icons.image
    case 'pdf':
      return Icons.pdf
    default:
      return Icons.file
  }
}

/**
 * Breadcrumb segment
 */
interface BreadcrumbSegment {
  name: string
  path: string
}

/**
 * Breadcrumbs component
 */
interface BreadcrumbsProps {
  segments: BreadcrumbSegment[]
  onNavigate: (path: string) => void
}

export function FolderBreadcrumbs({ segments, onNavigate }: BreadcrumbsProps) {
  return (
    <Flex align="center" gap={1} px={2} py={2} bg="gray.850" borderRadius="lg">
      {/* Home button */}
      <Box
        as="button"
        display="flex"
        alignItems="center"
        justifyContent="center"
        w={7}
        h={7}
        borderRadius="md"
        color="gray.400"
        bg="transparent"
        border="none"
        cursor="pointer"
        transition="all 0.1s"
        _hover={{ bg: 'gray.700', color: 'white' }}
        onClick={() => onNavigate('')}
        aria-label="Go to root"
      >
        {Icons.home}
      </Box>

      {segments.map((segment, index) => (
        <Flex key={segment.path} align="center" gap={1}>
          {/* Separator */}
          <Box color="gray.600" flexShrink={0}>
            {Icons.chevronRight}
          </Box>

          {/* Segment */}
          {index === segments.length - 1 ? (
            // Current (non-clickable)
            <Text fontSize="sm" fontWeight="500" color="white" px={2}>
              {segment.name}
            </Text>
          ) : (
            // Clickable ancestor
            <Box
              as="button"
              fontSize="sm"
              color="gray.400"
              bg="transparent"
              border="none"
              borderRadius="md"
              px={2}
              py={1}
              cursor="pointer"
              transition="all 0.1s"
              _hover={{ color: 'white', bg: 'gray.700' }}
              onClick={() => onNavigate(segment.path)}
            >
              {segment.name}
            </Box>
          )}
        </Flex>
      ))}
    </Flex>
  )
}

/**
 * Toolbar for folder browser
 */
interface ToolbarProps {
  canGoUp: boolean
  viewMode: 'grid' | 'list'
  onGoUp: () => void
  onRefresh: () => void
  onViewModeChange: (mode: 'grid' | 'list') => void
}

function Toolbar({ canGoUp, viewMode, onGoUp, onRefresh, onViewModeChange }: ToolbarProps) {
  return (
    <Flex align="center" justify="space-between" px={2} py={2}>
      {/* Left actions */}
      <Flex gap={1}>
        <Box
          as="button"
          display="flex"
          alignItems="center"
          justifyContent="center"
          w={8}
          h={8}
          borderRadius="md"
          color={canGoUp ? 'gray.400' : 'gray.600'}
          bg="transparent"
          border="none"
          cursor={canGoUp ? 'pointer' : 'not-allowed'}
          transition="all 0.1s"
          _hover={canGoUp ? { bg: 'gray.800', color: 'white' } : {}}
          onClick={canGoUp ? onGoUp : undefined}
          aria-label="Go up one level"
          aria-disabled={!canGoUp}
        >
          {Icons.arrowUp}
        </Box>

        <Box
          as="button"
          display="flex"
          alignItems="center"
          justifyContent="center"
          w={8}
          h={8}
          borderRadius="md"
          color="gray.400"
          bg="transparent"
          border="none"
          cursor="pointer"
          transition="all 0.1s"
          _hover={{ bg: 'gray.800', color: 'white' }}
          onClick={onRefresh}
          aria-label="Refresh"
        >
          {Icons.refresh}
        </Box>
      </Flex>

      {/* Right actions - view mode toggle */}
      <Flex gap={1} bg="gray.850" borderRadius="md" p={0.5}>
        <Box
          as="button"
          display="flex"
          alignItems="center"
          justifyContent="center"
          w={7}
          h={7}
          borderRadius="md"
          color={viewMode === 'grid' ? 'white' : 'gray.500'}
          bg={viewMode === 'grid' ? 'gray.700' : 'transparent'}
          border="none"
          cursor="pointer"
          transition="all 0.1s"
          onClick={() => onViewModeChange('grid')}
          aria-label="Grid view"
        >
          {Icons.gridView}
        </Box>
        <Box
          as="button"
          display="flex"
          alignItems="center"
          justifyContent="center"
          w={7}
          h={7}
          borderRadius="md"
          color={viewMode === 'list' ? 'white' : 'gray.500'}
          bg={viewMode === 'list' ? 'gray.700' : 'transparent'}
          border="none"
          cursor="pointer"
          transition="all 0.1s"
          onClick={() => onViewModeChange('list')}
          aria-label="List view"
        >
          {Icons.listView}
        </Box>
      </Flex>
    </Flex>
  )
}

/**
 * Grid item component
 */
interface ItemCardProps {
  item: PARAItem
  isSelected: boolean
  onClick: () => void
  onDoubleClick: () => void
}

function ItemCard({ item, isSelected, onClick, onDoubleClick }: ItemCardProps) {
  return (
    <Box
      as="button"
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      p={4}
      bg={isSelected ? 'purple.900' : 'gray.850'}
      borderWidth={1}
      borderColor={isSelected ? 'purple.500' : 'transparent'}
      borderRadius="xl"
      border="none"
      cursor="pointer"
      transition="all 0.15s"
      _hover={{ bg: isSelected ? 'purple.900' : 'gray.800', transform: 'translateY(-2px)' }}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      minW="120px"
      textAlign="center"
    >
      {/* Icon */}
      <Box color={item.isDirectory ? 'yellow.400' : 'gray.400'} mb={2}>
        {getItemIcon(item)}
      </Box>

      {/* Name */}
      <Text
        fontSize="sm"
        color={isSelected ? 'white' : 'gray.300'}
        fontWeight={isSelected ? 500 : 400}
        overflow="hidden"
        textOverflow="ellipsis"
        whiteSpace="nowrap"
        w="full"
        maxW="140px"
      >
        {item.name}
      </Text>

      {/* Meta info */}
      {!item.isDirectory && item.size && (
        <Text fontSize="xs" color="gray.600" mt={1}>
          {formatFileSize(item.size)}
        </Text>
      )}
    </Box>
  )
}

/**
 * List row component
 */
function ItemRow({ item, isSelected, onClick, onDoubleClick }: ItemCardProps) {
  return (
    <Box
      as="button"
      display="flex"
      alignItems="center"
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
      onDoubleClick={onDoubleClick}
    >
      {/* Icon */}
      <Box color={item.isDirectory ? 'yellow.400' : 'gray.400'} mr={3} flexShrink={0}>
        {getItemIcon(item)}
      </Box>

      {/* Name */}
      <Text
        fontSize="sm"
        color={isSelected ? 'white' : 'gray.300'}
        fontWeight={isSelected ? 500 : 400}
        flex={1}
        overflow="hidden"
        textOverflow="ellipsis"
        whiteSpace="nowrap"
      >
        {item.name}
      </Text>

      {/* Size */}
      {!item.isDirectory && (
        <Text fontSize="xs" color="gray.600" w="80px" textAlign="right" flexShrink={0}>
          {formatFileSize(item.size)}
        </Text>
      )}

      {/* Item count for folders */}
      {item.isDirectory && item.itemCount !== undefined && (
        <Text fontSize="xs" color="gray.600" w="80px" textAlign="right" flexShrink={0}>
          {item.itemCount} items
        </Text>
      )}
    </Box>
  )
}

/**
 * Empty state
 */
function EmptyState() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      py={12}
      px={4}
    >
      <Box color="gray.600" mb={4}>
        {Icons.folder}
      </Box>
      <Text color="gray.500" fontSize="sm">
        This folder is empty
      </Text>
    </Flex>
  )
}

/**
 * Main folder browser component
 */
interface FolderBrowserProps {
  items: PARAItem[]
  breadcrumbs: BreadcrumbSegment[]
  isLoading?: boolean
  selectedPath?: string
  canGoUp?: boolean
  onNavigate: (path: string) => void
  onGoUp: () => void
  onRefresh: () => void
  onSelect?: (item: PARAItem) => void
  onOpen?: (item: PARAItem) => void
}

export function FolderBrowser({
  items,
  breadcrumbs,
  isLoading,
  selectedPath,
  canGoUp = false,
  onNavigate,
  onGoUp,
  onRefresh,
  onSelect,
  onOpen,
}: FolderBrowserProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const handleItemClick = useCallback(
    (item: PARAItem) => {
      onSelect?.(item)
    },
    [onSelect]
  )

  const handleItemDoubleClick = useCallback(
    (item: PARAItem) => {
      if (item.isDirectory) {
        onNavigate(item.path)
      } else {
        onOpen?.(item)
      }
    },
    [onNavigate, onOpen]
  )

  // Sort items: directories first, then by name
  const sortedItems = [...items].sort((a, b) => {
    if (a.isDirectory && !b.isDirectory) return -1
    if (!a.isDirectory && b.isDirectory) return 1
    return a.name.localeCompare(b.name)
  })

  return (
    <Box bg="gray.900" borderRadius="xl" overflow="hidden">
      {/* Breadcrumbs */}
      <Box px={2} pt={2}>
        <FolderBreadcrumbs segments={breadcrumbs} onNavigate={onNavigate} />
      </Box>

      {/* Toolbar */}
      <Toolbar
        canGoUp={canGoUp}
        viewMode={viewMode}
        onGoUp={onGoUp}
        onRefresh={onRefresh}
        onViewModeChange={setViewMode}
      />

      {/* Content */}
      <Box px={2} pb={4} minH="300px">
        {isLoading ? (
          <Flex align="center" justify="center" py={12}>
            <Spinner size="lg" color="purple.400" />
          </Flex>
        ) : items.length === 0 ? (
          <EmptyState />
        ) : viewMode === 'grid' ? (
          <Grid
            templateColumns="repeat(auto-fill, minmax(140px, 1fr))"
            gap={3}
            p={2}
          >
            {sortedItems.map((item) => (
              <GridItem key={item.id}>
                <ItemCard
                  item={item}
                  isSelected={selectedPath === item.path}
                  onClick={() => handleItemClick(item)}
                  onDoubleClick={() => handleItemDoubleClick(item)}
                />
              </GridItem>
            ))}
          </Grid>
        ) : (
          <Box>
            {sortedItems.map((item) => (
              <ItemRow
                key={item.id}
                item={item}
                isSelected={selectedPath === item.path}
                onClick={() => handleItemClick(item)}
                onDoubleClick={() => handleItemDoubleClick(item)}
              />
            ))}
          </Box>
        )}
      </Box>

      {/* Status bar */}
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
          {items.length} item{items.length !== 1 ? 's' : ''}
        </Text>
        {selectedPath && (
          <Text fontSize="xs" color="gray.600" maxW="300px" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
            {selectedPath}
          </Text>
        )}
      </Flex>
    </Box>
  )
}
