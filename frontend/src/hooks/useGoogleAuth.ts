import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CredentialResponse } from '@react-oauth/google'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/services/api'
import { persistAuthSession } from '@/utils/authSession'

export function useGoogleAuth(redirectTo = '/dashboard') {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGoogleSuccess = async (response: CredentialResponse) => {
    if (!response.credential) {
      setError('Google sign-in did not return a credential')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await authApi.googleLogin(response.credential)
      const { access_token, user } = result.data
      persistAuthSession(access_token, user, login)
      navigate(redirectTo)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Google sign-in failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleError = () => {
    setError('Google sign-in was cancelled or failed')
  }

  return {
    handleGoogleSuccess,
    handleGoogleError,
    isLoading,
    error,
    setError,
  }
}

export const isGoogleAuthConfigured = Boolean(import.meta.env.VITE_GOOGLE_CLIENT_ID)
