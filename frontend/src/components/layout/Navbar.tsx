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
          <Link to="/" className="flex items-center gap-2 group">
            <div className="bg-primary-500 p-2 rounded-lg group-hover:scale-105 transition-transform">
              <Train className="w-6 h-6 text-railway-blue" />
            </div>
            <span className="font-display font-bold text-xl">SeatSwap</span>
          </Link>

          <div className="hidden md:flex items-center gap-3 lg:gap-6">
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
                <Link to="/profile" className="flex items-center gap-2 hover:bg-white/10 px-2 lg:px-3 py-2 rounded-lg transition-colors max-w-[140px] lg:max-w-none">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center shrink-0">
                    <User className="w-4 h-4 text-railway-blue" />
                  </div>
                  <span className="font-medium truncate hidden lg:inline">{user?.name?.split(' ')[0]}</span>
                </Link>
              </>
            ) : (
              <Link to="/login" className="btn-secondary !py-2 !px-4 text-sm">
                Login
              </Link>
            )}
          </div>

          <button
            className="md:hidden p-2"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {isMenuOpen && (
        <div className="md:hidden bg-blue-900 border-t border-white/10">
          <div className="px-4 py-4 space-y-2">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="block py-2 hover:text-primary-400" onClick={() => setIsMenuOpen(false)}>
                  My Trips
                </Link>
                <Link to="/tickets/upload" className="block py-2 hover:text-primary-400" onClick={() => setIsMenuOpen(false)}>
                  Upload Ticket
                </Link>
                <Link to="/exchange/requests" className="block py-2 hover:text-primary-400" onClick={() => setIsMenuOpen(false)}>
                  Requests
                </Link>
                <Link to="/profile" className="block py-2 hover:text-primary-400" onClick={() => setIsMenuOpen(false)}>
                  Profile
                </Link>
              </>
            ) : (
              <Link to="/login" className="block py-2 hover:text-primary-400" onClick={() => setIsMenuOpen(false)}>
                Login
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
