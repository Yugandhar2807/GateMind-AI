import type { LucideIcon } from 'lucide-react'

import { Card, CardContent } from '@/components/ui/card'

interface ComingSoonProps {
  icon: LucideIcon
  title: string
  phase: string
  description: string
}

export function ComingSoon({ icon: Icon, title, phase, description }: ComingSoonProps) {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="max-w-md text-center">
        <CardContent className="flex flex-col items-center gap-4 py-12">
          <div className="flex size-14 items-center justify-center rounded-full bg-signal-500/10">
            <Icon className="size-6 text-signal-500" />
          </div>
          <div>
            <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">{phase}</p>
            <h2 className="mt-1.5 font-display text-xl font-semibold">{title}</h2>
          </div>
          <p className="text-sm text-[var(--fg-muted)]">{description}</p>
        </CardContent>
      </Card>
    </div>
  )
}
