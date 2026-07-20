import type { Difficulty } from './roadmap'

export type QuestionType = 'mcq' | 'msq' | 'nat'
export type QuestionSource = 'pyq' | 'practice' | 'ai_generated' | 'mock'

export interface QuestionPublic {
  id: number
  topic_id: number
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
  topic_id?: number
  subject_id?: number
  difficulty?: Difficulty
  question_count: number
}

export interface PracticeAttemptStarted {
  attempt_id: number
  topic_id: number | null
  questions: QuestionPublic[]
}

export interface PracticeAnswerRequest {
  question_id: number
  selected_indices?: number[]
  nat_value?: number
  is_skipped: boolean
  time_taken_seconds: number
}

export interface PracticeAnswerResult {
  question_id: number
  is_correct: boolean | null
  marks_awarded: number
  correct_option_indices: number[]
  correct_value: number | null
  explanation_markdown: string | null
}

export interface PracticeSubmitResponse {
  attempt_id: number
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
