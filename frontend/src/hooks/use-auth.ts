import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { apiClient } from '@/lib/api-client'
import { useAuthStore } from '@/stores/auth-store'
import type { AuthTokens, User } from '@/types/user'

interface RegisterPayload {
  email: string
  password: string
  full_name: string
}

interface LoginPayload {
  email: string
  password: string
}

export function useMe() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const setUser = useAuthStore((s) => s.setUser)

  return useQuery({
    queryKey: ['me'],
    enabled: !!accessToken,
    queryFn: async () => {
      const { data } = await apiClient.get<User>('/users/me')
      setUser(data)
      return data
    },
  })
}

export function useLogin() {
  const setTokens = useAuthStore((s) => s.setTokens)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (payload: LoginPayload) => {
      const { data } = await apiClient.post<AuthTokens>('/auth/login', payload)
      return data
    },
    onSuccess: async (tokens) => {
      setTokens(tokens)
      await queryClient.invalidateQueries({ queryKey: ['me'] })
      navigate('/dashboard')
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (payload: RegisterPayload) => {
      const { data } = await apiClient.post<User>('/auth/register', payload)
      return data
    },
    onSuccess: () => navigate('/login', { replace: true, state: { justRegistered: true } }),
  })
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return () => {
    logout()
    queryClient.clear()
    navigate('/login')
  }
}
