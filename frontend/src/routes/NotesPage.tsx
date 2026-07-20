import * as React from 'react'
import { Link } from 'react-router-dom'
import { Eye, FileText, Loader2, Pencil, Plus, Trash2 } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Markdown } from '@/components/Markdown'
import { cn } from '@/lib/utils'
import { useCreateNote, useDeleteNote, useNotes, useUpdateNote } from '@/hooks/use-notes'
import type { Note } from '@/types/note'

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function NotesPage() {
  const { data: notes, isPending } = useNotes()
  const createNote = useCreateNote()
  const updateNote = useUpdateNote()
  const deleteNote = useDeleteNote()

  const [selectedId, setSelectedId] = React.useState<string | 'new' | null>(null)
  const [title, setTitle] = React.useState('')
  const [content, setContent] = React.useState('')
  const [mode, setMode] = React.useState<'edit' | 'preview'>('edit')

  const selected: Note | undefined = notes?.find((n) => n.id === selectedId)

  React.useEffect(() => {
    if (selected) {
      setTitle(selected.title)
      setContent(selected.content_markdown)
    } else if (selectedId === 'new') {
      setTitle('')
      setContent('')
    }
  }, [selectedId, selected?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleSave() {
    if (!title.trim()) return
    if (selectedId === 'new') {
      createNote.mutate(
        { title, content_markdown: content },
        { onSuccess: (note) => setSelectedId(note.id) },
      )
    } else if (selectedId) {
      updateNote.mutate({ id: selectedId, payload: { title, content_markdown: content } })
    }
  }

  function handleDelete(id: string) {
    deleteNote.mutate(id, { onSuccess: () => setSelectedId(null) })
  }

  return (
    <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h1 className="font-display text-lg font-semibold">Notes</h1>
          <Button size="sm" onClick={() => setSelectedId('new')}>
            <Plus /> New
          </Button>
        </div>

        {isPending ? (
          <Loader2 className="size-4 animate-spin text-[var(--fg-faint)]" />
        ) : !notes?.length ? (
          <p className="text-sm text-[var(--fg-faint)]">No notes yet.</p>
        ) : (
          <div className="flex flex-col gap-1.5">
            {notes.map((note) => (
              <button
                key={note.id}
                type="button"
                onClick={() => setSelectedId(note.id)}
                className={cn(
                  'rounded-[var(--radius-md)] border border-[var(--border)] px-3 py-2.5 text-left transition-colors',
                  selectedId === note.id ? 'border-signal-500/40 bg-signal-500/5' : 'hover:bg-[var(--bg-inset)]',
                )}
              >
                <p className="truncate text-sm font-medium">{note.title}</p>
                <p className="mt-0.5 text-xs text-[var(--fg-faint)]">{formatDate(note.updated_at)}</p>
              </button>
            ))}
          </div>
        )}
      </div>

      <div>
        {selectedId == null ? (
          <Card>
            <div className="flex flex-col items-center gap-3 py-16 text-center">
              <FileText className="size-8 text-[var(--fg-faint)]" />
              <p className="text-sm text-[var(--fg-muted)]">Select a note, or create a new one.</p>
            </div>
          </Card>
        ) : (
          <Card>
            <CardContent className="flex flex-col gap-3 pt-5">
              <div className="flex items-center gap-2">
                <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Note title" className="flex-1" />
                {selected?.topic_id && (
                  <Link to={`/roadmap/topics/${selected.topic_id}`}>
                    <Badge variant="signal">Linked topic</Badge>
                  </Link>
                )}
              </div>

              <div className="flex items-center gap-1 self-start rounded-[var(--radius-sm)] border border-[var(--border)] p-0.5">
                <button
                  type="button"
                  onClick={() => setMode('edit')}
                  className={cn(
                    'flex items-center gap-1.5 rounded-[calc(var(--radius-sm)-2px)] px-2.5 py-1 text-xs font-medium',
                    mode === 'edit' ? 'bg-[var(--bg-inset)] text-[var(--fg)]' : 'text-[var(--fg-faint)]',
                  )}
                >
                  <Pencil className="size-3.5" /> Edit
                </button>
                <button
                  type="button"
                  onClick={() => setMode('preview')}
                  className={cn(
                    'flex items-center gap-1.5 rounded-[calc(var(--radius-sm)-2px)] px-2.5 py-1 text-xs font-medium',
                    mode === 'preview' ? 'bg-[var(--bg-inset)] text-[var(--fg)]' : 'text-[var(--fg-faint)]',
                  )}
                >
                  <Eye className="size-3.5" /> Preview
                </button>
              </div>

              {mode === 'edit' ? (
                <Textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={16}
                  placeholder="Markdown, code fences, and LaTeX ($E=mc^2$) all supported..."
                  className="font-mono text-xs"
                />
              ) : (
                <div className="min-h-[24rem] rounded-[var(--radius-md)] border border-[var(--border)] p-4">
                  <Markdown>{content || '*Nothing to preview yet.*'}</Markdown>
                </div>
              )}

              <div className="flex items-center justify-between">
                <Button
                  variant="destructive"
                  size="sm"
                  disabled={!selectedId || selectedId === 'new'}
                  onClick={() => selectedId && selectedId !== 'new' && handleDelete(selectedId)}
                >
                  <Trash2 /> Delete
                </Button>
                <Button size="sm" onClick={handleSave} disabled={!title.trim() || createNote.isPending || updateNote.isPending}>
                  {(createNote.isPending || updateNote.isPending) && <Loader2 className="animate-spin" />}
                  Save
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
