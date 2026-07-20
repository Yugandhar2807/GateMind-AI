import { Flame, LogOut, Settings, User as UserIcon } from 'lucide-react'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ThemeToggle } from '@/components/theme-toggle'
import { useAuthStore } from '@/stores/auth-store'
import { useLogout } from '@/hooks/use-auth'
import { Link } from 'react-router-dom'

const EXAM_DATE = new Date('2027-02-07T00:00:00')

function daysRemaining() {
  const diff = EXAM_DATE.getTime() - Date.now()
  return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)))
}

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

export function Topbar() {
  const user = useAuthStore((s) => s.user)
  const logout = useLogout()

  return (
    <header className="glass sticky top-0 z-40 flex h-16 items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-2">
        <span className="font-mono text-xs tracking-wide text-[var(--fg-faint)] uppercase">GATE DA 2027</span>
        <span className="font-mono text-sm font-semibold text-signal-500 tabular">{daysRemaining()}d</span>
      </div>

      <div className="flex items-center gap-1.5">
        {user && user.current_streak_days > 0 && (
          <div className="mr-1.5 flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--bg-inset)] px-3 py-1.5 text-sm font-semibold">
            <Flame className="size-4 text-ember-500" />
            <span className="tabular">{user.current_streak_days}</span>
          </div>
        )}

        <ThemeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger className="ml-1 outline-none">
            <Avatar>
              {user?.photo_url && <AvatarImage src={user.photo_url} alt={user.full_name} />}
              <AvatarFallback>{user ? initials(user.full_name) : '·'}</AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>{user?.full_name ?? 'Account'}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <Link to="/settings">
                <UserIcon className="size-4" /> Profile
              </Link>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <Link to="/settings">
                <Settings className="size-4" /> Settings
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onSelect={() => logout()}>
              <LogOut className="size-4" /> Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
