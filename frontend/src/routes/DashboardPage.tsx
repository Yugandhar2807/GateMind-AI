import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  ArrowUpRight,
  BrainCircuit,
  CalendarClock,
  CalendarDays,
  Clock,
  Flame,
  ListChecks,
  Repeat,
  Sparkles,
  Target,
  TrendingUp,
  Trophy,
} from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { StudyTimer } from '@/components/StudyTimer'
import { useMe } from '@/hooks/use-auth'
import { useDashboard } from '@/hooks/use-dashboard'

const WEEKDAY = new Intl.DateTimeFormat('en-US', { weekday: 'short' })
const SHORT_DATE = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' })

const DIFFICULTY_META: Record<string, { label: string; color: string }> = {
  easy: { label: 'Easy', color: 'var(--color-mastery-500)' },
  medium: { label: 'Medium', color: 'var(--color-signal-500)' },
  hard: { label: 'Hard', color: 'var(--color-ember-500)' },
  very_hard: { label: 'Very hard', color: 'var(--color-risk-500)' },
}

function fmtMinutes(min: number) {
  if (min <= 0) return '0m'
  if (min < 60) return `${min}m`
  const h = Math.floor(min / 60)
  const m = min % 60
  return m ? `${h}h ${m}m` : `${h}h`
}

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

function ProgressRing({ value, size = 132, stroke = 11 }: { value: number; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const clamped = Math.min(100, Math.max(0, value))
  const offset = circ - (clamped / 100) * circ
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--bg-inset)" strokeWidth={stroke} />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="var(--color-signal-500)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: 'easeOut' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-2xl font-semibold tabular">{value}%</span>
        <span className="text-[10px] tracking-wide text-[var(--fg-faint)] uppercase">complete</span>
      </div>
    </div>
  )
}

function Widget({
  title,
  icon: Icon,
  action,
  className,
  children,
}: {
  title: string
  icon: React.ElementType
  action?: React.ReactNode
  className?: string
  children: React.ReactNode
}) {
  return (
    <Card className={className}>
      <CardContent className="flex h-full flex-col gap-4 pt-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-[var(--fg-muted)]">
            <Icon className="size-4" />
            <span className="text-xs font-semibold tracking-wide uppercase">{title}</span>
          </div>
          {action}
        </div>
        {children}
      </CardContent>
    </Card>
  )
}

function HeroStat({
  icon: Icon,
  label,
  value,
  sub,
  tone = 'signal',
}: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  tone?: 'signal' | 'ember' | 'mastery'
}) {
  const toneClass =
    tone === 'ember' ? 'text-ember-500' : tone === 'mastery' ? 'text-mastery-500' : 'text-signal-500'
  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
      <div className="flex items-center gap-1.5 text-[var(--fg-muted)]">
        <Icon className={`size-3.5 ${toneClass}`} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">{label}</span>
      </div>
      <p className="mt-1.5 truncate font-display text-lg font-semibold">{value}</p>
      {sub && <p className="truncate text-xs text-[var(--fg-faint)]">{sub}</p>}
    </div>
  )
}

function EmptyState({ children, to, cta }: { children: React.ReactNode; to?: string; cta?: string }) {
  return (
    <div className="flex flex-1 flex-col items-start justify-center gap-2 py-2 text-sm text-[var(--fg-muted)]">
      <p>{children}</p>
      {to && cta && (
        <Link to={to} className="inline-flex items-center gap-1 text-xs font-semibold text-signal-500 hover:underline">
          {cta} <ArrowUpRight className="size-3.5" />
        </Link>
      )}
    </div>
  )
}

export default function DashboardPage() {
  const { data: user } = useMe()
  const { data: dash, isPending } = useDashboard()

  if (isPending || !dash) {
    return (
      <div className="mx-auto max-w-6xl">
        <div className="h-40 animate-pulse rounded-[var(--radius-xl)] bg-[var(--bg-inset)]" />
      </div>
    )
  }

  const firstName = user?.full_name.split(' ')[0] ?? dash.greeting_name
  const topTask = dash.today_tasks[0]
  const chartData = dash.weekly_series.map((d) => ({
    day: WEEKDAY.format(new Date(d.date + 'T00:00:00')),
    minutes: d.minutes,
  }))
  const diffData = Object.entries(dash.difficulty_distribution)
    .filter(([, n]) => n > 0)
    .map(([k, n]) => ({ key: k, name: DIFFICULTY_META[k]?.label ?? k, value: n }))

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-5">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass relative overflow-hidden rounded-[var(--radius-xl)] p-6"
      >
        <div
          className="pointer-events-none absolute -top-24 -right-16 size-64 rounded-full opacity-30 blur-3xl"
          style={{ background: 'radial-gradient(circle, var(--color-signal-500), transparent 70%)' }}
        />
        <div className="relative flex flex-col gap-5">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Dashboard</p>
              <h1 className="mt-1 font-display text-2xl font-semibold sm:text-3xl">
                {greeting()}, {firstName} <span className="align-middle">👋</span>
              </h1>
            </div>
            {dash.days_remaining != null && (
              <div className="text-right">
                <p className="font-mono text-3xl font-semibold tabular text-signal-500">{dash.days_remaining}</p>
                <p className="text-xs tracking-wide text-[var(--fg-faint)] uppercase">days to GATE DA</p>
              </div>
            )}
          </div>

          <StudyTimer />

          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            <HeroStat
              icon={Target}
              label="Today's target"
              value={topTask ? topTask.topic_name : 'Pick a topic'}
              sub={topTask ? `${topTask.subject_name} · ${topTask.kind === 'revision' ? 'revision' : 'in progress'}` : 'Nothing queued yet'}
            />
            <HeroStat
              icon={Repeat}
              label="Revision due"
              value={`${dash.revision_due_today} ${dash.revision_due_today === 1 ? 'topic' : 'topics'}`}
              sub={dash.revision_due_today ? 'due today' : 'all caught up'}
              tone="ember"
            />
            <HeroStat
              icon={Flame}
              label="Current streak"
              value={`${dash.current_streak_days} ${dash.current_streak_days === 1 ? 'day' : 'days'}`}
              sub={`Longest: ${dash.longest_streak_days}d`}
              tone="ember"
            />
            <HeroStat
              icon={Trophy}
              label="AIR target"
              value={dash.target_air ? `Top ${dash.target_air}` : 'Set a goal'}
              sub={dash.has_mock_data ? 'prediction live' : 'prediction after 1st mock'}
              tone="mastery"
            />
          </div>
        </div>
      </motion.div>

      {/* Row: progress ring + weekly hours + difficulty */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <Widget title="Syllabus progress" icon={BrainCircuit}>
          <div className="flex items-center gap-5">
            <ProgressRing value={dash.weightage_completed_percent} />
            <div className="flex flex-col gap-2 text-sm">
              <Row dot="var(--color-mastery-500)" label="Completed" value={dash.topics_completed} />
              <Row dot="var(--color-signal-500)" label="In progress" value={dash.topics_in_progress} />
              <Row dot="var(--color-ember-500)" label="Needs revision" value={dash.topics_needs_revision} />
              <Row dot="var(--bg-inset)" label="Not started" value={dash.topics_not_started} />
            </div>
          </div>
          <p className="text-xs text-[var(--fg-faint)]">
            {dash.topics_completed}/{dash.topics_total} topics · weighted by importance
          </p>
        </Widget>

        <Widget
          title="This week"
          icon={Clock}
          action={<span className="font-mono text-xs text-[var(--fg-muted)] tabular">{fmtMinutes(dash.study_minutes_week)}</span>}
        >
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 4, right: 4, left: -22, bottom: 0 }}>
                <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: 'var(--fg-faint)', fontSize: 11 }} />
                <YAxis tickLine={false} axisLine={false} tick={{ fill: 'var(--fg-faint)', fontSize: 11 }} width={30} />
                <Tooltip
                  cursor={{ fill: 'var(--bg-inset)' }}
                  contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                  formatter={(v) => [`${v} min`, 'Studied']}
                />
                <Bar dataKey="minutes" fill="var(--color-signal-500)" radius={[4, 4, 0, 0]} maxBarSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between text-xs text-[var(--fg-faint)]">
            <span>Today: <span className="font-medium text-[var(--fg)]">{fmtMinutes(dash.study_minutes_today)}</span></span>
            <span>Month: <span className="font-medium text-[var(--fg)]">{fmtMinutes(dash.study_minutes_month)}</span></span>
          </div>
        </Widget>

        <Widget title="Difficulty mix" icon={Sparkles}>
          <div className="flex items-center gap-4">
            <div className="h-32 w-32 shrink-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={diffData} dataKey="value" nameKey="name" innerRadius={38} outerRadius={58} paddingAngle={2} stroke="none">
                    {diffData.map((d) => (
                      <Cell key={d.key} fill={DIFFICULTY_META[d.key]?.color ?? 'var(--color-ink-400)'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                    formatter={(v, n) => [`${v} topics`, n]}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-col gap-1.5 text-sm">
              {diffData.map((d) => (
                <Row key={d.key} dot={DIFFICULTY_META[d.key]?.color} label={d.name} value={d.value} />
              ))}
            </div>
          </div>
        </Widget>
      </div>

      {/* Row: today's tasks + upcoming revisions */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Widget
          title="Today's plan"
          icon={ListChecks}
          action={<Link to="/roadmap" className="text-xs font-semibold text-signal-500 hover:underline">Roadmap</Link>}
        >
          {dash.today_tasks.length === 0 ? (
            <EmptyState to="/roadmap" cta="Go to roadmap">
              Nothing queued for today. Start a topic or complete one to schedule revisions.
            </EmptyState>
          ) : (
            <ul className="flex flex-col gap-2">
              {dash.today_tasks.map((t) => (
                <li key={`${t.kind}-${t.topic_id}`}>
                  <Link
                    to={`/roadmap/topics/${t.topic_id}`}
                    className="flex items-center justify-between gap-2 rounded-[var(--radius-md)] border border-[var(--border)] px-3 py-2 text-sm hover:border-signal-500/50 hover:bg-[var(--bg-inset)]"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-medium">{t.topic_name}</p>
                      <p className="truncate text-xs text-[var(--fg-faint)]">{t.subject_name}</p>
                    </div>
                    <Badge variant={t.kind === 'revision' ? 'ember' : 'default'} className="shrink-0 capitalize">
                      {t.kind === 'revision' ? 'Revise' : 'In progress'}
                    </Badge>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Widget>

        <Widget title="Upcoming revisions" icon={CalendarClock}>
          {dash.upcoming_revisions.length === 0 ? (
            <EmptyState to="/roadmap" cta="Complete a topic">
              No revisions scheduled yet — completing a topic starts its 1/3/7/15/30/60/90-day ladder.
            </EmptyState>
          ) : (
            <ul className="flex flex-col gap-2">
              {dash.upcoming_revisions.slice(0, 6).map((r) => (
                <li key={`${r.topic_id}-${r.interval_day}`} className="flex items-center justify-between gap-2 text-sm">
                  <div className="min-w-0">
                    <p className="truncate font-medium">{r.topic_name}</p>
                    <p className="truncate text-xs text-[var(--fg-faint)]">{r.subject_name}</p>
                  </div>
                  <Badge variant={r.overdue ? 'risk' : 'default'} className="shrink-0">
                    {r.overdue ? 'Overdue · ' : ''}
                    {SHORT_DATE.format(new Date(r.due_date + 'T00:00:00'))}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Widget>
      </div>

      {/* Row: subject completion */}
      <Widget title="Subject completion" icon={ListChecks}>
        <div className="grid grid-cols-1 gap-x-8 gap-y-3 sm:grid-cols-2">
          {dash.subject_completion.map((s) => (
            <div key={s.subject_id}>
              <div className="mb-1 flex items-center justify-between gap-2 text-sm">
                <Link to="/roadmap" className="min-w-0 truncate font-medium hover:text-signal-500">
                  {s.name}
                  {!s.is_official_section && (
                    <span className="ml-1.5 align-middle text-[10px] text-[var(--fg-faint)]">(optional)</span>
                  )}
                </Link>
                <span className="shrink-0 font-mono text-xs text-[var(--fg-muted)] tabular">
                  {s.completed}/{s.total}
                  {s.weightage_max_percent != null && (
                    <span className="ml-1.5 text-[var(--fg-faint)]">· {s.weightage_max_percent}%</span>
                  )}
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-[var(--bg-inset)]">
                <motion.div
                  className="h-full rounded-full bg-signal-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${s.percent}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                />
              </div>
            </div>
          ))}
        </div>
      </Widget>

      {/* Row: forecast + last session + insights */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        <Widget title="Study forecast" icon={TrendingUp}>
          <div className="flex flex-col gap-3">
            <div>
              <p className="font-display text-2xl font-semibold">{dash.remaining_hours}h</p>
              <p className="text-xs text-[var(--fg-faint)]">estimated study left across remaining topics</p>
            </div>
            <div className="border-t border-[var(--border)] pt-3">
              {dash.predicted_completion_date ? (
                <>
                  <p className="font-medium">
                    {new Date(dash.predicted_completion_date + 'T00:00:00').toLocaleDateString(undefined, {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric',
                    })}
                  </p>
                  <p className="text-xs text-[var(--fg-faint)]">projected syllabus completion at your current pace</p>
                </>
              ) : (
                <p className="text-sm text-[var(--fg-muted)]">
                  Complete a few topics and I'll project your finish date from your real pace.
                </p>
              )}
            </div>
          </div>
        </Widget>

        <Widget title="Last session" icon={CalendarDays}>
          {dash.last_session ? (
            <div className="flex flex-col gap-1">
              <p className="font-display text-2xl font-semibold">{fmtMinutes(dash.last_session.duration_minutes)}</p>
              <p className="text-sm text-[var(--fg-muted)]">
                {dash.last_session.topic_name ?? 'Focus session'}
                {dash.last_session.subject_name ? ` · ${dash.last_session.subject_name}` : ''}
              </p>
              <p className="text-xs text-[var(--fg-faint)]">
                {new Date(dash.last_session.started_at).toLocaleString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  hour: 'numeric',
                  minute: '2-digit',
                })}
              </p>
            </div>
          ) : (
            <EmptyState>Start a study session from the timer above — your history shows up here.</EmptyState>
          )}
        </Widget>

        <Widget title="Weak & strong" icon={Target}>
          {!dash.has_accuracy_data ? (
            <EmptyState to="/practice" cta="Practice questions">
              Accuracy insights unlock once you answer practice questions and mock tests.
            </EmptyState>
          ) : (
            <div className="flex flex-col gap-3 text-sm">
              <div>
                <p className="mb-1 text-xs font-semibold text-risk-500 uppercase">Needs work</p>
                {dash.weak_topics.map((t) => (
                  <div key={t.topic_id} className="flex justify-between">
                    <span className="truncate">{t.topic_name}</span>
                    <span className="font-mono tabular text-[var(--fg-muted)]">{t.accuracy_percent}%</span>
                  </div>
                ))}
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold text-mastery-500 uppercase">Strongest</p>
                {dash.strong_topics.map((t) => (
                  <div key={t.topic_id} className="flex justify-between">
                    <span className="truncate">{t.topic_name}</span>
                    <span className="font-mono tabular text-[var(--fg-muted)]">{t.accuracy_percent}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Widget>
      </div>
    </div>
  )
}

function Row({ dot, label, value }: { dot?: string; label: string; value: number | string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="size-2.5 rounded-full" style={{ background: dot ?? 'var(--bg-inset)' }} />
      <span className="tabular font-medium">{value}</span>
      <span className="text-[var(--fg-faint)]">{label}</span>
    </div>
  )
}
