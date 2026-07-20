import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { ProgressUpdateRequest, SubjectNode, TopicProgress } from '@/types/roadmap'

export function useRoadmap() {
  return useQuery({
    queryKey: ['roadmap'],
    queryFn: async () => {
      const { data } = await apiClient.get<SubjectNode[]>('/roadmap')
      return data
    },
  })
}

export function useUpdateTopicProgress() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ topicId, payload }: { topicId: string; payload: ProgressUpdateRequest }) => {
      const { data } = await apiClient.patch<TopicProgress>(`/roadmap/topics/${topicId}/progress`, payload)
      return data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['roadmap'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['me'] })
      queryClient.invalidateQueries({ queryKey: ['topic', variables.topicId] })
    },
  })
}
