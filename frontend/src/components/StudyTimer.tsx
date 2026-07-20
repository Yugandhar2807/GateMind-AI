import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Coffee, Loader2, Play, Square } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useActiveSession, useStartSession, useStopSession } from '@/hooks/use-study'
import { cn } from '@/lib/utils'

function useElapsedSeconds(startISO: string | null | undefined) {
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    if (!startISO) return
    const t = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(t)
  }, [startISO])
  if (!startISO) return 0
  return Math.max(0, Math.floor((now - new Date(startISO).getTime()) / 1000))
}

function formatClock(sec: number) {
  const pad = (n: number) => String(n).padStart(2, '0')
  const h = Math.floor(sec / 3600)
  const m = Math.floor((sec % 3600) / 60)
  const s = sec % 60
  return h > 0 ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`
}

export function StudyTimer({ className }: { className?: string }) {
  const { data: active, isPending } = useActiveSession()
  const start = useStartSession()
  const stop = useStopSession()
  const [interruptions, setInterruptions] = useState(0)
  const [ending, setEnding] = useState(false)
  const [focus, setFocus] = useState(80)
  const [notes, setNotes] = useState('')
  const elapsed = useElapsedSeconds(active?.started_at)

  useEffect(() => {
    setInterruptions(active?.interruptions ?? 0)
    setEnding(false)
    setFocus(80)
    setNotes('')
  }, [active?.id, active?.interruptions])

  if (isPending) {
    return (
      <div className={cn('glass flex items-center justify-center rounded-[var(--radius-lg)] p-4', className)}>
        <Loader2 className="size-5 animate-spin text-signal-500" />
      </div>
    )
  }

  if (!active) {
    return (
      <div className={cn('glass flex flex-wrap items-center justify-between gap-3 rounded-[var(--radius-lg)] p-4', className)}>
        <div>
          <p className="text-sm font-semibold">Ready to focus?</p>
          <p className="text-xs text-[var(--fg-muted)]">Start a timed session — it saves to your study log automatically.</p>
        </div>
        <Button onClick={() => start.mutate({ session_type: 'learning' })} disabled={start.isPending}>
          {start.isPending ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />} Start Study
        </Button>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('rounded-[var(--radius-lg)] border border-signal-500/30 bg-signal-500/5 p-4', className)}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="relative flex size-2.5">
            <span className="absolute inline-flex size-full animate-ping rounded-full bg-signal-500 opacity-60" />
            <span className="relative inline-flex size-2.5 rounded-full bg-signal-500" />
          </span>
          <div>
            <p className="font-mono text-2xl font-semibold tabular">{formatClock(elapsed)}</p>
            <p className="text-xs text-[var(--fg-muted)]">
              {active.topic_name ? `Studying ${active.topic_name}` : 'Focus session in progress'}
            </p>
          </div>
        </div>
        {!ending && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setInterruptions((i) => i + 1)}
              className="inline-flex items-center gap-1 rounded-[var(--radius-md)] border border-[var(--border)] px-2.5 py-1.5 text-xs font-medium text-[var(--fg-muted)] hover:bg-[var(--bg-inset)]"
              title="Log an interruption"
            >
              <Coffee className="size-3.5" /> {interruptions}
            </button>
            <Button variant="destructive" size="sm" onClick={() => setEnding(true)}>
              <Square className="size-3.5" /> End
            </Button>
          </div>
        )}
      </div>

      <AnimatePresence>
        {ending && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="mt-4 flex flex-col gap-3 border-t border-[var(--border)] pt-4">
              <div>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="font-medium text-[var(--fg-muted)]">How focused were you?</span>
                  <span className="font-mono tabular text-signal-500">{focus}/100</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={focus}
                  onChange={(e) => setFocus(Number(e.target.value))}
                  className="w-full accent-[var(--color-signal-500)]"
                />
              </div>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Session notes (optional)"
                rows={2}
                className="w-full resize-none rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] p-2 text-sm outline-none focus-visible:border-signal-500"
              />
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => setEnding(false)}>
                  Keep going
                </Button>
                <Button
                  size="sm"
                  disabled={stop.isPending}
                  onClick={() =>
                    stop.mutate({ id: active.id, interruptions, focus_score: focus, notes: notes || null })
                  }
                >
                  {stop.isPending ? <Loader2 className="size-4 animate-spin" /> : null} Save session
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
