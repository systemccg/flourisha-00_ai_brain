'use client'

import {
  Box,
  Flex,
  Text,
  Button,
  Menu,
  Portal,
  Avatar,
} from '@chakra-ui/react'
import { useAuth } from '@/hooks/use-auth'
import { useRouter } from 'next/navigation'
import { ThemeToggle } from '@/components/ui'
import { SearchTrigger, UnifiedSearchBar } from '@/components/search'

/**
 * Header component for the dashboard
 * Displays user info, workspace switcher, and global actions
 */
export function Header() {
  const { user, signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push('/login')
  }

  return (
    <Box
      as="header"
      position="sticky"
      top={0}
      h="64px"
      bg="gray.900/80"
      backdropFilter="blur(12px)"
      borderBottomWidth={1}
      borderColor="gray.800"
      zIndex={10}
    >
      <Flex
        h="full"
        align="center"
        justify="space-between"
        px={6}
      >
        {/* Left: Breadcrumb / Page Title */}
        <Flex align="center" gap={3}>
          <Text color="gray.500" fontSize="sm">
            Dashboard
          </Text>
        </Flex>

        {/* Right: Actions & User Menu */}
        <Flex align="center" gap={4}>
          {/* Quick Search */}
          <SearchTrigger />

          {/* Search Modal (rendered via portal) */}
          <UnifiedSearchBar />

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications */}
          <Button
            variant="ghost"
            size="sm"
            color="gray.400"
            _hover={{ color: 'white', bg: 'gray.800' }}
            position="relative"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 01-3.46 0" />
            </svg>
            {/* Notification badge */}
            <Box
              position="absolute"
              top={1}
              right={1}
              w={2}
              h={2}
              bg="purple.500"
              borderRadius="full"
            />
          </Button>

          {/* User Menu */}
          <Menu.Root>
            <Menu.Trigger asChild>
              <Button
                variant="ghost"
                size="sm"
                px={2}
                _hover={{ bg: 'gray.800' }}
              >
                <Flex align="center" gap={2}>
                  <Avatar.Root size="sm">
                    <Avatar.Fallback bg="purple.500" color="white">
                      {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </Avatar.Fallback>
                    {user?.avatar_url && <Avatar.Image src={user.avatar_url} />}
                  </Avatar.Root>
                  <Box display={{ base: 'none', md: 'block' }} textAlign="left">
                    <Text fontSize="sm" color="white" fontWeight="500">
                      {user?.name || 'User'}
                    </Text>
                    <Text fontSize="xs" color="gray.500">
                      {user?.email}
                    </Text>
                  </Box>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </Flex>
              </Button>
            </Menu.Trigger>
            <Portal>
              <Menu.Positioner>
                <Menu.Content
                  bg="gray.800"
                  borderColor="gray.700"
                  minW="200px"
                  py={2}
                >
                  <Menu.Item
                    value="profile"
                    cursor="pointer"
                    _hover={{ bg: 'gray.700' }}
                    py={2}
                    px={4}
                    onClick={() => router.push('/dashboard/settings')}
                  >
                    <Flex align="center" gap={3}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                      </svg>
                      <Text fontSize="sm">Profile Settings</Text>
                    </Flex>
                  </Menu.Item>
                  <Menu.Item
                    value="keyboard"
                    cursor="pointer"
                    _hover={{ bg: 'gray.700' }}
                    py={2}
                    px={4}
                  >
                    <Flex align="center" gap={3}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect x="2" y="4" width="20" height="16" rx="2" ry="2" />
                        <path d="M6 8h.01" />
                        <path d="M10 8h.01" />
                        <path d="M14 8h.01" />
                        <path d="M18 8h.01" />
                        <path d="M8 12h.01" />
                        <path d="M12 12h.01" />
                        <path d="M16 12h.01" />
                        <path d="M7 16h10" />
                      </svg>
                      <Text fontSize="sm">Keyboard Shortcuts</Text>
                    </Flex>
                  </Menu.Item>
                  <Menu.Separator borderColor="gray.700" my={2} />
                  <Menu.Item
                    value="signout"
                    cursor="pointer"
                    _hover={{ bg: 'gray.700' }}
                    py={2}
                    px={4}
                    color="red.400"
                    onClick={handleSignOut}
                  >
                    <Flex align="center" gap={3}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                        <polyline points="16 17 21 12 16 7" />
                        <line x1="21" y1="12" x2="9" y2="12" />
                      </svg>
                      <Text fontSize="sm">Sign Out</Text>
                    </Flex>
                  </Menu.Item>
                </Menu.Content>
              </Menu.Positioner>
            </Portal>
          </Menu.Root>
        </Flex>
      </Flex>
    </Box>
  )
}
