'use client'

import type { ReactNode } from 'react'
import { ProtectedRoute } from '@/components/auth'
import { DashboardLayout as DashboardLayoutComponent } from '@/components/layout'

/**
 * Dashboard layout with protected route wrapper and sidebar
 * All pages under /dashboard require authentication
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <ProtectedRoute>
      <DashboardLayoutComponent>
        {children}
      </DashboardLayoutComponent>
    </ProtectedRoute>
  )
}
