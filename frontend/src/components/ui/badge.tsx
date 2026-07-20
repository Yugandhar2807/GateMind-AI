import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap',
  {
    variants: {
      variant: {
        default: 'border-[var(--border)] bg-[var(--bg-inset)] text-[var(--fg-muted)]',
        signal: 'border-signal-500/30 bg-signal-500/10 text-signal-500',
        mastery: 'border-mastery-500/30 bg-mastery-500/10 text-mastery-500',
        ember: 'border-ember-500/30 bg-ember-400/10 text-ember-500',
        risk: 'border-risk-500/30 bg-risk-500/10 text-risk-500',
        outline: 'border-[var(--border)] text-[var(--fg)]',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <span data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
