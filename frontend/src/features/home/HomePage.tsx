import { Link } from 'react-router-dom'
import { Train, Upload, Search, MessageCircle, Users, Star, Shield, Zap } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { useAuthStore } from '@/store/authStore'

export function HomePage() {
  const { isAuthenticated } = useAuthStore()
  
  // Determine navigation targets based on auth status
  const primaryCtaLink = isAuthenticated ? '/tickets/upload' : '/tickets/upload'
  const secondaryCtaLink = isAuthenticated ? '/dashboard' : '/signup'
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-railway-blue via-blue-800 to-blue-900 text-white overflow-hidden">
        {/* Decorative Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }} />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32 relative">
          <div className="max-w-3xl">
            <h1 className="font-display text-4xl md:text-6xl font-bold leading-tight mb-6">
              Sit Together with Your{' '}
              <span className="text-primary-400">Family</span> on Trains
            </h1>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl">
              Upload your train ticket, find passengers willing to exchange seats, 
              and ensure your family travels together comfortably.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to={primaryCtaLink}>
                <Button variant="secondary" size="lg">
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Ticket
                </Button>
              </Link>
              <Link to={secondaryCtaLink}>
                <Button variant="outline" size="lg" className="border-white text-white hover:bg-white hover:text-railway-blue">
                  {isAuthenticated ? 'My Trips' : 'Get Started Free'}
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Floating Train Illustration */}
        <div className="absolute right-0 bottom-0 hidden lg:block">
          <Train className="w-96 h-96 text-white/5" />
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Exchange seats with fellow passengers in three simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Upload,
                title: 'Upload Your Ticket',
                description: 'Take a photo or upload your e-ticket. Our AI extracts all the details automatically.',
                color: 'bg-blue-500',
              },
              {
                icon: Search,
                title: 'Find Matches',
                description: 'We find passengers on your train who might be willing to exchange seats.',
                color: 'bg-primary-500',
              },
              {
                icon: MessageCircle,
                title: 'Connect & Exchange',
                description: 'Chat with matched passengers, agree on the exchange, and travel together!',
                color: 'bg-green-500',
              },
            ].map((step, index) => (
              <div key={index} className="relative">
                <div className="bg-slate-50 rounded-2xl p-8 hover:shadow-xl transition-shadow h-full">
                  <div className={`${step.color} w-14 h-14 rounded-xl flex items-center justify-center mb-6`}>
                    <step.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="font-display text-xl font-bold text-slate-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-slate-600">
                    {step.description}
                  </p>
                </div>
                {index < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 w-8 h-8 text-slate-300">
                    →
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Why Choose SeatSwap?
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Users, title: 'Family First', desc: 'Designed for families traveling together' },
              { icon: Zap, title: 'Smart Matching', desc: 'AI-powered seat exchange suggestions' },
              { icon: Shield, title: 'Safe & Secure', desc: 'Verified users, secure messaging' },
              { icon: Star, title: 'Free to Use', desc: 'Basic features always free' },
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                <feature.icon className="w-10 h-10 text-railway-blue mb-4" />
                <h3 className="font-semibold text-lg text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-railway-blue">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="font-display text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Travel Together?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            {isAuthenticated 
              ? 'Upload a ticket and find passengers willing to exchange seats' 
              : 'Join thousands of families who\'ve successfully exchanged seats'}
          </p>
          <Link to={secondaryCtaLink}>
            <Button variant="secondary" size="lg">
              Start Free Today
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}

