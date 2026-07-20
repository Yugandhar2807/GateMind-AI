export type BookmarkType = 'resource' | 'question' | 'topic' | 'formula' | 'note' | 'flashcard'

export interface Bookmark {
  id: string
  bookmark_type: BookmarkType
  target_id: string
  notes: string | null
  created_at: string
  title: string
  subtitle: string | null
  link: string
  is_missing: boolean
}

export interface BookmarkToggleResponse {
  bookmarked: boolean
  bookmark_id: string | null
}
