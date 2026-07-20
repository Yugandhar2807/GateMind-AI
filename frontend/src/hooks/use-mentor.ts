import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'

export interface MentorMessage {
  id: string
  role: string
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  title: string
  updated_at: string
}

interface ChatResponse {
  conversation_id: string
  message: MentorMessage
}

export function useConversations() {
  return useQuery({
    queryKey: ['mentor', 'conversations'],
    queryFn: async () => {
      const { data } = await apiClient.get<Conversation[]>('/mentor/conversations')
      return data
    },
  })
}

export function useSendMessage() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: { message: string; conversation_id?: string | null }) => {
      const { data } = await apiClient.post<ChatResponse>('/mentor/chat', payload)
      return data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['mentor', 'conversations'] }),
  })
}
