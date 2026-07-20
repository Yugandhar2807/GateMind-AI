import * as React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { isAxiosError } from 'axios'
import { Loader2 } from 'lucide-react'

import { AuthLayout } from '@/routes/auth/AuthLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useLogin } from '@/hooks/use-auth'

export default function LoginPage() {
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const login = useLogin()
  const location = useLocation()
  const justRegistered = Boolean((location.state as { justRegistered?: boolean } | null)?.justRegistered)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    login.mutate({ email, password })
  }

  const errorMessage = isAxiosError(login.error)
    ? login.error.response?.status === 401
      ? 'Incorrect email or password.'
      : 'Something went wrong. Please try again.'
    : null

  return (
    <AuthLayout>
      <h2 className="font-display text-2xl font-semibold">Welcome back</h2>
      <p className="mt-1.5 text-sm text-[var(--fg-muted)]">Sign in to continue your prep.</p>

      {justRegistered && (
        <div className="mt-5 rounded-[var(--radius-md)] border border-mastery-500/30 bg-mastery-500/10 px-3.5 py-2.5 text-sm text-mastery-500">
          Account created &mdash; sign in below.
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
          />
        </div>

        {errorMessage && (
          <p role="alert" className="text-sm text-risk-500">
            {errorMessage}
          </p>
        )}

        <Button type="submit" size="lg" className="mt-2" disabled={login.isPending}>
          {login.isPending && <Loader2 className="animate-spin" />}
          Sign in
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[var(--fg-muted)]">
        New here?{' '}
        <Link to="/register" className="font-semibold text-signal-500 hover:underline">
          Create an account
        </Link>
      </p>
    </AuthLayout>
  )
}
