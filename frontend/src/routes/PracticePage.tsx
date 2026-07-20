import * as React from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, ChevronRight, Loader2, Target, Timer, XCircle } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Markdown } from '@/components/Markdown'
import { cn } from '@/lib/utils'
import { useRoadmap } from '@/hooks/use-roadmap'
import { useAnswerQuestion, useStartPractice, useSubmitAttempt, useTopicQuestionStats } from '@/hooks/use-practice'
import type { PracticeAnswerResult, PracticeSubmitResponse, QuestionPublic } from '@/types/practice'
import type { Difficulty } from '@/types/roadmap'

const DIFFICULTY_OPTIONS: { value: Difficulty | ''; label: string }[] = [
  { value: '', label: 'Any difficulty' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
  { value: 'very_hard', label: 'Very Hard' },
]

function SetupScreen({ onStart }: { onStart: (topicId: number, count: number, difficulty: Difficulty | '') => void }) {
  const { data: subjects, isPending } = useRoadmap()
  const [searchParams] = useSearchParams()
  const presetTopicId = searchParams.get('topic_id')

  const [subjectId, setSubjectId] = React.useState<number | ''>('')
  const [topicId, setTopicId] = React.useState<number | ''>(presetTopicId ? Number(presetTopicId) : '')
  const [count, setCount] = React.useState(10)
  const [difficulty, setDifficulty] = React.useState<Difficulty | ''>('')

  React.useEffect(() => {
    if (presetTopicId && subjects) {
      const id = Number(presetTopicId)
      const subj = subjects.find((s) => s.topics.some((t) => t.id === id))
      if (subj) setSubjectId(subj.id)
      setTopicId(id)
    }
  }, [presetTopicId, subjects])

  const stats = useTopicQuestionStats(typeof topicId === 'number' ? topicId : undefined)
  const currentSubject = subjects?.find((s) => s.id === subjectId)

  if (isPending) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-6 animate-spin text-signal-500" />
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-lg">
      <div className="mb-6">
        <p className="font-mono text-xs tracking-widest text-[var(--fg-faint)] uppercase">Practice</p>
        <h1 className="mt-1 font-display text-2xl font-semibold">Practice Engine</h1>
        <p className="mt-1 text-sm text-[var(--fg-muted)]">
          Real GATE DA questions (previous-year papers), instant feedback, negative marking applied
          exactly like the real exam.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 pt-5">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-[var(--fg-muted)] uppercase">Subject</label>
            <select
              value={subjectId}
              onChange={(e) => {
                setSubjectId(e.target.value ? Number(e.target.value) : '')
                setTopicId('')
              }}
              className="h-10 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm outline-none focus-visible:border-signal-500"
            >
              <option value="">Select a subject</option>
              {subjects?.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-[var(--fg-muted)] uppercase">Topic</label>
            <select
              value={topicId}
              onChange={(e) => setTopicId(e.target.value ? Number(e.target.value) : '')}
              disabled={!currentSubject}
              className="h-10 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm outline-none focus-visible:border-signal-500 disabled:opacity-50"
            >
              <option value="">Select a topic</option>
              {currentSubject?.topics.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>

          {typeof topicId === 'number' && (
            <p className="text-xs text-[var(--fg-faint)]">
              {stats.isPending
                ? 'Checking available questions…'
                : stats.data
                  ? `${stats.data.total} question${stats.data.total === 1 ? '' : 's'} available for this topic.`
                  : ''}
            </p>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-[var(--fg-muted)] uppercase">Difficulty</label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value as Difficulty | '')}
                className="h-10 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm outline-none focus-visible:border-signal-500"
              >
                {DIFFICULTY_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-[var(--fg-muted)] uppercase">Questions</label>
              <select
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                className="h-10 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3 text-sm outline-none focus-visible:border-signal-500"
              >
                {[5, 10, 15, 20].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Button
            size="lg"
            disabled={typeof topicId !== 'number' || !stats.data?.total}
            onClick={() => typeof topicId === 'number' && onStart(topicId, count, difficulty)}
          >
            <Target /> Start Practice
          </Button>
          {typeof topicId === 'number' && stats.data && stats.data.total === 0 && (
            <p className="text-center text-xs text-risk-500">
              No questions available for this topic yet.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function QuestionScreen({
  question,
  index,
  total,
  attemptId,
  onAnswered,
  onNext,
}: {
  question: QuestionPublic
  index: number
  total: number
  attemptId: number
  onAnswered: (result: PracticeAnswerResult) => void
  onNext: () => void
}) {
  const answerMutation = useAnswerQuestion(attemptId)
  const [selected, setSelected] = React.useState<number[]>([])
  const [natValue, setNatValue] = React.useState('')
  const [result, setResult] = React.useState<PracticeAnswerResult | null>(null)
  const [startTime] = React.useState(() => Date.now())

  React.useEffect(() => {
    setSelected([])
    setNatValue('')
    setResult(null)
  }, [question.id])

  function toggleOption(idx: number) {
    if (result) return
    if (question.question_type === 'mcq') {
      setSelected([idx])
    } else {
      setSelected((prev) => (prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]))
    }
  }

  function submit(skip: boolean) {
    const timeTaken = Math.round((Date.now() - startTime) / 1000)
    answerMutation.mutate(
      {
        question_id: question.id,
        selected_indices: question.question_type !== 'nat' ? selected : undefined,
        nat_value: question.question_type === 'nat' ? Number(natValue) : undefined,
        is_skipped: skip,
        time_taken_seconds: timeTaken,
      },
      {
        onSuccess: (data) => {
          setResult(data)
          onAnswered(data)
        },
      },
    )
  }

  const canSubmit = question.question_type === 'nat' ? natValue.trim() !== '' : selected.length > 0

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-4 flex items-center justify-between">
        <span className="font-mono text-xs text-[var(--fg-faint)] tabular">
          Question {index + 1} / {total}
        </span>
        <div className="flex items-center gap-2">
          <Badge variant="default" className="capitalize">
            {question.question_type}
          </Badge>
          <Badge variant="signal">{question.marks} mark{question.marks !== 1 ? 's' : ''}</Badge>
        </div>
      </div>
      <Progress value={((index + (result ? 1 : 0)) / total) * 100} className="mb-6" />

      <AnimatePresence mode="wait">
        <motion.div key={question.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
          <Card>
            <CardContent className="flex flex-col gap-4 pt-5">
              <Markdown>{question.question_markdown}</Markdown>

              {question.question_type !== 'nat' ? (
                <div className="flex flex-col gap-2">
                  {question.options?.map((opt, idx) => {
                    const isSelected = selected.includes(idx)
                    const isCorrect = result?.correct_option_indices.includes(idx)
                    return (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => toggleOption(idx)}
                        disabled={!!result}
                        className={cn(
                          'flex items-center gap-3 rounded-[var(--radius-md)] border px-3.5 py-2.5 text-left text-sm transition-colors',
                          !result && isSelected && 'border-signal-500 bg-signal-500/10',
                          !result && !isSelected && 'border-[var(--border)] hover:bg-[var(--bg-inset)]',
                          result && isCorrect && 'border-mastery-500 bg-mastery-500/10',
                          result && !isCorrect && isSelected && 'border-risk-500 bg-risk-500/10',
                          result && !isCorrect && !isSelected && 'border-[var(--border)] opacity-60',
                        )}
                      >
                        <span
                          className={cn(
                            'flex size-4 shrink-0 items-center justify-center rounded-full border text-[10px]',
                            isSelected ? 'border-signal-500 bg-signal-500 text-ink-950' : 'border-[var(--border)]',
                          )}
                        >
                          {isSelected && '✓'}
                        </span>
                        <Markdown className="text-sm">{opt}</Markdown>
                        {result && isCorrect && <CheckCircle2 className="ml-auto size-4 shrink-0 text-mastery-500" />}
                        {result && !isCorrect && isSelected && <XCircle className="ml-auto size-4 shrink-0 text-risk-500" />}
                      </button>
                    )
                  })}
                </div>
              ) : (
                <input
                  type="number"
                  step="any"
                  value={natValue}
                  onChange={(e) => setNatValue(e.target.value)}
                  disabled={!!result}
                  placeholder="Enter your numeric answer"
                  className="h-11 rounded-[var(--radius-md)] border border-[var(--border)] bg-[var(--bg-elevated)] px-3.5 text-sm outline-none focus-visible:border-signal-500 disabled:opacity-70"
                />
              )}

              {result && (
                <div
                  className={cn(
                    'rounded-[var(--radius-md)] border px-3.5 py-3 text-sm',
                    result.is_correct ? 'border-mastery-500/30 bg-mastery-500/10' : 'border-risk-500/30 bg-risk-500/10',
                  )}
                >
                  <p className={cn('font-semibold', result.is_correct ? 'text-mastery-500' : 'text-risk-500')}>
                    {result.is_correct ? 'Correct' : 'Incorrect'} · {result.marks_awarded >= 0 ? '+' : ''}
                    {result.marks_awarded} marks
                  </p>
                  {question.question_type === 'nat' && (
                    <p className="mt-1 text-[var(--fg-muted)]">Correct answer: {result.correct_value}</p>
                  )}
                  {result.explanation_markdown && (
                    <div className="mt-2 text-[var(--fg-muted)]">
                      <Markdown>{result.explanation_markdown}</Markdown>
                    </div>
                  )}
                </div>
              )}

              <div className="flex justify-between">
                {!result ? (
                  <>
                    <Button variant="ghost" onClick={() => submit(true)} disabled={answerMutation.isPending}>
                      Skip
                    </Button>
                    <Button onClick={() => submit(false)} disabled={!canSubmit || answerMutation.isPending}>
                      {answerMutation.isPending && <Loader2 className="animate-spin" />}
                      Submit Answer
                    </Button>
                  </>
                ) : (
                  <Button className="ml-auto" onClick={onNext}>
                    {index + 1 === total ? 'Finish' : 'Next Question'} <ChevronRight className="size-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

function ResultsScreen({ result, onRestart }: { result: PracticeSubmitResponse; onRestart: () => void }) {
  return (
    <div className="mx-auto max-w-lg">
      <Card>
        <CardContent className="flex flex-col items-center gap-4 py-10 text-center">
          <div className="flex size-16 items-center justify-center rounded-full bg-signal-500/10">
            <Target className="size-7 text-signal-500" />
          </div>
          <div>
            <p className="font-mono text-3xl font-semibold tabular">
              {result.score} / {result.max_score}
            </p>
            <p className="mt-1 text-sm text-[var(--fg-muted)]">{result.accuracy_percent}% accuracy</p>
          </div>

          <div className="grid w-full grid-cols-3 gap-3 text-sm">
            <div className="rounded-[var(--radius-md)] border border-[var(--border)] p-3">
              <p className="font-mono text-lg font-semibold text-mastery-500 tabular">{result.correct_count}</p>
              <p className="text-xs text-[var(--fg-faint)]">Correct</p>
            </div>
            <div className="rounded-[var(--radius-md)] border border-[var(--border)] p-3">
              <p className="font-mono text-lg font-semibold text-risk-500 tabular">{result.incorrect_count}</p>
              <p className="text-xs text-[var(--fg-faint)]">Incorrect</p>
            </div>
            <div className="rounded-[var(--radius-md)] border border-[var(--border)] p-3">
              <p className="font-mono text-lg font-semibold tabular">{result.skipped_count}</p>
              <p className="text-xs text-[var(--fg-faint)]">Skipped</p>
            </div>
          </div>

          <div className="flex w-full items-center justify-between text-xs text-[var(--fg-faint)]">
            <span className="flex items-center gap-1">
              <Timer className="size-3.5" /> avg {result.avg_time_per_question_seconds}s / question
            </span>
            {result.negative_marks_lost > 0 && <span>&minus;{result.negative_marks_lost} negative marking</span>}
          </div>

          <Button onClick={onRestart} className="w-full">
            Practice Again
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

export default function PracticePage() {
  const startMutation = useStartPractice()
  const submitMutation = useSubmitAttempt()
  const [session, setSession] = React.useState<{ attemptId: number; questions: QuestionPublic[] } | null>(null)
  const [index, setIndex] = React.useState(0)
  const [finalResult, setFinalResult] = React.useState<PracticeSubmitResponse | null>(null)

  function handleStart(topicId: number, count: number, difficulty: Difficulty | '') {
    startMutation.mutate(
      { topic_id: topicId, question_count: count, difficulty: difficulty || undefined },
      {
        onSuccess: (data) => {
          setSession({ attemptId: data.attempt_id, questions: data.questions })
          setIndex(0)
          setFinalResult(null)
        },
      },
    )
  }

  function handleNext() {
    if (!session) return
    if (index + 1 < session.questions.length) {
      setIndex((i) => i + 1)
    } else {
      submitMutation.mutate(session.attemptId, {
        onSuccess: (data) => setFinalResult(data),
      })
    }
  }

  function handleRestart() {
    setSession(null)
    setFinalResult(null)
    setIndex(0)
  }

  if (finalResult) {
    return <ResultsScreen result={finalResult} onRestart={handleRestart} />
  }

  if (session) {
    return (
      <QuestionScreen
        question={session.questions[index]}
        index={index}
        total={session.questions.length}
        attemptId={session.attemptId}
        onAnswered={() => {}}
        onNext={handleNext}
      />
    )
  }

  return <SetupScreen onStart={handleStart} />
}
