import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { CalendarClock, CheckCircle2, Clock, Flame, ListTodo, Target, Trophy } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { useMe } from '@/hooks/use-auth'
import { useDashboard } from '@/hooks/use-dashboard'

function formatMinutes(minutes: number) {
  if (minutes < 60) return `${minutes}m`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m ? `${h}h ${m}m` : `${h}h`
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
  iconClassName,
}: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  iconClassName?: string
}) {
  return (
    <Card>
      <CardContent className="flex flex-col gap-2 pt-5">
        <div className="flex items-center gap-2 text-[var(--fg-muted)]">
          <Icon className={`size-4 ${iconClassName ?? ''}`} />
          <span className="text-xs font-semibold tracking-wide uppercase">{label}</span>
        </div>
        <p className="font-mono text-2xl font-semibold tabular">{value}</p>
        {sub && <p className="text-xs text-[var(--fg-faint)]">{sub}</p>}
      </CardContent>
    </Card>
  )
}

const WEEKDAY_FORMATTER = new Intl.DateTimeFormat('en-US', { weekday: 'short' })

export default function DashboardPage() {
  const { data: user } = useMe()
  const { data: dash } = useDashboard()

  const chartData =
    dash?.weekly_series.map((d) => ({
      day: WEEKDAY_FORMATTER.format(new Date(d.date + 'T00:00:00')),
      minutes: d.minutes,
    })) ?? []

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-6">
      <div>
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Dashboard</p>
        <h1 className="mt-1 font-display text-2xl font-semibold">
          {user ? `Welcome back, ${user.full_name.split(' ')[0]}` : 'Welcome back'}
        </h1>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          icon={CalendarClock}
          label="Exam window"
          value={dash?.days_remaining != null ? `${dash.days_remaining}d` : '—'}
        />
        <StatCard
          icon={Flame}
          label="Current streak"
          value={`${dash?.current_streak_days ?? 0}d`}
          sub={dash ? `Longest: ${dash.longest_streak_days}d` : undefined}
          iconClassName="text-ember-500"
        />
        <StatCard icon={Target} label="Target score" value={dash?.target_score ? `${dash.target_score}/100` : '—'} />
        <StatCard icon={Trophy} label="Target AIR" value={dash?.target_air ? `Top ${dash.target_air}` : '—'} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>This week</CardTitle>
              <CardDescription>Study minutes logged per day</CardDescription>
            </div>
            <p className="font-mono text-sm text-[var(--fg-muted)] tabular">
              {formatMinutes(dash?.study_minutes_week ?? 0)} this week
            </p>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid vertical={false} stroke="var(--border)" />
                  <XAxis
                    dataKey="day"
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: 'var(--fg-faint)', fontSize: 12 }}
                  />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: 'var(--fg-faint)', fontSize: 12 }} width={32} />
                  <Tooltip
                    cursor={{ fill: 'var(--bg-inset)' }}
                    contentStyle={{
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    formatter={(value) => [`${value} min`, 'Studied']}
                  />
                  <Bar dataKey="minutes" fill="var(--color-signal-500)" radius={[4, 4, 0, 0]} maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Syllabus progress</CardTitle>
            <CardDescription>Weighted by topic importance</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-4 pt-0">
            <div>
              <div className="mb-1.5 flex items-baseline justify-between">
                <span className="font-mono text-xl font-semibold tabular">
                  {dash?.weightage_completed_percent ?? 0}%
                </span>
                <span className="text-xs text-[var(--fg-faint)]">weighted complete</span>
              </div>
              <Progress value={dash?.weightage_completed_percent ?? 0} />
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="size-3.5 text-mastery-500" />
                <span className="tabular">{dash?.topics_completed ?? 0}</span>
                <span className="text-[var(--fg-faint)]">done</span>
              </div>
              <div className="flex items-center gap-1.5">
                <ListTodo className="size-3.5 text-[var(--fg-faint)]" />
                <span className="tabular">{dash?.topics_not_started ?? 0}</span>
                <span className="text-[var(--fg-faint)]">not started</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock className="size-3.5 text-signal-500" />
                <span className="tabular">{dash?.topics_in_progress ?? 0}</span>
                <span className="text-[var(--fg-faint)]">in progress</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Badge variant="ember" className="px-1.5 py-0 text-[10px]">
                  {dash?.topics_needs_revision ?? 0}
                </Badge>
                <span className="text-[var(--fg-faint)]">need revision</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Upcoming revisions</CardTitle>
            <CardDescription>Spaced-repetition ladder (1/3/7/15/30/60/90 days)</CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            {!dash?.upcoming_revisions.length ? (
              <p className="text-sm text-[var(--fg-faint)]">
                None scheduled yet — complete a topic on the Roadmap to start its revision ladder.
              </p>
            ) : (
              <ul className="flex flex-col gap-2.5">
                {dash.upcoming_revisions.map((r, i) => (
                  <li key={i} className="flex items-center justify-between text-sm">
                    <div className="min-w-0">
                      <p className="truncate font-medium">{r.topic_name}</p>
                      <p className="truncate text-xs text-[var(--fg-faint)]">{r.subject_name}</p>
                    </div>
                    <Badge variant="default" className="shrink-0">
                      Day {r.interval_stage} · {new Date(r.scheduled_date + 'T00:00:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Weak &amp; strong topics</CardTitle>
            <CardDescription>From practice/mock accuracy</CardDescription>
          </CardHeader>
          <CardContent className="pt-0 text-sm text-[var(--fg-muted)]">
            {!dash?.weak_topics.length && !dash?.strong_topics.length ? (
              <p className="text-[var(--fg-faint)]">
                No accuracy data yet — this fills in once the{' '}
                <span className="font-medium text-[var(--fg)]">Practice Engine</span> (Phase 5) is live.
              </p>
            ) : (
              <p>Accuracy-based insights will render here.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming next</CardTitle>
        </CardHeader>
        <CardContent className="pt-0 text-sm text-[var(--fg-muted)]">
          Predicted marks and AIR need real practice/mock data to be honest rather than guessed — those arrive
          with the Practice Engine (<span className="font-semibold text-[var(--fg)]">Phase 5</span>) and Mock
          Engine (<span className="font-semibold text-[var(--fg)]">Phase 6</span>).
        </CardContent>
      </Card>
    </div>
  )
}
