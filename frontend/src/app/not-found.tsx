'use client'

import Link from 'next/link'
import { Box, Button, Container, Heading, Text, VStack } from '@chakra-ui/react'

export default function NotFound() {
  return (
    <Box minH="100vh" bg="gray.900" display="flex" alignItems="center" justifyContent="center">
      <Container maxW="md">
        <VStack gap={6} textAlign="center">
          <Heading size="2xl" color="purple.400">
            404
          </Heading>

          <Heading size="lg" color="white">
            Page Not Found
          </Heading>

          <Text color="gray.400">
            The page you're looking for doesn't exist or has been moved.
          </Text>

          <Link href="/">
            <Button colorPalette="purple" size="lg">
              Go Home
            </Button>
          </Link>
        </VStack>
      </Container>
    </Box>
  )
}
