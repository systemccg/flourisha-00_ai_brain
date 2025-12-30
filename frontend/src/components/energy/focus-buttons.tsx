'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { type FocusQuality, FOCUS_OPTIONS, getFocusOption } from '@/lib/types/energy'

interface FocusButtonsProps {
  value: FocusQuality | null
  onChange: (value: FocusQuality) => void
  disabled?: boolean
  size?: 'sm' | 'md' | 'lg'
  showDescriptions?: boolean
}

/**
 * Focus quality selector buttons
 * Deep / Shallow / Distracted
 */
export function FocusButtons({
  value,
  onChange,
  disabled = false,
  size = 'md',
  showDescriptions = false,
}: FocusButtonsProps) {
  const sizes = {
    sm: {
      px: 3,
      py: 2,
      fontSize: 'sm',
      emojiSize: 'md',
      gap: 2,
    },
    md: {
      px: 4,
      py: 3,
      fontSize: 'md',
      emojiSize: 'xl',
      gap: 3,
    },
    lg: {
      px: 5,
      py: 4,
      fontSize: 'lg',
      emojiSize: '2xl',
      gap: 4,
    },
  }

  const sizeProps = sizes[size]

  return (
    <Flex gap={sizeProps.gap} direction={{ base: 'column', sm: 'row' }}>
      {FOCUS_OPTIONS.map((option) => {
        const isSelected = value === option.value

        return (
          <Box
            key={option.value}
            flex={1}
            px={sizeProps.px}
            py={sizeProps.py}
            borderRadius="xl"
            borderWidth={2}
            borderColor={isSelected ? `${option.color}.500` : 'gray.700'}
            bg={isSelected ? `${option.color}.500/15` : 'gray.800/50'}
            cursor={disabled ? 'not-allowed' : 'pointer'}
            opacity={disabled ? 0.5 : 1}
            transition="all 0.15s ease-out"
            _hover={
              disabled
                ? undefined
                : {
                    borderColor: `${option.color}.400`,
                    bg: `${option.color}.500/10`,
                    transform: 'translateY(-2px)',
                  }
            }
            _active={
              disabled
                ? undefined
                : {
                    transform: 'translateY(0)',
                  }
            }
            onClick={() => !disabled && onChange(option.value)}
            role="button"
            tabIndex={0}
            onKeyDown={(e: React.KeyboardEvent) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                !disabled && onChange(option.value)
              }
            }}
          >
            <Flex direction="column" align="center" gap={1}>
              <Text fontSize={sizeProps.emojiSize} lineHeight="1">
                {option.emoji}
              </Text>
              <Text
                fontSize={sizeProps.fontSize}
                fontWeight={isSelected ? '600' : '500'}
                color={isSelected ? `${option.color}.400` : 'gray.300'}
              >
                {option.label}
              </Text>
              {showDescriptions && (
                <Text
                  fontSize="xs"
                  color={isSelected ? `${option.color}.400` : 'gray.500'}
                  textAlign="center"
                >
                  {option.description}
                </Text>
              )}
            </Flex>
          </Box>
        )
      })}
    </Flex>
  )
}

/**
 * Focus quality badge (read-only display)
 */
export function FocusBadge({
  value,
  size = 'md',
  showEmoji = true,
}: {
  value: FocusQuality
  size?: 'sm' | 'md'
  showEmoji?: boolean
}) {
  const option = getFocusOption(value)

  const sizes = {
    sm: {
      px: 2,
      py: 0.5,
      fontSize: 'xs',
      emojiSize: 'xs',
    },
    md: {
      px: 3,
      py: 1,
      fontSize: 'sm',
      emojiSize: 'sm',
    },
  }

  const sizeProps = sizes[size]

  return (
    <Flex
      align="center"
      gap={1.5}
      px={sizeProps.px}
      py={sizeProps.py}
      bg={`${option.color}.500/20`}
      borderRadius="full"
    >
      {showEmoji && (
        <Text fontSize={sizeProps.emojiSize} lineHeight="1">
          {option.emoji}
        </Text>
      )}
      <Text fontSize={sizeProps.fontSize} color={`${option.color}.400`} fontWeight="500">
        {option.label}
      </Text>
    </Flex>
  )
}

/**
 * Focus quality dot (minimal indicator)
 */
export function FocusDot({
  value,
  size = 8,
}: {
  value: FocusQuality
  size?: number
}) {
  const option = getFocusOption(value)

  return (
    <Box
      w={`${size}px`}
      h={`${size}px`}
      borderRadius="full"
      bg={`${option.color}.400`}
      title={option.label}
    />
  )
}

/**
 * Focus quality compact display with label
 */
export function FocusDisplay({ value }: { value: FocusQuality }) {
  const option = getFocusOption(value)

  return (
    <Flex align="center" gap={2}>
      <Text fontSize="lg">{option.emoji}</Text>
      <Box>
        <Text fontSize="sm" color={`${option.color}.400`} fontWeight="500">
          {option.label} Focus
        </Text>
        <Text fontSize="xs" color="gray.500">
          {option.description}
        </Text>
      </Box>
    </Flex>
  )
}
