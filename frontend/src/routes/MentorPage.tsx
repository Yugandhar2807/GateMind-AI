import { Bot } from 'lucide-react'

import { ComingSoon } from '@/routes/ComingSoon'

export default function MentorPage() {
  return (
    <ComingSoon
      icon={Bot}
      phase="Phase 8"
      title="AI Mentor"
      description="A local-LLM (Ollama) mentor that knows your syllabus, progress, and mistakes, and answers only in GATE DA context — arriving in Phase 8."
    />
  )
}
