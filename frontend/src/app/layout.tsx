'use client'

import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { AuthProvider } from '@/contexts/auth-context'

export default function RootLayout({
  children,
}: {
  children: ReactNode
}) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  )

  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <QueryClientProvider client={queryClient}>
          <ChakraProvider value={defaultSystem}>
            <AuthProvider>
              {children}
            </AuthProvider>
          </ChakraProvider>
        </QueryClientProvider>
      </body>
    </html>
  )
}
