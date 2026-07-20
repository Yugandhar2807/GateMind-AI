export type PreferredStudyTime = 'early_morning' | 'morning' | 'evening' | 'night' | 'late_night'
export type UserRole = 'student' | 'admin'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  photo_url: string | null
  target_score: number | null
  target_air: number | null
  daily_study_hours: number | null
  preferred_study_time: PreferredStudyTime | null
  exam_date: string | null
  gym_time: string | null
  current_streak_days: number
  longest_streak_days: number
  is_active: boolean
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}
