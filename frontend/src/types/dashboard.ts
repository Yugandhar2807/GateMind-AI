export interface DailyStudyPoint {
  date: string
  minutes: number
  topics_completed: number
}

export interface RevisionItem {
  topic_id: string
  topic_name: string
  subject_name: string
  due_date: string
  interval_day: number
  overdue: boolean
}

export interface SubjectCompletion {
  subject_id: string
  name: string
  slug: string
  completed: number
  total: number
  percent: number
  weightage_max_percent: number | null
  is_official_section: boolean
}

export interface WeakStrongTopic {
  topic_id: string
  topic_name: string
  subject_name: string
  accuracy_percent: number
}

export interface LastSession {
  topic_name: string | null
  subject_name: string | null
  session_type: string
  started_at: string
  duration_minutes: number
}

export interface TodayTask {
  topic_id: string
  topic_name: string
  subject_name: string
  kind: 'revision' | 'in_progress'
}

export interface DashboardSummary {
  greeting_name: string
  exam_date: string | null
  days_remaining: number | null
  target_score: number | null
  target_air: number | null

  current_streak_days: number
  longest_streak_days: number
  last_active_date: string | null

  topics_total: number
  topics_completed: number
  topics_in_progress: number
  topics_not_started: number
  topics_needs_revision: number
  weightage_completed_percent: number
  remaining_hours: number
  predicted_completion_date: string | null

  difficulty_distribution: Record<string, number>
  subject_completion: SubjectCompletion[]

  study_minutes_today: number
  study_minutes_week: number
  study_minutes_month: number
  weekly_series: DailyStudyPoint[]
  last_session: LastSession | null

  revision_due_today: number
  upcoming_revisions: RevisionItem[]
  today_tasks: TodayTask[]

  weak_topics: WeakStrongTopic[]
  strong_topics: WeakStrongTopic[]

  predicted_marks: number | null
  predicted_air: number | null
  next_mock_date: string | null
  has_accuracy_data: boolean
  has_mock_data: boolean
}
