'use client'

import { Box, Container, Heading, Text, VStack, Button, HStack } from '@chakra-ui/react'

export default function Home() {
  return (
    <Box minH="100vh" bg="gray.50" _dark={{ bg: 'gray.900' }}>
      <Container maxW="container.xl" py={20}>
        <VStack gap={8} textAlign="center">
          <Heading
            as="h1"
            size="2xl"
            bgGradient="to-r"
            gradientFrom="blue.500"
            gradientTo="purple.500"
            bgClip="text"
          >
            Flourisha AI Dashboard
          </Heading>

          <Text fontSize="xl" color="gray.600" _dark={{ color: 'gray.400' }} maxW="2xl">
            Your Personal AI Infrastructure - Knowledge Management, Productivity,
            and AI-Assisted Workflows
          </Text>

          <HStack gap={4} pt={4}>
            <Button
              size="lg"
              colorPalette="blue"
            >
              Get Started
            </Button>
            <Button
              size="lg"
              variant="outline"
            >
              Learn More
            </Button>
          </HStack>

          <Box
            mt={12}
            p={8}
            bg="white"
            _dark={{ bg: 'gray.800' }}
            borderRadius="xl"
            shadow="lg"
            w="full"
            maxW="4xl"
          >
            <VStack gap={6}>
              <Heading as="h2" size="lg">The Five Pillars</Heading>
              <HStack gap={8} flexWrap="wrap" justify="center">
                {[
                  { name: 'Capture', icon: '📥', desc: 'Content Ingestion' },
                  { name: 'Store', icon: '🧠', desc: 'Knowledge Hub' },
                  { name: 'Think', icon: '💭', desc: 'Strategic Command' },
                  { name: 'Execute', icon: '⚡', desc: 'Agentic Operations' },
                  { name: 'Grow', icon: '🌱', desc: 'System Evolution' },
                ].map((pillar) => (
                  <VStack
                    key={pillar.name}
                    p={4}
                    borderRadius="lg"
                    bg="gray.50"
                    _dark={{ bg: 'gray.700' }}
                    minW="140px"
                  >
                    <Text fontSize="3xl">{pillar.icon}</Text>
                    <Text fontWeight="bold">{pillar.name}</Text>
                    <Text fontSize="sm" color="gray.500">{pillar.desc}</Text>
                  </VStack>
                ))}
              </HStack>
            </VStack>
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}
