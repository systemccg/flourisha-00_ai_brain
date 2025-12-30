'use client'

import { Box, Flex, Grid, GridItem, Text, VStack, Button } from '@chakra-ui/react'
import { useState, useCallback } from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { PARAFolderTree, CompactFolderTree } from '@/components/para/folder-tree'
import { FolderBrowser, FolderBreadcrumbs } from '@/components/para/folder-browser'
import { usePARACategories, usePARANavigation, usePARASelection, usePARALazyLoad } from '@/hooks/use-para'
import type { PARAItem, PARACategory } from '@/lib/types'

/**
 * Sidebar toggle icon
 */
const SidebarIcon = () => (
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
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <line x1="9" y1="3" x2="9" y2="21" />
  </svg>
)

/**
 * File preview icons
 */
const Icons = {
  markdown: (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" opacity="0.7">
      <path d="M14.85 3H5.15C4.5 3 4 3.5 4 4.15v15.69C4 20.5 4.5 21 5.15 21h13.69c.66 0 1.15-.5 1.15-1.15V8L14.85 3zM7 15l2-2-2-2h1.5l1.25 1.5L11 11h1.5l-2 2 2 2H11l-1.25-1.5L8.5 15H7zm8 0h-1.5v-3h-1v2l-2-2.5 2-2.5v2h1V8H15v7z" />
    </svg>
  ),
  folder: (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" opacity="0.7">
      <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
    </svg>
  ),
  file: (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.7">
      <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  ),
  image: (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" opacity="0.7">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <polyline points="21 15 16 10 5 21" />
    </svg>
  ),
}

/**
 * PARA Browse page - file explorer for PARA structure
 */
export default function BrowsePage() {
  const [sidebarVisible, setSidebarVisible] = useState(true)

  // Load PARA categories for tree view
  const { data: categoryItems, isLoading: categoriesLoading } = usePARACategories()

  // Navigation state
  const {
    currentPath,
    items,
    breadcrumbs,
    parent,
    isLoading: browseLoading,
    navigate,
    navigateUp,
    refresh,
  } = usePARANavigation()

  // Selection state
  const { selectedItem, selectedPath, select, clear } = usePARASelection()

  // Lazy loading for tree
  const { loadChildren } = usePARALazyLoad()

  // Handle item selection from tree
  const handleTreeSelect = useCallback((item: PARAItem) => {
    select(item)
    if (item.isDirectory) {
      navigate(item.path)
    }
  }, [select, navigate])

  // Handle item selection from browser
  const handleBrowserSelect = useCallback((item: PARAItem) => {
    select(item)
  }, [select])

  // Handle opening a file
  const handleOpen = useCallback((item: PARAItem) => {
    if (!item.isDirectory) {
      // TODO: Open file preview or download
      console.log('Opening file:', item.path)
    }
  }, [])

  // Can navigate up?
  const canGoUp = !!parent || currentPath !== ''

  return (
    <PageContainer maxW="full">
      <PageHeader
        title="Browse Files"
        description="Navigate your PARA folder structure - Projects, Areas, Resources, and Archives."
        actions={
          <Button
            size="sm"
            variant={sidebarVisible ? 'solid' : 'outline'}
            colorPalette="gray"
            onClick={() => setSidebarVisible(!sidebarVisible)}
          >
            <SidebarIcon />
            <Text ml={2} display={{ base: 'none', md: 'block' }}>
              {sidebarVisible ? 'Hide Tree' : 'Show Tree'}
            </Text>
          </Button>
        }
      />

      <Grid
        templateColumns={sidebarVisible ? { base: '1fr', lg: '280px 1fr' } : '1fr'}
        gap={6}
      >
        {/* Sidebar - PARA Tree */}
        {sidebarVisible && (
          <GridItem>
            <Box
              bg="gray.900"
              borderRadius="xl"
              p={4}
              position="sticky"
              top={4}
              maxH="calc(100vh - 200px)"
              overflowY="auto"
            >
              <Text
                color="gray.500"
                fontSize="xs"
                fontWeight="600"
                textTransform="uppercase"
                letterSpacing="wide"
                mb={3}
              >
                PARA Structure
              </Text>

              {categoryItems ? (
                <PARAFolderTree
                  items={categoryItems}
                  selectedPath={selectedPath ?? undefined}
                  onSelect={handleTreeSelect}
                  onLoadChildren={loadChildren}
                  isLoading={categoriesLoading}
                />
              ) : (
                <Text color="gray.600" fontSize="sm">
                  Loading...
                </Text>
              )}
            </Box>
          </GridItem>
        )}

        {/* Main Browser */}
        <GridItem>
          <Grid
            templateColumns={selectedItem && !selectedItem.isDirectory ? { base: '1fr', xl: '1fr 320px' } : '1fr'}
            gap={6}
          >
            {/* File Browser */}
            <GridItem>
              <FolderBrowser
                items={items}
                breadcrumbs={breadcrumbs.map(b => ({ name: b.name, path: b.path }))}
                isLoading={browseLoading}
                selectedPath={selectedPath ?? undefined}
                canGoUp={canGoUp}
                onNavigate={navigate}
                onGoUp={navigateUp}
                onRefresh={refresh}
                onSelect={handleBrowserSelect}
                onOpen={handleOpen}
              />
            </GridItem>

            {/* File Preview Panel */}
            {selectedItem && !selectedItem.isDirectory && (
              <GridItem>
                <FilePreviewPanel
                  item={selectedItem}
                  onClose={clear}
                  onOpen={() => handleOpen(selectedItem)}
                />
              </GridItem>
            )}
          </Grid>
        </GridItem>
      </Grid>
    </PageContainer>
  )
}

/**
 * File preview panel component
 */
interface FilePreviewPanelProps {
  item: PARAItem
  onClose: () => void
  onOpen: () => void
}

function FilePreviewPanel({ item, onClose, onOpen }: FilePreviewPanelProps) {
  // Get preview icon based on file type
  const getPreviewIcon = () => {
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
      default:
        return Icons.file
    }
  }

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
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </Flex>

      {/* Preview Content */}
      <VStack align="stretch" gap={4} p={4}>
        {/* File Icon */}
        <Flex justify="center" py={4}>
          <Box color="gray.400">
            {getPreviewIcon()}
          </Box>
        </Flex>

        {/* File Name */}
        <Box textAlign="center">
          <Text color="white" fontWeight="600" fontSize="md">
            {item.name}
          </Text>
          {item.extension && (
            <Text color="gray.500" fontSize="sm" mt={1}>
              .{item.extension} file
            </Text>
          )}
        </Box>

        {/* File Details */}
        <Box
          bg="gray.850"
          borderRadius="lg"
          p={3}
        >
          <VStack align="stretch" gap={2}>
            {item.size !== undefined && (
              <Flex justify="space-between">
                <Text color="gray.500" fontSize="xs">Size</Text>
                <Text color="gray.300" fontSize="xs">{formatFileSize(item.size)}</Text>
              </Flex>
            )}
            {item.modifiedAt && (
              <Flex justify="space-between">
                <Text color="gray.500" fontSize="xs">Modified</Text>
                <Text color="gray.300" fontSize="xs">{formatDate(item.modifiedAt)}</Text>
              </Flex>
            )}
            <Flex justify="space-between">
              <Text color="gray.500" fontSize="xs">Path</Text>
              <Text
                color="gray.300"
                fontSize="xs"
                maxW="150px"
                overflow="hidden"
                textOverflow="ellipsis"
                whiteSpace="nowrap"
                title={item.path}
              >
                {item.path}
              </Text>
            </Flex>
          </VStack>
        </Box>

        {/* Actions */}
        <Flex gap={2} pt={2}>
          <Button
            size="sm"
            colorPalette="purple"
            variant="solid"
            flex={1}
            onClick={onOpen}
          >
            Open
          </Button>
          <Button
            size="sm"
            variant="outline"
            colorPalette="gray"
          >
            Download
          </Button>
        </Flex>
      </VStack>
    </Box>
  )
}

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes?: number): string {
  if (bytes === undefined || bytes === null) return '-'
  if (bytes === 0) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`
}

/**
 * Format date in human-readable format
 */
function formatDate(dateString?: string): string {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
