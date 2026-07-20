import { Link } from 'react-router-dom'
import { Bookmark as BookmarkIcon, ExternalLink, FileText, Layers, Link2, Loader2, Map } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { useBookmarks } from '@/hooks/use-bookmarks'
import type { Bookmark, BookmarkType } from '@/types/bookmark'

const TYPE_ICON: Record<BookmarkType, React.ElementType> = {
  resource: Link2,
  topic: Map,
  note: FileText,
  flashcard: Layers,
  question: FileText,
  formula: FileText,
}

const TYPE_LABEL: Record<BookmarkType, string> = {
  resource: 'Resource',
  topic: 'Topic',
  note: 'Note',
  flashcard: 'Flashcard',
  question: 'Question',
  formula: 'Formula',
}

function BookmarkRow({ bookmark }: { bookmark: Bookmark }) {
  const Icon = TYPE_ICON[bookmark.bookmark_type]
  const isExternal = bookmark.link.startsWith('http')

  const content = (
    <CardContent className="flex items-center gap-3 py-3.5">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--bg-inset)]">
        <Icon className="size-4 text-[var(--fg-muted)]" />
      </div>
      <div className="min-w-0 flex-1">
        <p className={`truncate text-sm font-medium ${bookmark.is_missing ? 'text-[var(--fg-faint)] italic' : ''}`}>
          {bookmark.title}
        </p>
        {bookmark.subtitle && <p className="truncate text-xs text-[var(--fg-faint)]">{bookmark.subtitle}</p>}
      </div>
      <Badge variant="default" className="shrink-0">
        {TYPE_LABEL[bookmark.bookmark_type]}
      </Badge>
      {isExternal && <ExternalLink className="size-3.5 shrink-0 text-[var(--fg-faint)]" />}
    </CardContent>
  )

  if (bookmark.is_missing) {
    return <Card className="opacity-60">{content}</Card>
  }

  return isExternal ? (
    <a href={bookmark.link} target="_blank" rel="noopener noreferrer">
      <Card className="transition-colors hover:border-signal-500/40">{content}</Card>
    </a>
  ) : (
    <Link to={bookmark.link}>
      <Card className="transition-colors hover:border-signal-500/40">{content}</Card>
    </Link>
  )
}

export default function BookmarksPage() {
  const { data: bookmarks, isPending } = useBookmarks()

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Bookmarks</p>
        <h1 className="mt-1 font-display text-2xl font-semibold">Saved for later</h1>
        <p className="mt-1 text-sm text-[var(--fg-muted)]">
          Resources and topics you&rsquo;ve bookmarked. Flashcard favorites live on the{' '}
          <Link to="/flashcards" className="text-signal-500 hover:underline">
            Flashcards
          </Link>{' '}
          page.
        </p>
      </div>

      {isPending ? (
        <Loader2 className="size-5 animate-spin text-signal-500" />
      ) : !bookmarks?.length ? (
        <Card>
          <div className="flex flex-col items-center gap-3 py-14 text-center">
            <BookmarkIcon className="size-8 text-[var(--fg-faint)]" />
            <p className="text-sm text-[var(--fg-muted)]">
              Nothing bookmarked yet. Click the bookmark icon on any topic or resource.
            </p>
          </div>
        </Card>
      ) : (
        <div className="flex flex-col gap-2">
          {bookmarks.map((b) => (
            <BookmarkRow key={b.id} bookmark={b} />
          ))}
        </div>
      )}
    </div>
  )
}
