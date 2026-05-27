import { useState } from 'react'
import { User, Phone, Mail, Star, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/services/api'
import { mapAuthUser } from '@/utils/authSession'

export function ProfilePage() {
  const { user, logout, updateUser } = useAuthStore()
  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const handleSave = async () => {
    setError(null)
    setSuccess(null)

    const digits = phone.replace(/\D/g, '')
    if (digits && digits.length !== 10) {
      setError('Mobile number must be 10 digits')
      return
    }

    setIsSaving(true)
    try {
      const response = await authApi.updateProfile({
        name: name.trim(),
        email: email.trim() || undefined,
        phone: digits || '',
      })
      const updated = mapAuthUser(response.data.user)
      updateUser(updated)
      setName(updated.name)
      setEmail(updated.email || '')
      setPhone(updated.phone || '')
      setSuccess('Profile updated successfully')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  const displayPhone = user?.phone ? `+91 ${user.phone}` : user?.email || 'No mobile added'

  return (
    <div className="page-container-narrow">
      <h1 className="page-title mb-6 sm:mb-8">Profile</h1>

      <div className="space-y-6">
        <Card>
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-6">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-primary-100 rounded-full flex items-center justify-center overflow-hidden shrink-0 mx-auto sm:mx-0">
                {user?.avatarUrl ? (
                  <img src={user.avatarUrl} alt="" className="w-full h-full object-cover" />
                ) : (
                  <User className="w-10 h-10 text-primary-600" />
                )}
              </div>
              <div className="flex-1 text-center sm:text-left min-w-0">
                <h2 className="font-semibold text-lg sm:text-xl truncate">{user?.name}</h2>
                <p className="text-slate-600 text-sm sm:text-base break-words">{displayPhone}</p>
                <div className="flex items-center justify-center sm:justify-start gap-4 mt-2 flex-wrap">
                  <span className="flex items-center gap-1 text-sm">
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                    {user?.rating?.toFixed(1) || '—'} rating
                  </span>
                  <span className="text-sm text-slate-500">
                    {user?.totalExchanges || 0} exchanges
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h3 className="font-display text-lg font-bold">Edit Profile</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}
            {success && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                {success}
              </div>
            )}

            <Input
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              icon={<User className="w-5 h-5" />}
            />

            <div className="space-y-1">
              <label className="block text-sm font-medium text-slate-700">Mobile Number</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium z-10">
                  +91
                </span>
                <div className="absolute left-12 top-1/2 -translate-y-1/2 text-slate-400">
                  <Phone className="w-5 h-5" />
                </div>
                <input
                  type="tel"
                  placeholder="10-digit mobile number"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="w-full pl-[4.5rem] pr-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                />
              </div>
            </div>

            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail className="w-5 h-5" />}
            />

            <Button onClick={handleSave} isLoading={isSaving} disabled={isSaving} className="w-full sm:w-auto">
              Save Changes
            </Button>
          </CardContent>
        </Card>

        <Button
          variant="outline"
          className="w-full text-red-600 border-red-200 hover:bg-red-50"
          onClick={logout}
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  )
}
