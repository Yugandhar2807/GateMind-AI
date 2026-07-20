import { Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'

import { useAuthStore } from '@/stores/auth-store'
import { useMe } from '@/hooks/use-auth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken)
  const { isPending, isError } = useMe()

  if (!accessToken) {
    return <Navigate to="/login" replace />
  }

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="size-6 animate-spin text-signal-500" />
      </div>
    )
  }

  if (isError) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
