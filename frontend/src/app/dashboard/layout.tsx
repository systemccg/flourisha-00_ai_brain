'use client'

import type { ReactNode } from 'react'
import { ProtectedRoute } from '@/components/auth'

/**
 * Dashboard layout with protected route wrapper
 * All pages under /dashboard require authentication
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return <ProtectedRoute>{children}</ProtectedRoute>
}
