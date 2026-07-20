import { useQuery } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { DashboardSummary } from '@/types/dashboard'

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardSummary>('/dashboard')
      return data
    },
  })
}
