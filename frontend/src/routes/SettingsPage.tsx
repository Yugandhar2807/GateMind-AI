import * as React from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Camera, Loader2 } from 'lucide-react'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { apiClient } from '@/lib/api-client'
import { cn } from '@/lib/utils'
import { useMe } from '@/hooks/use-auth'
import type { PreferredStudyTime, User } from '@/types/user'

const STUDY_TIME_OPTIONS: { value: PreferredStudyTime; label: string }[] = [
  { value: 'early_morning', label: 'Early morning (before 7am)' },
  { value: 'morning', label: 'Morning' },
  { value: 'evening', label: 'Evening' },
  { value: 'night', label: 'Night' },
  { value: 'late_night', label: 'Late night' },
]

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

export default function SettingsPage() {
  const { data: user } = useMe()
  const queryClient = useQueryClient()
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const [form, setForm] = React.useState({
    full_name: '',
    target_score: '',
    target_air: '',
    daily_study_hours: '',
    preferred_study_time: '' as PreferredStudyTime | '',
    exam_date: '',
    gym_time: '',
  })

  React.useEffect(() => {
    if (!user) return
    setForm({
      full_name: user.full_name,
      target_score: user.target_score?.toString() ?? '',
      target_air: user.target_air?.toString() ?? '',
      daily_study_hours: user.daily_study_hours?.toString() ?? '',
      preferred_study_time: user.preferred_study_time ?? '',
      exam_date: user.exam_date ?? '2027-02-07',
      gym_time: user.gym_time ?? '',
    })
  }, [user])

  const updateProfile = useMutation({
    mutationFn: async () => {
      const { data } = await apiClient.patch<User>('/users/me', {
        full_name: form.full_name || undefined,
        target_score: form.target_score ? Number(form.target_score) : undefined,
        target_air: form.target_air ? Number(form.target_air) : undefined,
        daily_study_hours: form.daily_study_hours ? Number(form.daily_study_hours) : undefined,
        preferred_study_time: form.preferred_study_time || undefined,
        exam_date: form.exam_date || undefined,
        gym_time: form.gym_time || undefined,
      })
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['me'], data)
    },
  })

  const uploadPhoto = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await apiClient.post<User>('/users/me/photo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['me'], data)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    updateProfile.mutate()
  }

  function handlePhotoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) uploadPhoto.mutate(file)
  }

  if (!user) return null

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Settings</p>
        <h1 className="mt-1 font-display text-2xl font-semibold">Your profile</h1>
      </div>

      <Card>
        <CardContent className="flex items-center gap-4 pt-5">
          <Avatar className="size-16">
            {user.photo_url && <AvatarImage src={user.photo_url} alt={user.full_name} />}
            <AvatarFallback className="text-lg">{initials(user.full_name)}</AvatarFallback>
          </Avatar>
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="hidden"
              onChange={handlePhotoChange}
            />
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploadPhoto.isPending}
            >
              {uploadPhoto.isPending ? <Loader2 className="animate-spin" /> : <Camera />}
              Change photo
            </Button>
            <p className="mt-1.5 text-xs text-[var(--fg-faint)]">PNG, JPEG or WebP, up to 10MB.</p>
          </div>
        </CardContent>
      </Card>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Exam target</CardTitle>
            <CardDescription>Drives dashboard countdowns and predicted-AIR framing.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-5 pt-0">
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="full_name">Full name</Label>
              <Input
                id="full_name"
                value={form.full_name}
                onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="target_score">Target score (/100)</Label>
                <Input
                  id="target_score"
                  type="number"
                  min={0}
                  max={100}
                  value={form.target_score}
                  onChange={(e) => setForm((f) => ({ ...f, target_score: e.target.value }))}
                  placeholder="e.g. 78"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="target_air">Target AIR</Label>
                <Input
                  id="target_air"
                  type="number"
                  min={1}
                  value={form.target_air}
                  onChange={(e) => setForm((f) => ({ ...f, target_air: e.target.value }))}
                  placeholder="e.g. 50"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="daily_study_hours">Daily study hours</Label>
                <Input
                  id="daily_study_hours"
                  type="number"
                  min={0}
                  max={24}
                  step={0.5}
                  value={form.daily_study_hours}
                  onChange={(e) => setForm((f) => ({ ...f, daily_study_hours: e.target.value }))}
                  placeholder="e.g. 2.5"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="exam_date">Exam date</Label>
                <Input
                  id="exam_date"
                  type="date"
                  value={form.exam_date}
                  onChange={(e) => setForm((f) => ({ ...f, exam_date: e.target.value }))}
                />
              </div>
            </div>

            <Separator />

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="preferred_study_time">Preferred study time</Label>
                <select
                  id="preferred_study_time"
                  value={form.preferred_study_time}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, preferred_study_time: e.target.value as PreferredStudyTime }))
                  }
                  className={cn(
                    'flex h-10 w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm text-[var(--fg)] outline-none',
                    'focus-visible:border-signal-500 focus-visible:ring-2 focus-visible:ring-signal-500/30',
                  )}
                >
                  <option value="">Not set</option>
                  {STUDY_TIME_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="gym_time">Gym time</Label>
                <Input
                  id="gym_time"
                  type="time"
                  value={form.gym_time}
                  onChange={(e) => setForm((f) => ({ ...f, gym_time: e.target.value }))}
                />
              </div>
            </div>

            {updateProfile.isSuccess && (
              <p className="text-sm text-mastery-500">Saved.</p>
            )}

            <Button type="submit" className="self-start" disabled={updateProfile.isPending}>
              {updateProfile.isPending && <Loader2 className="animate-spin" />}
              Save changes
            </Button>
          </CardContent>
        </Card>
      </form>
    </div>
  )
}
