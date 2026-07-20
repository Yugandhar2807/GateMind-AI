import * as React from 'react'
import * as TabsPrimitive from '@radix-ui/react-tabs'

import { cn } from '@/lib/utils'

const Tabs = TabsPrimitive.Root

function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      data-slot="tabs-list"
      className={cn('inline-flex items-center gap-1 border-b border-[var(--border)]', className)}
      {...props}
    />
  )
}

function TabsTrigger({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.Trigger>) {
  return (
    <TabsPrimitive.Trigger
      data-slot="tabs-trigger"
      className={cn(
        'relative -mb-px border-b-2 border-transparent px-3 py-2 text-sm font-medium text-[var(--fg-muted)] transition-colors',
        'hover:text-[var(--fg)]',
        'data-[state=active]:border-signal-500 data-[state=active]:text-[var(--fg)]',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal-500/40 rounded-t-[var(--radius-sm)]',
        className,
      )}
      {...props}
    />
  )
}

function TabsContent({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.Content>) {
  return <TabsPrimitive.Content data-slot="tabs-content" className={cn('pt-4', className)} {...props} />
}

export { Tabs, TabsList, TabsTrigger, TabsContent }
