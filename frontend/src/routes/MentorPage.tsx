import { useEffect, useRef, useState } from 'react'
import { Bot, Loader2, Send, Sparkles } from 'lucide-react'

import { Markdown } from '@/components/Markdown'
import { Button } from '@/components/ui/button'
import { useSendMessage, type MentorMessage } from '@/hooks/use-mentor'
import { cn } from '@/lib/utils'

const SUGGESTIONS = [
  'What should I study today?',
  'What are my weakest topics right now?',
  'Am I on track for my target AIR?',
  'Make me a 1-week revision plan.',
]

export default function MentorPage() {
  const [messages, setMessages] = useState<MentorMessage[]>([])
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [input, setInput] = useState('')
  const [error, setError] = useState<string | null>(null)
  const send = useSendMessage()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, send.isPending])

  async function submit(text: string) {
    const msg = text.trim()
    if (!msg || send.isPending) return
    setError(null)
    setInput('')
    const userMsg: MentorMessage = {
      id: `local-${Date.now()}`,
      role: 'user',
      content: msg,
      created_at: new Date().toISOString(),
    }
    setMessages((m) => [...m, userMsg])
    try {
      const res = await send.mutateAsync({ message: msg, conversation_id: conversationId })
      setConversationId(res.conversation_id)
      setMessages((m) => [...m, res.message])
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err?.response?.data?.detail ?? 'Something went wrong. Please try again.')
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-3xl flex-col">
      <div className="mb-4">
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">AI Mentor</p>
        <h1 className="mt-1 flex items-center gap-2 font-display text-2xl font-semibold">
          <Bot className="size-6 text-signal-500" /> Your GATE DA mentor
        </h1>
        <p className="mt-1 text-sm text-[var(--fg-muted)]">
          Reasons only from <span className="font-medium text-[var(--fg)]">your</span> progress, weak
          topics, revisions, and streak — running locally on Ollama.
        </p>
      </div>

      <div className="flex-1 overflow-y-auto rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
            <Sparkles className="size-8 text-signal-500" />
            <p className="text-sm text-[var(--fg-muted)]">Ask me anything about your preparation.</p>
            <div className="flex max-w-md flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => submit(s)}
                  className="rounded-full border border-[var(--border)] px-3 py-1.5 text-xs hover:border-signal-500 hover:text-signal-500"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {messages.map((m) => (
              <div key={m.id} className={cn('flex', m.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div
                  className={cn(
                    'max-w-[85%] rounded-[var(--radius-lg)] px-4 py-2.5 text-sm',
                    m.role === 'user' ? 'bg-signal-500 text-white' : 'bg-[var(--bg-inset)]',
                  )}
                >
                  {m.role === 'user' ? (
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  ) : (
                    <Markdown>{m.content}</Markdown>
                  )}
                </div>
              </div>
            ))}
            {send.isPending && (
              <div className="flex justify-start">
                <div className="rounded-[var(--radius-lg)] bg-[var(--bg-inset)] px-4 py-2.5">
                  <Loader2 className="size-4 animate-spin text-signal-500" />
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>
        )}
      </div>

      {error && <p className="mt-2 text-xs text-risk-500">{error}</p>}

      <form
        onSubmit={(e) => {
          e.preventDefault()
          submit(input)
        }}
        className="mt-3 flex items-end gap-2"
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              submit(input)
            }
          }}
          rows={1}
          placeholder="Ask your mentor…"
          className="flex-1 resize-none rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 py-2.5 text-sm outline-none focus-visible:border-signal-500"
        />
        <Button type="submit" disabled={send.isPending || !input.trim()}>
          {send.isPending ? <Loader2 className="size-4 animate-spin" /> : <Send className="size-4" />}
        </Button>
      </form>
    </div>
  )
}
