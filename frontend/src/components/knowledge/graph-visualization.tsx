'use client'

import { Box, Flex, Text, Spinner } from '@chakra-ui/react'
import { useRef, useCallback, useEffect, useState } from 'react'
import dynamic from 'next/dynamic'
import type { ForceGraphData, ForceGraphNode, ForceGraphLink, EntityType } from '@/lib/types'

// Dynamically import ForceGraph2D to avoid SSR issues
// Using any type for the component since react-force-graph has complex generics
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => (
    <Flex align="center" justify="center" h="100%">
      <Spinner size="lg" color="purple.400" />
    </Flex>
  ),
}) as any

/**
 * Entity type colors for the graph
 */
const ENTITY_COLORS: Record<EntityType, string> = {
  person: '#3b82f6',
  organization: '#8b5cf6',
  medication: '#22c55e',
  condition: '#ef4444',
  document: '#eab308',
  project: '#f97316',
  topic: '#06b6d4',
  date: '#6b7280',
  location: '#10b981',
  unknown: '#9ca3af',
}

/**
 * Get node color based on entity type
 */
function getNodeColor(node: ForceGraphNode, highlightedNodes: Set<string>, hoveredNode: ForceGraphNode | null): string {
  const baseColor = ENTITY_COLORS[node.type] || ENTITY_COLORS.unknown

  // Dim non-highlighted nodes when hovering
  if (hoveredNode && !highlightedNodes.has(node.id)) {
    return '#374151' // gray-700
  }

  return baseColor
}

/**
 * Props for GraphVisualization component
 */
interface GraphVisualizationProps {
  /** Graph data with nodes and links */
  data: ForceGraphData
  /** Currently selected node */
  selectedNode?: ForceGraphNode | null
  /** Currently hovered node */
  hoveredNode?: ForceGraphNode | null
  /** Set of highlighted node IDs */
  highlightedNodes?: Set<string>
  /** Set of highlighted link IDs (source-target) */
  highlightedLinks?: Set<string>
  /** Width of the container */
  width?: number
  /** Height of the container */
  height?: number
  /** Called when a node is clicked */
  onNodeClick?: (node: ForceGraphNode) => void
  /** Called when a node is hovered */
  onNodeHover?: (node: ForceGraphNode | null) => void
  /** Called when the background is clicked */
  onBackgroundClick?: () => void
  /** Whether the graph is loading */
  isLoading?: boolean
}

export function GraphVisualization({
  data,
  selectedNode,
  hoveredNode,
  highlightedNodes = new Set(),
  highlightedLinks = new Set(),
  width,
  height = 500,
  onNodeClick,
  onNodeHover,
  onBackgroundClick,
  isLoading,
}: GraphVisualizationProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const fgRef = useRef<any>(null)
  const [containerWidth, setContainerWidth] = useState(width || 800)

  // Update container width on resize
  useEffect(() => {
    if (!containerRef.current || width) return

    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth)
      }
    }

    updateWidth()
    const resizeObserver = new ResizeObserver(updateWidth)
    resizeObserver.observe(containerRef.current)

    return () => resizeObserver.disconnect()
  }, [width])

  // Zoom to fit when data changes
  useEffect(() => {
    if (fgRef.current && data.nodes.length > 0) {
      setTimeout(() => {
        fgRef.current?.zoomToFit(400, 50)
      }, 500)
    }
  }, [data.nodes.length])

  // Custom node paint function
  const nodeCanvasObject = useCallback(
    (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const typedNode = node as ForceGraphNode
      const label = typedNode.name
      const fontSize = 12 / globalScale
      const nodeSize = Math.sqrt(typedNode.val || 1) * 5

      // Determine colors
      const isSelected = selectedNode?.id === typedNode.id
      const isHighlighted = highlightedNodes.has(typedNode.id)
      const isDimmed = hoveredNode && !highlightedNodes.has(typedNode.id)

      // Node circle
      ctx.beginPath()
      ctx.arc(typedNode.x!, typedNode.y!, nodeSize, 0, 2 * Math.PI)
      ctx.fillStyle = isDimmed ? '#374151' : (ENTITY_COLORS[typedNode.type] || ENTITY_COLORS.unknown)
      ctx.fill()

      // Selection ring
      if (isSelected) {
        ctx.strokeStyle = '#a855f7' // purple-500
        ctx.lineWidth = 2 / globalScale
        ctx.stroke()
      } else if (isHighlighted && !isDimmed) {
        ctx.strokeStyle = 'rgba(168, 85, 247, 0.5)' // purple-500 with opacity
        ctx.lineWidth = 1.5 / globalScale
        ctx.stroke()
      }

      // Label
      if (!isDimmed || isSelected || isHighlighted) {
        ctx.font = `${isSelected ? 'bold ' : ''}${fontSize}px Inter, sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        ctx.fillStyle = isDimmed ? '#6b7280' : '#f3f4f6'
        ctx.fillText(label, typedNode.x!, typedNode.y! + nodeSize + 2)
      }
    },
    [selectedNode, hoveredNode, highlightedNodes]
  )

  // Custom link paint function
  const linkCanvasObject = useCallback(
    (link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const typedLink = link as ForceGraphLink
      const sourceNode = typedLink.source as ForceGraphNode
      const targetNode = typedLink.target as ForceGraphNode

      if (!sourceNode.x || !sourceNode.y || !targetNode.x || !targetNode.y) return

      const linkId = `${sourceNode.id}-${targetNode.id}`
      const isHighlighted = highlightedLinks.has(linkId)
      const isDimmed = hoveredNode && !isHighlighted

      // Draw line
      ctx.beginPath()
      ctx.moveTo(sourceNode.x, sourceNode.y)
      ctx.lineTo(targetNode.x, targetNode.y)
      ctx.strokeStyle = isDimmed ? '#1f2937' : (isHighlighted ? '#a855f7' : '#4b5563')
      ctx.lineWidth = (isHighlighted ? 2 : 1) / globalScale
      ctx.stroke()

      // Draw arrow
      if (!isDimmed) {
        const angle = Math.atan2(targetNode.y - sourceNode.y, targetNode.x - sourceNode.x)
        const targetNodeSize = Math.sqrt(targetNode.val || 1) * 5
        const arrowX = targetNode.x - Math.cos(angle) * (targetNodeSize + 5)
        const arrowY = targetNode.y - Math.sin(angle) * (targetNodeSize + 5)
        const arrowSize = 4 / globalScale

        ctx.beginPath()
        ctx.moveTo(arrowX, arrowY)
        ctx.lineTo(
          arrowX - arrowSize * Math.cos(angle - Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle - Math.PI / 6)
        )
        ctx.lineTo(
          arrowX - arrowSize * Math.cos(angle + Math.PI / 6),
          arrowY - arrowSize * Math.sin(angle + Math.PI / 6)
        )
        ctx.closePath()
        ctx.fillStyle = isHighlighted ? '#a855f7' : '#4b5563'
        ctx.fill()
      }
    },
    [hoveredNode, highlightedLinks]
  )

  // Handle node click
  const handleNodeClick = useCallback(
    (node: any) => {
      onNodeClick?.(node as ForceGraphNode)
    },
    [onNodeClick]
  )

  // Handle node hover
  const handleNodeHover = useCallback(
    (node: any) => {
      onNodeHover?.(node ? (node as ForceGraphNode) : null)
    },
    [onNodeHover]
  )

  // Handle background click
  const handleBackgroundClick = useCallback(() => {
    onBackgroundClick?.()
  }, [onBackgroundClick])

  // Empty state
  if (data.nodes.length === 0 && !isLoading) {
    return (
      <Flex
        ref={containerRef}
        direction="column"
        align="center"
        justify="center"
        h={height}
        bg="gray.900"
        borderRadius="xl"
      >
        <Box color="gray.600" mb={4}>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="3" />
            <path d="M12 2v7M12 15v7M2 12h7M15 12h7" />
          </svg>
        </Box>
        <Text color="gray.500" fontSize="md" fontWeight="500">
          No graph data
        </Text>
        <Text color="gray.600" fontSize="sm" mt={1}>
          Search for entities or select a topic to visualize connections
        </Text>
      </Flex>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <Flex
        ref={containerRef}
        align="center"
        justify="center"
        h={height}
        bg="gray.900"
        borderRadius="xl"
      >
        <Spinner size="xl" color="purple.400" />
      </Flex>
    )
  }

  return (
    <Box
      ref={containerRef}
      h={height}
      bg="gray.900"
      borderRadius="xl"
      overflow="hidden"
      position="relative"
    >
      <ForceGraph2D
        ref={fgRef}
        graphData={data}
        width={containerWidth}
        height={height}
        backgroundColor="#111827"
        nodeCanvasObject={nodeCanvasObject}
        linkCanvasObject={linkCanvasObject}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        onBackgroundClick={handleBackgroundClick}
        nodePointerAreaPaint={(node: any, color: string, ctx: CanvasRenderingContext2D) => {
          const typedNode = node as ForceGraphNode
          const size = Math.sqrt(typedNode.val || 1) * 5 + 5
          ctx.fillStyle = color
          ctx.beginPath()
          ctx.arc(typedNode.x!, typedNode.y!, size, 0, 2 * Math.PI)
          ctx.fill()
        }}
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
      />

      {/* Legend */}
      <Box
        position="absolute"
        bottom={4}
        left={4}
        bg="gray.800"
        borderRadius="lg"
        p={3}
        opacity={0.9}
      >
        <Text fontSize="xs" color="gray.400" fontWeight="600" mb={2}>
          Entity Types
        </Text>
        <Flex gap={3} flexWrap="wrap" maxW="200px">
          {Object.entries(ENTITY_COLORS)
            .filter(([type]) => type !== 'unknown')
            .slice(0, 6)
            .map(([type, color]) => (
              <Flex key={type} align="center" gap={1}>
                <Box w={2} h={2} borderRadius="full" bg={color} />
                <Text fontSize="xs" color="gray.400" textTransform="capitalize">
                  {type}
                </Text>
              </Flex>
            ))}
        </Flex>
      </Box>

      {/* Stats overlay */}
      <Box
        position="absolute"
        top={4}
        right={4}
        bg="gray.800"
        borderRadius="lg"
        px={3}
        py={2}
        opacity={0.9}
      >
        <Flex gap={4}>
          <Flex align="center" gap={1}>
            <Text fontSize="sm" fontWeight="600" color="white">
              {data.nodes.length}
            </Text>
            <Text fontSize="xs" color="gray.500">
              nodes
            </Text>
          </Flex>
          <Flex align="center" gap={1}>
            <Text fontSize="sm" fontWeight="600" color="white">
              {data.links.length}
            </Text>
            <Text fontSize="xs" color="gray.500">
              links
            </Text>
          </Flex>
        </Flex>
      </Box>
    </Box>
  )
}
