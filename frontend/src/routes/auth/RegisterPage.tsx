import * as React from 'react'
import { Link } from 'react-router-dom'
import { isAxiosError } from 'axios'
import { Loader2 } from 'lucide-react'

import { AuthLayout } from '@/routes/auth/AuthLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useRegister } from '@/hooks/use-auth'

const MIN_PASSWORD_LENGTH = 8

export default function RegisterPage() {
  const [fullName, setFullName] = React.useState('')
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const register = useRegister()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    register.mutate({ email, password, full_name: fullName })
  }

  const errorMessage = isAxiosError(register.error)
    ? register.error.response?.status === 409
      ? 'That email is already registered — try signing in instead.'
      : register.error.response?.status === 422
        ? 'Please check your details and try again.'
        : 'Something went wrong. Please try again.'
    : null

  return (
    <AuthLayout>
      <h2 className="font-display text-2xl font-semibold">Start your prep</h2>
      <p className="mt-1.5 text-sm text-[var(--fg-muted)]">Set up your GateMind AI profile.</p>

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="full_name">Full name</Label>
          <Input
            id="full_name"
            autoComplete="name"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Your name"
          />
        </div>

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
            autoComplete="new-password"
            required
            minLength={MIN_PASSWORD_LENGTH}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
          />
        </div>

        {errorMessage && (
          <p role="alert" className="text-sm text-risk-500">
            {errorMessage}
          </p>
        )}

        <Button type="submit" size="lg" className="mt-2" disabled={register.isPending}>
          {register.isPending && <Loader2 className="animate-spin" />}
          Create account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-[var(--fg-muted)]">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-signal-500 hover:underline">
          Sign in
        </Link>
      </p>
    </AuthLayout>
  )
}
