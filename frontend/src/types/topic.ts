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
  id: number
  title: string
  resource_type: ResourceType
  level: ResourceLevel
  url: string | null
  platform: string | null
  instructor: string | null
  description: string | null
  is_free: boolean
}

export interface TopicDetail {
  id: number
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
  subject_id: number
  subject_name: string
  subject_slug: string
  progress: TopicProgress
  resources: ResourceRead[]
}
