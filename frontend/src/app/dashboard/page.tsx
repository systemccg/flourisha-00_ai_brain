'use client'

import {
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  Text,
  VStack,
} from '@chakra-ui/react'
import { useAuth } from '@/hooks/use-auth'
import { useRouter } from 'next/navigation'

/**
 * Dashboard page - main authenticated landing page
 * Shows user info and navigation to key features
 */
export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
    router.push('/login')
  }

  return (
    <Box minH="100vh" bg="gray.900">
      {/* Header */}
      <Box borderBottomWidth={1} borderColor="gray.800" bg="gray.900/80" backdropFilter="blur(8px)">
        <Container maxW="7xl" py={4}>
          <Flex justify="space-between" align="center">
            <Heading
              size="lg"
              bgGradient="to-r"
              gradientFrom="purple.400"
              gradientTo="cyan.400"
              bgClip="text"
            >
              Flourisha
            </Heading>
            <Flex align="center" gap={4}>
              <Text color="gray.400">{user?.email}</Text>
              <Button
                size="sm"
                variant="outline"
                colorPalette="gray"
                onClick={handleSignOut}
              >
                Sign Out
              </Button>
            </Flex>
          </Flex>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="7xl" py={8}>
        <VStack gap={8} align="stretch">
          {/* Welcome Section */}
          <Box>
            <Heading size="xl" color="white" mb={2}>
              Welcome back, {user?.name || 'User'}
            </Heading>
            <Text color="gray.400">
              Your Personal AI Infrastructure is ready.
            </Text>
          </Box>

          {/* Quick Actions Grid */}
          <Grid
            templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }}
            gap={6}
          >
            <QuickActionCard
              title="Search Knowledge"
              description="Query your AI Brain across all three stores"
              icon="search"
              href="/dashboard/search"
            />
            <QuickActionCard
              title="OKR Tracking"
              description="View and update your objectives and key results"
              icon="target"
              href="/dashboard/okrs"
            />
            <QuickActionCard
              title="Energy Log"
              description="Track your energy and focus throughout the day"
              icon="battery"
              href="/dashboard/energy"
            />
            <QuickActionCard
              title="Skills"
              description="Browse and execute PAI skills"
              icon="magic"
              href="/dashboard/skills"
            />
            <QuickActionCard
              title="Knowledge Graph"
              description="Explore entity relationships in Neo4j"
              icon="graph"
              href="/dashboard/graph"
            />
            <QuickActionCard
              title="System Health"
              description="Monitor infrastructure and service status"
              icon="health"
              href="/dashboard/health"
            />
          </Grid>
        </VStack>
      </Container>
    </Box>
  )
}

/**
 * Quick action card component
 */
function QuickActionCard({
  title,
  description,
  icon,
  href,
}: {
  title: string
  description: string
  icon: string
  href: string
}) {
  const router = useRouter()

  const iconMap: Record<string, string> = {
    search: 'M10 18a8 8 0 100-16 8 8 0 000 16zM21 21l-6-6',
    target: 'M12 2a10 10 0 110 20 10 10 0 010-20zm0 6a4 4 0 110 8 4 4 0 010-8zm0 2a2 2 0 100 4 2 2 0 000-4z',
    battery: 'M17 6H3a2 2 0 00-2 2v8a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2zm4 3v6',
    magic: 'M12 2l3 9h9l-7 5 3 9-8-6-8 6 3-9-7-5h9z',
    graph: 'M8 6a2 2 0 100-4 2 2 0 000 4zm8 6a2 2 0 100-4 2 2 0 000 4zm-8 8a2 2 0 100-4 2 2 0 000 4z',
    health: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  }

  return (
    <Box
      as="button"
      onClick={() => router.push(href)}
      textAlign="left"
      bg="gray.800"
      p={6}
      borderRadius="xl"
      borderWidth={1}
      borderColor="gray.700"
      _hover={{
        borderColor: 'purple.500',
        transform: 'translateY(-2px)',
        shadow: 'lg',
      }}
      transition="all 0.2s"
    >
      <VStack align="start" gap={3}>
        <Box
          p={3}
          bg="purple.500/20"
          borderRadius="lg"
          color="purple.400"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d={iconMap[icon]} />
          </svg>
        </Box>
        <Heading size="md" color="white">
          {title}
        </Heading>
        <Text color="gray.400" fontSize="sm">
          {description}
        </Text>
      </VStack>
    </Box>
  )
}
