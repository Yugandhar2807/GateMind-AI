import * as React from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Clock, ExternalLink, Loader2, Plus, Star, Target, Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Markdown } from '@/components/Markdown'
import { BookmarkButton } from '@/components/BookmarkButton'
import { cn } from '@/lib/utils'
import { useTopicDetail } from '@/hooks/use-topic'
import { useUpdateTopicProgress } from '@/hooks/use-roadmap'
import { useCreateNote, useDeleteNote, useNotes } from '@/hooks/use-notes'
import type { Difficulty, ProgressStatus } from '@/types/roadmap'

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
const STATUS_OPTIONS: { value: ProgressStatus; label: string }[] = [
  { value: 'not_started', label: 'Not started' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'needs_revision', label: 'Needs revision' },
]

function EmptySection({ label }: { label: string }) {
  return (
    <p className="rounded-[var(--radius-md)] border border-dashed border-[var(--border)] px-4 py-6 text-center text-sm text-[var(--fg-faint)]">
      {label} hasn&rsquo;t been written for this topic yet.
    </p>
  )
}

const RANK_META: Record<string, { label: string; stars: string; cls: string }> = {
  gold: { label: 'Gold', stars: '★★★★★', cls: 'border-ember-500/40 bg-ember-500/10 text-ember-500' },
  silver: { label: 'Silver', stars: '★★★★', cls: 'border-[var(--border)] bg-[var(--bg-inset)] text-[var(--fg-muted)]' },
  bronze: { label: 'Bronze', stars: '★★★', cls: 'border-ember-400/30 bg-ember-400/10 text-ember-400' },
}

function ResourcesTab({ topicId }: { topicId: string }) {
  const { data } = useTopicDetail(topicId)
  const resources = data?.resources ?? []

  if (!resources.length) return <EmptySection label="No resources are linked to this topic" />

  return (
    <div className="flex flex-col gap-3">
      {resources.map((r) => {
        const rank = r.ranking ? RANK_META[r.ranking] : null
        const meta = [r.organization || r.platform, r.instructor, r.year ? String(r.year) : null]
          .filter(Boolean)
          .join(' · ')
        const extra = [
          r.duration_minutes ? `${r.duration_minutes} min` : null,
          r.rating ? `★ ${r.rating}` : null,
          r.language && r.language !== 'English' ? r.language : null,
        ]
          .filter(Boolean)
          .join(' · ')
        return (
          <Card key={r.id}>
            <CardContent className="flex items-start justify-between gap-3 py-4">
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  {rank && (
                    <span
                      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${rank.cls}`}
                      title={`${rank.label}-tier resource`}
                    >
                      {rank.stars}
                    </span>
                  )}
                  {r.url ? (
                    <a
                      href={r.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium hover:text-signal-500 hover:underline"
                    >
                      {r.title}
                    </a>
                  ) : (
                    <p className="font-medium">{r.title}</p>
                  )}
                  <Badge variant="outline" className="text-[10px] capitalize">
                    {r.resource_type.replace(/_/g, ' ')}
                  </Badge>
                  {r.needs_review && (
                    <Badge variant="ember" className="text-[10px]">
                      Needs review
                    </Badge>
                  )}
                </div>
                {(meta || extra) && (
                  <p className="mt-1 text-xs text-[var(--fg-muted)]">
                    {meta}
                    {meta && extra ? ' · ' : ''}
                    {extra}
                  </p>
                )}
                {(r.why_recommended || r.description) && (
                  <p className="mt-1.5 text-xs text-[var(--fg-faint)]">{r.why_recommended || r.description}</p>
                )}
              </div>
              <div className="flex shrink-0 items-center gap-1">
                <BookmarkButton bookmarkType="resource" targetId={r.id} />
                {r.url && (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label="Open resource"
                    className="inline-flex size-7 items-center justify-center rounded-[var(--radius-sm)] text-[var(--fg-faint)] hover:bg-[var(--bg-inset)] hover:text-signal-500"
                  >
                    <ExternalLink className="size-4" />
                  </a>
                )}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

function NotesTab({ topicId }: { topicId: string }) {
  const { data: notes, isPending } = useNotes(topicId)
  const createNote = useCreateNote()
  const deleteNote = useDeleteNote()
  const [draft, setDraft] = React.useState('')

  function handleAdd() {
    if (!draft.trim()) return
    createNote.mutate(
      { title: draft.slice(0, 60), content_markdown: draft, topic_id: topicId },
      { onSuccess: () => setDraft('') },
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Write a note about this topic (Markdown + LaTeX supported)..."
          rows={3}
        />
        <Button size="sm" className="self-end" onClick={handleAdd} disabled={createNote.isPending || !draft.trim()}>
          {createNote.isPending ? <Loader2 className="animate-spin" /> : <Plus />}
          Add note
        </Button>
      </div>

      {isPending ? (
        <Loader2 className="size-4 animate-spin text-[var(--fg-faint)]" />
      ) : !notes?.length ? (
        <EmptySection label="No notes" />
      ) : (
        <div className="flex flex-col gap-2.5">
          {notes.map((note) => (
            <Card key={note.id}>
              <CardContent className="flex items-start justify-between gap-3 py-4">
                <Markdown className="flex-1">{note.content_markdown}</Markdown>
                <button
                  type="button"
                  onClick={() => deleteNote.mutate(note.id)}
                  className="shrink-0 text-[var(--fg-faint)] hover:text-risk-500"
                  aria-label="Delete note"
                >
                  <Trash2 className="size-4" />
                </button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

export default function TopicPage() {
  const { topicId } = useParams<{ topicId: string }>()
  const id = topicId
  const { data: topic, isPending, isError } = useTopicDetail(id)
  const updateProgress = useUpdateTopicProgress()
  const [status, setStatus] = React.useState<ProgressStatus>('not_started')

  React.useEffect(() => {
    if (topic) setStatus(topic.progress.status)
  }, [topic?.progress.status])

  if (isPending) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-signal-500" />
      </div>
    )
  }

  if (isError || !topic || !id) {
    return <p className="text-sm text-risk-500">Couldn&rsquo;t load this topic.</p>
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div>
        <Link
          to="/roadmap"
          className="inline-flex items-center gap-1.5 text-sm text-[var(--fg-muted)] hover:text-[var(--fg)]"
        >
          <ArrowLeft className="size-3.5" /> Roadmap
        </Link>

        <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">{topic.subject_name}</p>
            <h1 className="mt-1 font-display text-2xl font-semibold">{topic.name}</h1>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {topic.difficulty && (
                <Badge variant={DIFFICULTY_VARIANT[topic.difficulty]}>{DIFFICULTY_LABEL[topic.difficulty]}</Badge>
              )}
              {topic.importance_1to5 != null && (
                <Badge variant="signal">
                  <Star className="size-3" /> Importance {topic.importance_1to5}/5
                </Badge>
              )}
              {topic.estimated_hours != null && (
                <Badge variant="default">
                  <Clock className="size-3" /> ~{topic.estimated_hours}h
                </Badge>
              )}
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <Link to={`/practice?topic_id=${id}`}>
              <Button variant="secondary" size="sm">
                <Target className="size-4" /> Practice
              </Button>
            </Link>
            <BookmarkButton
              bookmarkType="topic"
              targetId={id}
              className="size-9 border border-[var(--border)]"
            />
            <select
              value={status}
              onChange={(e) => {
                const next = e.target.value as ProgressStatus
                setStatus(next)
                updateProgress.mutate({ topicId: id, payload: { status: next } })
              }}
              className={cn(
                'h-9 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm font-medium outline-none',
                'focus-visible:border-signal-500 focus-visible:ring-2 focus-visible:ring-signal-500/30',
                status === 'completed' && 'border-mastery-500/40 text-mastery-500',
              )}
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2">
          <Progress value={topic.progress.completion_percent} className="max-w-xs" />
          <span className="font-mono text-xs text-[var(--fg-faint)] tabular">
            {Math.round(topic.progress.completion_percent)}%
          </span>
        </div>

        {topic.prerequisites_text && (
          <p className="mt-3 text-xs text-[var(--fg-faint)]">
            <span className="font-semibold text-[var(--fg-muted)]">Prerequisites:</span> {topic.prerequisites_text}
          </p>
        )}
        {topic.pyq_frequency && (
          <p className="mt-1 text-xs text-[var(--fg-faint)]">
            <span className="font-semibold text-[var(--fg-muted)]">PYQ pattern:</span> {topic.pyq_frequency}
          </p>
        )}
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="cheatsheet">Cheat Sheet</TabsTrigger>
          <TabsTrigger value="mistakes">Common Mistakes</TabsTrigger>
          <TabsTrigger value="resources">Resources ({topic.resources.length})</TabsTrigger>
          <TabsTrigger value="notes">Notes</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="flex flex-col gap-5">
          <div>
            <h4 className="mb-2 text-xs font-semibold tracking-wide text-[var(--fg-muted)] uppercase">Introduction</h4>
            {topic.introduction ? <Markdown>{topic.introduction}</Markdown> : <EmptySection label="An introduction" />}
          </div>
          <div>
            <h4 className="mb-2 text-xs font-semibold tracking-wide text-[var(--fg-muted)] uppercase">Theory</h4>
            {topic.theory_markdown ? <Markdown>{topic.theory_markdown}</Markdown> : <EmptySection label="Theory content" />}
          </div>
          <div>
            <h4 className="mb-2 text-xs font-semibold tracking-wide text-[var(--fg-muted)] uppercase">Formulas</h4>
            {topic.formulas_markdown ? (
              <Markdown>{topic.formulas_markdown}</Markdown>
            ) : (
              <EmptySection label="A formula sheet" />
            )}
          </div>
          <div>
            <h4 className="mb-2 text-xs font-semibold tracking-wide text-[var(--fg-muted)] uppercase">
              Real-world applications
            </h4>
            {topic.real_world_applications ? (
              <Markdown>{topic.real_world_applications}</Markdown>
            ) : (
              <EmptySection label="Real-world applications" />
            )}
          </div>
        </TabsContent>

        <TabsContent value="cheatsheet">
          {topic.cheat_sheet_markdown ? (
            <Markdown>{topic.cheat_sheet_markdown}</Markdown>
          ) : (
            <EmptySection label="A cheat sheet" />
          )}
        </TabsContent>

        <TabsContent value="mistakes">
          {topic.common_mistakes_markdown ? (
            <Markdown>{topic.common_mistakes_markdown}</Markdown>
          ) : (
            <EmptySection label="Common mistakes" />
          )}
        </TabsContent>

        <TabsContent value="resources">
          <ResourcesTab topicId={id} />
        </TabsContent>

        <TabsContent value="notes">
          <NotesTab topicId={id} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
