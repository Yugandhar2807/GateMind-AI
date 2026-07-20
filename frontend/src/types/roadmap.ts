export type Difficulty = 'easy' | 'medium' | 'hard' | 'very_hard'
export type PriorityLevel = 'high' | 'medium' | 'low'
export type NodeLevel = 'topic' | 'subtopic' | 'concept'
export type ProgressStatus = 'not_started' | 'in_progress' | 'completed' | 'needs_revision'

export interface TopicProgress {
  status: ProgressStatus
  completion_percent: number
  retention_percent: number | null
  accuracy_percent: number | null
  pyqs_solved: number
  practice_solved: number
  revision_count: number
  time_spent_minutes: number
  last_studied_at: string | null
  last_revised_at: string | null
  completed_at: string | null
}

export interface TopicNode {
  id: number
  slug: string
  name: string
  level: NodeLevel
  order_index: number
  difficulty: Difficulty | null
  importance_1to5: number | null
  pyq_frequency: string | null
  estimated_hours: number | null
  revision_frequency: string | null
  prerequisites_text: string | null
  progress: TopicProgress
  children: TopicNode[]
}

export interface SubjectProgressSummary {
  total: number
  completed: number
  in_progress: number
  not_started: number
  needs_revision: number
  avg_completion_percent: number
}

export interface SubjectNode {
  id: number
  slug: string
  name: string
  description: string | null
  weightage_min_percent: number | null
  weightage_max_percent: number | null
  difficulty: Difficulty | null
  priority: PriorityLevel | null
  order_index: number
  is_official_section: boolean
  progress_summary: SubjectProgressSummary
  topics: TopicNode[]
}

export interface ProgressUpdateRequest {
  status?: ProgressStatus
  completion_percent?: number
  time_spent_minutes_delta?: number
}
