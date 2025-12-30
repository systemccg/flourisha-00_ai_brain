'use client'

import { Box, Flex, Text } from '@chakra-ui/react'
import { type Quarter, getAvailableQuarters, getCurrentQuarter } from '@/lib/types/okr'

interface QuarterSelectorProps {
  selected: Quarter
  onChange: (quarter: Quarter) => void
}

/**
 * Quarter selector component for OKR filtering
 * Shows current quarter + 2 quarters ahead and 1 behind
 */
export function QuarterSelector({ selected, onChange }: QuarterSelectorProps) {
  const quarters = getAvailableQuarters()
  const currentQuarter = getCurrentQuarter()

  return (
    <Flex gap={2} align="center" flexWrap="wrap">
      {quarters.map((quarter) => {
        const isSelected = quarter === selected
        const isCurrent = quarter === currentQuarter

        return (
          <Box
            key={quarter}
            as="button"
            px={4}
            py={2}
            borderRadius="lg"
            bg={isSelected ? 'purple.500' : 'gray.800'}
            color={isSelected ? 'white' : 'gray.300'}
            fontWeight={isSelected ? '600' : '400'}
            fontSize="sm"
            cursor="pointer"
            position="relative"
            transition="all 0.15s"
            _hover={{
              bg: isSelected ? 'purple.400' : 'gray.700',
            }}
            onClick={() => onChange(quarter)}
          >
            {quarter}
            {isCurrent && (
              <Box
                position="absolute"
                top="-1"
                right="-1"
                w="2"
                h="2"
                bg={isSelected ? 'white' : 'purple.400'}
                borderRadius="full"
              />
            )}
          </Box>
        )
      })}
    </Flex>
  )
}

/**
 * Quarter badge component for display purposes
 */
export function QuarterBadge({ quarter }: { quarter: Quarter }) {
  const isCurrent = quarter === getCurrentQuarter()

  return (
    <Flex
      display="inline-flex"
      align="center"
      gap={2}
      px={3}
      py={1}
      bg="gray.800"
      borderRadius="full"
      fontSize="sm"
      color="gray.300"
    >
      <Text>{quarter}</Text>
      {isCurrent && (
        <Text fontSize="xs" color="purple.400" fontWeight="500">
          Current
        </Text>
      )}
    </Flex>
  )
}
