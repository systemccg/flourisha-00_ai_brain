/**
 * Energy Tracking Types
 * Real-time energy and focus quality tracking
 */

/**
 * Focus quality levels
 */
export type FocusQuality = 'deep' | 'shallow' | 'distracted'

/**
 * Energy data source
 */
export type EnergySource = 'chrome_extension' | 'sms' | 'manual' | 'web'

/**
 * Single energy tracking entry
 */
export interface EnergyEntry {
  id: string
  tenant_id: string
  user_id: string
  created_at: string
  timestamp: string
  energy_level: number // 1-10
  focus_quality: FocusQuality
  current_task?: string
  source: EnergySource
  location?: string
  notes?: string
}

/**
 * Payload for logging energy
 */
export interface LogEnergyPayload {
  energy_level: number // 1-10
  focus_quality: FocusQuality
  current_task?: string
  notes?: string
}

/**
 * Energy history query params
 */
export interface EnergyHistoryParams {
  days?: number
  start_date?: string
  end_date?: string
}

/**
 * Daily energy summary
 */
export interface DailyEnergySummary {
  date: string
  avg_energy: number
  primary_focus: FocusQuality
  measurement_count: number
  entries: EnergyEntry[]
}

/**
 * Energy by hour of day
 */
export interface HourlyEnergyPattern {
  hour: number
  avg_energy: number
  measurements: number
}

/**
 * Focus quality distribution
 */
export interface FocusDistribution {
  deep: number
  shallow: number
  distracted: number
  total: number
}

/**
 * Energy period forecast
 */
export interface EnergyPeriodForecast {
  period: 'morning' | 'afternoon' | 'evening'
  predicted_energy: number
  confidence: number // 0-100
  recommendation?: string
}

/**
 * Full daily energy forecast
 */
export interface EnergyForecast {
  date: string
  morning: EnergyPeriodForecast
  afternoon: EnergyPeriodForecast
  evening: EnergyPeriodForecast
  overall_predicted: number
  best_hours: number[] // Array of hours (0-23)
  schedule_impact: number
  historical_accuracy: number // 0-100
}

/**
 * Energy history response
 */
export interface EnergyHistoryResponse {
  entries: EnergyEntry[]
  summary: {
    avg_energy: number
    total_entries: number
    focus_distribution: FocusDistribution
  }
  daily_summaries: DailyEnergySummary[]
  hourly_patterns: HourlyEnergyPattern[]
}

/**
 * Current streak information
 */
export interface EnergyStreak {
  current_streak: number
  longest_streak: number
  last_entry_date: string
  entries_today: number
}

/**
 * Focus quality option for UI
 */
export interface FocusOption {
  value: FocusQuality
  label: string
  emoji: string
  description: string
  color: string
}

/**
 * Available focus quality options
 */
export const FOCUS_OPTIONS: FocusOption[] = [
  {
    value: 'deep',
    label: 'Deep',
    emoji: '🎯',
    description: 'Focused, productive work',
    color: 'green',
  },
  {
    value: 'shallow',
    label: 'Shallow',
    emoji: '📋',
    description: 'Administrative tasks',
    color: 'yellow',
  },
  {
    value: 'distracted',
    label: 'Distracted',
    emoji: '🌀',
    description: 'Unable to focus',
    color: 'red',
  },
]

/**
 * Get focus option by value
 */
export function getFocusOption(value: FocusQuality): FocusOption {
  return FOCUS_OPTIONS.find(opt => opt.value === value) || FOCUS_OPTIONS[0]
}

/**
 * Get color for energy level
 */
export function getEnergyColor(level: number): string {
  if (level >= 8) return 'green'
  if (level >= 6) return 'yellow'
  if (level >= 4) return 'orange'
  return 'red'
}

/**
 * Get label for energy level
 */
export function getEnergyLabel(level: number): string {
  if (level >= 9) return 'Peak Energy'
  if (level >= 7) return 'High Energy'
  if (level >= 5) return 'Moderate'
  if (level >= 3) return 'Low Energy'
  return 'Exhausted'
}
