'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import Link from 'next/link'
import { type ReactNode } from 'react'

/**
 * Breadcrumb item interface
 */
export interface BreadcrumbItem {
  /** Display label */
  label: string
  /** Link href - if not provided, item is not clickable */
  href?: string
  /** Optional icon */
  icon?: ReactNode
}

/**
 * Chevron separator icon
 */
const ChevronIcon = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="9 18 15 12 9 6" />
  </svg>
)

/**
 * Home icon
 */
const HomeIcon = () => (
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
    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
)

/**
 * Props for Breadcrumbs component
 */
interface BreadcrumbsProps {
  /** Breadcrumb items */
  items: BreadcrumbItem[]
  /** Show home icon as first item */
  showHome?: boolean
  /** Home href */
  homeHref?: string
  /** Separator between items */
  separator?: ReactNode
  /** Size variant */
  size?: 'sm' | 'md'
}

/**
 * Breadcrumbs navigation component
 * Displays hierarchical navigation path
 */
export function Breadcrumbs({
  items,
  showHome = true,
  homeHref = '/dashboard',
  separator,
  size = 'sm',
}: BreadcrumbsProps) {
  const fontSize = size === 'sm' ? 'sm' : 'md'
  const iconSize = size === 'sm' ? 14 : 16

  const renderSeparator = () => (
    <Box color="gray.600" mx={1}>
      {separator || <ChevronIcon />}
    </Box>
  )

  return (
    <Flex align="center" flexWrap="wrap">
      {/* Home link */}
      {showHome && (
        <>
          <Link href={homeHref}>
            <Flex
              align="center"
              color="gray.400"
              _hover={{ color: 'purple.400' }}
              transition="color 0.15s"
            >
              <HomeIcon />
            </Flex>
          </Link>
          {items.length > 0 && renderSeparator()}
        </>
      )}

      {/* Breadcrumb items */}
      {items.map((item, index) => {
        const isLast = index === items.length - 1

        return (
          <Flex key={index} align="center">
            {item.href && !isLast ? (
              <Link href={item.href}>
                <Flex
                  align="center"
                  gap={1.5}
                  color="gray.400"
                  _hover={{ color: 'purple.400' }}
                  transition="color 0.15s"
                >
                  {item.icon}
                  <Text fontSize={fontSize}>{item.label}</Text>
                </Flex>
              </Link>
            ) : (
              <Flex align="center" gap={1.5} color={isLast ? 'white' : 'gray.400'}>
                {item.icon}
                <Text fontSize={fontSize} fontWeight={isLast ? '500' : '400'}>
                  {item.label}
                </Text>
              </Flex>
            )}
            {!isLast && renderSeparator()}
          </Flex>
        )
      })}
    </Flex>
  )
}
