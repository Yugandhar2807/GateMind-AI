import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { Note, NoteCreate, NoteUpdate } from '@/types/note'

export function useNotes(topicId?: number) {
  return useQuery({
    queryKey: ['notes', topicId ?? 'all'],
    queryFn: async () => {
      const { data } = await apiClient.get<Note[]>('/notes', { params: topicId ? { topic_id: topicId } : {} })
      return data
    },
  })
}

export function useCreateNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: NoteCreate) => {
      const { data } = await apiClient.post<Note>('/notes', payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  })
}

export function useUpdateNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: number; payload: NoteUpdate }) => {
      const { data } = await apiClient.patch<Note>(`/notes/${id}`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  })
}

export function useDeleteNote() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/notes/${id}`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  })
}
