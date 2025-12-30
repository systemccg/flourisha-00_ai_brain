'use client'

import {
  Box,
  Flex,
  Text,
  Menu,
  Portal,
  Button,
} from '@chakra-ui/react'
import { useState, useCallback } from 'react'

/**
 * Workspace interface
 */
export interface Workspace {
  id: string
  name: string
  icon?: string
  color?: string
  isDefault?: boolean
}

/**
 * Check icon component
 */
const CheckIcon = () => (
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
    <polyline points="20 6 9 17 4 12" />
  </svg>
)

/**
 * Plus icon component
 */
const PlusIcon = () => (
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
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
)

/**
 * Default workspaces for development
 * In production, these would come from the API
 */
const defaultWorkspaces: Workspace[] = [
  {
    id: 'personal',
    name: 'Personal',
    icon: '🏠',
    color: 'purple',
    isDefault: true,
  },
  {
    id: 'business',
    name: 'Business',
    icon: '💼',
    color: 'blue',
  },
  {
    id: 'flourisha',
    name: 'Flourisha Dev',
    icon: '🌸',
    color: 'pink',
  },
]

/**
 * Color map for workspace colors
 */
const colorMap: Record<string, { bg: string; text: string }> = {
  purple: { bg: 'purple.500', text: 'purple.200' },
  blue: { bg: 'blue.500', text: 'blue.200' },
  pink: { bg: 'pink.500', text: 'pink.200' },
  green: { bg: 'green.500', text: 'green.200' },
  orange: { bg: 'orange.500', text: 'orange.200' },
  cyan: { bg: 'cyan.500', text: 'cyan.200' },
}

/**
 * Get workspace initial for avatar fallback
 */
function getWorkspaceInitial(workspace: Workspace): string {
  if (workspace.icon) return workspace.icon
  return workspace.name.charAt(0).toUpperCase()
}

/**
 * Workspace avatar component
 */
function WorkspaceAvatar({
  workspace,
  size = 'md',
}: {
  workspace: Workspace
  size?: 'sm' | 'md'
}) {
  const sizeMap = {
    sm: { box: 6, font: 'xs' },
    md: { box: 8, font: 'sm' },
  }
  const dimensions = sizeMap[size]
  const colors = colorMap[workspace.color || 'purple']

  return (
    <Flex
      w={dimensions.box}
      h={dimensions.box}
      align="center"
      justify="center"
      borderRadius="md"
      bg={colors.bg}
      color="white"
      fontSize={dimensions.font}
      fontWeight="600"
      flexShrink={0}
    >
      {getWorkspaceInitial(workspace)}
    </Flex>
  )
}

/**
 * Props for WorkspaceSwitcher
 */
interface WorkspaceSwitcherProps {
  /**
   * Available workspaces
   * @default defaultWorkspaces
   */
  workspaces?: Workspace[]
  /**
   * Currently selected workspace ID
   */
  currentWorkspaceId?: string
  /**
   * Callback when workspace is changed
   */
  onWorkspaceChange?: (workspace: Workspace) => void
  /**
   * Callback when "Create workspace" is clicked
   */
  onCreateWorkspace?: () => void
  /**
   * Show compact version (icon only)
   */
  compact?: boolean
}

/**
 * WorkspaceSwitcher component
 * Allows users to switch between different workspaces/contexts
 */
export function WorkspaceSwitcher({
  workspaces = defaultWorkspaces,
  currentWorkspaceId,
  onWorkspaceChange,
  onCreateWorkspace,
  compact = false,
}: WorkspaceSwitcherProps) {
  const [selectedId, setSelectedId] = useState(
    currentWorkspaceId || workspaces.find((w) => w.isDefault)?.id || workspaces[0]?.id
  )

  const currentWorkspace = workspaces.find((w) => w.id === selectedId) || workspaces[0]

  const handleSelect = useCallback(
    (workspace: Workspace) => {
      setSelectedId(workspace.id)
      onWorkspaceChange?.(workspace)
    },
    [onWorkspaceChange]
  )

  if (!currentWorkspace) return null

  return (
    <Menu.Root>
      <Menu.Trigger asChild>
        <Button
          variant="ghost"
          size="sm"
          px={compact ? 2 : 3}
          _hover={{ bg: 'gray.800' }}
        >
          <Flex align="center" gap={2}>
            <WorkspaceAvatar workspace={currentWorkspace} size="sm" />
            {!compact && (
              <>
                <Box textAlign="left" display={{ base: 'none', md: 'block' }}>
                  <Text fontSize="sm" color="white" fontWeight="500">
                    {currentWorkspace.name}
                  </Text>
                </Box>
                <Box color="gray.500">
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </Box>
              </>
            )}
          </Flex>
        </Button>
      </Menu.Trigger>

      <Portal>
        <Menu.Positioner>
          <Menu.Content
            bg="gray.800"
            borderColor="gray.700"
            minW="240px"
            py={2}
          >
            {/* Workspace list */}
            <Box px={2} pb={2}>
              <Text fontSize="xs" color="gray.500" fontWeight="500" mb={2} px={2}>
                WORKSPACES
              </Text>
              {workspaces.map((workspace) => {
                const isSelected = workspace.id === selectedId
                return (
                  <Menu.Item
                    key={workspace.id}
                    value={workspace.id}
                    cursor="pointer"
                    _hover={{ bg: 'gray.700' }}
                    py={2}
                    px={2}
                    borderRadius="md"
                    onClick={() => handleSelect(workspace)}
                  >
                    <Flex align="center" justify="space-between" w="full">
                      <Flex align="center" gap={3}>
                        <WorkspaceAvatar workspace={workspace} size="sm" />
                        <Box>
                          <Text fontSize="sm" fontWeight={isSelected ? '600' : '400'}>
                            {workspace.name}
                          </Text>
                          {workspace.isDefault && (
                            <Text fontSize="xs" color="gray.500">
                              Default
                            </Text>
                          )}
                        </Box>
                      </Flex>
                      {isSelected && (
                        <Box color="purple.400">
                          <CheckIcon />
                        </Box>
                      )}
                    </Flex>
                  </Menu.Item>
                )
              })}
            </Box>

            <Menu.Separator borderColor="gray.700" my={2} />

            {/* Create workspace */}
            <Menu.Item
              value="create"
              cursor="pointer"
              _hover={{ bg: 'gray.700' }}
              py={2}
              px={4}
              onClick={onCreateWorkspace}
            >
              <Flex align="center" gap={3}>
                <Box color="gray.400">
                  <PlusIcon />
                </Box>
                <Text fontSize="sm" color="gray.300">
                  Create workspace
                </Text>
              </Flex>
            </Menu.Item>
          </Menu.Content>
        </Menu.Positioner>
      </Portal>
    </Menu.Root>
  )
}

/**
 * Hook to manage workspace state
 * Can be used to persist workspace selection
 */
export function useWorkspace(defaultWorkspaceId?: string) {
  const [currentWorkspaceId, setCurrentWorkspaceId] = useState<string | undefined>(
    defaultWorkspaceId
  )

  const selectWorkspace = useCallback((workspace: Workspace) => {
    setCurrentWorkspaceId(workspace.id)
    // Optionally persist to localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('flourisha-workspace', workspace.id)
    }
  }, [])

  // Load from localStorage on mount
  useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('flourisha-workspace')
      if (stored) {
        setCurrentWorkspaceId(stored)
      }
    }
  })

  return {
    currentWorkspaceId,
    selectWorkspace,
  }
}
