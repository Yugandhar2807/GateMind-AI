export interface DailyStudyPoint {
  date: string
  minutes: number
  topics_completed: number
}

export interface UpcomingRevision {
  topic_id: string
  topic_name: string
  subject_name: string
  scheduled_date: string
  interval_stage: number
}

export interface WeakStrongTopic {
  topic_id: string
  topic_name: string
  subject_name: string
  accuracy_percent: number
}

export interface DashboardSummary {
  exam_date: string | null
  days_remaining: number | null
  target_score: number | null
  target_air: number | null
  current_streak_days: number
  longest_streak_days: number
  topics_total: number
  topics_completed: number
  topics_in_progress: number
  topics_not_started: number
  topics_needs_revision: number
  weightage_completed_percent: number | null
  study_minutes_today: number
  study_minutes_week: number
  study_minutes_month: number
  weekly_series: DailyStudyPoint[]
  upcoming_revisions: UpcomingRevision[]
  weak_topics: WeakStrongTopic[]
  strong_topics: WeakStrongTopic[]
  predicted_marks: number | null
  predicted_air: number | null
  next_mock_date: string | null
}
