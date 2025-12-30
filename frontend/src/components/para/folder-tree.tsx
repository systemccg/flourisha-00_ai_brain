'use client'

import { Box, Flex, Text, Spinner } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import {
  type PARAItem,
  type PARACategory,
  PARA_CATEGORIES,
  getFileIcon,
} from '@/lib/types'

/**
 * Icons for folders and files
 */
const Icons = {
  folder: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
    </svg>
  ),
  folderOpen: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z" />
    </svg>
  ),
  file: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  ),
  markdown: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M14.85 3H5.15C4.5 3 4 3.5 4 4.15v15.69C4 20.5 4.5 21 5.15 21h13.69c.66 0 1.15-.5 1.15-1.15V8L14.85 3zM7 15l2-2-2-2h1.5l1.25 1.5L11 11h1.5l-2 2 2 2H11l-1.25-1.5L8.5 15H7zm8 0h-1.5v-3h-1v2l-2-2.5 2-2.5v2h1V8H15v7z" />
    </svg>
  ),
  chevronRight: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  ),
  chevronDown: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  ),
  rocket: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2.5l-1.5 1.5L8 6.5 6 8.5l-2 2-1.5 1.5 3 3 1.5-1.5 2-2 2.5-2 1.5-1.5 4-4 1.5-1.5L12 2.5zM4.5 14l-2 2 5.5 5.5 2-2L4.5 14zm15 0l-5.5 5.5 2 2 5.5-5.5-2-2z" />
    </svg>
  ),
  layers: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </svg>
  ),
  book: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" />
    </svg>
  ),
  archive: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="21 8 21 21 3 21 3 8" />
      <rect x="1" y="3" width="22" height="5" />
      <line x1="10" y1="12" x2="14" y2="12" />
    </svg>
  ),
}

/**
 * Get category icon
 */
function getCategoryIcon(category: PARACategory) {
  switch (category) {
    case 'projects':
      return Icons.rocket
    case 'areas':
      return Icons.layers
    case 'resources':
      return Icons.book
    case 'archives':
      return Icons.archive
    default:
      return Icons.folder
  }
}

/**
 * Get file/folder icon based on type
 */
function getIcon(item: PARAItem, isExpanded: boolean) {
  if (item.isDirectory) {
    return isExpanded ? Icons.folderOpen : Icons.folder
  }
  if (item.extension === 'md' || item.extension === 'mdx') {
    return Icons.markdown
  }
  return Icons.file
}

/**
 * Tree node component
 */
interface TreeNodeProps {
  item: PARAItem
  depth: number
  isSelected: boolean
  expandedPaths: Set<string>
  onSelect: (item: PARAItem) => void
  onToggle: (path: string) => void
  onLoadChildren?: (path: string) => Promise<PARAItem[]>
}

function TreeNode({
  item,
  depth,
  isSelected,
  expandedPaths,
  onSelect,
  onToggle,
  onLoadChildren,
}: TreeNodeProps) {
  const [isLoading, setIsLoading] = useState(false)
  const isExpanded = expandedPaths.has(item.path)
  const hasChildren = item.isDirectory && (item.children?.length || 0) > 0
  const canExpand = item.isDirectory && (!item.childrenLoaded || hasChildren)

  const handleToggle = useCallback(async () => {
    if (!item.isDirectory) return

    if (!item.childrenLoaded && onLoadChildren) {
      setIsLoading(true)
      try {
        await onLoadChildren(item.path)
      } finally {
        setIsLoading(false)
      }
    }

    onToggle(item.path)
  }, [item, onLoadChildren, onToggle])

  const handleClick = useCallback(() => {
    if (item.isDirectory) {
      handleToggle()
    }
    onSelect(item)
  }, [item, handleToggle, onSelect])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleClick()
      }
      if (e.key === 'ArrowRight' && item.isDirectory && !isExpanded) {
        e.preventDefault()
        handleToggle()
      }
      if (e.key === 'ArrowLeft' && item.isDirectory && isExpanded) {
        e.preventDefault()
        onToggle(item.path)
      }
    },
    [handleClick, handleToggle, isExpanded, item.isDirectory, onToggle, item.path]
  )

  return (
    <Box>
      {/* Node row */}
      <Box
        as="button"
        display="flex"
        alignItems="center"
        w="full"
        py={1}
        px={2}
        pl={`${depth * 16 + 8}px`}
        bg={isSelected ? 'purple.900' : 'transparent'}
        borderRadius="md"
        cursor="pointer"
        border="none"
        textAlign="left"
        transition="all 0.1s"
        _hover={{ bg: isSelected ? 'purple.900' : 'gray.800' }}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="treeitem"
        aria-expanded={item.isDirectory ? isExpanded : undefined}
        aria-selected={isSelected}
      >
        {/* Expand/collapse chevron */}
        <Box
          w={4}
          h={4}
          mr={1}
          color="gray.500"
          opacity={canExpand ? 1 : 0}
          transform={isExpanded ? 'rotate(90deg)' : 'rotate(0deg)'}
          transition="transform 0.15s"
        >
          {isLoading ? (
            <Spinner size="xs" />
          ) : (
            Icons.chevronRight
          )}
        </Box>

        {/* Icon */}
        <Box
          mr={2}
          color={item.isDirectory ? 'yellow.400' : 'gray.400'}
          flexShrink={0}
        >
          {getIcon(item, isExpanded)}
        </Box>

        {/* Name */}
        <Text
          fontSize="sm"
          color={isSelected ? 'white' : 'gray.300'}
          fontWeight={isSelected ? 500 : 400}
          overflow="hidden"
          textOverflow="ellipsis"
          whiteSpace="nowrap"
          flex={1}
          textAlign="left"
        >
          {item.name}
        </Text>

        {/* Item count for directories */}
        {item.isDirectory && item.itemCount !== undefined && (
          <Text fontSize="xs" color="gray.600" ml={2}>
            {item.itemCount}
          </Text>
        )}
      </Box>

      {/* Children */}
      {isExpanded && item.children && (
        <Box role="group">
          {item.children.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              depth={depth + 1}
              isSelected={isSelected}
              expandedPaths={expandedPaths}
              onSelect={onSelect}
              onToggle={onToggle}
              onLoadChildren={onLoadChildren}
            />
          ))}
        </Box>
      )}
    </Box>
  )
}

/**
 * PARA category header
 */
interface CategoryHeaderProps {
  category: PARACategory
  isExpanded: boolean
  itemCount?: number
  onToggle: () => void
}

function CategoryHeader({ category, isExpanded, itemCount, onToggle }: CategoryHeaderProps) {
  const meta = PARA_CATEGORIES[category]

  return (
    <Box
      as="button"
      display="flex"
      alignItems="center"
      w="full"
      py={2}
      px={3}
      bg="gray.850"
      borderRadius="lg"
      cursor="pointer"
      border="none"
      textAlign="left"
      transition="all 0.1s"
      _hover={{ bg: 'gray.800' }}
      onClick={onToggle}
    >
      {/* Chevron */}
      <Box
        w={4}
        h={4}
        mr={2}
        color="gray.500"
        transform={isExpanded ? 'rotate(90deg)' : 'rotate(0deg)'}
        transition="transform 0.15s"
      >
        {Icons.chevronRight}
      </Box>

      {/* Category icon */}
      <Box
        mr={2}
        color={`${meta.color}.400`}
      >
        {getCategoryIcon(category)}
      </Box>

      {/* Category name */}
      <Text
        fontSize="sm"
        fontWeight="600"
        color="gray.200"
        flex={1}
        textAlign="left"
      >
        {meta.label}
      </Text>

      {/* Item count */}
      {itemCount !== undefined && (
        <Text fontSize="xs" color="gray.500">
          {itemCount} items
        </Text>
      )}
    </Box>
  )
}

/**
 * Main PARA folder tree component
 */
interface PARAFolderTreeProps {
  /** Items organized by category */
  items: Record<PARACategory, PARAItem[]>
  /** Currently selected item path */
  selectedPath?: string
  /** Callback when item is selected */
  onSelect?: (item: PARAItem) => void
  /** Callback to load children lazily */
  onLoadChildren?: (path: string) => Promise<PARAItem[]>
  /** Whether tree is loading */
  isLoading?: boolean
}

export function PARAFolderTree({
  items,
  selectedPath,
  onSelect,
  onLoadChildren,
  isLoading,
}: PARAFolderTreeProps) {
  // Track expanded paths
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())
  // Track expanded categories
  const [expandedCategories, setExpandedCategories] = useState<Set<PARACategory>>(
    new Set(['projects', 'areas'])
  )

  const handleToggle = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }, [])

  const handleCategoryToggle = useCallback((category: PARACategory) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }, [])

  const handleSelect = useCallback(
    (item: PARAItem) => {
      onSelect?.(item)
    },
    [onSelect]
  )

  // Categories in order
  const categories: PARACategory[] = ['projects', 'areas', 'resources', 'archives']

  if (isLoading) {
    return (
      <Flex align="center" justify="center" py={8}>
        <Spinner size="lg" color="purple.400" />
      </Flex>
    )
  }

  return (
    <Box role="tree" aria-label="PARA folder structure">
      {categories.map((category) => {
        const categoryItems = items[category] || []
        const isExpanded = expandedCategories.has(category)

        return (
          <Box key={category} mb={2}>
            <CategoryHeader
              category={category}
              isExpanded={isExpanded}
              itemCount={categoryItems.length}
              onToggle={() => handleCategoryToggle(category)}
            />

            {isExpanded && categoryItems.length > 0 && (
              <Box mt={1} ml={2}>
                {categoryItems.map((item) => (
                  <TreeNode
                    key={item.id}
                    item={item}
                    depth={0}
                    isSelected={selectedPath === item.path}
                    expandedPaths={expandedPaths}
                    onSelect={handleSelect}
                    onToggle={handleToggle}
                    onLoadChildren={onLoadChildren}
                  />
                ))}
              </Box>
            )}

            {isExpanded && categoryItems.length === 0 && (
              <Text fontSize="xs" color="gray.600" ml={8} py={2}>
                No items
              </Text>
            )}
          </Box>
        )
      })}
    </Box>
  )
}

/**
 * Compact folder tree for sidebar
 */
interface CompactFolderTreeProps {
  items: PARAItem[]
  selectedPath?: string
  onSelect?: (item: PARAItem) => void
  maxHeight?: string
}

export function CompactFolderTree({
  items,
  selectedPath,
  onSelect,
  maxHeight = '300px',
}: CompactFolderTreeProps) {
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())

  const handleToggle = useCallback((path: string) => {
    setExpandedPaths((prev) => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }, [])

  return (
    <Box maxH={maxHeight} overflowY="auto" role="tree">
      {items.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          depth={0}
          isSelected={selectedPath === item.path}
          expandedPaths={expandedPaths}
          onSelect={(i) => onSelect?.(i)}
          onToggle={handleToggle}
        />
      ))}
    </Box>
  )
}
