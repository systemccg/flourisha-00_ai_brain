'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { type ReactNode } from 'react'

/**
 * Nav tab item interface
 */
export interface NavTab {
  /** Tab label */
  label: string
  /** Tab href */
  href: string
  /** Optional icon */
  icon?: ReactNode
  /** Badge count */
  badge?: number
  /** Disabled state */
  disabled?: boolean
}

/**
 * Props for NavTabs component
 */
interface NavTabsProps {
  /** Tab items */
  tabs: NavTab[]
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Full width tabs */
  fullWidth?: boolean
}

/**
 * NavTabs component
 * Horizontal tab navigation with active state based on current route
 */
export function NavTabs({ tabs, size = 'md', fullWidth = false }: NavTabsProps) {
  const pathname = usePathname()

  const sizeStyles = {
    sm: { px: 3, py: 2, fontSize: 'sm', gap: 1.5 },
    md: { px: 4, py: 2.5, fontSize: 'sm', gap: 2 },
    lg: { px: 5, py: 3, fontSize: 'md', gap: 2 },
  }

  const styles = sizeStyles[size]

  return (
    <Flex
      borderBottomWidth={1}
      borderColor="gray.800"
      overflowX="auto"
      css={{
        '&::-webkit-scrollbar': {
          display: 'none',
        },
        scrollbarWidth: 'none',
      }}
    >
      {tabs.map((tab) => {
        const isActive = pathname === tab.href || pathname.startsWith(`${tab.href}/`)

        if (tab.disabled) {
          return (
            <Box
              key={tab.href}
              px={styles.px}
              py={styles.py}
              position="relative"
              cursor="not-allowed"
              opacity={0.5}
              flex={fullWidth ? 1 : 'none'}
            >
              <Flex align="center" justify="center" gap={styles.gap}>
                {tab.icon}
                <Text fontSize={styles.fontSize}>{tab.label}</Text>
              </Flex>
            </Box>
          )
        }

        return (
          <Link key={tab.href} href={tab.href} style={{ flex: fullWidth ? 1 : 'none' }}>
            <Box
              px={styles.px}
              py={styles.py}
              position="relative"
              color={isActive ? 'white' : 'gray.400'}
              _hover={{ color: 'white', bg: 'gray.900' }}
              transition="all 0.15s"
              whiteSpace="nowrap"
            >
              <Flex align="center" justify="center" gap={styles.gap}>
                {tab.icon}
                <Text fontSize={styles.fontSize} fontWeight={isActive ? '500' : '400'}>
                  {tab.label}
                </Text>
                {tab.badge !== undefined && tab.badge > 0 && (
                  <Box
                    bg={isActive ? 'purple.500' : 'gray.700'}
                    color="white"
                    fontSize="xs"
                    fontWeight="600"
                    px={1.5}
                    py={0.5}
                    borderRadius="full"
                    minW={5}
                    textAlign="center"
                  >
                    {tab.badge > 99 ? '99+' : tab.badge}
                  </Box>
                )}
              </Flex>

              {/* Active indicator */}
              {isActive && (
                <Box
                  position="absolute"
                  bottom={0}
                  left={0}
                  right={0}
                  h="2px"
                  bg="purple.500"
                />
              )}
            </Box>
          </Link>
        )
      })}
    </Flex>
  )
}
