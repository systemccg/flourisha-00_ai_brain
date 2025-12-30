'use client'

import { Box, Flex, Text, IconButton } from '@chakra-ui/react'
import { useTheme, type ThemeMode } from '@/contexts/theme-context'

/**
 * Sun icon for light mode
 */
const SunIcon = () => (
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
)

/**
 * Moon icon for dark mode
 */
const MoonIcon = () => (
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
    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
  </svg>
)

/**
 * System/Auto icon
 */
const SystemIcon = () => (
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
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
    <line x1="8" y1="21" x2="16" y2="21" />
    <line x1="12" y1="17" x2="12" y2="21" />
  </svg>
)

/**
 * Simple theme toggle button
 * Toggles between light and dark mode
 */
export function ThemeToggle() {
  const { resolvedTheme, toggle } = useTheme()

  return (
    <IconButton
      aria-label={`Switch to ${resolvedTheme === 'dark' ? 'light' : 'dark'} mode`}
      variant="ghost"
      size="sm"
      color="gray.400"
      _hover={{ color: 'white', bg: 'gray.800' }}
      onClick={toggle}
    >
      {resolvedTheme === 'dark' ? <SunIcon /> : <MoonIcon />}
    </IconButton>
  )
}

/**
 * Theme mode option configuration
 */
interface ThemeModeOption {
  value: ThemeMode
  label: string
  icon: React.ReactNode
}

const themeModes: ThemeModeOption[] = [
  { value: 'light', label: 'Light', icon: <SunIcon /> },
  { value: 'dark', label: 'Dark', icon: <MoonIcon /> },
  { value: 'system', label: 'System', icon: <SystemIcon /> },
]

/**
 * Theme mode selector with three options
 * Allows selection between light, dark, and system preference
 */
export function ThemeModeSelector() {
  const { mode, setMode } = useTheme()

  return (
    <Flex
      bg="gray.800"
      borderRadius="lg"
      p={1}
      gap={1}
    >
      {themeModes.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => setMode(option.value)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '6px 12px',
            borderRadius: '6px',
            border: 'none',
            background: mode === option.value ? '#374151' : 'transparent',
            color: mode === option.value ? '#ffffff' : '#6b7280',
            fontWeight: mode === option.value ? '500' : '400',
            fontSize: '14px',
            transition: 'all 0.15s',
            cursor: 'pointer',
          }}
        >
          {option.icon}
          <Text>{option.label}</Text>
        </button>
      ))}
    </Flex>
  )
}

/**
 * Compact theme toggle for sidebar footer
 * Shows current mode with icon
 */
export function CompactThemeToggle() {
  const { mode, resolvedTheme, setMode } = useTheme()

  // Cycle through modes: light -> dark -> system -> light
  const cycleMode = () => {
    const order: ThemeMode[] = ['light', 'dark', 'system']
    const currentIndex = order.indexOf(mode)
    const nextIndex = (currentIndex + 1) % order.length
    setMode(order[nextIndex])
  }

  const getIcon = () => {
    if (mode === 'system') return <SystemIcon />
    return resolvedTheme === 'dark' ? <MoonIcon /> : <SunIcon />
  }

  const getLabel = () => {
    if (mode === 'system') return 'System'
    return resolvedTheme === 'dark' ? 'Dark' : 'Light'
  }

  return (
    <button
      type="button"
      onClick={cycleMode}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        width: '100%',
        padding: '8px 12px',
        borderRadius: '8px',
        border: 'none',
        background: 'transparent',
        color: '#6b7280',
        transition: 'all 0.15s',
        cursor: 'pointer',
      }}
    >
      {getIcon()}
      <Text fontSize="sm">{getLabel()}</Text>
    </button>
  )
}
