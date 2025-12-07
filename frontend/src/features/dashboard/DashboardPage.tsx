import { Link } from 'react-router-dom'
import { Plus, Train, Calendar, ArrowRight } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { TicketCard } from '@/components/ticket/TicketCard'
import { useAuthStore } from '@/store/authStore'
import { Ticket } from '@/types'
import { ticketApi } from '@/services/api'

export function DashboardPage() {
  const { user } = useAuthStore()
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTickets()
  }, [])

  const loadTickets = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await ticketApi.getAll()
      // Transform API response to Ticket format
      const transformedTickets: Ticket[] = response.data.map((t: any) => ({
        id: t.id,
        userId: user?.id || '',
        pnr: t.pnr,
        trainNumber: t.train_number,
        trainName: t.train_name,
        travelDate: new Date(t.travel_date),
        boardingStation: t.boarding_station,
        destinationStation: t.destination_station,
        classType: t.class_type,
        quota: t.quota || 'GN',
        status: t.status || 'active',
        passengers: t.passengers || [],
        createdAt: new Date(t.created_at || Date.now()),
        updatedAt: new Date(t.updated_at || Date.now()),
      }))
      setTickets(transformedTickets)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load tickets')
      console.error('Error loading tickets:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteTicket = async (ticketId: string) => {
    const ticket = tickets.find(t => t.id === ticketId)
    const confirmMessage = ticket
      ? `Are you sure you want to delete ticket ${ticket.trainNumber} (PNR: ${ticket.pnr})? This action cannot be undone.`
      : 'Are you sure you want to delete this ticket? This action cannot be undone.'
    
    if (!window.confirm(confirmMessage)) {
      return
    }

    try {
      await ticketApi.delete(ticketId)
      // Remove ticket from local state
      setTickets(tickets.filter(t => t.id !== ticketId))
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete ticket')
      console.error('Error deleting ticket:', err)
    }
  }

  const upcomingTickets = tickets.filter(t => new Date(t.travelDate) >= new Date())
  const pastTickets = tickets.filter(t => new Date(t.travelDate) < new Date())

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
          { label: 'Pending Requests', value: 0, icon: Calendar },
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

      {/* Error Message */}
      {error && (
        <Card className="mb-8 border-red-200 bg-red-50">
          <CardContent className="p-4">
            <p className="text-red-700">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Upcoming Trips */}
      <section className="mb-12">
        <h2 className="font-display text-xl font-bold text-slate-900 mb-4">
          Upcoming Trips
        </h2>

        {isLoading ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-slate-600">Loading tickets...</p>
            </CardContent>
          </Card>
        ) : upcomingTickets.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {upcomingTickets.map((ticket) => (
              <TicketCard key={ticket.id} ticket={ticket} onDelete={handleDeleteTicket} />
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
              <TicketCard key={ticket.id} ticket={ticket} showActions={false} onDelete={handleDeleteTicket} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

