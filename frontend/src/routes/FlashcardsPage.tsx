import * as React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, Layers, Loader2, RotateCcw, Star, X } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Markdown } from '@/components/Markdown'
import { cn } from '@/lib/utils'
import { useDueFlashcards, useReviewFlashcard, useUpdateFlashcardState } from '@/hooks/use-flashcards'

export default function FlashcardsPage() {
  const { data: cards, isPending } = useDueFlashcards()
  const review = useReviewFlashcard()
  const updateState = useUpdateFlashcardState()
  const [index, setIndex] = React.useState(0)
  const [flipped, setFlipped] = React.useState(false)
  const [sessionDone, setSessionDone] = React.useState(0)

  const current = cards?.[index]

  function handleReview(correct: boolean) {
    if (!current) return
    review.mutate({ id: current.id, correct })
    setSessionDone((n) => n + 1)
    setFlipped(false)
    setIndex((i) => i + 1)
  }

  if (isPending) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-signal-500" />
      </div>
    )
  }

  const total = cards?.length ?? 0
  const isComplete = !current

  return (
    <div className="mx-auto flex max-w-xl flex-col items-center gap-6">
      <div className="w-full">
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Flashcards</p>
        <div className="mt-1 flex items-baseline justify-between">
          <h1 className="font-display text-2xl font-semibold">Today&rsquo;s review</h1>
          {total > 0 && (
            <p className="font-mono text-sm text-[var(--fg-muted)] tabular">
              {Math.min(sessionDone + 1, total)}/{total}
            </p>
          )}
        </div>
      </div>

      {total === 0 ? (
        <Card className="w-full">
          <div className="flex flex-col items-center gap-3 py-14 text-center">
            <Layers className="size-8 text-[var(--fg-faint)]" />
            <p className="text-sm text-[var(--fg-muted)]">Nothing due right now. Come back tomorrow.</p>
          </div>
        </Card>
      ) : isComplete ? (
        <Card className="w-full">
          <div className="flex flex-col items-center gap-3 py-14 text-center">
            <CheckCircle2 className="size-8 text-mastery-500" />
            <p className="text-sm font-medium">All caught up &mdash; {sessionDone} card{sessionDone === 1 ? '' : 's'} reviewed.</p>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => {
                setIndex(0)
                setSessionDone(0)
                setFlipped(false)
              }}
            >
              <RotateCcw /> Review again
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <AnimatePresence mode="wait">
            <motion.div
              key={current.id}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.2 }}
              className="relative w-full"
              style={{ perspective: 1200 }}
            >
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  updateState.mutate({ id: current.id, payload: { is_favorite: !current.is_favorite } })
                }}
                aria-label={current.is_favorite ? 'Unfavorite' : 'Favorite'}
                aria-pressed={current.is_favorite}
                className="absolute top-2 right-2 z-10 flex size-8 items-center justify-center rounded-full text-[var(--fg-faint)] hover:bg-[var(--bg-inset)] hover:text-ember-500"
              >
                <Star className={cn('size-4', current.is_favorite && 'fill-ember-500 text-ember-500')} />
              </button>
              <button
                type="button"
                onClick={() => setFlipped((f) => !f)}
                className="block w-full text-left"
                aria-label="Flip card"
              >
                <motion.div
                  animate={{ rotateY: flipped ? 180 : 0 }}
                  transition={{ duration: 0.4 }}
                  style={{ transformStyle: 'preserve-3d' }}
                  className="relative min-h-64"
                >
                  <Card
                    className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-8 text-center"
                    style={{ backfaceVisibility: 'hidden' }}
                  >
                    <Badge variant="default">{current.subject_name}</Badge>
                    <p className="font-display text-lg font-medium">{current.front_markdown}</p>
                    <p className="text-xs text-[var(--fg-faint)]">Click to reveal</p>
                  </Card>
                  <Card
                    className="absolute inset-0 flex flex-col items-center justify-center gap-4 overflow-y-auto p-8 text-center"
                    style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
                  >
                    <Markdown className="text-center">{current.back_markdown}</Markdown>
                  </Card>
                </motion.div>
              </button>
            </motion.div>
          </AnimatePresence>

          {flipped && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex w-full gap-3"
            >
              <Button variant="destructive" className="flex-1" onClick={() => handleReview(false)} disabled={review.isPending}>
                <X /> Didn&rsquo;t know it
              </Button>
              <Button className="flex-1" onClick={() => handleReview(true)} disabled={review.isPending}>
                <CheckCircle2 /> Got it
              </Button>
            </motion.div>
          )}

          <p className="text-xs text-[var(--fg-faint)]">Box {current.box}/5 &middot; {current.topic_name}</p>
        </>
      )}
    </div>
  )
}
