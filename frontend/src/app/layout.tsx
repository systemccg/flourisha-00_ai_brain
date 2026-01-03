'use client'

import './globals.css'
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'
import { AuthProvider } from '@/contexts/auth-context'
import { ThemeProvider } from '@/contexts/theme-context'
import { ToastProvider, ModalProvider } from '@/components/ui'

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
      <head>
        <title>Flourisha - Personal AI Infrastructure</title>
        <meta name="description" content="AI that recognizes, amplifies, and grows with you" />
        <meta name="theme-color" content="#111827" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <ChakraProvider value={defaultSystem}>
            <ThemeProvider>
              <AuthProvider>
                <ToastProvider>
                  <ModalProvider>
                    {children}
                  </ModalProvider>
                </ToastProvider>
              </AuthProvider>
            </ThemeProvider>
          </ChakraProvider>
        </QueryClientProvider>
      </body>
    </html>
  )
}
