'use client'

import { Button, Flex, Text } from '@chakra-ui/react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

/**
 * Arrow left icon
 */
const ArrowLeftIcon = () => (
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
    <line x1="19" y1="12" x2="5" y2="12" />
    <polyline points="12 19 5 12 12 5" />
  </svg>
)

/**
 * Props for BackButton component
 */
interface BackButtonProps {
  /** Button label */
  label?: string
  /** Show label on mobile */
  showLabelOnMobile?: boolean
  /** Custom onClick handler - if provided, won't use router.back() */
  onClick?: () => void
}

/**
 * BackButton component
 * Navigates to previous page using browser history
 */
export function BackButton({
  label = 'Back',
  showLabelOnMobile = false,
  onClick,
}: BackButtonProps) {
  const router = useRouter()

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      router.back()
    }
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      color="gray.400"
      _hover={{ color: 'white', bg: 'gray.800' }}
      onClick={handleClick}
    >
      <Flex align="center" gap={2}>
        <ArrowLeftIcon />
        <Text display={{ base: showLabelOnMobile ? 'block' : 'none', md: 'block' }}>
          {label}
        </Text>
      </Flex>
    </Button>
  )
}

/**
 * Props for BackLink component
 */
interface BackLinkProps {
  /** Link href */
  href: string
  /** Link label */
  label?: string
  /** Show label on mobile */
  showLabelOnMobile?: boolean
}

/**
 * BackLink component
 * Navigates to a specific route (not browser history)
 */
export function BackLink({
  href,
  label = 'Back',
  showLabelOnMobile = false,
}: BackLinkProps) {
  return (
    <Link href={href}>
      <Flex
        align="center"
        gap={2}
        color="gray.400"
        _hover={{ color: 'white' }}
        transition="color 0.15s"
        py={1}
      >
        <ArrowLeftIcon />
        <Text
          fontSize="sm"
          display={{ base: showLabelOnMobile ? 'block' : 'none', md: 'block' }}
        >
          {label}
        </Text>
      </Flex>
    </Link>
  )
}
