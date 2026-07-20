import { Bookmark } from 'lucide-react'

import { cn } from '@/lib/utils'
import { useBookmarkedIds, useToggleBookmark } from '@/hooks/use-bookmarks'
import type { BookmarkType } from '@/types/bookmark'

export function BookmarkButton({
  bookmarkType,
  targetId,
  className,
}: {
  bookmarkType: BookmarkType
  targetId: number
  className?: string
}) {
  const { data: ids } = useBookmarkedIds(bookmarkType)
  const toggle = useToggleBookmark()
  const isBookmarked = ids?.has(targetId) ?? false

  return (
    <button
      type="button"
      onClick={(e) => {
        e.preventDefault()
        e.stopPropagation()
        toggle.mutate({ bookmarkType, targetId })
      }}
      disabled={toggle.isPending}
      aria-label={isBookmarked ? 'Remove bookmark' : 'Add bookmark'}
      aria-pressed={isBookmarked}
      className={cn(
        'inline-flex size-7 shrink-0 items-center justify-center rounded-[var(--radius-sm)] text-[var(--fg-faint)] transition-colors hover:bg-[var(--bg-inset)] hover:text-[var(--fg)]',
        isBookmarked && 'text-signal-500 hover:text-signal-500',
        className,
      )}
    >
      <Bookmark className={cn('size-4', isBookmarked && 'fill-signal-500')} />
    </button>
  )
}
