import { User } from '@/types'

export interface AuthApiUser {
  id: string
  phone?: string | null
  name: string
  email?: string | null
  avatar_url?: string | null
  auth_provider?: string
  rating?: number
  total_exchanges?: number
}

export function mapAuthUser(user: AuthApiUser): User {
  return {
    id: user.id,
    phone: user.phone || '',
    name: user.name,
    email: user.email || undefined,
    avatarUrl: user.avatar_url || undefined,
    authProvider: user.auth_provider === 'google' ? 'google' : 'phone',
    rating: user.rating || 0,
    totalExchanges: user.total_exchanges || 0,
    createdAt: new Date(),
  }
}

export function persistAuthSession(
  accessToken: string,
  user: AuthApiUser,
  login: (user: User) => void,
) {
  localStorage.setItem('auth-token', accessToken)
  login(mapAuthUser(user))
}
