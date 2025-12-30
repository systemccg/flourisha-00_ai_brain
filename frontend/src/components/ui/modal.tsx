'use client'

import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react'
import {
  Box,
  Flex,
  Text,
  Button,
  IconButton,
  Portal,
} from '@chakra-ui/react'

/**
 * Modal sizes
 */
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full'

/**
 * Modal configuration for programmatic modals
 */
export interface ModalConfig {
  id: string
  title: string
  content: ReactNode
  size?: ModalSize
  showClose?: boolean
  closeOnOverlay?: boolean
  footer?: ReactNode
  onClose?: () => void
}

/**
 * Confirm modal options
 */
export interface ConfirmOptions {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmColorScheme?: string
  isDangerous?: boolean
}

/**
 * Modal context interface
 */
interface ModalContextType {
  modals: ModalConfig[]
  openModal: (config: Omit<ModalConfig, 'id'>) => string
  closeModal: (id: string) => void
  closeAll: () => void
  confirm: (options: ConfirmOptions) => Promise<boolean>
}

const ModalContext = createContext<ModalContextType | undefined>(undefined)

/**
 * Generate unique modal ID
 */
let modalCount = 0
function generateModalId(): string {
  return `modal-${++modalCount}-${Date.now()}`
}

/**
 * Size mappings for modal widths
 */
const sizeMap: Record<ModalSize, string> = {
  sm: '400px',
  md: '500px',
  lg: '700px',
  xl: '900px',
  full: '100vw',
}

/**
 * Single modal component
 */
function Modal({
  config,
  onClose,
}: {
  config: ModalConfig
  onClose: () => void
}) {
  const handleOverlayClick = () => {
    if (config.closeOnOverlay !== false) {
      onClose()
    }
  }

  const handleContentClick = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  const handleClose = () => {
    config.onClose?.()
    onClose()
  }

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="blackAlpha.700"
      backdropFilter="blur(4px)"
      display="flex"
      alignItems="center"
      justifyContent="center"
      zIndex={1000}
      onClick={handleOverlayClick}
      animation="fadeIn 0.2s ease-out"
    >
      <Box
        bg="gray.900"
        borderWidth={1}
        borderColor="gray.700"
        borderRadius={config.size === 'full' ? 0 : 'xl'}
        shadow="2xl"
        w={sizeMap[config.size || 'md']}
        maxW={config.size === 'full' ? '100vw' : 'calc(100vw - 32px)'}
        maxH={config.size === 'full' ? '100vh' : 'calc(100vh - 64px)'}
        overflow="hidden"
        display="flex"
        flexDirection="column"
        onClick={handleContentClick}
        animation="slideUp 0.2s ease-out"
      >
        {/* Header */}
        <Flex
          align="center"
          justify="space-between"
          px={6}
          py={4}
          borderBottomWidth={1}
          borderColor="gray.800"
          flexShrink={0}
        >
          <Text fontSize="lg" fontWeight="600" color="white">
            {config.title}
          </Text>
          {config.showClose !== false && (
            <IconButton
              aria-label="Close modal"
              variant="ghost"
              size="sm"
              color="gray.400"
              _hover={{ color: 'white', bg: 'gray.800' }}
              onClick={handleClose}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </IconButton>
          )}
        </Flex>

        {/* Content */}
        <Box
          flex={1}
          overflowY="auto"
          px={6}
          py={4}
        >
          {config.content}
        </Box>

        {/* Footer */}
        {config.footer && (
          <Flex
            px={6}
            py={4}
            borderTopWidth={1}
            borderColor="gray.800"
            justify="flex-end"
            gap={3}
            flexShrink={0}
          >
            {config.footer}
          </Flex>
        )}
      </Box>
      <style jsx global>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </Box>
  )
}

/**
 * ModalProvider component
 * Manages modal state and provides context for modal operations
 */
export function ModalProvider({ children }: { children: ReactNode }) {
  const [modals, setModals] = useState<ModalConfig[]>([])

  const closeModal = useCallback((id: string) => {
    setModals((prev) => prev.filter((m) => m.id !== id))
  }, [])

  const openModal = useCallback(
    (config: Omit<ModalConfig, 'id'>): string => {
      const id = generateModalId()
      const newModal: ModalConfig = {
        ...config,
        id,
      }

      setModals((prev) => [...prev, newModal])
      return id
    },
    []
  )

  const closeAll = useCallback(() => {
    setModals([])
  }, [])

  const confirm = useCallback(
    (options: ConfirmOptions): Promise<boolean> => {
      return new Promise((resolve) => {
        const handleConfirm = () => {
          resolve(true)
        }

        const handleCancel = () => {
          resolve(false)
        }

        openModal({
          title: options.title,
          size: 'sm',
          closeOnOverlay: false,
          showClose: false,
          content: (
            <Text color="gray.300">{options.message}</Text>
          ),
          footer: (
            <>
              <Button
                variant="ghost"
                colorPalette="gray"
                onClick={() => {
                  handleCancel()
                }}
              >
                {options.cancelText || 'Cancel'}
              </Button>
              <Button
                colorPalette={options.isDangerous ? 'red' : options.confirmColorScheme || 'purple'}
                onClick={() => {
                  handleConfirm()
                }}
              >
                {options.confirmText || 'Confirm'}
              </Button>
            </>
          ),
          onClose: handleCancel,
        })
      })
    },
    [openModal]
  )

  const value: ModalContextType = {
    modals,
    openModal,
    closeModal,
    closeAll,
    confirm,
  }

  return (
    <ModalContext.Provider value={value}>
      {children}
      <Portal>
        {modals.map((modal) => (
          <Modal
            key={modal.id}
            config={modal}
            onClose={() => closeModal(modal.id)}
          />
        ))}
      </Portal>
    </ModalContext.Provider>
  )
}

/**
 * Hook to access modal context
 */
export function useModal(): ModalContextType {
  const context = useContext(ModalContext)

  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider')
  }

  return context
}

/**
 * Standalone Modal component for declarative usage
 */
export interface StandaloneModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: ReactNode
  size?: ModalSize
  showClose?: boolean
  closeOnOverlay?: boolean
  footer?: ReactNode
}

export function StandaloneModal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showClose = true,
  closeOnOverlay = true,
  footer,
}: StandaloneModalProps) {
  if (!isOpen) return null

  return (
    <Portal>
      <Modal
        config={{
          id: 'standalone',
          title,
          content: children,
          size,
          showClose,
          closeOnOverlay,
          footer,
        }}
        onClose={onClose}
      />
    </Portal>
  )
}
