'use client'

import { Box, Flex, Grid, GridItem, Text, VStack, Badge, Button } from '@chakra-ui/react'
import { useState, useCallback, useEffect } from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { GraphVisualization, NodeDetailSidebar, GraphSearch } from '@/components/knowledge'
import { useKnowledgeGraph } from '@/hooks/use-graph'
import type { GraphEntity, ForceGraphNode } from '@/lib/types'

/**
 * Stats card component
 */
interface StatsCardProps {
  label: string
  value: number | string
  color?: string
}

function StatsCard({ label, value, color = 'gray' }: StatsCardProps) {
  return (
    <Box bg="gray.850" borderRadius="lg" p={3} textAlign="center">
      <Text fontSize="2xl" fontWeight="700" color={`${color}.400`}>
        {typeof value === 'number' ? value.toLocaleString() : value}
      </Text>
      <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="600">
        {label}
      </Text>
    </Box>
  )
}

/**
 * Sidebar toggle icon
 */
const SidebarIcon = () => (
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
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <line x1="15" y1="3" x2="15" y2="21" />
  </svg>
)

/**
 * Knowledge Graph Page - Visualize entity relationships
 */
export default function KnowledgeGraphPage() {
  const [sidebarVisible, setSidebarVisible] = useState(true)

  const {
    search,
    stats,
    statsLoading,
    visualization,
    focusedEntity,
    expandEntity,
    relatedData,
    relatedLoading,
    relatedError,
    loadRelated,
  } = useKnowledgeGraph()

  // Load related entities into visualization when data arrives
  useEffect(() => {
    if (relatedData) {
      loadRelated()
    }
  }, [relatedData, loadRelated])

  // Handle entity selection from search
  const handleSearchSelect = useCallback(
    (entity: GraphEntity) => {
      // Add to visualization
      visualization.loadFromSearch([entity])
      // Expand to show connections
      expandEntity(entity.name)
    },
    [visualization, expandEntity]
  )

  // Handle node click in graph
  const handleNodeClick = useCallback(
    (node: ForceGraphNode) => {
      visualization.handleNodeClick(node)
      // Load related entities for selected node
      expandEntity(node.name)
    },
    [visualization, expandEntity]
  )

  // Handle clicking a related entity in sidebar
  const handleRelatedClick = useCallback(
    (entity: GraphEntity) => {
      // Focus on the related entity
      expandEntity(entity.name)
    },
    [expandEntity]
  )

  return (
    <PageContainer maxW="full">
      <PageHeader
        title="Knowledge Graph"
        description="Visualize connections between entities in your knowledge base."
        actions={
          <Flex gap={2}>
            <Button
              size="sm"
              variant={sidebarVisible ? 'solid' : 'outline'}
              colorPalette="gray"
              onClick={() => setSidebarVisible(!sidebarVisible)}
            >
              <SidebarIcon />
              <Text ml={2} display={{ base: 'none', md: 'block' }}>
                {sidebarVisible ? 'Hide Panel' : 'Show Panel'}
              </Text>
            </Button>
          </Flex>
        }
      />

      {/* Stats Bar */}
      {stats && (
        <Grid
          templateColumns={{ base: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' }}
          gap={4}
          mb={6}
        >
          <GridItem>
            <StatsCard label="Total Entities" value={stats.total_entities} color="blue" />
          </GridItem>
          <GridItem>
            <StatsCard label="Total Relationships" value={stats.total_relationships} color="purple" />
          </GridItem>
          <GridItem>
            <StatsCard
              label="Most Common Type"
              value={
                stats.entities_by_type
                  ? Object.entries(stats.entities_by_type).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
                  : 'N/A'
              }
              color="green"
            />
          </GridItem>
          <GridItem>
            <StatsCard
              label="Last Updated"
              value={
                stats.last_updated
                  ? new Date(stats.last_updated).toLocaleDateString()
                  : 'N/A'
              }
              color="gray"
            />
          </GridItem>
        </Grid>
      )}

      <Grid
        templateColumns={sidebarVisible ? { base: '1fr', lg: '1fr 320px' } : '1fr'}
        gap={6}
      >
        {/* Main Content */}
        <GridItem>
          <VStack gap={6} align="stretch">
            {/* Search */}
            <GraphSearch
              query={search.query}
              selectedTypes={search.selectedTypes}
              results={search.results}
              total={search.total}
              isLoading={search.isLoading}
              selectedId={visualization.selectedNode?.id}
              onQueryChange={(q) => search.search(q)}
              onSearch={(q, types) => search.search(q, types)}
              onToggleType={search.toggleType}
              onClearFilters={search.clearFilters}
              onSelect={handleSearchSelect}
            />

            {/* Graph Visualization */}
            <GraphVisualization
              data={visualization.graphData}
              selectedNode={visualization.selectedNode}
              hoveredNode={visualization.hoveredNode}
              highlightedNodes={visualization.highlightedNodes}
              highlightedLinks={visualization.highlightedLinks}
              height={500}
              onNodeClick={handleNodeClick}
              onNodeHover={visualization.handleNodeHover}
              onBackgroundClick={visualization.clearSelection}
              isLoading={relatedLoading && visualization.graphData.nodes.length === 0}
            />

            {/* Graph Controls */}
            <Flex justify="space-between" align="center">
              <Flex gap={2}>
                <Button
                  size="sm"
                  variant="outline"
                  colorPalette="gray"
                  onClick={visualization.clearGraph}
                  disabled={visualization.graphData.nodes.length === 0}
                >
                  Clear Graph
                </Button>
              </Flex>

              <Text color="gray.600" fontSize="xs">
                Click a node to see connections. Double-click to expand.
              </Text>
            </Flex>
          </VStack>
        </GridItem>

        {/* Sidebar - Node Details */}
        {sidebarVisible && (
          <GridItem>
            <Box position="sticky" top={4}>
              <NodeDetailSidebar
                node={visualization.selectedNode}
                relatedData={relatedData}
                isLoading={relatedLoading}
                error={relatedError}
                onClose={visualization.clearSelection}
                onExpand={expandEntity}
                onRelatedClick={handleRelatedClick}
              />
            </Box>
          </GridItem>
        )}
      </Grid>
    </PageContainer>
  )
}
