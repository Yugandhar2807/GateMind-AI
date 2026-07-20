import type { Difficulty } from './roadmap'

export type QuestionType = 'mcq' | 'msq' | 'nat'
export type QuestionSource = 'pyq' | 'practice' | 'ai_generated' | 'mock'

export interface QuestionPublic {
  id: string
  topic_id: string
  question_type: QuestionType
  difficulty: Difficulty
  source: QuestionSource
  source_year: number | null
  question_markdown: string
  options: string[] | null
  marks: number
  negative_marks: number
  expected_time_seconds: number
}

export interface PracticeStartRequest {
  topic_id?: string
  subject_id?: string
  difficulty?: Difficulty
  question_count: number
}

export interface PracticeAttemptStarted {
  attempt_id: string
  topic_id: string | null
  questions: QuestionPublic[]
}

export interface PracticeAnswerRequest {
  question_id: string
  selected_indices?: number[]
  nat_value?: number
  is_skipped: boolean
  time_taken_seconds: number
}

export interface PracticeAnswerResult {
  question_id: string
  is_correct: boolean | null
  marks_awarded: number
  correct_option_indices: number[]
  correct_value: number | null
  explanation_markdown: string | null
}

export interface PracticeSubmitResponse {
  attempt_id: string
  score: number
  max_score: number
  accuracy_percent: number
  correct_count: number
  incorrect_count: number
  skipped_count: number
  negative_marks_lost: number
  avg_time_per_question_seconds: number
}

export interface TopicQuestionStats {
  total: number
  by_difficulty: Record<string, number>
  by_type: Record<string, number>
}
