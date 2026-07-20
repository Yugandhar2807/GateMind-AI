import { motion } from 'framer-motion'
import { Radar } from 'lucide-react'
import type { ReactNode } from 'react'

import { ThemeToggle } from '@/components/theme-toggle'

const EXAM_DATE = new Date('2027-02-07T00:00:00')

function daysRemaining() {
  const diff = EXAM_DATE.getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden overflow-hidden bg-ink-950 lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div
          className="pointer-events-none absolute inset-0 opacity-40"
          style={{
            backgroundImage:
              'linear-gradient(rgba(23,205,182,0.14) 1px, transparent 1px), linear-gradient(90deg, rgba(23,205,182,0.14) 1px, transparent 1px)',
            backgroundSize: '48px 48px',
          }}
        />
        <div className="pointer-events-none absolute -top-32 -right-32 h-96 w-96 rounded-full bg-signal-500/20 blur-[120px]" />

        <div className="relative flex items-center gap-2.5 text-ink-50">
          <div className="flex size-9 items-center justify-center rounded-[var(--radius-md)] bg-signal-500 text-ink-950">
            <Radar className="size-5" strokeWidth={2.5} />
          </div>
          <span className="font-display text-lg font-semibold tracking-tight">GateMind AI</span>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="relative max-w-md"
        >
          <p className="font-mono text-xs tracking-[0.2em] text-signal-400 uppercase">GATE DA · February 2027</p>
          <h1 className="mt-4 font-display text-4xl leading-[1.1] font-semibold text-ink-50">
            Mission control for your rank.
          </h1>
          <p className="mt-4 text-sm leading-relaxed text-ink-400">
            Every topic, PYQ, mock, and revision cycle tracked against a target Top&nbsp;50 AIR &mdash; built
            around your actual office hours, not an idealized study schedule.
          </p>

          <div className="mt-8 flex items-center gap-6 border-t border-ink-800 pt-6">
            <div>
              <p className="font-mono text-3xl font-semibold text-ink-50 tabular">{daysRemaining()}</p>
              <p className="mt-1 text-xs text-ink-500">days to exam</p>
            </div>
            <div className="h-8 w-px bg-ink-800" />
            <div>
              <p className="font-mono text-3xl font-semibold text-ink-50 tabular">103</p>
              <p className="mt-1 text-xs text-ink-500">tracked topics</p>
            </div>
            <div className="h-8 w-px bg-ink-800" />
            <div>
              <p className="font-mono text-3xl font-semibold text-ink-50 tabular">7+1</p>
              <p className="mt-1 text-xs text-ink-500">syllabus sections</p>
            </div>
          </div>
        </motion.div>

        <p className="relative font-mono text-[11px] text-ink-600">GateMind AI &middot; local-first &middot; your data never leaves this machine</p>
      </div>

      <div className="flex flex-col">
        <div className="flex justify-between p-6 lg:justify-end">
          <div className="flex items-center gap-2 lg:hidden">
            <div className="flex size-8 items-center justify-center rounded-[var(--radius-md)] bg-signal-500 text-ink-950">
              <Radar className="size-4" strokeWidth={2.5} />
            </div>
            <span className="font-display text-base font-semibold">GateMind AI</span>
          </div>
          <ThemeToggle />
        </div>

        <div className="flex flex-1 items-center justify-center p-6 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
            className="w-full max-w-sm"
          >
            {children}
          </motion.div>
        </div>
      </div>
    </div>
  )
}
