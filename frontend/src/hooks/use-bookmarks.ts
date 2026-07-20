import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '@/lib/api-client'
import type { Bookmark, BookmarkToggleResponse, BookmarkType } from '@/types/bookmark'

export function useBookmarks() {
  return useQuery({
    queryKey: ['bookmarks'],
    queryFn: async () => {
      const { data } = await apiClient.get<Bookmark[]>('/bookmarks')
      return data
    },
  })
}

export function useBookmarkedIds(bookmarkType: BookmarkType) {
  return useQuery({
    queryKey: ['bookmarks', 'ids', bookmarkType],
    queryFn: async () => {
      const { data } = await apiClient.get<string[]>('/bookmarks/ids', { params: { bookmark_type: bookmarkType } })
      return new Set(data)
    },
  })
}

export function useToggleBookmark() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ bookmarkType, targetId }: { bookmarkType: BookmarkType; targetId: string }) => {
      const { data } = await apiClient.post<BookmarkToggleResponse>('/bookmarks/toggle', {
        bookmark_type: bookmarkType,
        target_id: targetId,
      })
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}
