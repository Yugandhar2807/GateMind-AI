import type { Difficulty, NodeLevel, TopicProgress } from '@/types/roadmap'

export type ResourceType =
  | 'video'
  | 'book'
  | 'blog'
  | 'documentation'
  | 'research_paper'
  | 'github_repo'
  | 'article'
  | 'lecture_series'
export type ResourceLevel = 'beginner' | 'intermediate' | 'advanced' | 'research'

export interface ResourceRead {
  id: string
  title: string
  resource_type: ResourceType
  level: ResourceLevel
  url: string | null
  platform: string | null
  instructor: string | null
  description: string | null
  is_free: boolean
  ranking?: string | null
  category?: string | null
  organization?: string | null
  channel?: string | null
  year?: number | null
  duration_minutes?: number | null
  rating?: number | null
  language?: string | null
  why_recommended?: string | null
  needs_review?: boolean
}

export interface TopicDetail {
  id: string
  slug: string
  name: string
  level: NodeLevel
  difficulty: Difficulty | null
  importance_1to5: number | null
  pyq_frequency: string | null
  estimated_hours: number | null
  revision_frequency: string | null
  prerequisites_text: string | null
  introduction: string | null
  theory_markdown: string | null
  formulas_markdown: string | null
  real_world_applications: string | null
  mind_map_json: string | null
  cheat_sheet_markdown: string | null
  common_mistakes_markdown: string | null
  subject_id: string
  subject_name: string
  subject_slug: string
  progress: TopicProgress
  resources: ResourceRead[]
}
