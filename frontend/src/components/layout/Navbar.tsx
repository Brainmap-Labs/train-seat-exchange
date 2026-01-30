import { Link } from 'react-router-dom'
import { Train, Menu, X, User, Bell } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { user, isAuthenticated } = useAuthStore()

  return (
    <nav className="bg-railway-blue text-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-primary-500 p-2 rounded-lg group-hover:scale-105 transition-transform">
              <Train className="w-6 h-6 text-railway-blue" />
            </div>
            <span className="font-display font-bold text-xl">SeatSwap</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/about" className="hover:text-primary-400 transition-colors">About</Link>
            {/* <Link to="/how-it-works" className="hover:text-primary-400 transition-colors">How It Works</Link> */}
            <Link to="/faq" className="hover:text-primary-400 transition-colors">FAQ</Link>
            <Link to="/contact" className="hover:text-primary-400 transition-colors">Contact</Link>
            {/* <Link to="/privacy" className="hover:text-primary-400 transition-colors">Privacy</Link> */}
            {/* <Link to="/terms" className="hover:text-primary-400 transition-colors">Terms</Link> */}
            {/* <Link to="/refunds" className="hover:text-primary-400 transition-colors">Refunds</Link> */}
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="hover:text-primary-400 transition-colors">
                  My Trips
                </Link>
                <Link to="/tickets/upload" className="hover:text-primary-400 transition-colors">
                  Upload Ticket
                </Link>
                <Link to="/exchange/requests" className="hover:text-primary-400 transition-colors">
                  Requests
                </Link>
                <button className="relative p-2 hover:bg-white/10 rounded-lg transition-colors">
                  <Bell className="w-5 h-5" />
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                </button>
                <Link to="/profile" className="flex items-center gap-2 hover:bg-white/10 px-3 py-2 rounded-lg transition-colors">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-railway-blue" />
                  </div>
                  <span className="font-medium">{user?.name?.split(' ')[0]}</span>
                </Link>
              </>
            ) : (
              <>
                {/* <Link to="/login" className="hover:text-primary-400 transition-colors">
                  Login
                </Link> */}
                <Link to="/login" className="btn-secondary !py-2 !px-4 text-sm">
                  Login
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-blue-900 border-t border-white/10">
          <div className="px-4 py-4 space-y-2">
                <Link to="/about" className="block py-2 hover:text-primary-400">About</Link>
                {/* <Link to="/how-it-works" className="block py-2 hover:text-primary-400">How It Works</Link> */}
                <Link to="/faq" className="block py-2 hover:text-primary-400">FAQ</Link>
                <Link to="/contact" className="block py-2 hover:text-primary-400">Contact</Link>
                {/* <Link to="/privacy" className="block py-2 hover:text-primary-400">Privacy</Link> */}
                {/* <Link to="/terms" className="block py-2 hover:text-primary-400">Terms</Link> */}
                {/* <Link to="/refunds" className="block py-2 hover:text-primary-400">Refunds</Link> */}
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="block py-2 hover:text-primary-400">My Trips</Link>
                <Link to="/tickets/upload" className="block py-2 hover:text-primary-400">Upload Ticket</Link>
                <Link to="/exchange/requests" className="block py-2 hover:text-primary-400">Requests</Link>
                <Link to="/profile" className="block py-2 hover:text-primary-400">Profile</Link>
              </>
            ) : (
              <>
                <Link to="/login" className="block py-2 hover:text-primary-400">Login</Link>
                {/* <Link to="/login" className="block py-2 text-primary-400">Get Started</Link> */}
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}

