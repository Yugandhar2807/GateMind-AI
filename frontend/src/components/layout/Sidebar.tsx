import { NavLink } from 'react-router-dom'
import {
  BarChart3,
  Bookmark,
  Bot,
  ClipboardList,
  LayoutDashboard,
  Layers,
  Map,
  Radar,
  Settings,
  StickyNote,
  Target,
} from 'lucide-react'

import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/roadmap', label: 'Roadmap', icon: Map },
  { to: '/practice', label: 'Practice', icon: Target },
  { to: '/mocks', label: 'Mock Tests', icon: ClipboardList },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/mentor', label: 'AI Mentor', icon: Bot },
  { to: '/flashcards', label: 'Flashcards', icon: Layers },
  { to: '/notes', label: 'Notes', icon: StickyNote },
  { to: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
]

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-[var(--border)] bg-[var(--bg-elevated)] lg:flex">
      <div className="flex h-16 items-center gap-2.5 px-5">
        <div className="flex size-8 items-center justify-center rounded-[var(--radius-md)] bg-signal-500 text-ink-950">
          <Radar className="size-4.5" strokeWidth={2.5} />
        </div>
        <span className="font-display text-base font-semibold tracking-tight">GateMind AI</span>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 overflow-y-auto px-3 py-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-signal-500/10 text-signal-500'
                  : 'text-[var(--fg-muted)] hover:bg-[var(--bg-inset)] hover:text-[var(--fg)]',
              )
            }
          >
            <Icon className="size-4.5" strokeWidth={2} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-[var(--radius-md)] px-3 py-2.5 text-sm font-medium transition-colors',
              isActive
                ? 'bg-signal-500/10 text-signal-500'
                : 'text-[var(--fg-muted)] hover:bg-[var(--bg-inset)] hover:text-[var(--fg)]',
            )
          }
        >
          <Settings className="size-4.5" strokeWidth={2} />
          Settings
        </NavLink>
      </div>
    </aside>
  )
}
