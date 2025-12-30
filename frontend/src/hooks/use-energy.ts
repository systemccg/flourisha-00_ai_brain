'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, APIResponse, endpoints } from '@/lib/api'
import type {
  EnergyEntry,
  EnergyHistoryResponse,
  EnergyForecast,
  EnergyStreak,
  LogEnergyPayload,
  EnergyHistoryParams,
} from '@/lib/types/energy'

/**
 * Query keys for energy data
 */
export const energyKeys = {
  all: ['energy'] as const,
  history: (params?: EnergyHistoryParams) => [...energyKeys.all, 'history', params] as const,
  forecast: (date?: string) => [...energyKeys.all, 'forecast', date] as const,
  streak: () => [...energyKeys.all, 'streak'] as const,
  today: () => [...energyKeys.all, 'today'] as const,
}

/**
 * Fetch energy history
 */
async function fetchEnergyHistory(params?: EnergyHistoryParams): Promise<EnergyHistoryResponse> {
  const response = await api.get<APIResponse<EnergyHistoryResponse>>(endpoints.energy.history, {
    params,
  })

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch energy history')
  }

  return response.data.data
}

/**
 * Fetch energy forecast
 */
async function fetchEnergyForecast(date?: string): Promise<EnergyForecast> {
  const response = await api.get<APIResponse<EnergyForecast>>(`${endpoints.energy.log}/forecast`, {
    params: date ? { date } : undefined,
  })

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch energy forecast')
  }

  return response.data.data
}

/**
 * Fetch energy streak info
 */
async function fetchEnergyStreak(): Promise<EnergyStreak> {
  const response = await api.get<APIResponse<EnergyStreak>>(`${endpoints.energy.log}/streak`)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch energy streak')
  }

  return response.data.data
}

/**
 * Fetch today's energy entries
 */
async function fetchTodayEnergy(): Promise<EnergyEntry[]> {
  const response = await api.get<APIResponse<EnergyEntry[]>>(`${endpoints.energy.log}/today`)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to fetch today\'s energy')
  }

  return response.data.data
}

/**
 * Log energy entry
 */
async function logEnergy(payload: LogEnergyPayload): Promise<EnergyEntry> {
  const response = await api.post<APIResponse<EnergyEntry>>(endpoints.energy.log, payload)

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to log energy')
  }

  return response.data.data
}

/**
 * Hook for fetching energy history
 */
export function useEnergyHistory(params?: EnergyHistoryParams) {
  return useQuery({
    queryKey: energyKeys.history(params),
    queryFn: () => fetchEnergyHistory(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Hook for fetching energy forecast
 */
export function useEnergyForecast(date?: string) {
  return useQuery({
    queryKey: energyKeys.forecast(date),
    queryFn: () => fetchEnergyForecast(date),
    staleTime: 1000 * 60 * 15, // 15 minutes
  })
}

/**
 * Hook for fetching energy streak
 */
export function useEnergyStreak() {
  return useQuery({
    queryKey: energyKeys.streak(),
    queryFn: fetchEnergyStreak,
    staleTime: 1000 * 60 * 5,
  })
}

/**
 * Hook for fetching today's energy
 */
export function useTodayEnergy() {
  return useQuery({
    queryKey: energyKeys.today(),
    queryFn: fetchTodayEnergy,
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchInterval: 1000 * 60 * 5, // Refetch every 5 minutes
  })
}

/**
 * Hook for logging energy
 */
export function useLogEnergy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: logEnergy,
    onSuccess: () => {
      // Invalidate all energy queries
      queryClient.invalidateQueries({ queryKey: energyKeys.all })
    },
  })
}

/**
 * Combined energy dashboard data
 */
export function useEnergyDashboard() {
  const history = useEnergyHistory({ days: 7 })
  const forecast = useEnergyForecast()
  const streak = useEnergyStreak()
  const today = useTodayEnergy()

  return {
    history: history.data,
    forecast: forecast.data,
    streak: streak.data,
    today: today.data,
    isLoading: history.isLoading || forecast.isLoading || streak.isLoading || today.isLoading,
    error: history.error || forecast.error || streak.error || today.error,
    refetch: () => {
      history.refetch()
      forecast.refetch()
      streak.refetch()
      today.refetch()
    },
  }
}
