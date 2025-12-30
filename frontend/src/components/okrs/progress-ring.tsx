'use client'

import { Box, Text } from '@chakra-ui/react'

interface ProgressRingProps {
  /**
   * Progress value (0-100)
   */
  progress: number
  /**
   * Size of the ring in pixels
   * @default 80
   */
  size?: number
  /**
   * Stroke width in pixels
   * @default 8
   */
  strokeWidth?: number
  /**
   * Color of the progress arc
   * @default "purple.500"
   */
  color?: string
  /**
   * Background color of the track
   * @default "gray.700"
   */
  trackColor?: string
  /**
   * Show percentage text in center
   * @default true
   */
  showLabel?: boolean
  /**
   * Font size for the label
   * @default "lg"
   */
  labelSize?: string
}

/**
 * Circular progress ring component
 * Used for displaying objective overall progress
 */
export function ProgressRing({
  progress,
  size = 80,
  strokeWidth = 8,
  color = 'purple.500',
  trackColor = 'gray.700',
  showLabel = true,
  labelSize = 'lg',
}: ProgressRingProps) {
  // Ensure progress is within bounds
  const normalizedProgress = Math.min(100, Math.max(0, progress))

  // Calculate SVG properties
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (normalizedProgress / 100) * circumference

  // Determine color based on progress if using default
  const getProgressColor = () => {
    if (color !== 'purple.500') return color
    if (normalizedProgress >= 70) return 'green.400'
    if (normalizedProgress >= 50) return 'yellow.400'
    if (normalizedProgress >= 25) return 'orange.400'
    return 'red.400'
  }

  const progressColor = getProgressColor()

  return (
    <Box position="relative" w={`${size}px`} h={`${size}px`}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--chakra-colors-gray-700)"
          strokeWidth={strokeWidth}
        />
        {/* Progress arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`var(--chakra-colors-${progressColor.replace('.', '-')})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{
            transition: 'stroke-dashoffset 0.5s ease-in-out',
          }}
        />
      </svg>
      {showLabel && (
        <Box
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          textAlign="center"
        >
          <Text
            fontSize={labelSize}
            fontWeight="bold"
            color="white"
            lineHeight="1"
          >
            {Math.round(normalizedProgress)}%
          </Text>
        </Box>
      )}
    </Box>
  )
}

/**
 * Mini progress ring for inline use
 */
export function MiniProgressRing({
  progress,
  color,
}: {
  progress: number
  color?: string
}) {
  return (
    <ProgressRing
      progress={progress}
      size={32}
      strokeWidth={4}
      color={color}
      showLabel={false}
    />
  )
}
