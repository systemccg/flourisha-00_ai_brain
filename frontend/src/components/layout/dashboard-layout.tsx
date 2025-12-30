'use client'

import { Box, Flex } from '@chakra-ui/react'
import { type ReactNode } from 'react'
import { Sidebar, SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH } from './sidebar'
import { Header } from './header'

/**
 * Props for DashboardLayout component
 */
interface DashboardLayoutProps {
  children: ReactNode
  /**
   * Whether to show the header
   * @default true
   */
  showHeader?: boolean
  /**
   * Additional padding for the content area
   */
  contentPadding?: number | string
}

/**
 * DashboardLayout component
 * Provides the main layout structure with sidebar and optional header
 */
export function DashboardLayout({
  children,
  showHeader = true,
  contentPadding = 6,
}: DashboardLayoutProps) {
  return (
    <Flex minH="100vh" bg="gray.950">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <Box
        flex={1}
        ml={{ base: `${SIDEBAR_COLLAPSED_WIDTH}px`, md: `${SIDEBAR_WIDTH}px` }}
        transition="margin-left 0.2s"
      >
        {/* Header */}
        {showHeader && <Header />}

        {/* Page Content */}
        <Box
          as="main"
          p={contentPadding}
          minH={showHeader ? 'calc(100vh - 64px)' : '100vh'}
        >
          {children}
        </Box>
      </Box>
    </Flex>
  )
}

/**
 * PageContainer component
 * Standard container for page content with max width
 */
export function PageContainer({
  children,
  maxW = '7xl',
}: {
  children: ReactNode
  maxW?: string
}) {
  return (
    <Box maxW={maxW} mx="auto" w="full">
      {children}
    </Box>
  )
}

/**
 * PageHeader component
 * Consistent header for dashboard pages
 */
export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string
  description?: string
  actions?: ReactNode
}) {
  return (
    <Flex
      justify="space-between"
      align={{ base: 'start', md: 'center' }}
      flexDir={{ base: 'column', md: 'row' }}
      gap={4}
      mb={6}
    >
      <Box>
        <Box
          as="h1"
          fontSize={{ base: '2xl', md: '3xl' }}
          fontWeight="bold"
          color="white"
        >
          {title}
        </Box>
        {description && (
          <Box
            as="p"
            color="gray.400"
            mt={1}
            fontSize={{ base: 'sm', md: 'md' }}
          >
            {description}
          </Box>
        )}
      </Box>
      {actions && (
        <Flex gap={3} flexShrink={0}>
          {actions}
        </Flex>
      )}
    </Flex>
  )
}
