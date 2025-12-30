'use client'

import {
  Box,
  Flex,
  VStack,
  Text,
  IconButton,
} from '@chakra-ui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, type ReactNode } from 'react'

/**
 * Navigation item interface
 */
interface NavItem {
  name: string
  href: string
  icon: ReactNode
  badge?: number
}

/**
 * Navigation sections
 */
const mainNavItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
  },
  {
    name: 'Search',
    href: '/dashboard/search',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8" />
        <path d="M21 21l-4.35-4.35" />
      </svg>
    ),
  },
  {
    name: 'Knowledge Graph',
    href: '/dashboard/graph',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="6" cy="6" r="3" />
        <circle cx="18" cy="18" r="3" />
        <path d="M6 21V9a9 9 0 009 9" />
      </svg>
    ),
  },
  {
    name: 'PARA Browser',
    href: '/dashboard/para',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
      </svg>
    ),
  },
]

const trackingNavItems: NavItem[] = [
  {
    name: 'OKRs',
    href: '/dashboard/okrs',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="6" />
        <circle cx="12" cy="12" r="2" />
      </svg>
    ),
  },
  {
    name: 'Energy',
    href: '/dashboard/energy',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
      </svg>
    ),
  },
  {
    name: 'Morning Report',
    href: '/dashboard/morning-report',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="1" x2="12" y2="3" />
        <line x1="12" y1="21" x2="12" y2="23" />
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
        <line x1="1" y1="12" x2="3" y2="12" />
        <line x1="21" y1="12" x2="23" y2="12" />
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
      </svg>
    ),
  },
]

const systemNavItems: NavItem[] = [
  {
    name: 'Skills',
    href: '/dashboard/skills',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
  {
    name: 'Integrations',
    href: '/dashboard/integrations',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="2" width="8" height="8" rx="2" />
        <rect x="14" y="2" width="8" height="8" rx="2" />
        <rect x="14" y="14" width="8" height="8" rx="2" />
        <rect x="2" y="14" width="8" height="8" rx="2" />
        <path d="M6 10v4" />
        <path d="M18 10v4" />
        <path d="M10 6h4" />
        <path d="M10 18h4" />
      </svg>
    ),
  },
  {
    name: 'Health',
    href: '/dashboard/health',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
    ),
  },
  {
    name: 'Settings',
    href: '/dashboard/settings',
    icon: (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
      </svg>
    ),
  },
]

/**
 * NavLink component for sidebar navigation items
 */
function NavLink({ item, isCollapsed }: { item: NavItem; isCollapsed: boolean }) {
  const pathname = usePathname()
  const isActive = pathname === item.href ||
    (item.href !== '/dashboard' && pathname.startsWith(item.href))

  const content = (
    <Link href={item.href} style={{ width: '100%' }}>
      <Flex
        align="center"
        gap={3}
        px={3}
        py={2.5}
        borderRadius="lg"
        cursor="pointer"
        bg={isActive ? 'purple.500/20' : 'transparent'}
        color={isActive ? 'purple.300' : 'gray.400'}
        _hover={{
          bg: isActive ? 'purple.500/20' : 'gray.800',
          color: isActive ? 'purple.300' : 'white',
        }}
        transition="all 0.15s"
        position="relative"
        title={isCollapsed ? item.name : undefined}
      >
        {isActive && (
          <Box
            position="absolute"
            left={0}
            top="50%"
            transform="translateY(-50%)"
            w="3px"
            h="60%"
            bg="purple.500"
            borderRadius="full"
          />
        )}
        <Box flexShrink={0}>{item.icon}</Box>
        {!isCollapsed && (
          <Text fontSize="sm" fontWeight={isActive ? '600' : '400'}>
            {item.name}
          </Text>
        )}
        {!isCollapsed && item.badge !== undefined && item.badge > 0 && (
          <Box
            ml="auto"
            bg="purple.500"
            color="white"
            fontSize="xs"
            fontWeight="600"
            px={2}
            py={0.5}
            borderRadius="full"
          >
            {item.badge}
          </Box>
        )}
      </Flex>
    </Link>
  )

  return content
}

/**
 * NavSection component for grouped navigation items
 */
function NavSection({
  title,
  items,
  isCollapsed,
}: {
  title: string
  items: NavItem[]
  isCollapsed: boolean
}) {
  return (
    <Box>
      {!isCollapsed && (
        <Text
          fontSize="xs"
          fontWeight="600"
          color="gray.500"
          textTransform="uppercase"
          letterSpacing="wider"
          px={3}
          mb={2}
        >
          {title}
        </Text>
      )}
      <VStack gap={1} align="stretch">
        {items.map((item) => (
          <NavLink key={item.href} item={item} isCollapsed={isCollapsed} />
        ))}
      </VStack>
    </Box>
  )
}

/**
 * Sidebar component for dashboard navigation
 */
export function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <Box
      as="nav"
      position="fixed"
      left={0}
      top={0}
      h="100vh"
      w={isCollapsed ? '72px' : '240px'}
      bg="gray.900"
      borderRightWidth={1}
      borderColor="gray.800"
      transition="width 0.2s"
      zIndex={20}
      display="flex"
      flexDirection="column"
    >
      {/* Logo */}
      <Flex
        align="center"
        justify={isCollapsed ? 'center' : 'space-between'}
        h="64px"
        px={isCollapsed ? 3 : 4}
        borderBottomWidth={1}
        borderColor="gray.800"
        flexShrink={0}
      >
        {!isCollapsed && (
          <Text
            fontSize="xl"
            fontWeight="bold"
            bgGradient="to-r"
            gradientFrom="purple.400"
            gradientTo="cyan.400"
            bgClip="text"
          >
            Flourisha
          </Text>
        )}
        {isCollapsed && (
          <Text
            fontSize="xl"
            fontWeight="bold"
            bgGradient="to-r"
            gradientFrom="purple.400"
            gradientTo="cyan.400"
            bgClip="text"
          >
            F
          </Text>
        )}
        <IconButton
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          variant="ghost"
          size="sm"
          color="gray.400"
          _hover={{ color: 'white', bg: 'gray.800' }}
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="9 18 15 12 9 6" />
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="15 18 9 12 15 6" />
            </svg>
          )}
        </IconButton>
      </Flex>

      {/* Navigation */}
      <Box
        flex={1}
        overflowY="auto"
        py={4}
        px={isCollapsed ? 2 : 3}
      >
        <VStack gap={6} align="stretch">
          <NavSection title="Main" items={mainNavItems} isCollapsed={isCollapsed} />
          <NavSection title="Tracking" items={trackingNavItems} isCollapsed={isCollapsed} />
          <NavSection title="System" items={systemNavItems} isCollapsed={isCollapsed} />
        </VStack>
      </Box>

      {/* Footer */}
      <Box
        borderTopWidth={1}
        borderColor="gray.800"
        py={3}
        px={isCollapsed ? 2 : 3}
        flexShrink={0}
      >
        <a
          href="https://docs.flourisha.ai"
          target="_blank"
          rel="noopener noreferrer"
          title={isCollapsed ? 'Help & Documentation' : undefined}
        >
          <Flex
            align="center"
            gap={3}
            px={3}
            py={2}
            borderRadius="lg"
            color="gray.500"
            _hover={{ color: 'gray.300', bg: 'gray.800' }}
            transition="all 0.15s"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            {!isCollapsed && <Text fontSize="sm">Help</Text>}
          </Flex>
        </a>
      </Box>
    </Box>
  )
}

/**
 * Get the sidebar width for layout calculations
 */
export const SIDEBAR_WIDTH = 240
export const SIDEBAR_COLLAPSED_WIDTH = 72
