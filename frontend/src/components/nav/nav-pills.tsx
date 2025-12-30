'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { type ReactNode } from 'react'

/**
 * Nav pill item interface
 */
export interface NavPill {
  /** Pill label */
  label: string
  /** Pill href or value */
  href?: string
  value?: string
  /** Optional icon */
  icon?: ReactNode
  /** Badge count */
  badge?: number
  /** Disabled state */
  disabled?: boolean
}

/**
 * Props for NavPills component
 */
interface NavPillsProps {
  /** Pill items */
  pills: NavPill[]
  /** Currently selected value (for controlled mode) */
  value?: string
  /** Callback when pill is selected (for controlled mode) */
  onChange?: (value: string) => void
  /** Size variant */
  size?: 'sm' | 'md'
  /** Color scheme */
  colorScheme?: 'purple' | 'blue' | 'green' | 'gray'
}

/**
 * Color scheme mappings
 */
const colorSchemes = {
  purple: {
    activeBg: 'purple.500',
    activeColor: 'white',
    inactiveBg: 'gray.800',
    inactiveColor: 'gray.400',
    hoverBg: 'gray.700',
  },
  blue: {
    activeBg: 'blue.500',
    activeColor: 'white',
    inactiveBg: 'gray.800',
    inactiveColor: 'gray.400',
    hoverBg: 'gray.700',
  },
  green: {
    activeBg: 'green.500',
    activeColor: 'white',
    inactiveBg: 'gray.800',
    inactiveColor: 'gray.400',
    hoverBg: 'gray.700',
  },
  gray: {
    activeBg: 'gray.700',
    activeColor: 'white',
    inactiveBg: 'gray.800',
    inactiveColor: 'gray.400',
    hoverBg: 'gray.700',
  },
}

/**
 * NavPills component
 * Pill-style navigation tabs (can be used as route nav or controlled tabs)
 */
export function NavPills({
  pills,
  value,
  onChange,
  size = 'md',
  colorScheme = 'purple',
}: NavPillsProps) {
  const pathname = usePathname()
  const colors = colorSchemes[colorScheme]

  const sizeStyles = {
    sm: { px: 3, py: 1.5, fontSize: 'xs', gap: 1.5 },
    md: { px: 4, py: 2, fontSize: 'sm', gap: 2 },
  }

  const styles = sizeStyles[size]

  const isActive = (pill: NavPill) => {
    if (value !== undefined) {
      return pill.value === value
    }
    if (pill.href) {
      return pathname === pill.href || pathname.startsWith(`${pill.href}/`)
    }
    return false
  }

  const renderPill = (pill: NavPill) => {
    const active = isActive(pill)

    const content = (
      <Flex
        align="center"
        gap={styles.gap}
        px={styles.px}
        py={styles.py}
        borderRadius="full"
        bg={active ? colors.activeBg : colors.inactiveBg}
        color={active ? colors.activeColor : colors.inactiveColor}
        _hover={!active && !pill.disabled ? { bg: colors.hoverBg, color: 'white' } : {}}
        transition="all 0.15s"
        cursor={pill.disabled ? 'not-allowed' : 'pointer'}
        opacity={pill.disabled ? 0.5 : 1}
        whiteSpace="nowrap"
      >
        {pill.icon}
        <Text fontSize={styles.fontSize} fontWeight={active ? '600' : '400'}>
          {pill.label}
        </Text>
        {pill.badge !== undefined && pill.badge > 0 && (
          <Box
            bg={active ? 'whiteAlpha.300' : 'gray.700'}
            color={active ? 'white' : 'gray.300'}
            fontSize="xs"
            fontWeight="600"
            px={1.5}
            py={0.5}
            borderRadius="full"
            minW={5}
            textAlign="center"
          >
            {pill.badge > 99 ? '99+' : pill.badge}
          </Box>
        )}
      </Flex>
    )

    // If using href (route-based)
    if (pill.href && !pill.disabled) {
      return (
        <Link key={pill.href} href={pill.href}>
          {content}
        </Link>
      )
    }

    // If using value (controlled)
    return (
      <Box
        key={pill.value || pill.label}
        onClick={() => {
          if (!pill.disabled && onChange && pill.value) {
            onChange(pill.value)
          }
        }}
      >
        {content}
      </Box>
    )
  }

  return (
    <Flex
      align="center"
      gap={2}
      p={1}
      bg="gray.900"
      borderRadius="full"
      overflowX="auto"
      css={{
        '&::-webkit-scrollbar': {
          display: 'none',
        },
        scrollbarWidth: 'none',
      }}
    >
      {pills.map(renderPill)}
    </Flex>
  )
}
