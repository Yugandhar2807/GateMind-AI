import * as React from 'react'
import { Link } from 'react-router-dom'
import { ChevronDown, Loader2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { useRoadmap, useUpdateTopicProgress } from '@/hooks/use-roadmap'
import type { Difficulty, PriorityLevel, ProgressStatus, SubjectNode, TopicNode } from '@/types/roadmap'

const DIFFICULTY_LABEL: Record<Difficulty, string> = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
  very_hard: 'Very Hard',
}

const DIFFICULTY_VARIANT: Record<Difficulty, 'mastery' | 'default' | 'ember' | 'risk'> = {
  easy: 'mastery',
  medium: 'default',
  hard: 'ember',
  very_hard: 'risk',
}

const PRIORITY_LABEL: Record<PriorityLevel, string> = { high: 'High priority', medium: 'Medium priority', low: 'Low priority' }

const STATUS_OPTIONS: { value: ProgressStatus; label: string }[] = [
  { value: 'not_started', label: 'Not started' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'needs_revision', label: 'Needs revision' },
]

function weightageLabel(min: number | null, max: number | null) {
  if (min == null) return null
  if (max == null || max === min) return `~${min}%`
  return `${min}–${max}%`
}

function TopicRow({ topic }: { topic: TopicNode }) {
  const updateProgress = useUpdateTopicProgress()
  const [localStatus, setLocalStatus] = React.useState(topic.progress.status)

  React.useEffect(() => setLocalStatus(topic.progress.status), [topic.progress.status])

  function handleStatusChange(status: ProgressStatus) {
    setLocalStatus(status)
    updateProgress.mutate({ topicId: topic.id, payload: { status } })
  }

  return (
    <div className="grid grid-cols-[1fr_auto] items-center gap-3 border-t border-[var(--border)] px-4 py-3 first:border-t-0 sm:grid-cols-[1fr_140px_110px_170px]">
      <div className="min-w-0">
        <Link
          to={`/roadmap/topics/${topic.id}`}
          className="truncate text-sm font-medium hover:text-signal-500 hover:underline"
        >
          {topic.name}
        </Link>
        {topic.pyq_frequency && (
          <p className="mt-0.5 truncate text-xs text-[var(--fg-faint)]" title={topic.pyq_frequency}>
            {topic.pyq_frequency}
          </p>
        )}
      </div>

      <div className="hidden sm:block">
        {topic.difficulty && (
          <Badge variant={DIFFICULTY_VARIANT[topic.difficulty]}>{DIFFICULTY_LABEL[topic.difficulty]}</Badge>
        )}
      </div>

      <div className="hidden items-center gap-2 sm:flex">
        <Progress value={topic.progress.completion_percent} className="w-16" />
        <span className="font-mono text-xs text-[var(--fg-faint)] tabular">
          {Math.round(topic.progress.completion_percent)}%
        </span>
      </div>

      <div className="col-span-2 flex justify-end sm:col-span-1">
        <select
          value={localStatus}
          onChange={(e) => handleStatusChange(e.target.value as ProgressStatus)}
          disabled={updateProgress.isPending}
          className={cn(
            'h-8 rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-elevated)] px-2 text-xs font-medium outline-none',
            'focus-visible:border-signal-500 focus-visible:ring-2 focus-visible:ring-signal-500/30',
            localStatus === 'completed' && 'border-mastery-500/40 text-mastery-500',
          )}
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {updateProgress.isPending && <Loader2 className="ml-2 size-3.5 animate-spin text-[var(--fg-faint)]" />}
      </div>
    </div>
  )
}

function SubjectSection({ subject }: { subject: SubjectNode }) {
  const [open, setOpen] = React.useState(subject.order_index === 0)
  const weightage = weightageLabel(subject.weightage_min_percent, subject.weightage_max_percent)

  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--bg-elevated)]">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-4 px-4 py-3.5 text-left"
      >
        <ChevronDown className={cn('size-4 shrink-0 text-[var(--fg-faint)] transition-transform', open && 'rotate-180')} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-display text-base font-semibold">{subject.name}</h3>
            {!subject.is_official_section && (
              <Badge variant="outline" className="text-[10px]">
                Not an official section
              </Badge>
            )}
            {weightage && <Badge variant="signal">{weightage}</Badge>}
            {subject.priority && <Badge variant="default">{PRIORITY_LABEL[subject.priority]}</Badge>}
          </div>
          <p className="mt-1 text-xs text-[var(--fg-muted)]">
            {subject.progress_summary.completed}/{subject.progress_summary.total} topics complete
            {subject.progress_summary.in_progress > 0 && ` · ${subject.progress_summary.in_progress} in progress`}
          </p>
        </div>
        <div className="hidden w-32 items-center gap-2 sm:flex">
          <Progress value={subject.progress_summary.avg_completion_percent} />
          <span className="font-mono text-xs text-[var(--fg-faint)] tabular">
            {Math.round(subject.progress_summary.avg_completion_percent)}%
          </span>
        </div>
      </button>

      {open && (
        <div className="border-t border-[var(--border)]">
          {subject.topics.map((topic) => (
            <TopicRow key={topic.id} topic={topic} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function RoadmapPage() {
  const { data: subjects, isPending, isError } = useRoadmap()

  if (isPending) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-signal-500" />
      </div>
    )
  }

  if (isError || !subjects) {
    return <p className="text-sm text-risk-500">Couldn&rsquo;t load the roadmap. Try refreshing.</p>
  }

  const totals = subjects.reduce(
    (acc, s) => ({
      total: acc.total + s.progress_summary.total,
      completed: acc.completed + s.progress_summary.completed,
    }),
    { total: 0, completed: 0 },
  )

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6">
      <div>
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Roadmap</p>
        <div className="mt-1 flex items-baseline justify-between">
          <h1 className="font-display text-2xl font-semibold">The Master Roadmap</h1>
          <p className="font-mono text-sm text-[var(--fg-muted)] tabular">
            {totals.completed}/{totals.total} topics
          </p>
        </div>
        <p className="mt-1 text-sm text-[var(--fg-muted)]">
          7 official GATE DA sections + General Aptitude, ordered by dependency and priority. Change a topic&rsquo;s
          status below — completing one automatically schedules its 1/3/7/15/30/60/90-day revision ladder.
        </p>
      </div>

      <div className="flex flex-col gap-3">
        {subjects.map((subject) => (
          <SubjectSection key={subject.id} subject={subject} />
        ))}
      </div>
    </div>
  )
}
