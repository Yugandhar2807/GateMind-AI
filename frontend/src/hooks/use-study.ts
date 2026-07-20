import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'

export interface StudySession {
  id: string
  topic_id: string | null
  topic_name: string | null
  subject_name: string | null
  session_type: string
  started_at: string
  ended_at: string | null
  duration_minutes: number
  interruptions: number
  focus_score: number | null
  notes: string | null
  is_active: boolean
}

export function useActiveSession() {
  return useQuery({
    queryKey: ['study', 'active'],
    queryFn: async () => {
      const { data } = await apiClient.get<StudySession | null>('/study/sessions/active')
      return data
    },
  })
}

export function useRecentSessions() {
  return useQuery({
    queryKey: ['study', 'recent'],
    queryFn: async () => {
      const { data } = await apiClient.get<StudySession[]>('/study/sessions')
      return data
    },
  })
}

export function useStartSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { topic_id?: string | null; session_type?: string }) => {
      const { data } = await apiClient.post<StudySession>('/study/sessions/start', payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['study'] }),
  })
}

interface StopPayload {
  id: string
  notes?: string | null
  interruptions?: number
  focus_score?: number | null
}

export function useStopSession() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, ...payload }: StopPayload) => {
      const { data } = await apiClient.post<StudySession>(`/study/sessions/${id}/stop`, payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['study'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      qc.invalidateQueries({ queryKey: ['me'] })
    },
  })
}
