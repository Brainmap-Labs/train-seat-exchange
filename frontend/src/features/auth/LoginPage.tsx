import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Phone, ArrowRight, Train } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import { useAuthStore } from '@/store/authStore'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [step, setStep] = useState<'phone' | 'otp'>('phone')
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSendOtp = async () => {
    if (phone.length !== 10) return
    setIsLoading(true)
    // TODO: API call to send OTP
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsLoading(false)
    setStep('otp')
  }

  const handleVerifyOtp = async () => {
    if (otp.length !== 6) return
    setIsLoading(true)
    // TODO: API call to verify OTP
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock login
    login({
      id: '1',
      phone,
      name: 'User',
      rating: 4.5,
      totalExchanges: 0,
      createdAt: new Date(),
    })
    
    setIsLoading(false)
    navigate('/dashboard')
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-8">
          {/* Logo */}
          <div className="flex justify-center mb-8">
            <div className="bg-railway-blue p-4 rounded-2xl">
              <Train className="w-10 h-10 text-primary-400" />
            </div>
          </div>

          <h1 className="font-display text-2xl font-bold text-center text-slate-900 mb-2">
            {step === 'phone' ? 'Login to SeatSwap' : 'Verify OTP'}
          </h1>
          <p className="text-center text-slate-600 mb-8">
            {step === 'phone' 
              ? 'Enter your mobile number to continue'
              : `We've sent a 6-digit code to +91 ${phone}`
            }
          </p>

          {step === 'phone' ? (
            <div className="space-y-6">
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 font-medium">
                  +91
                </span>
                <Input
                  type="tel"
                  placeholder="Enter mobile number"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))}
                  className="pl-14"
                  icon={<Phone className="w-5 h-5" />}
                />
              </div>
              <Button 
                className="w-full" 
                onClick={handleSendOtp}
                isLoading={isLoading}
                disabled={phone.length !== 10}
              >
                Send OTP
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="flex justify-center gap-2">
                {[0, 1, 2, 3, 4, 5].map((index) => (
                  <input
                    key={index}
                    type="text"
                    maxLength={1}
                    value={otp[index] || ''}
                    onChange={(e) => {
                      const value = e.target.value.replace(/\D/g, '')
                      const newOtp = otp.split('')
                      newOtp[index] = value
                      setOtp(newOtp.join('').slice(0, 6))
                      // Auto-focus next input
                      if (value && e.target.nextElementSibling) {
                        (e.target.nextElementSibling as HTMLInputElement).focus()
                      }
                    }}
                    className="w-12 h-14 text-center text-2xl font-bold border-2 border-slate-200 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none"
                  />
                ))}
              </div>

              <Button 
                className="w-full" 
                onClick={handleVerifyOtp}
                isLoading={isLoading}
                disabled={otp.length !== 6}
              >
                Verify & Continue
              </Button>

              <button 
                className="w-full text-center text-sm text-slate-600 hover:text-railway-blue"
                onClick={() => setStep('phone')}
              >
                Change phone number
              </button>
            </div>
          )}

          <p className="text-xs text-center text-slate-500 mt-8">
            By continuing, you agree to our{' '}
            <a href="/terms" className="text-railway-blue hover:underline">Terms</a>
            {' '}and{' '}
            <a href="/privacy" className="text-railway-blue hover:underline">Privacy Policy</a>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

