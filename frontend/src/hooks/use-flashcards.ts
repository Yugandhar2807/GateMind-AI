import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { Flashcard, FlashcardStateUpdate } from '@/types/flashcard'

export function useDueFlashcards() {
  return useQuery({
    queryKey: ['flashcards', 'due'],
    queryFn: async () => {
      const { data } = await apiClient.get<Flashcard[]>('/flashcards/due')
      return data
    },
  })
}

export function useAllFlashcards(topicId?: string) {
  return useQuery({
    queryKey: ['flashcards', 'all', topicId ?? 'any'],
    queryFn: async () => {
      const { data } = await apiClient.get<Flashcard[]>('/flashcards', { params: topicId ? { topic_id: topicId } : {} })
      return data
    },
  })
}

export function useReviewFlashcard() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, correct }: { id: string; correct: boolean }) => {
      const { data } = await apiClient.post<Flashcard>(`/flashcards/${id}/review`, { correct })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

export function useUpdateFlashcardState() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: FlashcardStateUpdate }) => {
      const { data } = await apiClient.patch<Flashcard>(`/flashcards/${id}/state`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['flashcards'] }),
  })
}
