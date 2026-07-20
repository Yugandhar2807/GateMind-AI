import { BarChart3 } from 'lucide-react'

import { ComingSoon } from '@/routes/ComingSoon'

export default function AnalyticsPage() {
  return (
    <ComingSoon
      icon={BarChart3}
      phase="Phase 7"
      title="Analytics"
      description="Contribution heatmap, retention curves, accuracy trends, and predicted AIR over time — arriving in Phase 7."
    />
  )
}
