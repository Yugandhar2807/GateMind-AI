import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '@/lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-[var(--radius-md)] text-sm font-semibold transition-all duration-150 disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg]:size-4 outline-none focus-visible:ring-2 focus-visible:ring-signal-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--bg)]",
  {
    variants: {
      variant: {
        default:
          'bg-signal-500 text-ink-950 shadow-[var(--shadow-glow)] hover:bg-signal-400 active:bg-signal-600',
        secondary:
          'bg-[var(--bg-inset)] text-[var(--fg)] border border-[var(--border)] hover:border-[var(--border-strong)]',
        ghost: 'text-[var(--fg-muted)] hover:bg-[var(--bg-inset)] hover:text-[var(--fg)]',
        outline:
          'border border-[var(--border)] text-[var(--fg)] hover:bg-[var(--bg-inset)] hover:border-[var(--border-strong)]',
        destructive: 'bg-risk-500 text-white hover:bg-risk-400',
        link: 'text-signal-500 underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-8 rounded-[var(--radius-sm)] px-3 text-xs',
        lg: 'h-12 rounded-[var(--radius-lg)] px-6 text-base',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

function Button({ className, variant, size, asChild = false, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : 'button'
  return <Comp data-slot="button" className={cn(buttonVariants({ variant, size, className }))} {...props} />
}

export { Button, buttonVariants }
