'use client'

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react'
import { Box, Flex, Text, IconButton, Portal } from '@chakra-ui/react'

/**
 * Toast types for different notification styles
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info'

/**
 * Toast configuration
 */
export interface ToastConfig {
  id: string
  type: ToastType
  title: string
  description?: string
  duration?: number
  isClosable?: boolean
}

/**
 * Toast context interface
 */
interface ToastContextType {
  toasts: ToastConfig[]
  addToast: (toast: Omit<ToastConfig, 'id'>) => string
  removeToast: (id: string) => void
  success: (title: string, description?: string) => string
  error: (title: string, description?: string) => string
  warning: (title: string, description?: string) => string
  info: (title: string, description?: string) => string
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

/**
 * Generate unique toast ID
 */
let toastCount = 0
function generateToastId(): string {
  return `toast-${++toastCount}-${Date.now()}`
}

/**
 * Icon components for toast types
 */
const ToastIcons: Record<ToastType, ReactNode> = {
  success: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  ),
  error: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="15" y1="9" x2="9" y2="15" />
      <line x1="9" y1="9" x2="15" y2="15" />
    </svg>
  ),
  warning: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
  info: (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  ),
}

/**
 * Color schemes for toast types
 */
const toastColors: Record<ToastType, { bg: string; border: string; icon: string }> = {
  success: {
    bg: 'green.900/90',
    border: 'green.600',
    icon: 'green.400',
  },
  error: {
    bg: 'red.900/90',
    border: 'red.600',
    icon: 'red.400',
  },
  warning: {
    bg: 'yellow.900/90',
    border: 'yellow.600',
    icon: 'yellow.400',
  },
  info: {
    bg: 'blue.900/90',
    border: 'blue.600',
    icon: 'blue.400',
  },
}

/**
 * Default toast duration in milliseconds
 */
const DEFAULT_DURATION = 5000

/**
 * Single toast component
 */
function Toast({
  toast,
  onRemove,
}: {
  toast: ToastConfig
  onRemove: (id: string) => void
}) {
  const colors = toastColors[toast.type]
  const isClosable = toast.isClosable !== false

  return (
    <Box
      bg={colors.bg}
      borderWidth={1}
      borderColor={colors.border}
      borderRadius="lg"
      backdropFilter="blur(12px)"
      shadow="lg"
      p={4}
      minW="320px"
      maxW="420px"
      animation="slideIn 0.3s ease-out"
    >
      <Flex align="start" gap={3}>
        {/* Icon */}
        <Box color={colors.icon} flexShrink={0} mt={0.5}>
          {ToastIcons[toast.type]}
        </Box>

        {/* Content */}
        <Box flex={1}>
          <Text fontWeight="600" color="white" fontSize="sm">
            {toast.title}
          </Text>
          {toast.description && (
            <Text color="gray.300" fontSize="sm" mt={1}>
              {toast.description}
            </Text>
          )}
        </Box>

        {/* Close Button */}
        {isClosable && (
          <IconButton
            aria-label="Close notification"
            variant="ghost"
            size="xs"
            color="gray.400"
            _hover={{ color: 'white', bg: 'whiteAlpha.200' }}
            onClick={() => onRemove(toast.id)}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </IconButton>
        )}
      </Flex>
    </Box>
  )
}

/**
 * ToastProvider component
 * Manages toast state and provides context for toast operations
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastConfig[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const addToast = useCallback(
    (toast: Omit<ToastConfig, 'id'>): string => {
      const id = generateToastId()
      const newToast: ToastConfig = {
        ...toast,
        id,
        duration: toast.duration ?? DEFAULT_DURATION,
        isClosable: toast.isClosable ?? true,
      }

      setToasts((prev) => [...prev, newToast])

      // Auto-remove after duration
      if (newToast.duration && newToast.duration > 0) {
        setTimeout(() => {
          removeToast(id)
        }, newToast.duration)
      }

      return id
    },
    [removeToast]
  )

  // Convenience methods
  const success = useCallback(
    (title: string, description?: string) =>
      addToast({ type: 'success', title, description }),
    [addToast]
  )

  const error = useCallback(
    (title: string, description?: string) =>
      addToast({ type: 'error', title, description, duration: 8000 }),
    [addToast]
  )

  const warning = useCallback(
    (title: string, description?: string) =>
      addToast({ type: 'warning', title, description }),
    [addToast]
  )

  const info = useCallback(
    (title: string, description?: string) =>
      addToast({ type: 'info', title, description }),
    [addToast]
  )

  const value: ToastContextType = {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
  }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Portal>
        <Box
          position="fixed"
          bottom={6}
          right={6}
          zIndex={9999}
          display="flex"
          flexDirection="column"
          gap={3}
          pointerEvents="none"
        >
          {toasts.map((toast) => (
            <Box key={toast.id} pointerEvents="auto">
              <Toast toast={toast} onRemove={removeToast} />
            </Box>
          ))}
        </Box>
      </Portal>
      <style jsx global>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </ToastContext.Provider>
  )
}

/**
 * Hook to access toast context
 */
export function useToast(): ToastContextType {
  const context = useContext(ToastContext)

  if (context === undefined) {
    throw new Error('useToast must be used within a ToastProvider')
  }

  return context
}
