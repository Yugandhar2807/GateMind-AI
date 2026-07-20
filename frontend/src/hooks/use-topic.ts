import { useQuery } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { TopicDetail } from '@/types/topic'

export function useTopicDetail(topicId: string | undefined) {
  return useQuery({
    queryKey: ['topic', topicId],
    enabled: topicId != null,
    queryFn: async () => {
      const { data } = await apiClient.get<TopicDetail>(`/roadmap/topics/${topicId}`)
      return data
    },
  })
}
