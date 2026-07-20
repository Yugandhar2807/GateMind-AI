import * as React from 'react'

import { cn } from '@/lib/utils'

function Input({ className, type, ...props }: React.ComponentProps<'input'>) {
  return (
    <input
      type={type}
      data-slot="input"
      className={cn(
        'flex h-10 w-full rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3.5 py-2 text-sm text-[var(--fg)] placeholder:text-[var(--fg-faint)] transition-colors outline-none',
        'focus-visible:border-signal-500 focus-visible:ring-2 focus-visible:ring-signal-500/30',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'aria-invalid:border-risk-500 aria-invalid:ring-risk-500/30',
        className,
      )}
      {...props}
    />
  )
}

export { Input }
