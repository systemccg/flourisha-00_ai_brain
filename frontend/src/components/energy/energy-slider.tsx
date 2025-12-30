'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { getEnergyColor, getEnergyLabel } from '@/lib/types/energy'

interface EnergySliderProps {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
  showLabels?: boolean
  size?: 'sm' | 'md' | 'lg'
}

/**
 * Energy level slider (1-10 scale)
 * Features color gradient and value display
 */
export function EnergySlider({
  value,
  onChange,
  disabled = false,
  showLabels = true,
  size = 'md',
}: EnergySliderProps) {
  const color = getEnergyColor(value)
  const label = getEnergyLabel(value)

  const sizes = {
    sm: {
      trackHeight: '8px',
      thumbSize: '20px',
      fontSize: 'sm',
      padding: 2,
    },
    md: {
      trackHeight: '12px',
      thumbSize: '28px',
      fontSize: 'md',
      padding: 3,
    },
    lg: {
      trackHeight: '16px',
      thumbSize: '36px',
      fontSize: 'lg',
      padding: 4,
    },
  }

  const sizeProps = sizes[size]

  // Calculate position percentage (1-10 mapped to 0-100%)
  const positionPercent = ((value - 1) / 9) * 100

  return (
    <Box>
      {/* Value Display */}
      <Flex justify="space-between" align="baseline" mb={2}>
        <Flex align="center" gap={2}>
          <Text
            fontSize="3xl"
            fontWeight="bold"
            color={`${color}.400`}
            lineHeight="1"
          >
            {value}
          </Text>
          <Text fontSize={sizeProps.fontSize} color="gray.400">
            / 10
          </Text>
        </Flex>
        <Text fontSize={sizeProps.fontSize} color={`${color}.400`} fontWeight="500">
          {label}
        </Text>
      </Flex>

      {/* Slider Track */}
      <Box position="relative" py={sizeProps.padding}>
        {/* Background Track with Gradient */}
        <Box
          h={sizeProps.trackHeight}
          borderRadius="full"
          bg="linear-gradient(to right, var(--chakra-colors-red-500), var(--chakra-colors-orange-500), var(--chakra-colors-yellow-500), var(--chakra-colors-green-500))"
          opacity={0.3}
        />

        {/* Filled Track */}
        <Box
          position="absolute"
          top="50%"
          left={0}
          transform="translateY(-50%)"
          h={sizeProps.trackHeight}
          w={`${positionPercent}%`}
          borderRadius="full"
          bg={`${color}.500`}
          transition="width 0.15s ease-out, background 0.15s ease-out"
        />

        {/* Invisible Range Input */}
        <input
          type="range"
          min={1}
          max={10}
          value={value}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange(parseInt(e.target.value, 10))
          }
          disabled={disabled}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: disabled ? 'not-allowed' : 'pointer',
            zIndex: 2,
          }}
        />

        {/* Custom Thumb */}
        <Box
          position="absolute"
          top="50%"
          left={`${positionPercent}%`}
          transform="translate(-50%, -50%)"
          w={sizeProps.thumbSize}
          h={sizeProps.thumbSize}
          borderRadius="full"
          bg={`${color}.500`}
          boxShadow="0 2px 8px rgba(0,0,0,0.3)"
          border="3px solid white"
          transition="left 0.15s ease-out, background 0.15s ease-out, transform 0.1s"
          _hover={{
            transform: 'translate(-50%, -50%) scale(1.1)',
          }}
          pointerEvents="none"
        />
      </Box>

      {/* Scale Labels */}
      {showLabels && (
        <Flex justify="space-between" mt={2}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
            <Text
              key={n}
              fontSize="xs"
              color={n === value ? `${color}.400` : 'gray.600'}
              fontWeight={n === value ? '600' : '400'}
              w="20px"
              textAlign="center"
              transition="color 0.15s"
            >
              {n}
            </Text>
          ))}
        </Flex>
      )}
    </Box>
  )
}

/**
 * Compact energy display (read-only)
 */
export function EnergyDisplay({ value }: { value: number }) {
  const color = getEnergyColor(value)

  return (
    <Flex align="center" gap={2}>
      <Box
        w="32px"
        h="32px"
        borderRadius="lg"
        bg={`${color}.500/20`}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text fontSize="sm" fontWeight="bold" color={`${color}.400`}>
          {value}
        </Text>
      </Box>
      <Box flex={1} h="6px" bg="gray.700" borderRadius="full" overflow="hidden">
        <Box
          h="full"
          w={`${(value / 10) * 100}%`}
          bg={`${color}.500`}
          borderRadius="full"
          transition="width 0.3s ease-out"
        />
      </Box>
    </Flex>
  )
}

/**
 * Mini energy badge
 */
export function EnergyBadge({ value, showLabel = false }: { value: number; showLabel?: boolean }) {
  const color = getEnergyColor(value)
  const label = getEnergyLabel(value)

  return (
    <Flex
      align="center"
      gap={1.5}
      px={2}
      py={1}
      bg={`${color}.500/20`}
      borderRadius="full"
    >
      <Text fontSize="sm" fontWeight="bold" color={`${color}.400`}>
        {value}
      </Text>
      {showLabel && (
        <Text fontSize="xs" color={`${color}.400`}>
          {label}
        </Text>
      )}
    </Flex>
  )
}
