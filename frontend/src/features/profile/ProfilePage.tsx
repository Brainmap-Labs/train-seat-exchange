import { useState } from 'react'
import { User, Phone, Mail, Star, LogOut } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { useAuthStore } from '@/store/authStore'

export function ProfilePage() {
  const { user, logout } = useAuthStore()
  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')

  const handleSave = () => {
    // TODO: API call
    console.log('Saving profile...')
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="font-display text-3xl font-bold text-slate-900 mb-8">Profile</h1>

      <div className="space-y-6">
        {/* Avatar & Stats */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-primary-100 rounded-full flex items-center justify-center">
                <User className="w-10 h-10 text-primary-600" />
              </div>
              <div className="flex-1">
                <h2 className="font-semibold text-xl">{user?.name}</h2>
                <p className="text-slate-600">+91 {user?.phone}</p>
                <div className="flex items-center gap-4 mt-2">
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

        {/* Edit Profile */}
        <Card>
          <CardHeader>
            <h3 className="font-display text-lg font-bold">Edit Profile</h3>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              icon={<User className="w-5 h-5" />}
            />
            <Input
              label="Phone Number"
              value={user?.phone || ''}
              disabled
              icon={<Phone className="w-5 h-5" />}
            />
            <Input
              label="Email (optional)"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail className="w-5 h-5" />}
            />
            <Button onClick={handleSave}>Save Changes</Button>
          </CardContent>
        </Card>

        {/* Logout */}
        <Button variant="outline" className="w-full text-red-600 border-red-200 hover:bg-red-50" onClick={logout}>
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  )
}

