/**
 * OKR System Type Definitions
 * Based on FRONTEND_FEATURE_REGISTRY.md Section 3.3
 */

/**
 * Status thresholds at week 8 of 12:
 * - >=70% = ON_TRACK (green)
 * - 50-69% = NEEDS_ATTENTION (yellow)
 * - <50% = AT_RISK (red)
 * - Blocked = BLOCKED (gray)
 */
export type OKRStatus = 'ON_TRACK' | 'NEEDS_ATTENTION' | 'AT_RISK' | 'BLOCKED' | 'COMPLETED'

/**
 * Quarter format: Q1-2026, Q2-2026, etc.
 */
export type Quarter = `Q${1 | 2 | 3 | 4}-${number}`

/**
 * Key Result definition
 */
export interface KeyResult {
  id: string
  objective_id: string
  title: string
  description?: string
  metric_type: 'percentage' | 'number' | 'boolean' | 'currency'
  target_value: number
  current_value: number
  start_value: number
  unit?: string
  progress: number // 0-100 calculated from current/target
  status: OKRStatus
  velocity?: number // weekly progress rate
  forecast_date?: string // predicted completion date
  created_at: string
  updated_at: string
}

/**
 * Objective definition
 */
export interface Objective {
  id: string
  quarter: Quarter
  title: string
  description?: string
  owner_id?: string
  owner_name?: string
  progress: number // 0-100 average of KR progress
  status: OKRStatus
  key_results: KeyResult[]
  created_at: string
  updated_at: string
}

/**
 * OKR measurement record
 */
export interface OKRMeasurement {
  id: string
  kr_id: string
  value: number
  notes?: string
  measured_at: string
  measured_by?: string
}

/**
 * Create OKR payload
 */
export interface CreateOKRPayload {
  quarter: Quarter
  objective: string
  description?: string
  key_results: {
    title: string
    description?: string
    metric_type: KeyResult['metric_type']
    target_value: number
    start_value?: number
    unit?: string
  }[]
}

/**
 * Record measurement payload
 */
export interface RecordMeasurementPayload {
  kr_id: string
  value: number
  notes?: string
}

/**
 * OKR quarterly summary
 */
export interface QuarterlySummary {
  quarter: Quarter
  total_objectives: number
  total_key_results: number
  overall_progress: number
  status_breakdown: {
    on_track: number
    needs_attention: number
    at_risk: number
    blocked: number
    completed: number
  }
  week_number: number // Current week of the quarter (1-12)
  weeks_remaining: number
}

/**
 * API response for OKRs list
 */
export interface OKRsResponse {
  objectives: Objective[]
  summary: QuarterlySummary
}

/**
 * Get status color for UI
 */
export function getStatusColor(status: OKRStatus): string {
  switch (status) {
    case 'ON_TRACK':
    case 'COMPLETED':
      return 'green'
    case 'NEEDS_ATTENTION':
      return 'yellow'
    case 'AT_RISK':
      return 'red'
    case 'BLOCKED':
      return 'gray'
    default:
      return 'gray'
  }
}

/**
 * Get status label for UI
 */
export function getStatusLabel(status: OKRStatus): string {
  switch (status) {
    case 'ON_TRACK':
      return 'On Track'
    case 'NEEDS_ATTENTION':
      return 'Needs Attention'
    case 'AT_RISK':
      return 'At Risk'
    case 'BLOCKED':
      return 'Blocked'
    case 'COMPLETED':
      return 'Completed'
    default:
      return 'Unknown'
  }
}

/**
 * Calculate status based on progress and week
 */
export function calculateStatus(progress: number, weekNumber: number, isBlocked: boolean = false): OKRStatus {
  if (isBlocked) return 'BLOCKED'
  if (progress >= 100) return 'COMPLETED'

  // At week 8 (of 12), threshold is based on expected progress
  // Scale: at week 8, should be at ~67% (8/12)
  const expectedProgress = (weekNumber / 12) * 100
  const progressRatio = progress / expectedProgress

  if (progressRatio >= 0.7) return 'ON_TRACK'
  if (progressRatio >= 0.5) return 'NEEDS_ATTENTION'
  return 'AT_RISK'
}

/**
 * Get available quarters (current + next 2)
 */
export function getAvailableQuarters(): Quarter[] {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1
  const currentQuarter = Math.ceil(currentMonth / 3)

  const quarters: Quarter[] = []

  for (let i = -1; i <= 2; i++) {
    let q = currentQuarter + i
    let year = currentYear

    if (q > 4) {
      q -= 4
      year += 1
    } else if (q < 1) {
      q += 4
      year -= 1
    }

    quarters.push(`Q${q as 1 | 2 | 3 | 4}-${year}`)
  }

  return quarters
}

/**
 * Get current quarter
 */
export function getCurrentQuarter(): Quarter {
  const now = new Date()
  const month = now.getMonth() + 1
  const quarter = Math.ceil(month / 3) as 1 | 2 | 3 | 4
  return `Q${quarter}-${now.getFullYear()}`
}
