import { ClipboardList } from 'lucide-react'

import { ComingSoon } from '@/routes/ComingSoon'

export default function MocksPage() {
  return (
    <ComingSoon
      icon={ClipboardList}
      phase="Phase 6"
      title="Mock Test Engine"
      description="Weekly/monthly/quarterly auto-generated mocks with full post-submission analysis — arriving in Phase 6."
    />
  )
}
