import type { Difficulty } from '@/types/roadmap'

export interface Flashcard {
  id: string
  topic_id: string
  topic_name: string
  subject_name: string
  front_markdown: string
  back_markdown: string
  difficulty: Difficulty
  box: number
  is_bookmarked: boolean
  is_favorite: boolean
  review_later: boolean
  next_review_at: string | null
}

export interface FlashcardStateUpdate {
  is_bookmarked?: boolean
  is_favorite?: boolean
  review_later?: boolean
}
