/**
 * Core type definitions for Flourisha Frontend
 */

// ============================================================================
// User & Auth Types
// ============================================================================

export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  personal_workspace_id: string
  subscription_tier: 'free' | 'pro' | 'team'
  created_at: string
  updated_at: string
}

export interface Workspace {
  id: string
  name: string
  slug: string
  type: 'personal' | 'team'
  icon_url?: string
  description?: string
  member_count: number
  created_at: string
}

// ============================================================================
// OKR Types
// ============================================================================

export interface Objective {
  id: string
  title: string
  description?: string
  quarter: string
  status: 'on_track' | 'needs_attention' | 'at_risk' | 'blocked'
  progress: number
  key_results: KeyResult[]
  created_at: string
  updated_at: string
}

export interface KeyResult {
  id: string
  objective_id: string
  title: string
  description?: string
  target_value: number
  current_value: number
  unit: string
  progress: number
  status: 'on_track' | 'needs_attention' | 'at_risk' | 'blocked'
  measurements: Measurement[]
}

export interface Measurement {
  id: string
  kr_id: string
  value: number
  notes?: string
  recorded_at: string
  recorded_by: string
}

// ============================================================================
// Energy Tracking Types
// ============================================================================

export type FocusQuality = 'deep' | 'shallow' | 'distracted'

export interface EnergyEntry {
  id: string
  energy_level: number // 1-10
  focus_quality: FocusQuality
  current_task?: string
  source: 'chrome_extension' | 'sms' | 'manual'
  recorded_at: string
}

export interface EnergyForecast {
  hour: number
  predicted_energy: number
  confidence: number
  recommendation?: string
}

// ============================================================================
// Knowledge Types
// ============================================================================

export interface SearchResult {
  id: string
  title: string
  content_type: string
  summary: string
  similarity_score: number
  source: 'vector' | 'graph' | 'whole'
  tags: string[]
  created_at: string
}

export interface GraphNode {
  id: string
  name: string
  type: string
  properties: Record<string, unknown>
}

export interface GraphRelationship {
  id: string
  source_id: string
  target_id: string
  type: string
  properties: Record<string, unknown>
}

export interface PARAFolder {
  name: string
  path: string
  type: 'projects' | 'areas' | 'resources' | 'archives'
  children?: PARAFolder[]
  file_count?: number
}

// ============================================================================
// Skill & Agent Types
// ============================================================================

export interface Skill {
  id: string
  name: string
  description: string
  triggers: string[]
  category: string
  is_active: boolean
}

export interface Agent {
  id: string
  name: string
  type: string
  capabilities: string[]
  status: 'idle' | 'running' | 'error'
}

// ============================================================================
// Integration Types
// ============================================================================

export interface Integration {
  id: string
  name: string
  type: 'mcp' | 'direct_api' | 'skill'
  category: 'email' | 'calendar' | 'storage' | 'project_mgmt' | 'communication' | 'database'
  status: 'connected' | 'disconnected' | 'error'
  connected_at?: string
  last_sync?: string
  settings?: Record<string, unknown>
}

// ============================================================================
// System Health Types
// ============================================================================

export interface ServiceStatus {
  name: string
  status: 'healthy' | 'degraded' | 'down'
  uptime_percent: number
  last_check: string
  response_time_ms?: number
}

export interface SystemHealth {
  overall_status: 'healthy' | 'degraded' | 'down'
  services: ServiceStatus[]
  last_updated: string
}
