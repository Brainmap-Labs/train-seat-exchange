import { Link } from 'react-router-dom'
import { Plus, Train, Calendar, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { TicketCard } from '@/components/ticket/TicketCard'
import { useAuthStore } from '@/store/authStore'
import { Ticket } from '@/types'

// Mock data - replace with API call
const mockTickets: Ticket[] = [
  {
    id: '1',
    userId: '1',
    pnr: '4521678901',
    trainNumber: '12301',
    trainName: 'Howrah Rajdhani',
    travelDate: new Date('2025-01-15'),
    boardingStation: { code: 'NDLS', name: 'New Delhi' },
    destinationStation: { code: 'HWH', name: 'Howrah Junction' },
    classType: '3A',
    quota: 'GN',
    status: 'active',
    passengers: [
      { id: '1', name: 'Rahul Kumar', age: 35, gender: 'M', coach: 'B2', seatNumber: 45, berthType: 'LB', bookingStatus: 'CNF', currentStatus: 'CNF' },
      { id: '2', name: 'Priya Kumar', age: 32, gender: 'F', coach: 'B2', seatNumber: 47, berthType: 'MB', bookingStatus: 'CNF', currentStatus: 'CNF' },
      { id: '3', name: 'Aryan Kumar', age: 8, gender: 'M', coach: 'B3', seatNumber: 12, berthType: 'UB', bookingStatus: 'CNF', currentStatus: 'CNF' },
    ],
    createdAt: new Date(),
    updatedAt: new Date(),
  },
]

export function DashboardPage() {
  const { user } = useAuthStore()
  const upcomingTickets = mockTickets.filter(t => new Date(t.travelDate) >= new Date())
  const pastTickets = mockTickets.filter(t => new Date(t.travelDate) < new Date())

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-3xl font-bold text-slate-900">
            Welcome back, {user?.name?.split(' ')[0] || 'Traveler'}!
          </h1>
          <p className="text-slate-600 mt-1">Manage your trips and seat exchanges</p>
        </div>
        <Link to="/tickets/upload">
          <Button>
            <Plus className="w-5 h-5 mr-2" />
            Add Ticket
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Upcoming Trips', value: upcomingTickets.length, icon: Train },
          { label: 'Total Exchanges', value: user?.totalExchanges || 0, icon: ArrowRight },
          { label: 'Your Rating', value: user?.rating?.toFixed(1) || '—', icon: Calendar },
          { label: 'Pending Requests', value: 2, icon: Calendar },
        ].map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="bg-primary-100 p-2 rounded-lg">
                  <stat.icon className="w-5 h-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
                  <p className="text-sm text-slate-500">{stat.label}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Upcoming Trips */}
      <section className="mb-12">
        <h2 className="font-display text-xl font-bold text-slate-900 mb-4">
          Upcoming Trips
        </h2>

        {upcomingTickets.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upcomingTickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} />
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <Train className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="font-semibold text-slate-900 mb-2">No upcoming trips</h3>
              <p className="text-slate-600 mb-4">Upload your train ticket to get started</p>
              <Link to="/tickets/upload">
                <Button variant="outline">Upload Ticket</Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </section>

      {/* Past Trips */}
      {pastTickets.length > 0 && (
        <section>
          <h2 className="font-display text-xl font-bold text-slate-900 mb-4">
            Past Trips
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {pastTickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} showActions={false} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

