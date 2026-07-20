import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type {
  PracticeAnswerRequest,
  PracticeAnswerResult,
  PracticeAttemptStarted,
  PracticeStartRequest,
  PracticeSubmitResponse,
  TopicQuestionStats,
} from '@/types/practice'

export function useTopicQuestionStats(topicId: number | undefined) {
  return useQuery({
    queryKey: ['practice', 'stats', topicId],
    enabled: topicId != null,
    queryFn: async () => {
      const { data } = await apiClient.get<TopicQuestionStats>(`/practice/topics/${topicId}/stats`)
      return data
    },
  })
}

export function useStartPractice() {
  return useMutation({
    mutationFn: async (payload: PracticeStartRequest) => {
      const { data } = await apiClient.post<PracticeAttemptStarted>('/practice/start', payload)
      return data
    },
  })
}

export function useAnswerQuestion(attemptId: number | null) {
  return useMutation({
    mutationFn: async (payload: PracticeAnswerRequest) => {
      const { data } = await apiClient.post<PracticeAnswerResult>(`/practice/attempts/${attemptId}/answer`, payload)
      return data
    },
  })
}

export function useSubmitAttempt() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (attemptId: number) => {
      const { data } = await apiClient.post<PracticeSubmitResponse>(`/practice/attempts/${attemptId}/submit`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['roadmap'] })
      queryClient.invalidateQueries({ queryKey: ['me'] })
    },
  })
}
